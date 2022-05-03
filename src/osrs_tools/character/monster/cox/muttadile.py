"""Adorable little critter and its fearsome momma.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-01                                                         #
###############################################################################
"""
from __future__ import annotations

import math

from osrs_tools.data import (
    COX_POINTS_PER_HITPOINT,
    DT,
    MUTTA_EATS_PER_ROOM,
    MUTTA_HP_RATIO_HEALED_PER_EAT,
    LevelModifier,
    Stances,
    Styles,
)
from osrs_tools.style import MonsterStyle, MonsterStyles

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################

_MONSTER_NAME_SMOL = "muttadile (small)"
_LVLS_SMOL, _AGG_SMOL, _DEF_SMOL = get_base_levels_and_stats(_MONSTER_NAME_SMOL)

_MONSTER_NAME_BIG = "muttadile (big)"
_LVLS_BIG, _AGG_BIG, _DEF_BIG = get_base_levels_and_stats(_MONSTER_NAME_BIG)

###############################################################################
# abstract class                                                              #
###############################################################################


class MuttadileABC(CoxMonster):
    """Abstract muttadile from which big and smol inherit"""

    def count_per_room(self) -> int:
        _ = self
        return 1

    def points_per_room(self, freeze: bool = True) -> int:
        count = self.count_per_room()
        effective_hp = self.base_hp

        if freeze is False:
            value = 1 + MUTTA_EATS_PER_ROOM * MUTTA_HP_RATIO_HEALED_PER_EAT
            comment = "muttadile (no freeze)"
            hp_modifier = LevelModifier(value, comment)
            effective_hp *= hp_modifier

        return math.floor(count * int(effective_hp) * COX_POINTS_PER_HITPOINT)


###############################################################################
# smol muttadile                                                              #
###############################################################################


class SmallMuttadile(MuttadileABC):
    """The small muttadile from the Chambers of Xeric."""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> SmallMuttadile:
        _rng_style = MonsterStyle(
            Styles.NPC_RANGED,
            DT.RANGED,
            Stances.NPC,
            _attack_speed=4,
            ignores_prayer=True,
        )
        _mel_style = MonsterStyle(
            Styles.NPC_MELEE,
            DT.CRUSH,
            Stances.NPC,
            _attack_speed=4,
        )

        _styles = MonsterStyles(
            _MONSTER_NAME_SMOL, [_rng_style, _mel_style], _rng_style
        )

        return cls(
            name=_MONSTER_NAME_SMOL,
            _levels=_LVLS_SMOL,
            _aggressive_bonus=_AGG_SMOL,
            combat_level=None,
            _defensive_bonus=_DEF_SMOL,
            styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )


###############################################################################
# beeeeg muttadile                                                            #
###############################################################################


class BigMuttadile(MuttadileABC):
    """The big muttadile from the Chambers of Xeric."""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> BigMuttadile:
        _rng_style = MonsterStyle(
            Styles.NPC_RANGED,
            DT.RANGED,
            Stances.NPC,
            _attack_speed=4,
            ignores_prayer=True,
        )
        _mag_style = MonsterStyle(
            Styles.NPC_MAGIC,
            DT.MAGIC,
            Stances.NPC,
            _attack_speed=4,
            ignores_prayer=True,
        )
        _mel_style = MonsterStyle(
            Styles.NPC_MELEE,
            DT.CRUSH,
            Stances.NPC,
            _attack_speed=4,
        )

        _styles = MonsterStyles(
            _MONSTER_NAME_BIG, [_rng_style, _mag_style, _mel_style], _rng_style
        )

        return cls(
            name=_MONSTER_NAME_BIG,
            _levels=_LVLS_BIG,
            _aggressive_bonus=_AGG_BIG,
            combat_level=None,
            _defensive_bonus=_DEF_BIG,
            styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )
