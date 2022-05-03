"""Big blue lad, prone to getting arclight spec'd into oblivion and surged.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-30                                                         #
###############################################################################
"""
from __future__ import annotations

from osrs_tools.combat import combat as cmb
from osrs_tools.data import Level, MonsterTypes

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################

_MONSTER_NAME = "ice demon"
_LVLS, _AGG, _DEF = get_base_levels_and_stats(_MONSTER_NAME)


class IceDemon(CoxMonster):
    """Ice Demon from the Chambers of Xeric."""

    @property
    def effective_magic_defence_level(self) -> Level:
        defensive_level = self.levels.defence  # unique ice demon mechanic
        style_bonus = self.style.combat_bonus.magic_attack
        return cmb.effective_level(defensive_level, style_bonus)

    def count_per_room(self, **kwargs) -> int:
        _ = self
        return 1

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> IceDemon:
        return cls(
            name=_MONSTER_NAME,
            _levels=_LVLS,
            _aggressive_bonus=_AGG,
            combat_level=None,
            _defensive_bonus=_DEF,
            party_size=party_size,
            challenge_mode=challenge_mode,
            special_attributes=[MonsterTypes.XERICIAN, MonsterTypes.DEMON],
        )
