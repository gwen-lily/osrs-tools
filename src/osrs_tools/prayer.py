"""Prayer & PrayerCollection definition, along with all important prayers.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from dataclasses import dataclass, field

from osrsbox import prayers_api

from osrs_tools.data import LevelModifier, Skills
from osrs_tools.exceptions import OsrsException

###############################################################################
# errors 'n such                                                              #
###############################################################################

PRAYERS = prayers_api.load()


class PrayerError(OsrsException):
    pass


###############################################################################
# prayer & prayer collection                                                  #
###############################################################################


@dataclass(order=True, frozen=True)
class Prayer:
    name: str
    drain_effect: int
    attack: LevelModifier | None = None
    strength: LevelModifier | None = None
    defence: LevelModifier | None = None
    ranged_attack: LevelModifier | None = None
    ranged_strength: LevelModifier | None = None
    magic_attack: LevelModifier | None = None
    magic_strength: LevelModifier | None = None
    magic_defence: LevelModifier | None = None

    @classmethod
    def from_osrsbox(
        cls,
        *,
        name: str | None = None,
        prayer_id: int | None = None,
        drain_effect: int,
        **kwargs,
    ):
        """Get Prayer from osrsbox-db source.

        Specify either name or id.

        Parameters
        ----------
        drain_effect : int
            The prayer's drain effect, check the wiki.
        name : str | None, optional
            The name of the prayer, by default None
        prayer_id : int | None, optional
            The id of the prayer, by default None

        Raises
        ------
        PrayerError
        """
        options = {
            Skills.ATTACK.value: None,
            Skills.STRENGTH.value: None,
            Skills.DEFENCE.value: None,
            "ranged_attack": None,
            "ranged_strength": None,
            "magic_attack": None,
            "magic_strength": None,
            "magic_defence": None,
        }

        for pp in PRAYERS.all_prayers:
            if pp.name == name or pp.id == prayer_id:
                options.update(pp.bonuses)  # update with osrsbox source first
                if options.get("magic"):
                    val = options.pop("magic")
                    options["magic_attack"] = val

                if options.get("ranged"):
                    val = options.pop("ranged")
                    options["ranged_attack"] = val

                options.update(kwargs)  # fix any jank as needed (augury)
                comment = pp.name

                active_options = {
                    k: LevelModifier(1 + 0.01 * v, comment)
                    for k, v in options.items()
                    if v is not None
                }
                return cls(pp.name, drain_effect, **active_options)

        raise PrayerError(f"{name=}")


@dataclass
class PrayerCollection:
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

    def pray(self, *prayers: Prayer | PrayerCollection):
        """Add any prayers to the current collection."""
        for p in prayers:
            if isinstance(p, Prayer):
                self.prayers.append(p)
            elif isinstance(p, PrayerCollection):
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


###############################################################################
# prayer definition                                                           #
###############################################################################

Augury = Prayer.from_osrsbox(
    prayer_id=29, defence=25, magic_defence=25, drain_effect=24
)
Rigour = Prayer.from_osrsbox(prayer_id=28, drain_effect=24)
Piety = Prayer.from_osrsbox(prayer_id=27, drain_effect=24)
Chivalry = Prayer.from_osrsbox(prayer_id=26, drain_effect=24)
Preserve = Prayer.from_osrsbox(prayer_id=25, drain_effect=2)
Smite = Prayer.from_osrsbox(prayer_id=24, drain_effect=18)
Redemption = Prayer.from_osrsbox(prayer_id=23, drain_effect=6)
Retribution = Prayer.from_osrsbox(prayer_id=22, drain_effect=3)
MysticMight = Prayer.from_osrsbox(prayer_id=21, drain_effect=12)
EagleEye = Prayer.from_osrsbox(prayer_id=20, drain_effect=12)
ProtectFromMelee = Prayer.from_osrsbox(prayer_id=19, drain_effect=12)
ProtectFromMissiles = Prayer.from_osrsbox(prayer_id=18, drain_effect=12)
ProtectFromMagic = Prayer.from_osrsbox(prayer_id=17, drain_effect=12)
IncredibleReflexes = Prayer.from_osrsbox(prayer_id=16, drain_effect=12)
MysticLore = Prayer.from_osrsbox(prayer_id=13, drain_effect=6)
