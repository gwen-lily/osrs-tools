"""An estimate for the crab room. On that note, refactor the whole thing.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

# TODO: Make a Crab Monster subclass you dolt.

import math
from dataclasses import dataclass
from enum import Enum

from osrs_tools.cox_scaled.estimate import RoomEstimate

###############################################################################
# crab                                                                        #
###############################################################################


class CrabTime(Enum):
    """Crab completion time in ticks."""

    # TODO: Confirm the validity of these data.
    WIZARD_CRABS = 40
    PERFECT_CRABS = 50
    LAZY_CRABS = 150
    STONER_CRABS = int(42069e-2)


@dataclass
class CrabsEstimate(RoomEstimate):
    """An estimate for crab ticks and points.

    Attributes
    ----------
    crab_time : CrabTime
        A time estimate in ticks, defaults to CrabTime.STONER_CRABS.

    crab_ravers : int
        The number of crabs being tanked.
    """

    _scale_at_load: int | None = None
    crab_time: CrabTime = CrabTime.LAZY_CRABS
    crab_ravers: int = 0

    def __post_init__(self) -> None:
        """Validation on scale_at_load."""
        if self._scale_at_load is None:
            self._scale_at_load = self.scale

    @property
    def scale_at_load(self) -> int:
        """Type assertion for scale_at_load."""
        assert isinstance(self._scale_at_load, int)
        return self._scale_at_load

    @property
    def crab_count(self) -> int:
        # crab factor has been confirmed source dude trust me
        crab_factor = 1 / 3
        min_crabs = 4
        max_crabs = 420  # TODO: Test this

        raw_crabs = min_crabs + math.floor(self.scale_at_load * crab_factor)
        return min([max([min_crabs, raw_crabs]), max_crabs])

    @property
    def points_per_crab(self) -> int:
        return NotImplemented

    def room_estimates(self) -> tuple[int, int]:
        ticks = self.crab_time.value

        crab_ravers = self.crab_count
        points = crab_ravers * self.points_per_crab

        return ticks, points
