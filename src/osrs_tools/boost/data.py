"""Data for the boost sub-module

###############################################################################
# email:    orchid.lilith@proton.me                                           #
# created:  2022-05-04                                                        #
###############################################################################
"""

from typing import Callable

from osrs_tools.tracked_value import Level

###############################################################################
# type alias                                                                  #
###############################################################################

SkillModifierCallableType = Callable[[Level], Level]
