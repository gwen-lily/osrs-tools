"""Data for the cox sub-module of osrs-tools

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-25                                                         #
###############################################################################
"""

from enum import Enum, auto, unique
from typing import Callable


@unique
class RangedAttackPattern(Enum):
    """Strategies for killing the head"""

    FOUR_TO_ONE = auto()
    TWO_TO_ZERO = auto()


@unique
class MeleeAttackPattern(Enum):
    """Strategies for killing the melee hand"""

    FOUR_TO_ONE = auto()
    ONE_TO_ZERO = auto()
    CHAD_FACETANK = auto()


###############################################################################
# thieving                                                                    #
###############################################################################

POINTS_PER_GRUB = 100
PARTY_AVERAGE_THIEVING_LEVEL = 42  # personal estimate
GrubEstimate = Callable[..., int]
