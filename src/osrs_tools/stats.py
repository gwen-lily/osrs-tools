"""Stats & its many subclasses.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field, fields
from functools import total_ordering, wraps
from typing import Any, Callable

import osrs_tools.resource_reader as rr
from osrs_tools.data import (
    Boost,
    Level,
    MonsterCombatSkills,
    Skills,
    StyleBonus,
    TrackedFloat,
    TrackedInt,
)
from osrs_tools.exceptions import OsrsException

###############################################################################
# errors 'n such                                                              #
###############################################################################


class StatsError(OsrsException):
    pass


###############################################################################
# main classes                                                                #
###############################################################################

# stats #######################################################################


@dataclass
@total_ordering
class Stats:
    """Base stats class."""

    def _dunder_helper(self, other, func: Callable[[Any, Any], Any]) -> Any:

        if isinstance(other, self.__class__):
            val = self.__class__(
                **{
                    f.name: func(getattr(self, f.name), getattr(other, f.name))
                    for f in fields(self)
                }
            )
        else:
            raise NotImplementedError

        assert isinstance(val, self.__class__)
        return val

    def __add__(self, other):
        return self._dunder_helper(other, lambda x, y: x + y)

    def __sub__(self, other):
        return self._dunder_helper(other, lambda x, y: x - y)

    def __copy__(self):
        unpacked = [copy(getattr(self, f.name)) for f in fields(self)]
        return self.__class__(*unpacked)

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            val = all(
                getattr(self, f.name) < getattr(other, f.name) for f in fields(self)
            )
        else:
            raise NotImplementedError

        return val


class StatsOptional(Stats):
    """Stats object with optional parameters that don't break arithmetic."""

    # TODO: Define eq, lt, etc...

    @staticmethod
    def _arithmetic_wrapper(
        func: Callable[[Any, Any], Any], bidirectional: bool = False
    ) -> Callable[[Any, Any], Any]:
        """Takes a callable and modifies it to deal with optional attributes.

        Parameters
        ----------
        func : Callable[[Any, Any], Any]
            A callable that takes two inputs and returns one. The simplest
            example is lambda x, y: x + y

        bidirectional : bool, optional
            Set to True if the ordering of arithmetic does not matter, ie.
            it is commutative. By default False.

        Returns
        -------
        Callable[[Any, Any], Any]
            The modified callable.

        Raises
        ------
        NotImplementedError
        """

        @wraps(func)
        def inner(__x, __y, /) -> Any:
            if __x is not None and __y is None:
                arith_val = __x
            elif __x is None and __y is not None:
                if bidirectional:
                    arith_val = __y
                else:
                    raise NotImplementedError
            elif __x is not None and __y is not None:
                arith_val = func(__x, __y)
            else:
                raise NotImplementedError

            return arith_val

        return inner

    def __add__(self, other):
        mod_func = self._arithmetic_wrapper(lambda x, y: x + y, bidirectional=True)
        return self._dunder_helper(other, mod_func)

    def __sub__(self, other):
        mod_func = self._arithmetic_wrapper(lambda x, y: x - y, bidirectional=False)
        return self._dunder_helper(other, mod_func)

    # type validation methods

    def _level_getter(self, __skill: Skills, /) -> Level:
        """Get a protected skill attribute and return the Level."""
        attribute_name = f"_{__skill.value}"
        gear = getattr(self, attribute_name)
        assert isinstance(gear, Level)

        return gear

    def _level_setter(self, __skill: Skills, __value: Level, /):
        """Validate slot membership and set protected slot attribute."""
        attribute_name = f"_{__skill.value}"
        setattr(self, attribute_name, __value)


# levels ######################################################################


