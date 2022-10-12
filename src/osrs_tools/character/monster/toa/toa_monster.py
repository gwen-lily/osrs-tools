import math
from abc import ABC
from dataclasses import dataclass, field

from osrs_tools.data import (
    TOA_MAX_PARTY_SIZE,
    TOA_MAX_RAID_LEVEL,
    TOA_PATH_MOD_0,
    TOA_PATH_MOD_1,
    TOA_RAID_LVL_MOD,
    TOA_TEAM_MOD_HIGH,
    TOA_TEAM_MOD_LOW,
    MonsterLocations,
    MonsterTypes,
)
from osrs_tools.stats.combat_stats import MonsterLevels
from osrs_tools.tracked_value.tracked_values import Level
from typing_extensions import Self

from ..monster import Monster


@dataclass
class ToaMonster(Monster, ABC):
    raid_level: int = field(default=300)
    path_level: int = field(default=0)
    party_size: int = field(default=1)
    _levels: MonsterLevels = field(repr=False)
    location: MonsterLocations = MonsterLocations.TOA
    special_attributes: list[MonsterTypes] = field(default_factory=lambda: [MonsterTypes.TOA])

    # dunder and helper methods

    def __post__init__(self):
        self._scale_levels()  # modify self._levels

        if not (0 <= self.path_level <= TOA_MAX_RAID_LEVEL):
            raise ValueError(self.path_level)

        if not (1 <= self.party_size <= TOA_MAX_PARTY_SIZE):
            raise ValueError(self.party_size)

        return super().__post_init__()

    def __str__(self):
        string = f"{self.name} ({self.party_size}, {self.raid_level})"
        return string

    def _scale_levels(self, __hp_value: int, __post_mod: int | None = None, /) -> Self:
        """scale attack, strength, defence, and hitpoints levels.

        Parameters
        ----------
        __hp_value : int
            unique value for every monster, NOT the same as base HP (irrelevant)
        __post_mod : _type_
            the modifier applied after the floor step

        Returns
        -------
        Self
        """

        # inner functions

        def _raid_level_factor():
            return 1 + TOA_RAID_LVL_MOD * (self.raid_level // 5)

        def _path_level_factor():
            factor_0 = TOA_PATH_MOD_0 if self.path_level > 0 else TOA_PATH_MOD_1
            factor_1 = TOA_PATH_MOD_1 * (self.path_level - 1)
            return 1 + factor_1 + factor_0

        def _team_size_factor() -> float:
            if 1 <= (ps := self.party_size) <= 3:
                return 1 + TOA_TEAM_MOD_LOW * (ps - 1)

            return 3.4 + TOA_TEAM_MOD_HIGH * (ps - 4)

        # scaling

        base_hitpoints = __hp_value  # not actually base hitpoints, but analogous
        base_attack = int(self._levels.attack)
        base_strength = int(self._levels.strength)
        base_defence = int(self._levels.defence)

        # hitpoints scales on raid level, path level, and team size
        hp = math.floor(base_hitpoints * _raid_level_factor() * _path_level_factor() * _team_size_factor())

        # true for bosses and some boss minions
        if isinstance(__post_mod, int):
            hp *= __post_mod

        # attack scales on raid level
        attack = math.floor(base_attack * _raid_level_factor())

        # strength on raid level and path level
        max_strength = (150 * base_strength) // 100
        strength = math.floor(base_strength * _raid_level_factor() * _path_level_factor())
        strength = min([max([base_strength, strength]), max_strength])

        # defence scales on raid level
        defence = math.floor(base_defence * _raid_level_factor())

        # re-assignment
        self._levels.attack = Level(attack)
        self._levels.strength = Level(strength)
        self._levels.defence = Level(defence)
        self._levels.hitpoints = Level(hp)

        return self
