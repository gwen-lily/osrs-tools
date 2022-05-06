"""PrayerCollection definition

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from dataclasses import dataclass, field

from osrs_tools.data import Skills
from osrs_tools.tracked_value import LevelModifier

from .prayer import Prayer, PrayerError


@dataclass
class Prayers:
    """Container class for prayers.

    Attributes
    ----------
    name : str
        Name of the collection
    prayers : list[Prayer], optional
        A list of the active prayers.

    Raises
    ------
    PrayerError
    """

    name: str = field(default_factory=str)
    prayers: list[Prayer] = field(default_factory=list)

    # dunder & utility methods

    def __iter__(self):
        yield from self.prayers

    def __len__(self) -> int:
        return len(self.prayers)

    def _get_prayer_collection_attribute(self, attribute: str) -> LevelModifier | None:
        relevant_prayers = [
            p for p in self.prayers if p.__getattribute__(attribute) is not None
        ]
        if len(relevant_prayers) == 0:
            return None
        elif len(relevant_prayers) == 1:
            return relevant_prayers[0].__getattribute__(attribute)
        else:
            raise PrayerError(f"{attribute=} with {relevant_prayers=}")

    # basic methods

    def pray(self, *prayers: Prayer | Prayers):
        """Add any prayers to the current collection."""
        for p in prayers:
            if isinstance(p, Prayer):
                self.prayers.append(p)
            elif isinstance(p, Prayers):
                self.prayers.extend(p.prayers)

    def reset_prayers(self):
        """Remove all active prayers."""
        self.prayers = []

    # properties

    @property
    def drain_effect(self):
        return sum([p.drain_effect for p in self.prayers])

    # class methods

    @classmethod
    def no_prayers(cls):
        raise DeprecationWarning
        # return cls()

    @property
    def attack(self):
        return self._get_prayer_collection_attribute(Skills.ATTACK.value)

    @property
    def strength(self):
        return self._get_prayer_collection_attribute(Skills.STRENGTH.value)

    @property
    def defence(self):
        return self._get_prayer_collection_attribute(Skills.DEFENCE.value)

    @property
    def ranged_attack(self):
        return self._get_prayer_collection_attribute("ranged_attack")

    @property
    def ranged_strength(self):
        return self._get_prayer_collection_attribute("ranged_strength")

    @property
    def magic_attack(self):
        return self._get_prayer_collection_attribute("magic_attack")

    @property
    def magic_strength(self):
        return self._get_prayer_collection_attribute("magic_strength")

    @property
    def magic_defence(self):
        return self._get_prayer_collection_attribute("magic_defence")
