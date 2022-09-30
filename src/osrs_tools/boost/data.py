"""Data for the boost sub-module

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-04                                                        #
###############################################################################
"""

from typing import Callable

from osrs_tools.tracked_value import Level

###############################################################################
# type alias                                                                  #
###############################################################################

SkillModifierCallableType = Callable[[Level], Level]
