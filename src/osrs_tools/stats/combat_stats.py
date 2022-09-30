"""Definition of CombatStats, PlayerLevels, & MonsterLevels

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022                                                              #
###############################################################################
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from functools import total_ordering

from osrs_highscores import Highscores
from osrs_tools import utils as rr
from osrs_tools.boost import Boost
from osrs_tools.data import MonsterCombatSkills, Skills
from osrs_tools.tracked_value import Level

from .stats import StatsOptional

###############################################################################
# abstract class                                                              #
###############################################################################


@dataclass
class CombatStats(StatsOptional):
    """The minimum stats required to simulate combat.

    Players add more levels (including prayer), monsters don't.
    """

    _attack: Level | None = None
    _strength: Level | None = None
    _defence: Level | None = None
    _ranged: Level | None = None
    _magic: Level | None = None
    _hitpoints: Level | None = None

    def __getitem__(self, __key: Skills, /) -> Level:
        _val = getattr(self, f"_{__key.value}")
        assert isinstance(_val, Level)
        return _val

    def __setitem__(self, __key: Skills, __value: Level, /) -> None:
        setattr(self, f"_{__key.value}", __value)

    @property
    def attack(self) -> Level:
        return self._level_getter(Skills.ATTACK)

    @attack.setter
    def attack(self, __value: Level):
        return self._level_setter(Skills.ATTACK, __value)

    @property
    def strength(self) -> Level:
        return self._level_getter(Skills.STRENGTH)

    @strength.setter
    def strength(self, __value: Level):
        return self._level_setter(Skills.STRENGTH, __value)

    @property
    def defence(self) -> Level:
        return self._level_getter(Skills.DEFENCE)

    @defence.setter
    def defence(self, __value: Level):
        return self._level_setter(Skills.DEFENCE, __value)

    @property
    def ranged(self) -> Level:
        return self._level_getter(Skills.RANGED)

    @ranged.setter
    def ranged(self, __value: Level):
        return self._level_setter(Skills.RANGED, __value)

    @property
    def magic(self) -> Level:
        return self._level_getter(Skills.MAGIC)

    @magic.setter
    def magic(self, __value: Level):
        return self._level_setter(Skills.MAGIC, __value)

    @property
    def hitpoints(self) -> Level:
        return self._level_getter(Skills.HITPOINTS)

    @hitpoints.setter
    def hitpoints(self, __value: Level):
        return self._level_setter(Skills.HITPOINTS, __value)


###############################################################################
# main classes                                                                #
###############################################################################


@dataclass
@total_ordering
class PlayerLevels(CombatStats):
    _attack: Level | None = None
    _strength: Level | None = None
    _defence: Level | None = None
    _ranged: Level | None = None
    _prayer: Level | None = None
    _magic: Level | None = None
    _runecraft: Level | None = None
    _hitpoints: Level | None = None
    _crafting: Level | None = None
    _mining: Level | None = None
    _smithing: Level | None = None
    _fishing: Level | None = None
    _cooking: Level | None = None
    _firemaking: Level | None = None
    _woodcutting: Level | None = None
    _agility: Level | None = None
    _herblore: Level | None = None
    _thieving: Level | None = None
    _fletching: Level | None = None
    _slayer: Level | None = None
    _farming: Level | None = None
    _construction: Level | None = None
    _hunter: Level | None = None

    # dunder methods

    def __getitem__(self, __value: Skills) -> Level:
        return self.__getattribute__(__value.value)

    def __iter__(self):
        lvl_dict = {sk: self[sk] for sk in Skills}
        yield from lvl_dict.items()

    def __add__(self, other: PlayerLevels | Boost) -> PlayerLevels:
        if isinstance(other, PlayerLevels):
            val = super().__add__(other)
        elif isinstance(other, Boost):
            val = copy(self)

            # create a copy, then modify levels in place
            for modifier in other.modifiers:
                old_lvl = getattr(val, modifier.skill.value)
                new_lvl = modifier.value(old_lvl)
                setattr(val, modifier.skill.value, new_lvl)

        else:
            raise TypeError(other)

        return val

    # basic methods

    def max_levels_per_skill(self, other: PlayerLevels) -> PlayerLevels:
        mod_func = self._arithmetic_wrapper(max, bidirectional=True)
        return self._dunder_helper(other, mod_func)

    @staticmethod
    def max_skill_level() -> Level:
        return Level(99, "maximum")

    def min_skill_level(self, __skill: Skills, /) -> Level:
        comment = "minimum"
        value = 10 if __skill is Skills.HITPOINTS else 1
        return Level(value, comment)

    # class methods

    @classmethod
    def maxed_player(cls):
        """Returns the levels of a maxed player (126 cmb 99 all)"""
        maxed_levels = [cls.max_skill_level()] * 23
        return cls(*maxed_levels)

    @classmethod
    def starting_stats(cls) -> PlayerLevels:
        skills_dict: dict[str, Level] = {}

        for skill in Skills:
            val = 10 if skill is Skills.HITPOINTS else 1
            comment = "minimum"
            skills_dict[f"_{skill.value}"] = Level(val, comment)

        return cls(**skills_dict)

    @classmethod
    def no_requirements(cls):
        """Wrapper for cls.starting_stats"""
        return cls.starting_stats()

    @classmethod
    def zeros(cls):
        return cls(*(Level(0) for _ in Skills))

    @classmethod
    def max_levels(cls):
        return cls(*(Level(120) for _ in Skills))

    @classmethod
    def from_rsn(cls, rsn: str):
        _hs = Highscores(rsn)

        levels = [
            Level(getattr(_hs, skill.value).level, f"{rsn}: {skill.value}")
            for skill in Skills
        ]
        return cls(*levels)

    # type validation properties
    # attack, strength, defence, ranged, magic, & hitpoints in super.

    @property
    def prayer(self) -> Level:
        return self._level_getter(Skills.PRAYER)

    @prayer.setter
    def prayer(self, __value: Level):
        return self._level_setter(Skills.PRAYER, __value)

    @property
    def runecraft(self) -> Level:
        return self._level_getter(Skills.RUNECRAFT)

    @runecraft.setter
    def runecraft(self, __value: Level):
        return self._level_setter(Skills.RUNECRAFT, __value)

    @property
    def crafting(self) -> Level:
        return self._level_getter(Skills.CRAFTING)

    @crafting.setter
    def crafting(self, __value: Level):
        return self._level_setter(Skills.CRAFTING, __value)

    @property
    def mining(self) -> Level:
        return self._level_getter(Skills.MINING)

    @mining.setter
    def mining(self, __value: Level):
        return self._level_setter(Skills.MINING, __value)

    @property
    def smithing(self) -> Level:
        return self._level_getter(Skills.SMITHING)

    @smithing.setter
    def smithing(self, __value: Level):
        return self._level_setter(Skills.SMITHING, __value)

    @property
    def fishing(self) -> Level:
        return self._level_getter(Skills.FISHING)

    @fishing.setter
    def fishing(self, __value: Level):
        return self._level_setter(Skills.FISHING, __value)

    @property
    def cooking(self) -> Level:
        return self._level_getter(Skills.COOKING)

    @cooking.setter
    def cooking(self, __value: Level):
        return self._level_setter(Skills.COOKING, __value)

    @property
    def firemaking(self) -> Level:
        return self._level_getter(Skills.FIREMAKING)

    @firemaking.setter
    def firemaking(self, __value: Level):
        return self._level_setter(Skills.FIREMAKING, __value)

    @property
    def woodcutting(self) -> Level:
        return self._level_getter(Skills.WOODCUTTING)

    @woodcutting.setter
    def woodcutting(self, __value: Level):
        return self._level_setter(Skills.WOODCUTTING, __value)

    @property
    def agility(self) -> Level:
        return self._level_getter(Skills.AGILITY)

    @agility.setter
    def agility(self, __value: Level):
        return self._level_setter(Skills.AGILITY, __value)

    @property
    def herblore(self) -> Level:
        return self._level_getter(Skills.HERBLORE)

    @herblore.setter
    def herblore(self, __value: Level):
        return self._level_setter(Skills.HERBLORE, __value)

    @property
    def thieving(self) -> Level:
        return self._level_getter(Skills.THIEVING)

    @thieving.setter
    def thieving(self, __value: Level):
        return self._level_setter(Skills.THIEVING, __value)

    @property
    def fletching(self) -> Level:
        return self._level_getter(Skills.FLETCHING)

    @fletching.setter
    def fletching(self, __value: Level):
        return self._level_setter(Skills.FLETCHING, __value)

    @property
    def slayer(self) -> Level:
        return self._level_getter(Skills.SLAYER)

    @slayer.setter
    def slayer(self, __value: Level):
        return self._level_setter(Skills.SLAYER, __value)

    @property
    def farming(self) -> Level:
        return self._level_getter(Skills.FARMING)

    @farming.setter
    def farming(self, __value: Level):
        return self._level_setter(Skills.FARMING, __value)

    @property
    def construction(self) -> Level:
        return self._level_getter(Skills.CONSTRUCTION)

    @construction.setter
    def construction(self, __value: Level):
        return self._level_setter(Skills.CONSTRUCTION, __value)

    @property
    def hunter(self) -> Level:
        return self._level_getter(Skills.HUNTER)

    @hunter.setter
    def hunter(self, __value: Level):
        return self._level_setter(Skills.HUNTER, __value)


@total_ordering
@dataclass
class MonsterLevels(CombatStats):
    _attack: Level | None = None
    _strength: Level | None = None
    _defence: Level | None = None
    _ranged: Level | None = None
    _magic: Level | None = None
    _hitpoints: Level | None = None

    @classmethod
    def from_bb(cls, name: str):
        mon_df = rr.lookup_normal_monster_by_name(name)
        return cls(
            mon_df[Skills.ATTACK.value].values[0],
            mon_df[Skills.STRENGTH.value].values[0],
            mon_df[Skills.DEFENCE.value].values[0],
            mon_df[Skills.RANGED.value].values[0],
            mon_df[Skills.MAGIC.value].values[0],
            mon_df[Skills.HITPOINTS.value].values[0],
        )

    @classmethod
    def dummy_levels(cls, hitpoints: Level | int | None = None):
        if isinstance(hitpoints, int):
            hp = Level(hitpoints)
        elif isinstance(hitpoints, Level):
            hp = hitpoints
        else:
            hp = Level(1000)

        return cls(
            _attack=Level(1),
            _strength=Level(1),
            _defence=Level(0),
            _ranged=Level(1),
            _magic=Level(1),
            _hitpoints=hp,
        )

    @classmethod
    def zeros(cls):
        return cls(*(Level(0) for _ in MonsterCombatSkills))
