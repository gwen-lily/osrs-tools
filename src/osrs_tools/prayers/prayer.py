"""Prayer definition

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from dataclasses import dataclass

from osrs_tools.data import PRAYERS, LevelModifier, Skills
from osrs_tools.exceptions import OsrsException

###############################################################################
# errors 'n such                                                              #
###############################################################################


class PrayerError(OsrsException):
    pass


###############################################################################
# main class                                                                  #
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

        raise ValueError(name)
