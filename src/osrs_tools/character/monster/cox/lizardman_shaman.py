"""Imagine not stacking and chinning shamans in every raid :3

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-01                                                         #
###############################################################################
"""
from __future__ import annotations

from osrs_tools.data import DT, Slayer, Stances, Styles
from osrs_tools.style.style import MonsterStyle, MonsterStyles

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################

_MONSTER_NAME = "lizardman shaman"
_LVLS, _AGG, _DEF = get_base_levels_and_stats(_MONSTER_NAME)


class LizardmanShaman(CoxMonster):
    """The Lizardman Shaman from the Chambers of Xeric."""

    def count_per_room(self, scale_at_load_time: int | None = None) -> int:
        """
        source: @JagexAsh
        https://twitter.com/JagexAsh/status/1386459382834139136
        """
        scale_at_load_time = (
            self.party_size if scale_at_load_time is None else scale_at_load_time
        )

        count = min([2 + scale_at_load_time // 5, 5])
        return count

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> LizardmanShaman:
        _rng_style = MonsterStyle(
            Styles.NPC_RANGED,
            DT.RANGED,
            Stances.NPC,
            _attack_speed=4,
        )
        _mel_style = MonsterStyle(
            Styles.NPC_MELEE,
            DT.CRUSH,
            Stances.NPC,
            _attack_speed=4,
        )

        _styles = MonsterStyles(_MONSTER_NAME, [_rng_style, _mel_style], _rng_style)

        return cls(
            name=_MONSTER_NAME,
            _levels=_LVLS,
            _aggressive_bonus=_AGG,
            combat_level=None,
            _defensive_bonus=_DEF,
            slayer_category=Slayer.LIZARDMEN,
            styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )
