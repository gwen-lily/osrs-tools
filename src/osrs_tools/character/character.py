"""Characters, Players, and Monsters (oh my!)

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-22                                                        #
###############################################################################
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass, field

from osrs_tools import gear
from osrs_tools import utils_combat as cmb
from osrs_tools.boost.boost import Boost
from osrs_tools.data import (
    ARCLIGHT_FLAT_REDUCTION,
    DT,
    DWH_MODIFIER,
    TICKS_PER_SESSION,
    VULNERABILITY_MODIFIER,
    VULNERABILITY_MODIFIER_TOME_OF_WATER,
    ArclightReducedSkills,
    BgsReducedSkills,
    Effect,
    MagicDamageTypes,
    MeleeDamageTypes,
    RangedDamageTypes,
    Skills,
)
from osrs_tools.exceptions import OsrsException
from osrs_tools.stats import AggressiveStats, CombatStats, DefensiveStats
from osrs_tools.style import Style, StylesCollection
from osrs_tools.timers import RepeatedEffect, TimedEffect, Timer
from osrs_tools.tracked_value import DamageValue, EquipmentStat, Level, Roll
from osrs_tools.tracked_value.tracked_values import LevelModifier
from typing_extensions import Self

###############################################################################
# exceptions                                                                  #
###############################################################################


class CharacterError(OsrsException):
    ...


###############################################################################
# main class                                                                  #
###############################################################################


@dataclass
class Character(ABC):
    _levels: CombatStats
    levels: CombatStats = field(init=False, repr=True)
    _active_style: Style | None = None
    last_attacked: Character | None = field(init=False, repr=False, default=None)
    last_attacked_by: Character | None = field(init=False, repr=False, default=None)
    name: str = field(default_factory=str)
    _timers: list[Timer] = field(default_factory=list)

    # dunder and helper methods

    def __post_init__(self) -> None:
        self.reset_stats()

    def __str__(self):
        return self.name

    # event and effect methods ################################################

    # abstract

    @abstractmethod
    def _initialize_timers(self, reinitialize: bool = False) -> Self:
        """Initialize some standard timers.

        Attributes
        ----------

        reinitialize : bool, optional
            Set to True to overwrite existing timers, defaults to True
        """

    @abstractmethod
    def _update_stats(self) -> Self:
        """Update a Character's stats."""

    # implemented

    def _get_event_timer(
        self, effect: Effect, reinitialize: bool, interval: int, reapply: bool
    ) -> RepeatedEffect | None:
        if effect in self.effects and not reinitialize:
            return

        return RepeatedEffect(TICKS_PER_SESSION, [effect], interval, reapply)

    def _remove_effect_timer(self, __effect: Effect, /) -> Self:
        if __effect in self.effects:
            for _et in self.effect_timers:
                if __effect in _et.effects:
                    self.timers.remove(_et)
                    break

        return self

    def reset_character(self) -> Self:
        return self.reset_stats()._initialize_timers()

    def _boost(self, *boosts: Boost) -> Self:
        for boost in boosts:
            self.lvl = self.lvl + boost

        self._initialize_timers()
        return self

    def reset_stats(self) -> Self:
        """Set the character's active levels to its base levels."""
        self.levels = copy(self._levels)
        return self._remove_effect_timer(Effect.UPDATE_STATS)

    # shorthand properties ####################################################

    @property
    def lvl(self) -> CombatStats:
        return self.levels

    @lvl.setter
    def lvl(self, __value: CombatStats) -> None:
        self.levels = __value

    @property
    def hp(self) -> Level:
        return self.lvl.hitpoints

    @hp.setter
    def hp(self, __value: Level, /) -> None:
        self.lvl.hitpoints = __value

    @property
    def base_hp(self) -> Level:
        assert isinstance(self._levels.hitpoints, Level)
        return self._levels.hitpoints

    @property
    def style(self) -> Style:
        assert self._active_style is not None
        return self._active_style

    @style.setter
    def style(self, __value: Style) -> None:
        if __value not in self.styles:
            raise ValueError(__value)

        self._active_style = __value

    # proper properties #######################################################

    @property
    def alive(self) -> bool:
        return self.hp > 0

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

    # abstract properties #####################################################

    @property
    @abstractmethod
    def styles(self) -> StylesCollection:
        ...

    @property
    @abstractmethod
    def aggressive_bonus(self) -> AggressiveStats:
        ...

    @property
    @abstractmethod
    def defensive_bonus(self) -> DefensiveStats:
        ...

    @property
    @abstractmethod
    def effective_melee_attack_level(self) -> Level:
        ...

    @property
    @abstractmethod
    def effective_melee_strength_level(self) -> Level:
        ...

    @property
    @abstractmethod
    def effective_defence_level(self) -> Level:
        ...

    @property
    @abstractmethod
    def effective_ranged_attack_level(self) -> Level:
        ...

    @property
    @abstractmethod
    def effective_ranged_strength_level(self) -> Level:
        ...

    @property
    @abstractmethod
    def effective_magic_attack_level(self) -> Level:
        ...

    @property
    @abstractmethod
    def effective_magic_defence_level(self) -> Level:
        ...

    # combat methods ##########################################################

    def damage(self, other: Character, *amount: int | DamageValue) -> DamageValue:
        damage_dealt = DamageValue(0)

        for _amt in amount:

            if _amt <= 0:
                continue

            damage_allowed = min([self.hp, _amt])
            self.hp -= damage_allowed
            damage_dealt += damage_allowed

        return damage_dealt

    def heal(self, amount: int | DamageValue, overheal: bool = False):

        # must be non-negative
        if amount >= 0:
            raise ValueError(amount)

        if overheal:
            self.hp += amount
        else:
            if (new_hp := self.hp + amount) <= self._levels.hitpoints:
                self.hp = new_hp
            else:
                self.hp = copy(self._levels.hitpoints)

    def defence_roll(self, other: Character, special_defence_roll: DT | None = None) -> Roll:
        """Returns the defence roll of self when attacked by other.

        Optionally with a specific damage type.

        Parameters
        ----------

        other : Character
            The character performing the attack.

        special_defence_roll : DT | None, optional
            The damage type used to determine defence bonuses. Defaults to None

        Raises
        ------
        ValueError


        Returns
        -------
        Roll
        """
        # Basic definitions and error handling
        db = self.defensive_bonus
        _sdr = special_defence_roll
        dt = _sdr if _sdr else other.style.damage_type

        if dt in MeleeDamageTypes or dt in RangedDamageTypes:
            defensive_stat = self.effective_defence_level
        elif dt in MagicDamageTypes:
            defensive_stat = self.effective_magic_defence_level
        else:
            raise ValueError(dt)

        defensive_bonus = getattr(db, dt.value)
        assert isinstance(defensive_bonus, (int, EquipmentStat))
        defensive_roll = cmb.maximum_roll(defensive_stat, defensive_bonus)

        return defensive_roll

    def apply_dwh(self, success: bool = True) -> Self:
        """Reduce a character's defence level on a non-zero DWH attack

        The Dragon Warhammer uniquely requires that a successful attack deal
        damage in order to proc the defence reduction

        Parameters
        ----------
        success : bool, optional
            True if the attack dealt damage, by default True

        Returns
        -------
        Self

        """
        if success:
            self.lvl.defence *= LevelModifier(DWH_MODIFIER)

        return self

    def apply_bgs(self, amount: DamageValue) -> Self:
        """Reduce a character's stats in order

        BGS reduces the following stats, in order: defence, strength, attack,
        magic, & ranged.

        Parameters
        ----------
        amount : DamageValue
            The amount of damage dealt by the special attack

        Returns
        -------
        Self
        """
        possible_reduction = amount

        for skill in BgsReducedSkills:
            if not possible_reduction > 0:
                continue

            level = self.lvl[skill]
            reduction = int(min([level, possible_reduction]))
            possible_reduction -= reduction
            self.lvl[skill] -= reduction

        return self

    def apply_arclight(self, success: bool = True) -> Self:
        if success:
            _mod = LevelModifier(ARCLIGHT_FLAT_REDUCTION, gear.Arclight.name)

            for skill in ArclightReducedSkills:
                base_level = self._levels[skill]
                level = self.lvl[skill]
                reduction = int(min([level, base_level * _mod]))
                self.lvl[skill] -= reduction

        return self

    def apply_vulnerability(self, success: bool = True, tome_of_water: bool = True) -> Self:
        if success:
            if tome_of_water:
                _mod_val = VULNERABILITY_MODIFIER_TOME_OF_WATER
            else:
                _mod_val = VULNERABILITY_MODIFIER

            _mod = LevelModifier(_mod_val, "vulnerability")

            self.lvl[Skills.DEFENCE] *= _mod

        return self

    # dunder methods ##########################################################
