"""Some right proper chinnable, yet dangerous lads if you ask me.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-01                                                         #
###############################################################################
"""
from __future__ import annotations

from osrs_tools.data import DT, Stances, Styles
from osrs_tools.style import MonsterStyle, MonsterStyles

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################


_MONSTER_NAME_MAGE = "deathly mage"
_LVLS_MAGE, _AGG_MAGE, _DEF_MAGE = get_base_levels_and_stats(_MONSTER_NAME_MAGE)

_MONSTER_NAME_RNG = "deathly ranger"
_LVLS_RNG, _AGG_RNG, _DEF_RNG = get_base_levels_and_stats(_MONSTER_NAME_RNG)

###############################################################################
# abstract class                                                              #
###############################################################################


class DeathlyABC(CoxMonster):
    """Abstract rope monster from which Mage and Ranger inherit."""

    def count_per_room(self) -> int:
        """
        source: @JagexAsh
        https://twitter.com/JagexAsh/status/1386459382834139136
        """
        count = min([1 + self.party_size // 5, 4])
        return count


###############################################################################
# deathly mage                                                                #
###############################################################################


class DeathlyMage(DeathlyABC):
    """The Deathly Mage from the Chambers of Xeric"""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> DeathlyMage:
        _style = MonsterStyle(
            Styles.NPC_MAGIC,
            DT.MAGIC,
            Stances.NPC,
            _attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True,
        )
        _styles = MonsterStyles(_MONSTER_NAME_MAGE, [_style], _style)

        return cls(
            name=_MONSTER_NAME_MAGE,
            _levels=_LVLS_MAGE,
            _aggressive_bonus=_AGG_MAGE,
            combat_level=None,
            _defensive_bonus=_DEF_MAGE,
            styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )


###############################################################################
# deathly ranger                                                              #
###############################################################################


class DeathlyRanger(DeathlyABC):
    """Deathly Ranger from the Chambers of Xeric."""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> DeathlyRanger:
        _style = MonsterStyle(
            Styles.NPC_RANGED,
            DT.RANGED,
            Stances.NPC,
            _attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True,
        )
        _styles = MonsterStyles(_MONSTER_NAME_RNG, [_style], _style)

        return cls(
            name=_MONSTER_NAME_RNG,
            _levels=_LVLS_RNG,
            _aggressive_bonus=_AGG_RNG,
            combat_level=None,
            _defensive_bonus=_DEF_RNG,
            styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )
