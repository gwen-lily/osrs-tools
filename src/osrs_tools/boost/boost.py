"""Definition of boost and some subclasses

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-02                                                        #
###############################################################################
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass, fields

from osrs_tools.data import Skills

from .data import SkillModifierCallableType
from .skill_modifier import SkillModifier

###############################################################################
# main classes                                                                #
###############################################################################


@dataclass
class Boost:
    """Describes OSRS potions and boost effects.

    Attributes
    ----------
    name : str
        The name of the boost.
    modifiers: list[SkillModifier]
        A list of SkillModifiers.
    """

    name: str
    modifiers: list[SkillModifier]

    def __str__(self):
        _s = f"{self.__class__.__name__}({self.name})"
        return _s

    # class methods

    @classmethod
    def uniform_boost(
        cls, name: str, skills: list[Skills], skill_modifier: SkillModifierCallableType
    ):
        _modifiers: list[SkillModifier] = []

        for skill in skills:
            _modifiers.append(SkillModifier(skill, skill_modifier))

        return cls(name, _modifiers)


class DivineBoost(Boost):
    """A divine potion effect"""

    # class methods

    @classmethod
    def from_boost(cls, __boost: Boost) -> DivineBoost:
        """Create a divine boost from an existing boost."""
        unpacked = {
            field.name: copy(getattr(__boost, field.name)) for field in fields(__boost)
        }
        return cls(**unpacked)


class OverloadBoost(Boost):
    """An overload potion effect"""
