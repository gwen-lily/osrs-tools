"""I think I might have accidentally just used the bridge pattern?

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-24                                                        #
###############################################################################
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from osrs_tools.character import Character
from osrs_tools.character.player import Player
from osrs_tools.data import Effect
from osrs_tools.timers import (
    RepeatedEffect,
    RepeatedEffectUpdate,
    TimedEffect,
    TimedEffectExpired,
)


@dataclass
class CharacterUpdater(ABC):
    """Abstract character updater from which others inherit."""

    lad: Character

    @abstractmethod
    def tick(self, ticks: int = 1, *args, **kwargs) -> None:
        """Update characters."""


@dataclass
class PlayerUpdater(CharacterUpdater):
    """Character updater."""

    lad: Player

    def tick(self, ticks: int = 1, *args, **kwargs) -> None:
        for timer in self.lad.effect_timers:
            try:
                timer.tick(ticks)
            except TimedEffectExpired as exc:
                self._remove_effects(exc.timer)
            except RepeatedEffectUpdate as exc:
                self._update_effects(exc.timer)

    def _remove_effects(self, *timers: TimedEffect) -> None:
        for timer in timers:
            if isinstance(timer, RepeatedEffect):
                if timer.reapply_on_expiration:
                    self._update_effects(timer)

            self.lad.timers.remove(timer)

    def _update_effects(self, __timer: RepeatedEffect, /) -> None:
        for effect in __timer.effects:

            if effect is Effect.PRAYER_DRAIN:
                self.lad.lvl.prayer -= 1
            elif effect is Effect.UPDATE_STATS:
                self.lad._update_stats()
            elif effect is Effect.REGEN_SPECIAL_ENERGY:
                self.lad._regenerate_special_attack()
            elif effect in (Effect.OVERLOAD, Effect.DIVINE_POTION):
                self.lad.boost(*__timer.boosts)
