"""Handles the bulk of combat calculations for players.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-25                                                         #
###############################################################################
"""

import math
from dataclasses import dataclass
from re import S

import numpy as np
from osrs_tools import gear
from osrs_tools import utils_combat as cmb
from osrs_tools.character import Character
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import AutocastError, Player
from osrs_tools.combat import Damage, Hitsplat
from osrs_tools.data import (
    ABYSSAL_BLUDGEON_DMG_MOD,
    BOLT_PROC,
    DIAMOND_BOLTS_DMG,
    DIAMOND_BOLTS_PROC,
    DT,
    PVM_MAX_TARGETS,
    RUBY_BOLTS_HP_CAP,
    RUBY_BOLTS_HP_RATIO,
    MagicDamageTypes,
    MeleeDamageTypes,
    RangedDamageTypes,
)
from osrs_tools.gear import BoneDagger, Chinchompas, DorgeshuunCrossbow, SpecialWeapon, SpecialWeaponError
from osrs_tools.modifiers import MonsterModifiers, PlayerModifiers
from osrs_tools.spell import Spell
from osrs_tools.tracked_value import DamageModifier, EquipmentStat, TrackedFloat

from .damage_calculation import DamageCalculation


@dataclass
class PvMCalc(DamageCalculation):
    attacker: Player
    defender: Monster

    def _get_damage_type(self, spell: Spell | None = None):
        # spell overrides attack styles so we check for it this way
        try:
            spell = spell if spell is not None else self.attacker.autocast
        except AutocastError as exc:
            if self.attacker.style.damage_type in MagicDamageTypes:
                raise exc

        dt = self.attacker.style.damage_type if spell is None else DT.MAGIC
        return dt

    def get_damage(
        self,
        special_attack: bool = False,
        distance: int | None = None,
        spell: Spell | None = None,
        additional_targets: int | Character | list[Character] = 0,
    ) -> Damage:
        """Returns a damage distribution.

        Parameters
        ----------
        special_attack : bool, optional
            True if a special attack is performed, by default False
        distance : int | None, optional
            Distance between the attacker and target, with 0 being the same
            tile, by default None
        spell : Spell | None, optional
            A specific spell being cast, will override autocast, by default None
        additional_targets : int | Character | list[Character], optional
            Additional targets that will be hit by AoE attacks, by default 0

        Returns
        -------
        Damage
        """

        # shorthand
        lad = self.attacker
        target = self.defender
        eqp = self.attacker.eqp
        wpn = self.attacker.wpn

        # special attack validation
        if special_attack:
            if not isinstance(wpn, SpecialWeapon):
                raise SpecialWeaponError(wpn)

        # get damage type and bonuses
        dt = self._get_damage_type(spell)

        PMods = PlayerModifiers(lad, target, special_attack, distance, spell, additional_targets, dt)
        ab = PMods.aggressive_bonus  # more information (dinhs/smoke)
        accuracy_bonus, strength_bonus = ab[dt]

        # effective levels and strength bonus validation
        if dt in MeleeDamageTypes:
            _eff_acc_lvl = lad.effective_melee_attack_level
            assert isinstance(strength_bonus, EquipmentStat)
        elif dt in RangedDamageTypes:
            _eff_acc_lvl = lad.effective_ranged_attack_level
            assert isinstance(strength_bonus, EquipmentStat)
        elif dt in MagicDamageTypes:
            _eff_acc_lvl = lad.effective_magic_attack_level
            assert isinstance(strength_bonus, TrackedFloat)
        else:
            raise ValueError(dt)

        arms, dms = PMods.get_modifiers()

        # generic special properties. If for whatever reason this is wrong just
        # re-calculate whatever values you need in __get_special_distribution.

        if isinstance(wpn, SpecialWeapon):
            full_arms = arms + wpn.special_attack_roll_modifiers
            full_dms = dms + wpn.special_damage_modifiers

            try:
                defence_roll_dt = wpn.special_defence_roll
            except AssertionError:
                defence_roll_dt = dt

        else:
            full_arms = arms
            full_dms = dms
            defence_roll_dt = dt

        MMods = MonsterModifiers(target, lad, defence_roll_dt)

        # # beeg parameters # #################################################
        att_roll = cmb.maximum_roll(_eff_acc_lvl, accuracy_bonus, *full_arms)
        def_roll = MMods.defence_roll()
        accuracy = cmb.accuracy(att_roll, def_roll)
        max_hit = lad.max_hit(*full_dms, spell=spell)

        if (_dam := PMods.chaos_gauntlets_damage_bonus()) is not None:
            max_hit += _dam

        # osmumten's fang rolls twice and only fails if both attacks fail
        if lad.eqp.osmumtens_fang:
            accuracy = 1 - (1 - accuracy) ** 2

        attack_speed = lad.attack_speed(spell)

        # # inner functions # #################################################
        def __get_crossbow_distribution() -> Damage:
            """Get the damage distribution for a crossbow.

            Returns
            -------
            Damage
            """

            def __proc_chance(base_activation_chance: float) -> float:
                """Find the proc chance of a bolt effect.

                Parameters
                ----------
                base_activation_chance : float
                    The probability as a float of the effect procuring.

                Returns
                -------
                float
                    The probability as a float of the effect procuring.
                """
                _proc_chance = base_activation_chance

                # TODO: Order of these two?

                if lad.kandardin_hard_diary:
                    _proc_chance += (1 / 10) * base_activation_chance

                if wpn == gear.ArmadylCrossbow and special_attack:
                    _proc_chance *= 2

                return _proc_chance

            if eqp.enchanted_diamond_bolts:
                proc_chance = __proc_chance(DIAMOND_BOLTS_PROC)
                dmg_mod = DamageModifier(DIAMOND_BOLTS_DMG, f"diamond {BOLT_PROC}")

                if wpn == gear.ZaryteCrossbow:
                    dmg_mod += dmg_mod / 10

                effect_max_hit = max_hit * dmg_mod

                dmg_vals = np.arange(int(effect_max_hit) + 1)
                prbs = np.zeros(dmg_vals.shape)

                for dv in dmg_vals:
                    # chance of damage value occuring as a result of...

                    # an unsuccessful attack
                    p_miss = (1 - proc_chance) * (1 - accuracy) if dv == 0 else 0.0

                    if dv > max_hit:
                        p_norm = 0.0
                    else:
                        # a successful attack
                        p_norm = (1 - proc_chance) * accuracy * 1 / (int(max_hit) + 1)

                    # a proc
                    p_effect = proc_chance * 1 / (int(effect_max_hit) + 1)

                    prbs[dv] = sum([p_miss, p_norm, p_effect])

            elif eqp.enchanted_ruby_bolts:
                proc_chance = __proc_chance(0.06)
                hp_ratio = RUBY_BOLTS_HP_RATIO
                hp_cap = RUBY_BOLTS_HP_CAP

                if wpn == gear.ZaryteCrossbow:
                    hp_ratio *= 0.10

                actual = self.defender.hp * hp_ratio
                possible = hp_cap * hp_ratio

                effect_damage = min([actual, possible])
                true_max = max([max_hit, effect_damage])

                dmg_vals = np.arange(int(true_max) + 1)
                prbs = np.zeros(dmg_vals.shape)

                for dv in dmg_vals:
                    p_miss = 0 if dv > 0 else (1 - proc_chance) * (1 - accuracy)

                    if dv <= max_hit:
                        p_norm = (1 - proc_chance) * accuracy * 1 / (int(max_hit) + 1)
                    else:
                        p_norm = 0

                    p_effect = proc_chance if dv == effect_damage else 0

            else:
                raise NotImplementedError

            hitsplat = Hitsplat(dmg_vals, prbs)

            return Damage(attack_speed, [hitsplat])

        def __get_special_distribution() -> Damage:
            """Return a special or unique distribution based on weapon.

            Returns
            -------
            Damage
            """

            assert isinstance(wpn, SpecialWeapon)

            # options for partial completion in logic tree
            damage = None
            hs = None
            _max_hit = None
            _accuracy = None

            # osmumten's fang special behaves normally lmao

            # dorgeshuun weapons: crossbow & dagger
            if lad.eqp.weapon in [BoneDagger, DorgeshuunCrossbow] and target.last_attacked_by is not self:
                _accuracy = 1.0

            # seercull
            elif wpn == gear.Seercull:
                _pry = lad.prayers
                if not (_pry.ranged_attack is None and _pry.ranged_strength is None):
                    raise SpecialWeaponError(f"{wpn} cannot have active prayers")

                _accuracy = 1.0

            # abyssal bludgeon
            elif lad.wearing(gear.AbyssalBludgeon):
                pp_missing = min([0, int(lad._levels.prayer - lad.lvl.prayer)])
                value = 1 + (ABYSSAL_BLUDGEON_DMG_MOD * pp_missing)
                comment = "Abyssal bludgeon: Penance"

                full_dms = dms + [DamageModifier(value, comment)]
                _max_hit = lad.max_hit(*full_dms, spell=spell)

            # Dragon Claws: Slice and Dice
            elif lad.wearing(gear.DragonClaws):
                # scenario A: first attack is successful (4-2-1-1)
                p_A = accuracy
                min_hit_A = math.floor(int(max_hit) / 2)
                max_hit_A = int(max_hit) - 1

                dmg_val_A1 = list(range(min_hit_A, max_hit_A + 1))
                dmg_val_A2 = [math.floor(dmg / 2) for dmg in dmg_val_A1]
                dmg_val_A3 = [math.floor(dmg / 2) for dmg in dmg_val_A2]
                dmg_val_A4 = [dmg for dmg in dmg_val_A3]  # TODO: probability of the 1 ocurring?
                n_A = len(dmg_val_A1)

                # scenario B: second attack is successful (0-4-2-2)
                p_B = accuracy * (1 - accuracy)
                min_hit_B = math.floor(int(max_hit) * 3 / 8)
                max_hit_B = math.floor(int(max_hit) * 7 / 8)

                dmg_val_B2 = list(range(min_hit_B, max_hit_B + 1))
                dmg_val_B3 = [math.floor(dmg / 2) for dmg in dmg_val_B2]
                dmg_val_B4 = [dmg for dmg in dmg_val_A3]
                n_B = len(dmg_val_B2)

                # scenario C: third attack is successful (0-0-3-3)
                p_C = accuracy * (1 - accuracy) ** 2
                min_hit_C = math.floor(int(max_hit) * 1 / 4)
                max_hit_C = math.floor(int(max_hit) * 3 / 4)

                dmg_val_C3 = list(range(min_hit_C, max_hit_C + 1))
                dmg_val_C4 = [dmg for dmg in dmg_val_C3]
                n_C = len(dmg_val_C3)

                # scenario D: fourth attack is successful (0-0-0-5)
                p_D = accuracy * (1 - accuracy) ** 3
                min_hit_D = math.floor(int(max_hit) * 1 / 4)
                max_hit_D = math.floor(int(max_hit) * 5 / 4)

                dmg_val_D4 = list(range(min_hit_D, max_hit_D + 1))
                n_D = len(dmg_val_D4)

                # scenario E: The big buh (0-0-0-0)
                p_E = (1 - accuracy) ** 4
                assert sum([p_A, p_B, p_C, p_D, p_E]) == 1

                # Hitsplat 1
                hs_1_min = 0
                hs_1_max = max_hit_A
                hs_1_dmg = np.arange(hs_1_min, hs_1_max + 1)
                hs_1_prb = np.zeros(shape=hs_1_dmg.shape)

                hs_1_prb[0] = p_B + p_C + p_D + p_E
                for idx, dv in enumerate(hs_1_dmg):
                    if dv in dmg_val_A1:
                        hs_1_prb[idx] += p_A / n_A

                # Hitsplat 2
                hs_2_min = 0
                hs_2_max = max_hit_B
                hs_2_dmg = np.arange(hs_2_min, hs_2_max + 1)
                hs_2_prb = np.zeros(shape=hs_2_dmg.shape)

                hs_2_prb[0] = p_C + p_D + p_E
                for idx, dv in enumerate(hs_2_dmg):
                    if dv in dmg_val_A2:
                        hs_2_prb[idx] += p_A / n_A

                    if dv in dmg_val_B2:
                        hs_2_prb[idx] += p_B / n_B

                # Hitsplat 3
                hs_3_min = 0
                hs_3_max = max_hit_C
                hs_3_dmg = np.arange(hs_3_min, hs_3_max + 1)
                hs_3_prb = np.zeros(shape=hs_3_dmg.shape)

                hs_3_prb[0] += p_D + 0.5 * p_E
                hs_3_prb[1] += 0.5 * p_E
                for idx, dv in enumerate(hs_3_dmg):
                    if dv in dmg_val_A3:
                        hs_3_prb[idx] += p_A / n_A

                    if dv in dmg_val_B3:
                        hs_3_prb[idx] += p_B / n_B

                    if dv in dmg_val_C3:
                        hs_3_prb[idx] += p_C / n_C

                # Hitsplat 4
                hs_4_min = 0
                hs_4_max = max_hit_D
                hs_4_dmg = np.arange(hs_4_min, hs_4_max + 1)
                hs_4_prb = np.zeros(shape=hs_4_dmg.shape)

                hs_4_prb[0] += 0.5 * p_E
                hs_4_prb[1] += 0.5 * p_E
                for idx, dv in enumerate(hs_4_dmg):
                    if dv in dmg_val_A4:
                        hs_4_prb[idx] += p_A / n_A

                    if dv in dmg_val_B4:
                        hs_4_prb[idx] += p_B / n_B

                    if dv in dmg_val_C4:
                        hs_4_prb[idx] += p_C / n_C

                    if dv in dmg_val_D4:
                        hs_4_prb[idx] += p_D / n_D

                hs = [
                    Hitsplat.clamp_to_hitpoints_cap(dmg, prb, target.hp)
                    for dmg, prb in [
                        (hs_1_dmg, hs_1_prb),
                        (hs_2_dmg, hs_2_prb),
                        (hs_3_dmg, hs_3_prb),
                        (hs_4_dmg, hs_4_prb),
                    ]
                ]

            # Abyssal Dagger: # TODO: Name
            elif lad.wearing(gear.AbyssalDagger):
                raise NotImplementedError

            # Dragon Dagger: # TODO: Name
            elif lad.wearing(gear.DragonDagger):
                raise NotImplementedError

            else:
                # perform any necessary prep
                pass

            # some weapons override accuracy directly
            if _accuracy is None:
                _accuracy = accuracy

            if _max_hit is None:
                _max_hit = max_hit

            # return

            if damage is not None:
                return damage

            if hs is not None:
                return Damage(attack_speed, hs)

            return Damage.basic_constructor(lad.attack_speed(), _max_hit, _accuracy, target.hp)

        def __get_standard_distribution() -> Damage:
            """Return a normal distribution from accuracy and max hit.

            This is not to be confused in any way with a normal distribution.

            Returns
            -------
            Damage
            """

            hs: list[Hitsplat] = []
            damage = None

            if lad.wpn == gear.ScytheOfVitur:
                # hits with 100%, 50%, and 25% max hit.
                for mod_power in range(0, -3, -1):
                    _mh = max_hit * (2**mod_power)
                    _hs = Hitsplat.basic_constructor(_mh, accuracy, target.hp)
                    hs.append(_hs)

            # osmumten's fang
            elif lad.eqp.osmumtens_fang:
                # standard_max = lad.max_hit(*full_dms, spell=spell)
                _min_hit = math.floor(0.15 * int(max_hit))
                _max_hit = math.floor(0.85 * int(max_hit))
                dmg_ary = np.arange(_min_hit, _max_hit + 1)
                prb_ary = np.zeros(shape=dmg_ary.shape)

                for idx in prb_ary:
                    prb_ary[idx] = accuracy * (1 / (_max_hit - _min_hit + 1))

                prb_ary[0] += 1 - accuracy

                hs = [Hitsplat.clamp_to_hitpoints_cap(dmg_ary, prb_ary, target.hp)]

            elif eqp.weapon in Chinchompas and additional_targets:
                max_targets = PVM_MAX_TARGETS

                if isinstance(additional_targets, int):
                    targets = min([1 + additional_targets, max_targets])
                    hs = [Hitsplat.basic_constructor(max_hit, accuracy, target.hp) for _ in range(targets)]

                elif isinstance(additional_targets, (list, Character)):
                    if isinstance(additional_targets, list):
                        assert all(isinstance(_at, Character) for _at in additional_targets)
                        _additional_targets = additional_targets
                    else:
                        _additional_targets = [additional_targets]

                    _target: list[Character] = [target]  # type hint necc.
                    targets = _target + _additional_targets
                    clamp = len(targets) <= max_targets
                    targets = targets[:max_targets] if clamp else targets

                    hs = [Hitsplat.basic_constructor(max_hit, accuracy, t.hp) for t in targets]

                else:
                    raise NotImplementedError

            # return

            if damage is not None:
                return damage

            if hs:
                return Damage(attack_speed, hs)

            return Damage.basic_constructor(attack_speed, max_hit, accuracy, target.hp)

        # # return # ##########################################################

        if eqp.crossbow:
            return __get_crossbow_distribution()

        if special_attack:
            return __get_special_distribution()

        return __get_standard_distribution()
