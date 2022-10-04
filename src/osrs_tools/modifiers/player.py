# roll & damage modifier methods ##########################################

from __future__ import annotations

import math
from copy import copy
from dataclasses import dataclass

from osrs_tools.character import Character
from osrs_tools.character.monster import Monster
from osrs_tools.character.monster.cox import CoxMonster, Guardian, IceDemon
from osrs_tools.character.monster.toa import ToaMonster
from osrs_tools.character.player import AutocastError, NoTaskError, Player
from osrs_tools.data import (
    CRYSTAL_PIECE_ARM,
    CRYSTAL_PIECE_DM,
    CRYSTAL_SET_ARM,
    CRYSTAL_SET_DM,
    DT,
    INQUISITOR_PIECE_BONUS,
    INQUISITOR_SET_BONUS,
    MagicDamageTypes,
    MeleeDamageTypes,
    MonsterLocations,
    MonsterTypes,
    RangedDamageTypes,
    Slayer,
    Slots,
    Styles,
)
from osrs_tools.gear import Chinchompas, SalveAmuletEI, SalveAmuletI
from osrs_tools.gear.common_gear import (
    AbyssalBludgeon,
    Arclight,
    BerserkerNecklace,
    ChaosGauntlets,
    CrawsBow,
    CrystalArmorSet,
    DragonHunterCrossbow,
    DragonHunterLance,
    InquisitorSet,
    Seercull,
    SlayerHelmetI,
    ThammaronsSceptre,
    TomeOfFire,
    TwistedBow,
    ViggorasChainmace,
)
from osrs_tools.spell.spell import Spell
from osrs_tools.spell.spells import BoltSpells, FireSpells, StandardSpell
from osrs_tools.stats import AggressiveStats, additional_stats
from osrs_tools.style import BulwarkStyles, ChinchompaStyles
from osrs_tools.tracked_value import (
    DamageModifier,
    DamageValue,
    EquipmentStat,
    Level,
    LevelModifier,
    ModifierPair,
    RollModifier,
    TrackedFloat,
    VoidModifiers,
    create_modifier_pair,
)

from .character import CharacterModifiers

###########################################################################
# main classes                                                            #
###########################################################################