@dataclass
@total_ordering
class PlayerLevels(StatsOptional):
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

    def __add__(self, other: PlayerLevels | Boost) -> PlayerLevels:
        if isinstance(other, PlayerLevels):
            val = super().__add__(other)
        elif isinstance(other, Boost):
            val = copy(self)

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
        maxed_levels = [cls.max_skill_level()] * 23
        return cls(*maxed_levels)

    @classmethod
    def starting_stats(cls):
        skills_dict: dict[str, Level] = {}

        for skill in Skills:
            val = 10 if skill is Skills.HITPOINTS else 1
            comment = "minimum"
            skills_dict[skill.value] = Level(val, comment)

        return cls(**skills_dict)

    @classmethod
    def no_requirements(cls):
        """Wrapper for cls.starting_stats"""
        return cls.starting_stats()

    @classmethod
    def zeros(cls):
        return cls(*(Level(0) for _ in Skills))

    @classmethod
    def from_rsn(cls, rsn: str):
        _hs = rr.lookup_player_highscores(rsn)
        levels = [
            Level(getattr(_hs, skill.value).level, f"{rsn}: {skill.value}")
            for skill in Skills
        ]
        return cls(*levels)

    # type validation properties
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
    def prayer(self) -> Level:
        return self._level_getter(Skills.PRAYER)

    @prayer.setter
    def prayer(self, __value: Level):
        return self._level_setter(Skills.PRAYER, __value)

    @property
    def magic(self) -> Level:
        return self._level_getter(Skills.MAGIC)

    @magic.setter
    def magic(self, __value: Level):
        return self._level_setter(Skills.MAGIC, __value)

    @property
    def runecraft(self) -> Level:
        return self._level_getter(Skills.RUNECRAFT)

    @runecraft.setter
    def runecraft(self, __value: Level):
        return self._level_setter(Skills.RUNECRAFT, __value)

    @property
    def hitpoints(self) -> Level:
        return self._level_getter(Skills.HITPOINTS)

    @hitpoints.setter
    def hitpoints(self, __value: Level):
        return self._level_setter(Skills.HITPOINTS, __value)

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
class MonsterLevels(StatsOptional):
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

    # type validation properties

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


# additional stats ############################################################


@dataclass
class StyleStats(Stats):
    """Integer container class for validation, security, and logging."""

    melee_attack: StyleBonus = field(default_factory=StyleBonus.zero)
    melee_strength: StyleBonus = field(default_factory=StyleBonus.zero)
    defence: StyleBonus = field(default_factory=StyleBonus.zero)
    ranged_attack: StyleBonus = field(default_factory=StyleBonus.zero)
    ranged_strength: StyleBonus = field(default_factory=StyleBonus.zero)
    magic_attack: StyleBonus = field(default_factory=StyleBonus.zero)

    # class methods

    @classmethod
    def melee_shared_bonus(cls):
        value = 1
        comment = "shared style"
        return cls(
            melee_attack=StyleBonus(value, comment),
            melee_strength=StyleBonus(value, comment),
            defence=StyleBonus(value, comment),
        )

    @classmethod
    def melee_accurate_bonuses(cls):
        value = 3
        comment = "accurate style"
        return cls(melee_attack=StyleBonus(value, comment))

    @classmethod
    def melee_strength_bonuses(cls):
        value = 3
        comment = "aggressive style"
        return cls(melee_strength=StyleBonus(value, comment))

    @classmethod
    def defensive_bonuses(cls):
        value = 3
        comment = "defensive style"
        return cls(defence=StyleBonus(value, comment))

    @classmethod
    def ranged_bonus(cls):
        value = 3
        comment = "ranged (accurate) style"
        return cls(
            ranged_attack=StyleBonus(value, comment),
            ranged_strength=StyleBonus(value, comment),
        )

    @classmethod
    def magic_bonus(cls):
        value = 3
        comment = "magic (accurate) style"
        return cls(magic_attack=StyleBonus(value, comment))

    @classmethod
    def npc_bonus(cls):
        bonus = StyleBonus(1, "npc style")
        return cls(
            melee_attack=bonus,
            melee_strength=bonus,
            defence=bonus,
            ranged_attack=bonus,
            magic_attack=bonus,
        )

    @classmethod
    def no_style_bonus(cls):
        raise DeprecationWarning


