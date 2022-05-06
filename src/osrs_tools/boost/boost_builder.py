"""A builder class for Boost objects

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-02                                                        #
###############################################################################
"""
from osrs_tools.data import Skills
from osrs_tools.tracked_value import (
    Level,
    LevelModifier,
    MaximumVisibleLevel,
    MinimumVisibleLevel,
)

from .skill_modifier import SkillModifier, SkillModifierCallableType


class BoostBuilder:
    """Builder for Boost, SkillModifier, etc.

    OSRS boosts tend to have the form:
        boost(level) = base_boost + math.floor(ratio_boost*level)

    This builder class simplifies definition to one line of the form:
        [f: (int, float, bool | None)] -> [f': (int,) -> int].


    Raises
    ------
    TypeError
    """

    @staticmethod
    def create_callable(
        base: int,
        ratio: float,
        negative: bool | None = None,
        comment: str | None = None,
    ) -> SkillModifierCallableType:
        """Create and return a CallableLevelsModifier.

        This documentation was written in a questionable state to say the
        least, if you by some chance are reading this, please open an issue
        on github.

        Parameters
        ----------
        base : int
            Note that's "base boost", not to be confused with the "bass boost"
            you might find on your speaker.
        ratio : float
            Get ratio'd nerd.
        negative : bool | None, optional
            No positive vibes allowed. Listen to gy!be., by default None.
        comment : str | None, optional
            A note on the source or operations of the modifier. Defaults to
            None.

        Returns
        -------
        CallableLevelsModifierType
        """

        def inner_builder(lvl: Level) -> Level:
            ratio_mod = LevelModifier(float(ratio), comment)
            diffval = (lvl * ratio_mod) + base

            new_lvl = lvl - diffval if negative is True else lvl + diffval
            new_lvl = min([max([MinimumVisibleLevel, new_lvl]), MaximumVisibleLevel])

            return new_lvl

        return inner_builder

    def create_skill_modifier(
        self,
        skill: Skills,
        base: int,
        ratio: float,
        negative: bool | None = None,
        comment: str | None = None,
    ) -> SkillModifier:
        _callable = self.create_callable(base, ratio, negative, comment)
        return SkillModifier(skill, _callable)
