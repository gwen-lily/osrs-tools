from __future__ import annotations

from attrs import define, field
from cached_property import cached_property
from osrsbox import prayers_api
from osrsbox.prayers_api import prayer_properties

from osrs_tools.data import LevelModifier, Skills
from osrs_tools.exceptions import OsrsException

PRAYERS = prayers_api.load()


# noinspection PyArgumentList
@define(order=True, frozen=True)
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
        cls, *, name: str = None, prayer_id: int = None, drain_effect: int, **kwargs
    ):
        """Generate Prayer object from osrsbox-db Prayers module.

        Args:
                drain_effect (int): Each prayer has an associated drain effect (see more at
                https://oldschool.runescape.wiki/w/Prayer#Prayer_drain_mechanics).
                name (str, optional): The name of the prayer in the osrsbox-db. Defaults to None.
                prayer_id (int, optional): The id of the prayer in the osrsbox-db. Defaults to None.

        Raises:
                PrayerError: Raised if the search parameters yield no info.

        Returns:
                Prayer:
        """
        options = {
            Skills.ATTACK.name: None,
            Skills.STRENGTH.name: None,
            Skills.defence.name: None,
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

MysticLore = Prayer.from_osrsbox(prayer_id=13, drain_effect=6)


def prayer_collection_validator(instance, attribute: str, value: tuple[Prayer, ...]):
    pass  # TODO: Create validators that handle better than the current system.


@define
class PrayerCollection:
    name: str = field(factory=str, converter=str)
    prayers: tuple[Prayer, ...] = field(factory=tuple)

    def pray(self, *prayers: Prayer | PrayerCollection):
        prayers_list = []

        for p in prayers:
            if isinstance(p, Prayer):
                prayers_list.append(p)
            elif isinstance(p, PrayerCollection):
                prayers_list.extend(p.prayers)

        self.prayers = tuple(prayers_list)

    def reset_prayers(self):
        self.prayers = tuple()

    @property
    def drain_effect(self):
        return sum([p.drain_effect for p in self.prayers])

    @classmethod
    def no_prayers(cls):
        return cls()

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

    @property
    def attack(self):
        return self._get_prayer_collection_attribute(Skills.ATTACK.name)

    @property
    def strength(self):
        return self._get_prayer_collection_attribute(Skills.STRENGTH.name)

    @property
    def defence(self):
        return self._get_prayer_collection_attribute(Skills.defence.name)

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

    def __iter__(self):
        return iter(self.prayers)


class PrayerError(OsrsException):
    pass
