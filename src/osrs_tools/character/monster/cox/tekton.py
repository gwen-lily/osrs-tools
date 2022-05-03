"""The large lad, Tekton and his enraged form.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-01                                                         #
###############################################################################
"""
from __future__ import annotations

import math

from osrs_tools.data import COX_POINTS_PER_HITPOINT, DT, LevelModifier, Stances, Styles
from osrs_tools.style import MonsterStyle, MonsterStyles

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################

_MONSTER_NAME_SMOL = "tekton"
_LVLS_SMOL, _AGG_SMOL, _DEF_SMOL = get_base_levels_and_stats(_MONSTER_NAME_SMOL)

_MONSTER_NAME_BIG = "tekton (enraged)"
_LVLS_BIG, _AGG_BIG, _DEF_BIG = get_base_levels_and_stats(_MONSTER_NAME_BIG)

###############################################################################
# abstract class                                                              #
###############################################################################


class TektonABC(CoxMonster):
    """Abstract Tekton from which Normal and Enraged inherit"""

    @property
    def cm_def_scaling_factor(self) -> LevelModifier | None:
        if self.challenge_mode:
            value = 12 / 10
            comment = "cm defensive (tekton)"
            return LevelModifier(value, comment)

    def count_per_room(self) -> int:
        _ = self
        return 1

    def points_per_room(self, freeze: bool = True) -> int:
        count = self.count_per_room()
        effective_hp = self.base_hp
        return math.floor(count * int(effective_hp) * COX_POINTS_PER_HITPOINT)


###############################################################################
# tekton (normal)                                                             #
###############################################################################


class Tekton(TektonABC):
    """The small muttadile from the Chambers of Xeric."""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> Tekton:
        _mel_style = MonsterStyle(
            Styles.NPC_MELEE,
            DT.CRUSH,
            Stances.NPC,
            _attack_speed=4,
        )

        _styles = MonsterStyles(_MONSTER_NAME_SMOL, [_mel_style], _mel_style)

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
# tekton (enraged)                                                            #
###############################################################################


class BigMuttadile(TektonABC):
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
