"""They don't guard very well. Bunch a big chickens if you ask me.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-01                                                         #
###############################################################################
"""
from __future__ import annotations

from osrs_tools.character.character import Character
from osrs_tools.character.player import Player
from osrs_tools.data import DT, Stances, Styles
from osrs_tools.style import MonsterStyle, MonsterStyles
from osrs_tools.tracked_value import DamageValue, Level

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################

_MONSTER_NAME = "guardian"
_LVLS, _AGG, _DEF = get_base_levels_and_stats(_MONSTER_NAME)


class Guardian(CoxMonster):
    """The Guardian from the Chambers of Xeric."""

    def damage(self, other: Character, *amount: int | DamageValue) -> DamageValue:
        if not isinstance(other, Player) or not other.eqp.pickaxe:
            return DamageValue(0)

        return super().damage(other, *amount)

    def count_per_room(self) -> int:
        """Source: dude trust me"""
        _ = self
        return 2

    @classmethod
    def simple(
        cls,
        party_size: int,
        challenge_mode: bool = False,
        party_average_mining_level: Level | None = None,
    ) -> Guardian:
        _mel_style = MonsterStyle(
            Styles.NPC_MELEE,
            DT.CRUSH,
            Stances.NPC,
            _attack_speed=4,
            ignores_prayer=True,
        )
        _styles = MonsterStyles(_MONSTER_NAME, [_mel_style], _mel_style)

        return cls(
            name=_MONSTER_NAME,
            _levels=_LVLS,
            _aggressive_bonus=_AGG,
            combat_level=None,
            _defensive_bonus=_DEF,
            styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )
