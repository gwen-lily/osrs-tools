"""The strategy sub-module, where all good abstractions of dps come from!

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-06                                                        #
###############################################################################
"""

from .basic_combat_strategies import (
    EliteVoidStrategy,
    MagicStrategy,
    MeleeStrategy,
    RangedStrategy,
)
from .derivative_combat_strategies import *
from .strategy import CombatStrategy, SkillingStrategy, Strategy
