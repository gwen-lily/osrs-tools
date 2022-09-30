"""The data structure that tracks a skill and the callable to modify it

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-02                                                        #
###############################################################################
"""

from dataclasses import dataclass

from osrs_tools.data import Skills

from .data import SkillModifierCallableType

###############################################################################
# main class                                                                  #
###############################################################################


@dataclass
class SkillModifier:
    """Container for one-value callables that act on Levels.

    Skill modifiers take in one ore more levels and return one or more levels
    for now, there is only a one to one type, if I need more for some reason it
    will be easy to upscale. Fun fact! The earlier version was too ambitious,
    and it sucked. Alhamdullilah, it works now!

    Attributes
    ----------

    skill : Skills
        The skill enum.

    value : SkillModifierCallableType
        The actual modifier function.

    """

    skill: Skills
    value: SkillModifierCallableType
