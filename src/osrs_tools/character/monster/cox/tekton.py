"""The large lad, Tekton and his enraged form.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-01                                                         #
###############################################################################
"""
from __future__ import annotations

from osrs_tools.data import DT, Stances, Styles
from osrs_tools.style import MonsterStyle, MonsterStyles
from osrs_tools.tracked_value import LevelModifier

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
        if not self.challenge_mode:
            return

        value = 12 / 10
        comment = "cm defensive (tekton)"
        return LevelModifier(value, comment)

    def count_per_room(self) -> int:
        _ = self
        return 1


###############################################################################
# tekton (normal)                                                             #
###############################################################################


class Tekton(TektonABC):
    """The normal tekton from the Chambers of Xeric."""

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
            _styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )


###############################################################################
# tekton (enraged)                                                            #
###############################################################################


class TektonEnraged(TektonABC):
    """The enraged tekton from the Chambers of Xeric."""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> TektonEnraged:

        _mel_style = MonsterStyle(
            Styles.NPC_MELEE,
            DT.CRUSH,
            Stances.NPC,
            _attack_speed=4,
        )

        _styles = MonsterStyles(_MONSTER_NAME_SMOL, [_mel_style], _mel_style)

        return cls(
            name=_MONSTER_NAME_BIG,
            _levels=_LVLS_BIG,
            _aggressive_bonus=_AGG_BIG,
            combat_level=None,
            _defensive_bonus=_DEF_BIG,
            _styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )
