"""Don't hate the player, hate the game.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-27                                                        #
###############################################################################
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from osrs_tools import gear
from osrs_tools import utils_combat as cmb
from osrs_tools.boost import Boost, DivineBoost, OverloadBoost
from osrs_tools.data import (
    DIVINE_DURATION,
    DT,
    OVERLOAD_DURATION,
    PLAYER_MAX_COMBAT_LEVEL,
    RUN_ENERGY_MAX,
    RUN_ENERGY_MIN,
    SPECIAL_ENERGY_DAMAGE,
    SPECIAL_ENERGY_INCREMENT,
    SPECIAL_ENERGY_MAX,
    SPECIAL_ENERGY_MIN,
    UPDATE_STATS_INTERVAL,
    UPDATE_STATS_INTERVAL_PRESERVE,
    MagicDamageTypes,
    MeleeDamageTypes,
    RangedDamageTypes,
    Skills,
    Slayer,
    Slots,
)
from osrs_tools.gear import Equipment, Weapon
from osrs_tools.prayer import Prayer, Prayers, Preserve
from osrs_tools.spell import (
    AncientSpell,
    GodSpell,
    PoweredSpell,
    PoweredSpells,
    Spell,
    StandardSpell,
    StandardSpells,
)
from osrs_tools.stats import AggressiveStats, DefensiveStats, PlayerLevels
from osrs_tools.style import PlayerStyle, UnarmedStyles, WeaponStyles
from osrs_tools.timers import (
    GET_UPDATE_CALLABLE,
    Effect,
    RepeatedEffect,
    TimedEffect,
    Timer,
)
from osrs_tools.tracked_value import (
    DamageModifier,
    DamageValue,
    Level,
    LevelModifier,
    MaximumVisibleLevel,
    MinimumVisibleLevel,
    VoidModifiers,
)
from typing_extensions import Self

from .character import Character, CharacterError

###############################################################################
# exceptions                                                                  #
###############################################################################


class PlayerError(CharacterError):
    ...


class NoTaskError(PlayerError):
    ...


class AutocastError(PlayerError):
    ...


###############################################################################
# main class                                                                  #
###############################################################################


@dataclass
class Player(Character):
    _levels: PlayerLevels = field(default_factory=PlayerLevels.maxed_player, repr=False)
    _attack_delay: int = field(init=False, default=0)
    _active_style: PlayerStyle | None = None
    _autocast: Spell | None = field(init=False, default=None)
    charged: bool = True
    equipment: Equipment = field(default_factory=Equipment)
    kandardin_hard_diary: bool = True
    levels: PlayerLevels = field(init=False)
    _min_levels: PlayerLevels = field(repr=False, default_factory=PlayerLevels.zeros)
    _max_levels: PlayerLevels = field(
        repr=False, default_factory=PlayerLevels.max_levels
    )
    _prayers: Prayers = field(default_factory=Prayers)
    _run_energy: int = field(init=False, default=RUN_ENERGY_MAX)
    slayer_task: Slayer = Slayer.NONE
    _special_energy: int = field(init=False, default=SPECIAL_ENERGY_MAX)
    _timers: list[Timer] = field(init=False, default_factory=list)

    # dunder and helper methods ###############################################

    def __post_init__(self) -> None:
        self.reset_stats()

        try:
            self.wpn
        except AssertionError:
            self.wpn = Weapon.unarmed()
            self.style = UnarmedStyles.default

    # event and effect methods ################################################

    def _initialize_timers(self, reinitialize: bool = False) -> None:
        """Initialize some standard timers.

        Attributes
        ----------

        reinitialize : bool, optional
            Set to True to overwrite existing timers, defaults to True

        """

        def get_timer(*tups: tuple[Effect, GET_UPDATE_CALLABLE]) -> list:
            timers: list[RepeatedEffect] = []

            for efct, func in tups:
                if (_t := func(reinitialize)) is not None:
                    self._remove_effect_timer(efct)
                    timers.append(_t)

            return timers

        effects_pairs = (
            (Effect.UPDATE_STATS, self._get_update_stats_timer),
            (Effect.REGEN_SPECIAL_ENERGY, self._get_special_energy_timer),
            (Effect.PRAYER_DRAIN, self._get_prayer_drain_timer),
        )

        new_timers = get_timer(*effects_pairs)
        self.timers.extend(new_timers)

    def _get_special_energy_timer(
        self, reinitialize: bool = False
    ) -> RepeatedEffect | None:
        if self.special_energy_full:
            return

        interval = SPECIAL_ENERGY_INCREMENT

        return self._get_event_timer(
            Effect.REGEN_SPECIAL_ENERGY,
            reinitialize,
            interval,
            True,
        )

    def _get_update_stats_timer(
        self, reinitialize: bool = False
    ) -> RepeatedEffect | None:
        if not self.affected_by_boost:
            return

        if Preserve in self.prayers:
            interval = UPDATE_STATS_INTERVAL_PRESERVE
        else:
            interval = UPDATE_STATS_INTERVAL

        return self._get_event_timer(
            Effect.UPDATE_STATS,
            reinitialize,
            interval,
            True,
        )

    def _get_prayer_drain_timer(
        self, reinitialize: bool = False
    ) -> RepeatedEffect | None:
        if len(self.prayers) == 0:
            return

        return self._get_event_timer(
            Effect.PRAYER_DRAIN,
            reinitialize,
            int(self.ticks_per_pp_lost),
            True,
        )

    def reset_prayers(self) -> Self:
        """Deactivate prayers and remove the drain timer."""
        self.prayers.reset_prayers()
        self._remove_effect_timer(Effect.PRAYER_DRAIN)

        return self

    def reset_special_energy(self) -> Self:
        self.special_energy = SPECIAL_ENERGY_MAX
        self._remove_effect_timer(Effect.REGEN_SPECIAL_ENERGY)

        return self

    def reset_run_energy(self) -> Self:
        self.run_energy = RUN_ENERGY_MAX

        return self

    def _update_stats(self) -> Self:
        for skill in Skills:
            if (stat := self.lvl[skill]) < self._levels[skill]:
                stat += 1
            elif stat > self._levels[skill]:
                stat -= 1

        return self

    def reset_character(self) -> Self:
        self.reset_prayers().reset_special_energy().reset_run_energy()
        return super().reset_character()

    def _regenerate_special_attack(self):
        self.special_energy += SPECIAL_ENERGY_INCREMENT

    def cast_energy_transfer(self, other: Player) -> None:
        if not self.special_energy_full or self.hp <= 10:
            return

        self.hp -= DamageValue(SPECIAL_ENERGY_DAMAGE, "spec transfer")
        other.reset_special_energy().reset_run_energy()

    def boost(self, *boosts: Boost) -> Self:
        """For each boost, create repeated effects and init timers."""

        for boost in boosts:
            # set up each boosts' timer.

            if isinstance(boost, OverloadBoost):
                timer = RepeatedEffect(
                    OVERLOAD_DURATION,
                    [Effect.OVERLOAD],
                    OVERLOAD_DURATION,
                    True,
                    [boost],
                )
                self.timers.append(timer)

            elif isinstance(boost, DivineBoost):
                timer = RepeatedEffect(
                    DIVINE_DURATION,
                    [Effect.DIVINE_POTION],
                    DIVINE_DURATION,
                    False,
                    [boost],
                )
                self.timers.append(timer)

            else:
                pass  # normal potions don't require any more work

        return super().boost(*boosts)

    def pray(self, *prayers: Prayer | Prayers):
        self.prayers.pray(*prayers)

        if Effect.PRAYER_DRAIN not in self.effects:
            self._initialize_timers()

    # wrapper methods #########################################################

    def wearing(self, *args, **kwargs) -> bool:
        """Simple wrapper for Equipment.wearing."""
        return self.eqp.wearing(*args, **kwargs)

    # combat methods ##########################################################

    def max_hit(
        self, *damage_modifiers: DamageModifier, spell: Spell | None = None
    ) -> DamageValue:
        """The max hit from base damage and standard modifiers.

        Parameters
        ----------
        other : Character
            The target of the attack.
        *damage_modifiers: DamageModifier
            Optional damage modifiers.

        spell : Spell | None, optional
            Provide a spell if making an attack with a spell, by default None

        Returns
        -------
        DamageValue

        Raises
        ------
        PlayerError
        StyleError
        SpellError
        """

        # basic defintions and error handling
        ab = self.aggressive_bonus

        if spell is not None:
            dt = DT.MAGIC
        elif isinstance(self._autocast, Spell) and self.style.is_spell_style:
            spell = self.autocast
            dt = DT.MAGIC
        else:
            dt = self.style.damage_type

        # melee and ranged damage is simple
        if dt in [MeleeDamageTypes, RangedDamageTypes]:
            if dt in MeleeDamageTypes:
                effective_level = self.effective_melee_strength_level
                bonus = ab.melee_strength
            else:
                effective_level = self.effective_ranged_strength_level
                bonus = ab.ranged_strength

            base_damage = cmb.base_damage(effective_level, bonus)
            return DamageValue(math.floor(base_damage))

        # magic is a little less simple
        if spell is None:
            # no spell or autocast specified, try to manually set it.
            if self.wpn == Weapon.from_bb("sanguinesti staff"):
                self.autocast = PoweredSpells.SANGUINESTI_STAFF.value
            elif self.wpn == Weapon.from_bb("trident of the swamp"):
                self.autocast = PoweredSpells.TRIDENT_OF_THE_SWAMP.value
            elif self.wpn == Weapon.from_bb("trident of the seas"):
                self.autocast = PoweredSpells.TRIDENT_OF_THE_SEAS.value
            elif self.wpn == Weapon.from_bb("iban's staff"):
                self.autocast = StandardSpells.IBAN_BLAST.value
            else:
                raise ValueError(self.wpn, self._autocast)

            spell = self.autocast

        # spell is specified
        if isinstance(spell, StandardSpell) or isinstance(spell, AncientSpell):
            base_damage = spell.max_hit()
        elif isinstance(spell, GodSpell):
            base_damage = spell.max_hit(self.charged)
        elif isinstance(spell, PoweredSpell):
            base_damage = spell.max_hit(self.visible_magic)
        else:
            raise ValueError(spell)

        _max_hit = cmb.max_hit(base_damage, *damage_modifiers)

        # unique: chaos gauntlets flat bonus handled via player_modifiers

        return _max_hit

    def attack_speed(self, __spell: Spell | None = None, /) -> int:
        active_spell = None

        # check for spell casting
        if __spell is not None:
            active_spell = __spell
        elif isinstance(self._autocast, Spell) and self.style.is_spell_style:
            active_spell = self.autocast

        if not isinstance(active_spell, Spell):
            return self.wpn.attack_speed + self.style.attack_speed_modifier

        _asm = self.style.attack_speed_modifier

        if self.wpn == Weapon.from_bb("harmonised nightmare staff"):
            if isinstance(active_spell, StandardSpell):
                _asm -= 1

        return active_spell.attack_speed + _asm

    # shorthand properties ####################################################

    @property
    def lvl(self) -> PlayerLevels:
        return self.levels

    @lvl.setter
    def lvl(self, __value: PlayerLevels) -> None:
        super().lvl = __value

    @property
    def style(self) -> PlayerStyle:
        val = super().style
        assert isinstance(val, PlayerStyle)

        return val

    @style.setter
    def style(self, __value: PlayerStyle) -> None:
        super().style = __value

    @property
    def styles(self) -> WeaponStyles:
        val = super().style
        assert isinstance(val, WeaponStyles)

        return val

    @property
    def eqp(self) -> Equipment:
        return self.equipment

    @eqp.setter
    def eqp(self, __value: Equipment) -> None:
        self.equipment = __value

    @property
    def wpn(self) -> Weapon:
        _val = self.eqp[Slots.WEAPON]
        assert isinstance(_val, Weapon)

        return _val

    @wpn.setter
    def wpn(self, __value: Weapon) -> None:
        self.eqp[Slots.WEAPON] = __value

    # access properties #######################################################

    @property
    def autocast(self) -> Spell:
        if not isinstance(self._autocast, Spell):
            raise AutocastError(self._autocast)

        return self._autocast

    @autocast.setter
    def autocast(self, __value: Spell, /) -> None:
        self._autocast = __value

    @property
    def prayers(self) -> Prayers:
        return self._prayers

    @prayers.setter
    def prayers(self, __value: Prayers) -> None:
        self._prayers = __value

    # proper properties #######################################################

    @property
    def aggressive_bonus(self) -> AggressiveStats:
        """Simple wrapper for Equipment which accounts for edge cases.

        Returns
        -------

        AggressiveStats
        """
        ab = self.eqp.aggressive_bonus

        if self.wpn in gear.Chinchompas:
            # don't account for ammo if using chinchompas or thrown weapons
            # TODO: Thrown weapons
            ammo = self.eqp[Slots.AMMUNITION]

            if ammo is not None:
                ammo_bonus = ammo.aggressive_bonus.ranged_strength
                ab.ranged_strength -= ammo_bonus

        return ab

    @property
    def defensive_bonus(self) -> DefensiveStats:
        """Simple wrapper to match aggressive_bonus and provide Player level access.

        Returns
        -------
            DefensiveStats: DefensiveStats object.
        """
        return self.eqp.defensive_bonus

    @property
    def combat_level(self) -> Level:
        """Calculates a Player's combat level.

        This formula makes use of TrackedValue and its subclasses quite
        heavily. Floor division and all that slick stuff is baked in to the
        dunders, so be careful if you modify anything here.

        Returns
        -------
        Level
        """

        lvl_atk = self.lvl.attack
        lvl_str = self.lvl.strength
        lvl_def = self.lvl.defence
        lvl_rng = self.lvl.ranged
        lvl_mag = self.lvl.magic
        lvl_pray = self.lvl.prayer
        lvl_hp = self.lvl.hitpoints

        _base_level = lvl_def + lvl_hp + (lvl_pray // 2)
        base_level = float((1 / 4) * _base_level.value)

        melee_level = float((13 / 40) * (lvl_atk + lvl_str).value)
        magic_level = float((13 / 40) * (lvl_mag + lvl_mag // 2).value)
        ranged_level = float((13 / 40) * (lvl_rng + lvl_rng // 2).value)
        type_level = max([melee_level, magic_level, ranged_level])

        value = math.floor(base_level + type_level)
        comment = "combat level"
        combat_level = Level(value, comment)

        return combat_level

    @staticmethod
    def max_combat_level() -> Level:
        return Level(PLAYER_MAX_COMBAT_LEVEL, "max combat level")

    @property
    def special_energy(self) -> int:
        return self._special_energy

    @special_energy.setter
    def special_energy(self, __value: int) -> None:
        _clmp = min([max([SPECIAL_ENERGY_MIN, __value]), SPECIAL_ENERGY_MAX])
        self._special_energy = _clmp

    @property
    def run_energy(self) -> int:
        return self._run_energy

    @run_energy.setter
    def run_energy(self, __value: int) -> None:
        _clmp = min([max([RUN_ENERGY_MIN, __value]), RUN_ENERGY_MAX])
        self._run_energy = _clmp

    @property
    def special_energy_full(self) -> bool:
        return self._special_energy == SPECIAL_ENERGY_MAX

    @property
    def prayer_drain_resistance(self) -> int:
        return 2 * self.eqp.prayer_bonus + 60

    @property
    def ticks_per_pp_lost(self) -> float:
        return self.prayer_drain_resistance / self.prayers.drain_effect

    @property
    def attack_range(self) -> int:
        # return min([max([0, self.wpn.attack_range]), 10])
        raise NotImplementedError

    @property
    def can_attack(self) -> bool:
        return self._attack_delay == 0

    # timers

    @property
    def timers(self) -> list[Timer]:
        return self._timers

    @property
    def simple_timers(self) -> list[Timer]:
        """Return only timers with no associated effects."""
        return [t for t in self._timers if type(t) is Timer]

    @property
    def effect_timers(self) -> list[TimedEffect]:
        """Return only TimedEffects."""
        return [e for e in self._timers if isinstance(e, TimedEffect)]

    @property
    def repeated_effect_timers(self) -> list[RepeatedEffect]:
        """Return only RepeatedEffects."""
        return [e for e in self.effect_timers if isinstance(e, RepeatedEffect)]

    @property
    def effects(self) -> list[Effect]:
        _effects: list[Effect] = []

        for _et in self.effect_timers:
            _effects.extend(_et.effects)

        return _effects

    @property
    def affected_by_boost(self) -> bool:
        return self._levels == self.levels

    # combat properties #######################################################

    # visible

    @property
    def visible_attack(self) -> Level:
        return min([max([MinimumVisibleLevel, self.lvl.attack]), MaximumVisibleLevel])

    @property
    def visible_strength(self) -> Level:
        return min([max([MinimumVisibleLevel, self.lvl.strength]), MaximumVisibleLevel])

    @property
    def visible_defence(self) -> Level:
        return min([max([MinimumVisibleLevel, self.lvl.defence]), MaximumVisibleLevel])

    @property
    def visible_magic(self) -> Level:
        return min([max([MinimumVisibleLevel, self.lvl.magic]), MaximumVisibleLevel])

    @property
    def visible_ranged(self) -> Level:
        return min([max([MinimumVisibleLevel, self.lvl.ranged]), MaximumVisibleLevel])

    # invisible

    @property
    def invisible_attack(self) -> Level:
        if isinstance(self.prayers.attack, LevelModifier):
            return self.visible_attack * self.prayers.attack
        else:
            return self.visible_attack

    @property
    def invisible_strength(self) -> Level:
        if isinstance(self.prayers.strength, LevelModifier):
            return self.visible_strength * self.prayers.strength
        else:
            return self.visible_strength

    @property
    def invisible_defence(self) -> Level:
        if isinstance(self.prayers.defence, LevelModifier):
            return self.visible_defence * self.prayers.defence
        else:
            return self.visible_defence

    @property
    def invisible_magic(self) -> Level:
        if isinstance(self.prayers.magic_attack, LevelModifier):
            return self.visible_magic * self.prayers.magic_attack
        else:
            return self.visible_magic

    @property
    def invisible_ranged_attack(self) -> Level:
        if isinstance(self.prayers.ranged_attack, LevelModifier):
            return self.visible_ranged * self.prayers.ranged_attack
        else:
            return self.visible_ranged

    @property
    def invisible_ranged_strength(self) -> Level:
        if isinstance(self.prayers.ranged_strength, LevelModifier):
            return self.visible_ranged * self.prayers.ranged_strength
        else:
            return self.visible_ranged

    # effective

    @property
    def effective_melee_attack_level(self) -> Level:
        accuracy_level = self.invisible_attack
        style_bonus = self.style.combat_bonus.melee_attack

        if (void_modifiers := self._void_modifiers()) is not None:
            void_alm, _ = void_modifiers
            return cmb.effective_level(accuracy_level, style_bonus, void_alm)
        else:
            return cmb.effective_level(accuracy_level, style_bonus)

    @property
    def effective_melee_strength_level(self) -> Level:
        strength_level = self.invisible_strength
        style_bonus = self.style.combat_bonus.melee_strength

        if (void_modifiers := self._void_modifiers()) is not None:
            _, void_slm = void_modifiers
            return cmb.effective_level(strength_level, style_bonus, void_slm)
        else:
            return cmb.effective_level(strength_level, style_bonus)

    @property
    def effective_defence_level(self) -> Level:
        accuracy_level = self.invisible_defence
        style_bonus = self.style.combat_bonus.defence
        return cmb.effective_level(accuracy_level, style_bonus)

    @property
    def effective_ranged_attack_level(self) -> Level:
        accuracy_level = self.invisible_ranged_attack
        style_bonus = self.style.combat_bonus.ranged_attack

        if (void_modifiers := self._void_modifiers()) is not None:
            void_alm, _ = void_modifiers
            return cmb.effective_level(accuracy_level, style_bonus, void_alm)
        else:
            return cmb.effective_level(accuracy_level, style_bonus)

    @property
    def effective_ranged_strength_level(self) -> Level:
        strength_level = self.invisible_ranged_strength
        style_bonus = self.style.combat_bonus.ranged_attack

        if (void_modifiers := self._void_modifiers()) is not None:
            _, void_slm = void_modifiers
            return cmb.effective_level(strength_level, style_bonus, void_slm)
        else:
            return cmb.effective_level(strength_level, style_bonus)

    @property
    def effective_magic_attack_level(self) -> Level:
        accuracy_level = self.invisible_magic
        style_bonus = self.style.combat_bonus.magic_attack

        if (void_modifiers := self._void_modifiers()) is not None:
            void_alm, _ = void_modifiers
            return cmb.effective_level(accuracy_level, style_bonus, void_alm)
        else:
            return cmb.effective_level(accuracy_level, style_bonus)

    @property
    def effective_magic_defence_level(self) -> Level:
        """Bitterkoekje formula for effective magic defence level

        source:
            https://docs.google.com/document/d/1hk7FxOAOFT4oxguC8411QQhE4kk-_GzqWcwkaPmaYns/edit

        Returns
        -------
        Level
        """
        # order important
        adj_eff_def_lvl = self.effective_defence_level * LevelModifier(
            0.30, "magic defence 30%"
        )
        adj_eff_mag_lvl = self.effective_magic_attack_level * LevelModifier(
            0.70, "magic defence 70%"
        )

        invisible_magic_defence = adj_eff_def_lvl + adj_eff_mag_lvl
        bonus = self.style.combat_bonus.defence

        return cmb.effective_level(invisible_magic_defence, bonus)

    # class methods ###########################################################

    @classmethod
    def from_rsn(cls, rsn: str) -> Player:
        return cls(_levels=PlayerLevels.from_rsn(rsn), name=rsn)

    # modifiers that make sense here ##########################################

    def _void_modifiers(self) -> VoidModifiers | None:
        """Returns void level modifiers if the player is wearing a void set.

        Raises
        ------
            ValueError: Raised if the active style damage type is unsupported.

        Returns
        -------
            VoidModifiers | None: A pair of accuracy and strength level
            modifiers if applicable, else None.
        """
        lad = self

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
