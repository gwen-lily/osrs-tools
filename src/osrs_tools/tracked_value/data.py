"""Useful info for tracked values

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-03                                                         #
###############################################################################
"""

from .tracked_value import TrackedFloat
from .tracked_values import Level, LevelModifier, RollModifier

###############################################################################
# definition                                                                  #
###############################################################################

ModifierPair = tuple[RollModifier, TrackedFloat]
VoidModifiers = tuple[LevelModifier, LevelModifier]

MinimumVisibleLevel = Level(0, "min visible lvl")
MaximumVisibleLevel = Level(125, "max visible lvl")     # yagex lmaooooooo
