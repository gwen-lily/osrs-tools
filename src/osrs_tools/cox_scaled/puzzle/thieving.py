"""An estimate for the thieving room.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

import math
from dataclasses import dataclass, field
from typing import Callable

from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.cox_scaled.strategy import SkillingStrategy
from osrs_tools.modifier import Level

###############################################################################
# thieving data & helper functions                                            #
###############################################################################

POINTS_PER_GRUB = 100
_PARTY_AVERAGE_THIEVING_LEVEL = 42  # personal estimate
GrubEstimate = Callable[..., int]


def flat_grub_estimate(__scale: int, /) -> int:
    return (16 * __scale) - 1


def _jank_grub_estimate(__scale: int, __modifier: float | None = None, /) -> int:
    if __modifier is None:
        __modifier = 268 / flat_grub_estimate(28)  # a single datapoint

    flat_estimate = flat_grub_estimate(__scale)
    return math.floor(flat_estimate * __modifier)


def party_level_scaling_estimate(
    __scale: int,
    /,
    *,
    party_thieving_level: int | Level = _PARTY_AVERAGE_THIEVING_LEVEL,
) -> int:
    modifier = int(party_thieving_level) / 99
    return _jank_grub_estimate(__scale, modifier)


###############################################################################
# strategy & estimate                                                         #
###############################################################################


@dataclass
class ThievingStrategy(SkillingStrategy):
    grub_estimate: GrubEstimate = party_level_scaling_estimate
    ticks_per_grub: int | float = 4.5


@dataclass
class ThievingEstimate(RoomEstimate):
    strategy: ThievingStrategy = field(default_factory=ThievingStrategy)

    def room_estimates(self) -> tuple[int, int]:
        grubs = self.strategy.grub_estimate(self.scale)

        ticks = math.floor(self.strategy.ticks_per_grub * grubs)
        points = POINTS_PER_GRUB * grubs
        return ticks, points