@dataclass
class PlayerModifiers(CharacterModifiers):
    player: Player
    target: Character
    special_attack: bool
    distance: int | None
    spell: Spell | None
    additional_targets: int | Character | list[Character]
    dt: DT

    # properties

    @property
    def aggressive_bonus(self) -> AggressiveStats:
        """Wrapper for Player.aggressive_bonus with additional functionality.

        Dinh's bulwark and smoke staff.

        Returns
        -------

        AggressiveStats
        """
        lad = self.player
        target = self.target
        ab = lad.eqp.aggressive_bonus
        ab2 = copy(ab)

        if (dinhs := self._dinhs_strength_modifier()) is not None:
            ab2.melee_strength += dinhs
        elif (smoke := self._smoke_modifier()) is not None:
            _, gear_damage_bonus = smoke
            ab2.magic_strength += gear_damage_bonus
        elif lad.eqp.tumekens_shadow:
            if isinstance(target, Monster):
                if MonsterTypes.TOA in target.special_attributes:
                    tumeken_mod = 4
                else:
                    tumeken_mod = 3
            else:
                tumeken_mod = 3

            ab2.magic_attack *= tumeken_mod
            raw_magic_strength = tumeken_mod * float(ab.magic_strength)
            ab2.magic_strength = TrackedFloat(min([max([0, raw_magic_strength]), 1.0]))

        return ab2

    def get_modifiers(self) -> tuple[list[RollModifier], list[DamageModifier]]:
        """Get all attack roll and damage modifiers relevant to the calculation.

        This is a bit of a long and bloated function, so I'm glad I
        removed it from the main tree at least. Also, it allowed for
        simpler special attack roll and defence roll calculations.

        Returns
        -------
        tuple[list[RollModifier], list[DamageModifier]]
            A tuple with a list of roll modifiers and a list of damage modifiers.
        """

        # basic attack roll and damage modifiers
        salve_modifiers = self._salve_modifier()
        slayer_modifiers = self._slayer_modifier()

        # Only one of slayer or salve bonus is allowed
        if salve_modifiers is not None:
            _sos_mods = salve_modifiers
        elif slayer_modifiers is not None:
            _sos_mods = slayer_modifiers
        else:
            _sos_mods = None

        # Attack roll & damage modifiers
        crystal_modifiers = self._crystal_armor_modifier()
        arclight_modifiers = self._arclight_modifier()
        draconic_modifiers = self._draconic_modifier()
        wilderness_modifiers = self._wilderness_modifier()
        twisted_bow_modifiers = self._twisted_bow_modifier()
        obsidian_modifiers = self._obsidian_modifier()
        inquisitor_modifiers = self._inquisitor_modifier()

        # attack roll modifiers
        chinchompa_arm = self._chin_modifier()
        smoke_values = self._smoke_modifier()

        if smoke_values is not None:
            smoke_arm, _ = smoke_values
        else:
            smoke_arm = None

        # damage modifiers
        magic_dm = self._magic_damage_modifier()
        berserker_dm = self._berserker_necklace_damage_modifier()
        guardians_dm = self._guardians_damage_modifier()
        ice_demon_dm = self._ice_demon_damage_modifier()
        tome_dm = self._tome_of_fire_damage_modifier()

        _mod_or_none = [
            _sos_mods,
            crystal_modifiers,
            arclight_modifiers,
            draconic_modifiers,
            wilderness_modifiers,
            twisted_bow_modifiers,
            obsidian_modifiers,
            inquisitor_modifiers,
            chinchompa_arm,
            magic_dm,
            berserker_dm,
            guardians_dm,
            ice_demon_dm,
            tome_dm,
            smoke_arm,
        ]

        # special modifiers

        _arms: list[RollModifier] = []
        _dms: list[DamageModifier] = []

        for _mod in _mod_or_none:
            if isinstance(_mod, RollModifier):
                _arms.append(_mod)
            elif isinstance(_mod, DamageModifier):
                _dms.append(_mod)
            elif isinstance(_mod, tuple):
                arm, dm = _mod
                _arms.append(arm)
                _dms.append(dm)
            elif _mod is None:
                continue
            else:
                raise TypeError(_mod)

        return _arms, _dms

    def _void_modifiers(self) -> VoidModifiers | None:
        """Returns void level modifiers if the player is wearing either void set.

        Raises
        ------
            ValueError: Raised if the active style damage type is unsupported.

        Returns
        -------
            VoidModifiers | None: A pair of accuracy and strength level
            modifiers if applicable, else None.
        """
        lad = self.player

        if lad.eqp.elite_void_set:
            comment = "elite void"
            if (dt := lad.style.damage_type) in MeleeDamageTypes:
                accuracy_level_modifier = 1.1
                strength_level_modifier = 1.1
            elif dt in RangedDamageTypes:
                accuracy_level_modifier = 1.1
                strength_level_modifier = 1.125
            elif dt in MagicDamageTypes:
                accuracy_level_modifier = 1.45
                strength_level_modifier = 1.025
            else:
                raise ValueError(lad.style.damage_type)

        elif lad.eqp.normal_void_set:
            comment = "normal void"
            if (dt := lad.style.damage_type) in MeleeDamageTypes:
                accuracy_level_modifier = 1.1
                strength_level_modifier = 1.1
            elif dt in RangedDamageTypes:
                accuracy_level_modifier = 1.1
                strength_level_modifier = 1.1
            elif dt in MagicDamageTypes:
                accuracy_level_modifier = 1.45
                strength_level_modifier = 1.1
            else:
                raise ValueError(lad.style.damage_type)

        else:
            return

        alm = LevelModifier(accuracy_level_modifier, comment)
        slm = LevelModifier(strength_level_modifier, comment)

        return alm, slm

    def _salve_modifier(self) -> ModifierPair | None:
        lad = self.player
        chump = self.target

        if not lad.eqp.salve or not isinstance(chump, Monster):
            return

        assert isinstance(chump, Monster)

        if MonsterTypes.UNDEAD in chump.special_attributes:
            comment = "salve"
            if lad.wearing(SalveAmuletI):
                modifier = 7 / 6
            elif lad.wearing(SalveAmuletEI):
                modifier = 1.2
            else:
                raise NotImplementedError

            return create_modifier_pair(modifier, comment)

    def _dinhs_strength_modifier(self) -> EquipmentStat | None:
        """Bonus equipment strength bonus when using Dinh's offensively.

        Source:
            https://oldschool.runescape.wiki/w/Dinh's_bulwark#Strength_buff

        Returns
        -------
        int | None
            _description_
        """
        lad = self.player

        if lad.style != BulwarkStyles[Styles.PUMMEL]:
            return

        db = lad.eqp.defensive_bonus
        mean_def_bonus = sum([db.stab, db.slash, db.crush, db.ranged]) / 4
        value = math.floor((math.floor(mean_def_bonus - 200) / 3) - 38)
        comment = "dinh's passive"

        return EquipmentStat(value, comment)

    def _smoke_modifier(self) -> ModifierPair | None:
        lad = self.player
        _spell = self.spell

        try:
            __spell = _spell if _spell is not None else lad.autocast
        except AutocastError as exc:
            if lad.style.damage_type not in MagicDamageTypes:
                return

            raise exc

        if not lad.eqp.smoke_staff or not isinstance(__spell, StandardSpell):
            return

        arm = 1.1
        gear_damage_bonus = 0.1  # additive
        comment = "smoke staff"

        rm = RollModifier(arm, comment)
        additive_damage_modifier = TrackedFloat(gear_damage_bonus, comment)
        return rm, additive_damage_modifier

    def _magic_damage_modifier(self) -> DamageModifier | None:
        lad = self.player
        _dt = self.dt

        if _dt not in MagicDamageTypes:
            return

        value = 1.0 + float(self.aggressive_bonus.magic_strength)
        comment = "magic damage"
        return DamageModifier(value, comment)

    def _slayer_modifier(self) -> ModifierPair | None:
        lad = self.player
        chump = self.target
        assert isinstance(chump, Monster)

        if lad.wearing(Seercull):
            return  # seercull cannot benefit from slayer bonus

        if not lad.wearing(SlayerHelmetI):
            return

        if lad.slayer_task is not chump.slayer_category:
            return

        comment = "slayer"
        if (dt := lad.style.damage_type) in MeleeDamageTypes:
            modifier = 7 / 6
        elif dt in RangedDamageTypes:
            modifier = 1.15
        elif dt in MagicDamageTypes:
            modifier = 1.15
        else:
            raise ValueError(dt)

        return create_modifier_pair(modifier, comment)

    def _arclight_modifier(self) -> ModifierPair | None:
        lad = self.player
        chump = self.target

        if lad.wpn == Arclight and isinstance(chump, Monster) and MonsterTypes.DEMON in chump.special_attributes:
            modifier = 1.7
            comment = "arclight"
            return create_modifier_pair(modifier, comment)

    def _draconic_modifier(self) -> ModifierPair | None:
        lad = self.player
        chump = self.target
        assert isinstance(chump, Monster)

        if lad.eqp.dragonbane_weapon and MonsterTypes.DRACONIC in chump.special_attributes:
            comment = "draconic"
            if lad.eqp.wearing(DragonHunterLance):
                modifier = 1.2
            elif lad.eqp.wearing(DragonHunterCrossbow):
                modifier = 1.3
            else:
                raise NotImplementedError

            return create_modifier_pair(modifier, comment)

    def _wilderness_modifier(self) -> ModifierPair | None:
        lad = self.player
        chump = self.target

        if lad.eqp.wilderness_weapon and isinstance(chump, Monster) and chump.location is MonsterLocations.WILDERNESS:
            comment = "wilderness"
            if lad.eqp.wearing(CrawsBow):
                arm = 1.5
                dm = 1.5
            elif lad.eqp.wearing(ViggorasChainmace):
                arm = 1.5
                dm = 1.5
            elif lad.eqp.wearing(ThammaronsSceptre):
                arm = 2
                dm = 1.25
            else:
                raise NotImplementedError

            return RollModifier(arm, comment), DamageModifier(dm, comment)

    def _twisted_bow_modifier(self) -> ModifierPair | None:
        lad = self.player
        chump = self.target

        if lad.wpn != TwistedBow:
            return

        comment = "twisted bow"

        accuracy_modifier_ceiling = 1.40
        damage_modifier_ceiling = 2.50
        _magic_ceiling = 350 if isinstance(chump, CoxMonster) else 250
        magic_ceiling = Level(_magic_ceiling, f"{comment} magic ceiling")

        magic = min(
            [
                max([chump._levels.magic, chump.aggressive_bonus.magic_attack]),
                magic_ceiling,
            ]
        )

        accuracy_modifier_percent = (
            140 + math.floor((10 * 3 * magic / 10 - 10) / 100) - math.floor(((3 * magic / 10 - 100) ** 2 / 100))
        )
        damage_modifier_percent = (
            250 + math.floor((10 * 3 * magic / 10 - 14) / 100) - math.floor(((3 * magic / 10 - 140) ** 2 / 100))
        )

        arm = min([accuracy_modifier_ceiling, accuracy_modifier_percent / 100])
        dm = min([damage_modifier_ceiling, damage_modifier_percent / 100])
        return RollModifier(arm, comment), DamageModifier(dm, comment)

    def _obsidian_modifier(self) -> ModifierPair | None:
        lad = self.player

        if lad.eqp.obsidian_armor_set and lad.eqp.obsidian_weapon:
            modifier = 1.1
            comment = "obsidian weapon & armour set"
            return create_modifier_pair(modifier, comment)

    def _berserker_necklace_damage_modifier(self) -> DamageModifier | None:
        lad = self.player

        if lad.wearing(BerserkerNecklace) and lad.eqp.obsidian_weapon:
            modifier = 1.2
            comment = "obsidian weapon & berserker necklace"
            return DamageModifier(modifier, comment)

    def _dharok_damage_modifier(self) -> DamageModifier | None:
        lad = self.player

        if lad.eqp.dharok_set:
            base_hp = lad._levels.hitpoints
            modifier = 1 + (base_hp - lad.hp) / 100 * (base_hp / 100)
            comment = "dharok's set"
            return DamageModifier(modifier, comment)

    def _leafy_modifier(self) -> ModifierPair | None:
        lad = self.player
        chump = self.target

        if lad.eqp.leafy_weapon and isinstance(chump, Monster) and MonsterTypes.LEAFY in chump.special_attributes:
            modifier = 1.175
            comment = "leafy"
            return create_modifier_pair(modifier, comment)

    def _keris_damage_modifier(self) -> DamageModifier | None:
        lad = self.player
        chump = self.target

        if lad.eqp.keris and isinstance(chump, Monster) and MonsterTypes.KALPHITE in chump.special_attributes:
            modifier = 4 / 3
            comment = "keris"
            return DamageModifier(modifier, comment)

    def _crystal_armor_modifier(self) -> ModifierPair | None:
        lad = self.player

        if lad.eqp.crystal_weapon:
            comment = "crystal weapon & armour"

            if lad.eqp.crystal_armor_set:
                _arm = 1 + CRYSTAL_SET_ARM + 3 * CRYSTAL_PIECE_ARM
                _dm = 1 + CRYSTAL_SET_DM + 3 * CRYSTAL_PIECE_DM
            else:
                _arm = 1
                _dm = 1

                qualifying_armor = CrystalArmorSet

                for armor in qualifying_armor:
                    if lad.wearing(armor):
                        _arm += CRYSTAL_PIECE_ARM
                        _dm += CRYSTAL_PIECE_DM

                # don't return if no crystal pieces are equipped
                if _arm == 1 and _dm == 1:
                    return

            return RollModifier(_arm, comment), DamageModifier(_dm, comment)

    def _inquisitor_modifier(self) -> ModifierPair | None:
        lad = self.player

        if lad.style.damage_type is DT.CRUSH:
            comment = "inquisitor"

            if lad.eqp.inquisitor_set:
                modifier = 1 + INQUISITOR_SET_BONUS + 3 * INQUISITOR_PIECE_BONUS
            else:
                modifier = 1
                qualifying_armor = InquisitorSet

                for armor in qualifying_armor:
                    if lad.wearing(armor):
                        modifier += INQUISITOR_PIECE_BONUS

                if modifier == 1:
                    return

            return create_modifier_pair(modifier, comment)

    def _chin_modifier(self) -> RollModifier | None:
        lad = self.player
        dist = self.distance

        if dist is None or not lad.eqp[Slots.WEAPON] not in Chinchompas:
            return

        comment = "chinchompa"
        if lad.style == ChinchompaStyles[Styles.SHORT_FUSE]:
            if 0 <= dist <= 3:
                chin_arm = 1.00
            elif 4 <= dist <= 6:
                chin_arm = 0.75
            else:
                chin_arm = 0.50
        elif lad.style == ChinchompaStyles[Styles.MEDIUM_FUSE]:
            if 4 <= dist <= 6:
                chin_arm = 1.00
            else:
                chin_arm = 0.75
        elif lad.style == ChinchompaStyles[Styles.LONG_FUSE]:
            if 0 <= dist <= 3:
                chin_arm = 0.50
            elif 4 <= dist <= 6:
                chin_arm = 0.75
            else:
                chin_arm = 1.00
        else:
            raise ValueError(lad.style)

        return RollModifier(chin_arm, comment)

    def _vampyric_modifier(self):
        raise NotImplementedError

    def _tome_of_fire_damage_modifier(self) -> DamageModifier | None:
        lad = self.player

        if lad.eqp._shield is None:
            return

        if lad.eqp[Slots.SHIELD] == TomeOfFire and self.spell in FireSpells:
            modifier = 1.50
            comment = "tome of fire"
            return DamageModifier(modifier, comment)

    def chaos_gauntlets_damage_bonus(self) -> DamageValue | None:
        """Returns the flat damage bonus provided by chaos gauntlets.

        Paramters
        ---------

        spell : Spell, optional
            The spell being cast. Defaults to None.

        Returns
        -------
        DamageValue | None
        """
        lad = self.player
        _spell = self.spell

        if not lad.eqp._hands == ChaosGauntlets:
            return

        try:
            __spell = _spell if _spell is not None else lad.autocast
        except AutocastError as exc:
            if lad.style.damage_type not in MagicDamageTypes:
                return

            raise exc

        if __spell in BoltSpells:
            comment = "chaos gauntlets"
            damage_boost = DamageValue(3, comment)
            return damage_boost

    def _guardians_damage_modifier(self) -> DamageModifier | None:
        lad = self.player
        chump = self.target

        if not lad.eqp.pickaxe or not isinstance(chump, Guardian):
            return

        clmp_mining = min([100, lad.lvl.mining])

        dm = (50 + clmp_mining + lad.wpn.reqs.mining) / 150
        comment = "guardian"
        return DamageModifier(dm, comment)

    def _ice_demon_damage_modifier(self) -> DamageModifier | None:
        lad = self.player
        chump = self.target
        _spell = self.spell

        if not isinstance(chump, IceDemon):
            return

        try:
            _spell = _spell if _spell is not None else lad.autocast
        except AutocastError as exc:
            if lad.style.damage_type in MagicDamageTypes:
                raise exc

        if _spell is None or _spell not in FireSpells:
            damage_modifier = 0.33
        else:
            damage_modifier = 1.50

        comment = "ice demon"
        return DamageModifier(damage_modifier, comment)

    def _abyssal_bludgeon_special_modifier(self) -> DamageModifier | None:
        """Returns the damage modifier an abyssal bludgeon receives.

        Special Attack: Penance

        Parameters
        ----------

        special_attack : bool
            True if performing a special attack, False otherwise.

        Returns
        -------
        DamageModifier | None:
        """
        lad = self.player
        spec = self.special_attack

        if not spec or not lad.wpn == AbyssalBludgeon:
            return

        pp_missing = min([0, lad._levels.prayer - lad.lvl.prayer])
        damage_modifier = 1 + (int(pp_missing) * 0.005)
        comment = "abyssal bludgeon: penance"

        return DamageModifier(damage_modifier, comment)

    # class methods

    @classmethod
    def simple(cls, player: Player, target: Character):

        if player._autocast is not None:
            spell = player.autocast
            dt = DT.MAGIC
        else:
            spell = None
            dt = player.style.damage_type

        return cls(
            player=player, target=target, special_attack=False, distance=None, spell=spell, additional_targets=0, dt=dt
        )
