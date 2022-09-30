"""The abyssal portal we smack on loop with tbows from a distance.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-01                                                         #
###############################################################################
"""
from __future__ import annotations

from osrs_tools.data import MonsterTypes
from osrs_tools.tracked_value import LevelModifier

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################

_MONSTER_NAME = "abyssal portal"
_LVLS, _AGG, _DEF = get_base_levels_and_stats(_MONSTER_NAME)


class AbyssalPortal(CoxMonster):
    """__FOO__ from the Chambers of Xeric."""

    @property
    def party_off_scaling_factor(self) -> LevelModifier:
        return self.party_def_scaling_factor

    @staticmethod
    def count_per_room() -> int:
        return 1

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> AbyssalPortal:
        return cls(
            name=_MONSTER_NAME,
            _levels=_LVLS,
            _aggressive_bonus=_AGG,
            combat_level=None,
            _defensive_bonus=_DEF,
            special_attributes=[MonsterTypes.XERICIAN, MonsterTypes.DEMON],
            party_size=party_size,
            challenge_mode=challenge_mode,
        )
