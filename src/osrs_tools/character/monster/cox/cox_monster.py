"""Definition of the abstract cox monster.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-30                                                         #
###############################################################################
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass, field

from osrs_tools import resource_reader as rr
from osrs_tools.character.player import Player
from osrs_tools.data import (
    COX_POINTS_PER_HITPOINT,
    PARTY_AVERAGE_MINING_LEVEL,
    Level,
    LevelModifier,
    MonsterLocations,
    MonsterTypes,
)
from osrs_tools.stats import (
    AggressiveStats,
    DefensiveStats,
    MonsterLevels,
    PlayerLevels,
)
from typing_extensions import Self

from ..monster import Monster

###############################################################################
# helper functions                                                            #
###############################################################################


def get_base_levels_and_stats(
    name: str,
) -> tuple[MonsterLevels, AggressiveStats, DefensiveStats]:
    mon_df = rr.get_cox_monster_base_stats_by_name(name)

    levels = MonsterLevels(
        _attack=Level(mon_df["melee"].values[0]),
        _strength=Level(mon_df["melee"].values[0]),
        _defence=Level(mon_df["defence"].values[0]),
        _ranged=Level(mon_df["ranged"].values[0]),
        _magic=Level(mon_df["magic"].values[0]),
        _hitpoints=Level(mon_df["hp"].values[0]),
    )
    aggressive_melee_bonus = mon_df["melee att+"].values[0]
    aggressive_bonus = AggressiveStats(
        stab=aggressive_melee_bonus,
        slash=aggressive_melee_bonus,
        crush=aggressive_melee_bonus,
        magic_attack=mon_df["magic att+"].values[0],
        ranged_attack=mon_df["ranged att+"].values[0],
        melee_strength=mon_df["melee str+"].values[0],
        ranged_strength=mon_df["ranged str+"].values[0],
        magic_strength=mon_df["magic str+"].values[0],
    )
    defensive_bonus = DefensiveStats(
        stab=mon_df["stab def+"].values[0],
        slash=mon_df["slash def+"].values[0],
        crush=mon_df["crush def+"].values[0],
        magic=mon_df["magic def+"].values[0],
        ranged=mon_df["ranged def+"].values[0],
    )
    return levels, aggressive_bonus, defensive_bonus


###############################################################################
# main abstract class                                                         #
###############################################################################


@dataclass
class CoxMonster(Monster, ABC):
    """CoxMonster is an abstract class from which all cox monsters derive.

    Every CoxMonster class should override pretty much every attribute until
    all that is left is party size, challenge mode, and a few kwargs.
    """

    challenge_mode: bool = False
    _levels: MonsterLevels = field(repr=False)
    location: MonsterLocations = MonsterLocations.COX
    party_size: int = field(default=1)
    party_max_combat_level: Level = field(default_factory=Player.max_combat_level)
    party_max_hitpoints_level: Level = field(
        default_factory=PlayerLevels.max_skill_level
    )
    party_average_mining_level: Level = field(
        default_factory=lambda: Level(PARTY_AVERAGE_MINING_LEVEL)
    )
    special_atttributes: list[MonsterTypes] = field(
        default_factory=lambda: [MonsterTypes.XERICIAN]
    )

    # dunder and helper methods

    def __post_init__(self) -> None:
        self._scale_levels()  # modify self._levels

        return super().__post_init__()  # reset character & stats

    def __copy__(self) -> CoxMonster:
        _val = super().__copy__()
        assert isinstance(_val, CoxMonster)

        return _val

    def __str__(self):
        _s = f"{self.name} ({self.party_size})"
        return _s

    def _scale_levels(self) -> Self:
        """Scale levels by cox modifiers."""

        # order matters, floor each intermediate value (handled via my arcane dataclasses)
        _lvl: MonsterLevels = self._levels

        hp_scaled = (
            _lvl.hitpoints
            * self.player_hp_scaling_factor
            * self.party_hp_scaling_factor
        )
        hp_scaled = (
            hp_scaled * self.cm_hp_scaling_factor if self.challenge_mode else hp_scaled
        )

        # TODO: Refactor this into Olm/Head/Hands
        # if isinstance(self, OlmHead) and hp_scaled > 13600:
        #     hp_scaled = Level(13600, "olm head max hp")
        # elif (
        #     isinstance(self, OlmMeleeHand) or isinstance(self, OlmMageHand)
        # ) and hp_scaled > 10200:
        #     hp_scaled = Level(10200, "olm hand max hp")

        _lvl.hitpoints = hp_scaled

        # attack and strength
        melee_scaled = (
            _lvl.attack
            * self.player_off_def_scaling_factor
            * self.party_off_scaling_factor
        )
        melee_scaled = (
            melee_scaled * self.cm_off_scaling_factor
            if self.challenge_mode
            else melee_scaled
        )
        _lvl.attack = melee_scaled
        _lvl.strength = copy(_lvl.attack)

        defence_scaled = (
            _lvl.defence
            * self.player_off_def_scaling_factor
            * self.party_def_scaling_factor
        )
        _lvl.defence = (
            defence_scaled * self.cm_def_scaling_factor
            if self.challenge_mode
            else defence_scaled
        )

        magic_scaled = (
            _lvl.magic
            * self.player_off_def_scaling_factor
            * self.party_off_scaling_factor
        )
        _lvl.magic = (
            magic_scaled * self.cm_off_scaling_factor
            if self.challenge_mode
            else magic_scaled
        )

        ranged_scaled = (
            _lvl.ranged
            * self.player_off_def_scaling_factor
            * self.party_off_scaling_factor
        )
        _lvl.ranged = (
            ranged_scaled * self.cm_off_scaling_factor
            if self.challenge_mode
            else ranged_scaled
        )

        return self

    # properties

    @property
    def player_hp_scaling_factor(self) -> LevelModifier:
        value = int(self.party_max_combat_level) / int(Player.max_combat_level())
        comment = "player hp"
        return LevelModifier(value, comment)

    @property
    def player_off_def_scaling_factor(self) -> LevelModifier:
        value = (math.floor(int(self.party_max_hitpoints_level) * 4 / 9) + 55) / 99
        comment = "player offensive & defensive"
        return LevelModifier(value, comment)

    @property
    def party_hp_scaling_factor(self) -> LevelModifier:
        n = self.party_size
        value = 1 + math.floor(n / 2)
        comment = "party hp"
        return LevelModifier(value, comment)

    @property
    def party_off_scaling_factor(self) -> LevelModifier:
        n = self.party_size
        value = (7 * math.floor(math.sqrt(n - 1)) + (n - 1) + 100) / 100
        comment = "party offensive"
        return LevelModifier(value, comment)

    @property
    def party_def_scaling_factor(self) -> LevelModifier:
        n = self.party_size
        value = (
            math.floor(math.sqrt(n - 1)) + math.floor((7 / 10) * (n - 1)) + 100
        ) / 100
        comment = "party defensive"
        return LevelModifier(value, comment)

    @property
    def cm_hp_scaling_factor(self) -> LevelModifier | None:
        if self.challenge_mode:
            value = 3 / 2
            comment = "cm hp"
            return LevelModifier(value, comment)

    @property
    def cm_off_scaling_factor(self) -> LevelModifier | None:
        if self.challenge_mode:
            value = 3 / 2
            comment = "cm offensive"
            return LevelModifier(value, comment)

    @property
    def cm_def_scaling_factor(self) -> LevelModifier | None:
        if self.challenge_mode:
            value = 3 / 2
            comment = "cm defensive"
            return LevelModifier(value, comment)

    # methods

    @abstractmethod
    def count_per_room(self, **kwargs) -> int:
        ...

    def points_per_room(self, **kwargs) -> int:
        _count = self.count_per_room(**kwargs)
        hp = self._levels.hitpoints
        assert isinstance(hp, Level)

        return int(hp * _count * COX_POINTS_PER_HITPOINT)

    # class methods

    @abstractmethod
    @classmethod
    def simple(
        cls, party_size: int, challenge_mode: bool = False, **kwargs
    ) -> CoxMonster:
        """A simple constructor for concrete CoxMonsters.

        Parameters
        ----------
        party_size : int
            The size of the raid at the start.
        challenge_mode : bool, optional
            True if the raid is challenge mode, by default False

        Returns
        -------
        CoxMonster
        """
