"""Definition of the abstract cox monster.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-30                                                         #
###############################################################################
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from osrs_tools import utils
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.data import COX_POINTS_PER_HITPOINT, PARTY_AVERAGE_MINING_LEVEL, MonsterLocations, MonsterTypes, Skills
from osrs_tools.stats import AggressiveStats, DefensiveStats, MonsterLevels, PlayerLevels
from osrs_tools.tracked_value import Level, LevelModifier
from typing_extensions import Self

###############################################################################
# helper functions                                                            #
###############################################################################


def get_base_levels_and_stats(
    name: str,
) -> tuple[MonsterLevels, AggressiveStats, DefensiveStats]:
    mon_df = utils.get_cox_monster_base_stats_by_name(name)

    _attack = mon_df["melee"].values[0]
    _strength = mon_df["melee"].values[0]
    _defence = mon_df["defence"].values[0]
    _ranged = mon_df["ranged"].values[0]
    _magic = mon_df["magic"].values[0]
    _hitpoints = mon_df["hp"].values[0]

    aggressive_melee_bonus = mon_df["melee att+"].values[0]
    magic_attack = mon_df["magic att+"].values[0]
    ranged_attack = mon_df["ranged att+"].values[0]
    melee_strength = mon_df["melee str+"].values[0]
    ranged_strength = mon_df["ranged str+"].values[0]
    magic_strength = mon_df["magic str+"].values[0]

    stab_defence = mon_df["stab def+"].values[0]
    slash_defence = mon_df["slash def+"].values[0]
    crush_defence = mon_df["crush def+"].values[0]
    magic_defence = mon_df["magic def+"].values[0]
    ranged_defence = mon_df["ranged def+"].values[0]

    values = [
        # levels
        _attack,
        _strength,
        _defence,
        _ranged,
        _magic,
        _hitpoints,
        # aggressive
        aggressive_melee_bonus,
        magic_attack,
        ranged_attack,
        melee_strength,
        ranged_strength,
        magic_strength,
        # defensive
        stab_defence,
        slash_defence,
        crush_defence,
        magic_defence,
        ranged_defence,
    ]

    assert all((elem := e) is not None for e in values)

    levels = MonsterLevels(
        _attack=Level(_attack),
        _strength=Level(_strength),
        _defence=Level(_defence),
        _ranged=Level(_ranged),
        _magic=Level(_magic),
        _hitpoints=Level(_hitpoints),
    )

    aggressive_bonus = AggressiveStats(
        stab=aggressive_melee_bonus,
        slash=aggressive_melee_bonus,
        crush=aggressive_melee_bonus,
        magic_attack=magic_attack,
        ranged_attack=ranged_attack,
        melee_strength=melee_strength,
        ranged_strength=ranged_strength,
        magic_strength=magic_strength,
    )
    defensive_bonus = DefensiveStats(
        stab=stab_defence,
        slash=slash_defence,
        crush=crush_defence,
        magic=magic_defence,
        ranged=ranged_defence,
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
    party_max_hitpoints_level: Level = field(default_factory=PlayerLevels.max_skill_level)
    party_average_mining_level: Level = field(default_factory=lambda: Level(PARTY_AVERAGE_MINING_LEVEL))
    special_atttributes: list[MonsterTypes] = field(default_factory=lambda: [MonsterTypes.XERICIAN])

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

        def _scale_level(skills: list[Skills], *modifiers: LevelModifier | None) -> None:
            """Scale a level by the given modifiers

            Parameters
            ----------
            skills : list[Skills]
                A list of skills to scale
            """
            for _skill in skills:
                _skill_lvl = getattr(self._levels, _skill.value)

                for _mod in [_m for _m in modifiers if _m is not None]:
                    _skill_lvl *= _mod

                setattr(self._levels, _skill.value, _skill_lvl)

        _scale_level(
            [Skills.HITPOINTS],
            self.player_hp_scaling_factor,
            self.party_hp_scaling_factor,
            self.cm_hp_scaling_factor,
        )

        _scale_level(
            [Skills.ATTACK, Skills.STRENGTH],
            self.player_off_def_scaling_factor,
            self.party_off_scaling_factor,
            self.cm_off_scaling_factor,
        )

        _scale_level(
            [Skills.DEFENCE],
            self.player_off_def_scaling_factor,
            self.party_def_scaling_factor,
            self.cm_def_scaling_factor,
        )

        _scale_level(
            [Skills.MAGIC],
            self.player_off_def_scaling_factor,
            self.party_off_scaling_factor,
            self.cm_off_scaling_factor,
        )

        _scale_level(
            [Skills.RANGED],
            self.player_off_def_scaling_factor,
            self.party_off_scaling_factor,
            self.cm_off_scaling_factor,
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
        value = (math.floor(math.sqrt(n - 1)) + math.floor((7 / 10) * (n - 1)) + 100) / 100
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

    @classmethod
    @abstractmethod
    def simple(cls, party_size: int, challenge_mode: bool = False, **kwargs) -> CoxMonster:
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
