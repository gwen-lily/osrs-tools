"""The Great Olm, possibly the Greatest Olm, quite frankly.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-01                                                         #
###############################################################################
"""
from __future__ import annotations

from dataclasses import dataclass, field

from osrs_tools.data import OLM_HAND_MAX_HP, OLM_HEAD_MAX_HP, MonsterTypes
from osrs_tools.tracked_value import Level, LevelModifier
from typing_extensions import Self

from .cox_monster import CoxMonster, get_base_levels_and_stats

###############################################################################
# get info                                                                    #
###############################################################################

_HEAD_NAME = "Great Olm"
_LVLS_HEAD, _AGG_HEAD, _DEF_HEAD = get_base_levels_and_stats(_HEAD_NAME)

_MAGE_HAND_NAME = "Great Olm (right/mage claw)"
_LVLS_MAGE, _AGG_MAGE, _DEF_MAGE = get_base_levels_and_stats(_MAGE_HAND_NAME)

_MELEE_HAND_NAME = "Great Olm (left/melee claw)"
_LVLS_MELEE, _AGG_MELEE, _DEF_MELEE = get_base_levels_and_stats(_MELEE_HAND_NAME)

###############################################################################
# abstract classes                                                            #
###############################################################################


@dataclass
class OlmABC(CoxMonster):
    """Abstract Olm from which others inherit"""

    special_attributes: list[MonsterTypes] = field(
        init=False,
        default_factory=lambda: [MonsterTypes.XERICIAN, MonsterTypes.DRACONIC],
    )

    # properties

    @property
    def player_hp_scaling_factor(self) -> LevelModifier:
        return LevelModifier(1, f"player hp ({self.name})")

    @property
    def player_off_def_scaling_factor(self) -> LevelModifier:
        return LevelModifier(1, f"player offensive & defensive ({self.name})")

    @property
    def party_hp_scaling_factor(self) -> LevelModifier:
        n = self.party_size
        value = ((n + 1) - 3 * (n // 8)) / 2
        comment = "party hp (olm)"
        return LevelModifier(value, comment)

    @property
    def challenge_mode_hp_scaling_factor(self) -> LevelModifier | None:
        if self.challenge_mode:
            value = 1
            comment = "cm hp (olm)"
            return LevelModifier(value, comment)

        return

    @property
    def phases(self) -> int:
        return min([3 + (self.party_size // 8), 9])


class OlmHandABC(OlmABC):
    """Abstract Olm hand from which Mage hand and Melee hand inherit"""

    # dunder and helper methods

    def _scale_levels(self) -> Self:
        super()._scale_levels()

        _HP = Level(OLM_HAND_MAX_HP)

        if self._levels.hitpoints > _HP:
            self._levels.hitpoints = _HP

        return self

    def count_per_room(self) -> int:
        return self.phases


###############################################################################
# main classes                                                                #
###############################################################################


class OlmHead(OlmABC):

    # dunder and helper methods

    def _scale_levels(self) -> Self:
        super()._scale_levels()

        _HP = Level(OLM_HEAD_MAX_HP)

        if self._levels.hitpoints > _HP:
            self._levels.hitpoints = _HP

        return self

    @staticmethod
    def count_per_room() -> int:
        return 1

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> OlmHead:
        return cls(
            name=_HEAD_NAME,
            _levels=_LVLS_HEAD,
            _aggressive_bonus=_AGG_HEAD,
            combat_level=None,
            _defensive_bonus=_DEF_HEAD,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )


@dataclass
class OlmMeleeHand(OlmHandABC):
    _crippled: bool = False

    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> OlmMeleeHand:
        return cls(
            name=_MELEE_HAND_NAME,
            _levels=_LVLS_MELEE,
            _aggressive_bonus=_AGG_MELEE,
            combat_level=None,
            _defensive_bonus=_DEF_MELEE,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )

    def cripple(self):
        pass

    @property
    def crippled(self) -> bool:
        raise NotImplementedError


class OlmMageHand(OlmHandABC):
    @classmethod
    def simple(cls, party_size: int, challenge_mode: bool = False) -> OlmMageHand:
        return cls(
            name=_MAGE_HAND_NAME,
            _levels=_LVLS_MAGE,
            _aggressive_bonus=_AGG_MAGE,
            combat_level=None,
            _defensive_bonus=_DEF_MAGE,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )
