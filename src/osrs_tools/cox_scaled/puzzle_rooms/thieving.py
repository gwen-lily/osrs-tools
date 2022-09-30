"""An estimate for the thieving room.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

import math
from dataclasses import dataclass, field

from osrs_tools.cox_scaled.data import POINTS_PER_GRUB, GrubEstimate
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.strategy import SkillingStrategy

from . import utils

###############################################################################
# thieving data & helper functions                                            #
###############################################################################


###############################################################################
# strategy & estimate                                                         #
###############################################################################


@dataclass
class ThievingStrategy(SkillingStrategy):
    grub_estimate: GrubEstimate = utils.party_level_scaling_estimate
    ticks_per_grub: int | float = 4.5


@dataclass
class ThievingEstimate(RoomEstimate):
    strategy: ThievingStrategy = field(default_factory=ThievingStrategy)

    def room_estimates(self) -> tuple[int, int]:
        grubs = self.strategy.grub_estimate(self.scale)

        ticks = math.floor(self.strategy.ticks_per_grub * grubs)
        points = POINTS_PER_GRUB * grubs
        return ticks, points