@dataclass
class AggressiveStats(Stats):
    """Class with information relevant to offensive damage calculation.

    Included attributes are attack bonus values: stab, slash, crush, magic
    attack, ranged attack, melee strength, ranged strength, and magic strength
    (not to be confused with magic damage).

    Attributes
    ----------

    stab : TrackedInt
        Accuracy bonus for stab damage type. Defaults to 0.
    slash : TrackedInt
        Accuracy bonus for slash damage type. Defaults to 0.
    crush : TrackedInt
        Accuracy bonus for crush damage type. Defaults to 0.
    magic_attack : TrackedInt
        Accuracy bonus for magic damage type. Defaults to 0.
    ranged_attack : TrackedInt
        Accuracy bonus for ranged damage type. Defaults to 0.
    melee_strength : TrackedInt
        Strength bonus for melee damage types. Defaults to 0.
    ranged_strength : TrackedInt
        Strength bonus for ranged damage type. Defaults to 0.
    magic_strength : TrackedFloat
        Strength bonus for magic damage type. Uniquely expressed as a float
        as opposed to a straight bonus. Defaults to 0.
    """

    stab: TrackedInt = field(default_factory=TrackedInt.zero)
    slash: TrackedInt = field(default_factory=TrackedInt.zero)
    crush: TrackedInt = field(default_factory=TrackedInt.zero)
    magic_attack: TrackedInt = field(default_factory=TrackedInt.zero)
    ranged_attack: TrackedInt = field(default_factory=TrackedInt.zero)
    melee_strength: TrackedInt = field(default_factory=TrackedInt.zero)
    ranged_strength: TrackedInt = field(default_factory=TrackedInt.zero)
    magic_strength: TrackedFloat = field(default_factory=TrackedFloat.zero)

    def __add__(self, other: int | AggressiveStats) -> AggressiveStats:
        if isinstance(other, int):
            if other == 0:
                return copy(self)
            else:
                raise ValueError(other)

        elif isinstance(other, AggressiveStats):
            new_vals = {}

            for f in fields(self):
                self_val = getattr(self, f.name)
                other_val = getattr(other, f.name)
                new_vals[f.name] = self_val + other_val
        else:
            raise TypeError(other)

        return AggressiveStats(**new_vals)

    @classmethod
    def no_bonus(cls):
        raise DeprecationWarning

    @classmethod  # TODO: Look into bitterkoekje's general attack stat and see where it matters
    def from_bb(cls, name: str):
        mon_df = rr.lookup_normal_monster_by_name(name)

        general_attack_bonus = mon_df["attack bonus"]
        val = general_attack_bonus.values[0]
        assert val is not None

        if val > 0:
            stab_attack, slash_attack, crush_attack = 3 * (general_attack_bonus,)
        else:
            stab_attack = mon_df["stab attack"].values[0]
            slash_attack = mon_df["slash attack"].values[0]
            crush_attack = mon_df["crush attack"].values[0]

        return cls(
            stab_attack,
            slash_attack,
            crush_attack,
            mon_df["magic attack"].values[0],
            mon_df["ranged attack"].values[0],
            mon_df["melee strength"].values[0],
            mon_df["ranged strength"].values[0],
            mon_df["magic strength"].values[0],
        )

    @classmethod
    def from_osrsbox(cls, name: str):
        raise NotImplementedError


@dataclass
class DefensiveStats(Stats):
    """Class with information relevant to defensive damage calculation.

    Attributes
    ----------

    stab : TrackedInt
        Defence bonus for stab damage type.
    slash : TrackedInt
        Defence bonus for slash damage type.
    crush : TrackedInt
        Defence bonus for crush damage type.
    magic : TrackedInt
        Defence bonus for magic damage type.
    ranged : TrackedInt
        Defence bonus for ranged damage type.
    """

    stab: TrackedInt = field(default_factory=TrackedInt.zero)
    slash: TrackedInt = field(default_factory=TrackedInt.zero)
    crush: TrackedInt = field(default_factory=TrackedInt.zero)
    magic: TrackedInt = field(default_factory=TrackedInt.zero)
    ranged: TrackedInt = field(default_factory=TrackedInt.zero)

    def __add__(self, other: int | DefensiveStats) -> DefensiveStats:
        if isinstance(other, int):
            if other == 0:
                return copy(self)
            else:
                raise ValueError(other)

        elif isinstance(other, DefensiveStats):
            new_vals = {}

            for f in fields(self):
                self_val = getattr(self, f.name)
                other_val = getattr(other, f.name)
                new_vals[f.name] = self_val + other_val
        else:
            raise TypeError(other)

        return DefensiveStats(**new_vals)

    @classmethod
    def no_bonus(cls):
        raise DeprecationWarning

    @classmethod
    def from_bb(cls, name: str):
        mon_df = rr.lookup_normal_monster_by_name(name)

        return cls(
            mon_df["stab defence"].values[0],
            mon_df["slash defence"].values[0],
            mon_df["crush defence"].values[0],
            mon_df["magic defence"].values[0],
            mon_df["ranged defence"].values[0],
        )

    @classmethod
    def from_osrsbox(cls, name: str):
        raise NotImplementedError
