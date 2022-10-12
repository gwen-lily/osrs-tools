"""The three musketeers, the vanguards, the boys, whatever you call em they're here.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-10-12                                                         #
###############################################################################
"""
from __future__ import annotations

from osrs_tools.data import DT, Stances, Styles
from osrs_tools.style import MonsterStyle, MonsterStyles

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################

_MELEE_NAME = "vanguard (melee)"
_LVLS_MEL, _AGG_MEL, _DEF_MEL = get_base_levels_and_stats(_MELEE_NAME)

_RANGED_NAME = "vanguard (ranged)"
_LVLS_RNG, _AGG_RNG, _DEF_RNG = get_base_levels_and_stats(_RANGED_NAME)

_MAGIC_NAME = "vanguard (magic)"
_LVLS_MAG, _AGG_MAG, _DEF_MAG = get_base_levels_and_stats(_RANGED_NAME)

###############################################################################
# abstract class                                                              #
###############################################################################


class VanguardABC(CoxMonster):
    """Abstract Vanguard from which the others inherit"""

    def count_per_room(self) -> int:
        _ = self
        return 1


###############################################################################
# tekton (normal)                                                             #
###############################################################################


class MeleeVanguard(VanguardABC):
    """The melee vanguard from the Chambers of Xeric."""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> MeleeVanguard:
        _mel_style = MonsterStyle(
            Styles.NPC_MELEE,
            DT.CRUSH,
            Stances.NPC,
            _attack_speed=4,
        )

        _styles = MonsterStyles(_MELEE_NAME, [_mel_style], _mel_style)

        return cls(
            name=_MELEE_NAME,
            _levels=_LVLS_MEL,
            _aggressive_bonus=_AGG_MEL,
            combat_level=None,
            _defensive_bonus=_DEF_MEL,
            _styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )


class RangedVanguard(VanguardABC):
    """The melee vanguard from the Chambers of Xeric."""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> RangedVanguard:
        _rng_style = MonsterStyle(
            Styles.NPC_RANGED,
            DT.RANGED,
            Stances.NPC,
            _attack_speed=4,
        )

        _styles = MonsterStyles(_RANGED_NAME, [_rng_style], _rng_style)

        return cls(
            name=_RANGED_NAME,
            _levels=_LVLS_RNG,
            _aggressive_bonus=_AGG_RNG,
            combat_level=None,
            _defensive_bonus=_DEF_RNG,
            _styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )


class MageVanguard(VanguardABC):
    """The mage vanguard from the Chambers of Xeric."""

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> MageVanguard:
        _mag_style = MonsterStyle(
            Styles.NPC_MAGIC,
            DT.MAGIC,
            Stances.NPC,
            _attack_speed=4,
        )

        _styles = MonsterStyles(_MAGIC_NAME, [_mag_style], _mag_style)

        return cls(
            name=_MAGIC_NAME,
            _levels=_LVLS_MAG,
            _aggressive_bonus=_AGG_MAG,
            combat_level=None,
            _defensive_bonus=_DEF_MAG,
            _styles=_styles,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )
