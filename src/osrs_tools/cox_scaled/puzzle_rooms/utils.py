"""utils for the puzzle-rooms sub-module of the cox-scaled sub-module of...

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-05                                                        #
###############################################################################
"""

import math

from osrs_tools.cox_scaled.data import PARTY_AVERAGE_THIEVING_LEVEL
from osrs_tools.tracked_value import Level


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
    party_thieving_level: int | Level = PARTY_AVERAGE_THIEVING_LEVEL,
) -> int:
    modifier = int(party_thieving_level) / 99
    return _jank_grub_estimate(__scale, modifier)
