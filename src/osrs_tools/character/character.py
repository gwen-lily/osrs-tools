"""Characters, Players, and Monsters (oh my!)

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-22                                                        #
###############################################################################
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass, field, fields

from osrs_tools.combat import combat as cmb
from osrs_tools.data import (
    DT,
    TICKS_PER_SESSION,
    Boost,
    DamageValue,
    Effect,
    EquipmentStat,
    Level,
    MagicDamageTypes,
    MeleeDamageTypes,
    RangedDamageTypes,
    Roll,
)
from osrs_tools.exceptions import OsrsException
from osrs_tools.stats import AggressiveStats, CombatStats, DefensiveStats
from osrs_tools.timers import RepeatedEffect, Timer
from typing_extensions import Self

from ..style import Style, StylesCollection

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

    def __post_init__(self) -> None:
        self.reset_stats()

    def __copy__(self) -> Player:
        unpacked = {
            field.name: copy(getattr(self, field.name))
            for field in fields(self)
            if field.init is True
        }

        return self.__class__(**unpacked)

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

    def boost(self, *boosts: Boost) -> Self:
        for boost in boosts:
            self.lvl += boost

        return self._initialize_timers()

    def reset_stats(self) -> Self:
        """Set the character's active levels to its base levels."""
        self.lvl = copy(self._levels)
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

    @styles.setter
    @abstractmethod
    def styles(self, __value: Style, /) -> None:
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

    def defence_roll(
        self, other: Character, special_defence_roll: DT | None = None
    ) -> Roll:
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

        if dt in (MeleeDamageTypes, RangedDamageTypes):
            defensive_stat = self.effective_defence_level
        elif dt in MagicDamageTypes:
            defensive_stat = self.effective_magic_defence_level
        else:
            raise ValueError(dt)

        defensive_bonus = getattr(db, dt.value)
        assert isinstance(defensive_bonus, (int, EquipmentStat))
        defensive_roll = cmb.maximum_roll(defensive_stat, defensive_bonus)

        # TODO: Use inheritance you absolute dingo. This is why you suck.
        # if isinstance(other, Player):
        #     if other.eqp.brimstone_ring and dt in MagicDamageTypes:
        #         reduction = math.floor(int(defensive_roll) / 10) / 4
        #         defensive_roll = defensive_roll - reduction

        return defensive_roll

    # dunder methods ##########################################################

    def __str__(self):
        return self.name
