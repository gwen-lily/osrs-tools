"""Timers and timed effects for OSRS.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-24                                                        #
###############################################################################
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from osrs_tools.data import DEFAULT_EFFECT_INTERVAL, Boost, Effect
from osrs_tools.exceptions import OsrsException

###############################################################################
# misc                                                                        #
###############################################################################

# enums #######################################################################


class Routine(Enum):
    """Enumerator of basic routine classifications."""

    SPECIAL_ENERGY = auto()


# exceptions ##################################################################


class TimerException(OsrsException):
    """Exception class for the timers module."""


# expiration


class TimerExpired(TimerException):
    """Exception raised when a timer expires.

    Attributes
    ----------

    timer : Timer
        The timer that raised the exception.

    """

    def __init__(self, __timer: Timer, /, *args) -> None:
        self.timer = __timer
        super().__init__(*args)


class TimedEffectExpired(TimerExpired):
    """Exception raised when a TimedEffect expires.

    Attributes
    ----------

    timer : TimedEffect
        The TimedEffect that raised the exception.
    """

    def __init__(self, __timer: TimedEffect, /, *args) -> None:
        super().__init__(__timer, *args)
        self.timer = __timer


class RepeatedEffectExpired(TimedEffectExpired):
    """Exception raised when a repeated effect timer expires.

    Attributes
    ----------

    timer : RepeatedEffected
        The RepeatedEffect that raised the exception.
    """

    def __init__(self, __timer: RepeatedEffect, /, *args):
        super().__init__(__timer, *args)
        self.timer = __timer


# update


class RepeatedEffectUpdate(TimerException):
    """Exception raised when a timer raises an interval alert."""

    def __init__(self, __timer: RepeatedEffect, /, *args):
        super().__init__(*args)
        self.timer = __timer


###############################################################################
# main classes                                                                #
###############################################################################


@dataclass
class Timer:
    """A basic timer.

    Attributes
    ----------

    start : int
        The initial value of the count, by default 0
    stop : int
        The final value of the count.
    count : int
        The current tick count.

    Raises
    ------
    TimerExpired
        Raised when the count expires.
    """

    start: int = field(init=False, default=0)
    stop: int
    count: int = field(init=False, default=0)

    # dunder and helper methods ###############################################

    def _is_expired(self) -> bool:
        return self.count >= self.stop

    # proper methods #########################################################

    def tick(self, ticks: int = 1) -> None:
        """Update the tick count and perform any necessary actions.

        Parameters
        ----------
        ticks : int, optional
            The number of ticks to increment. Defaults to 1

        Raises
        ------
        EffectExpired
            Raised when the count >= stop.
        """

        self.count += ticks

        if self._is_expired():
            raise TimerExpired


@dataclass
class TimedEffect(Timer):
    """A timer that tracks an effect or list of effects.

    Attributes
    ----------

    effects : list[Effect], optional
        A list of Effect enumerators. All effects must be on the same cycle,
        else it wouldn't make sense to bundle them in a single object like
        this. Defaults to empty list

    Raises
    ------
    EffectExpired
        Raised when the count expires.
    """

    effects: list[Effect] = field(default_factory=list)

    def tick(self, ticks: int = 1) -> None:
        try:
            super().tick(ticks)
        except TimerExpired as exc:
            raise TimedEffectExpired(self) from exc


@dataclass
class RepeatedEffect(TimedEffect):
    """An effect with a tick-based expiration timer and repeated actions.

    The simplest example is an Overload, which boosts the player every 25
    ticks for a duration of 500 ticks.

    Attributes
    ----------

    interval : int, optional
        The interval at which a unique action is performed. Defaults to
        DEFAULT_EFFECT_INTERVAL (25 ticks).
    apply_on_expiration: bool, optional
        Apply the interval effect on expiration, such as with Overload.

    """

    interval: int = DEFAULT_EFFECT_INTERVAL
    reapply_on_expiration: bool = True
    boosts: list[Boost] = field(default_factory=list)

    # dunder and helper methods ###############################################

    def _is_interval(self) -> bool:
        return self.count % self.interval == 0

    # proper methods #########################################################

    def tick(self, ticks: int = 1) -> None:

        try:
            super().tick(ticks)

            if self._is_interval:
                raise RepeatedEffectUpdate(self)

        except TimedEffectExpired as exc:
            raise RepeatedEffectExpired(self) from exc
