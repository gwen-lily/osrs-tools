from __future__ import annotations

import math
from copy import copy
from dataclasses import dataclass, field, fields
from enum import Enum, unique
from functools import total_ordering
from typing import Any, Callable

import numpy as np

###############################################################################
# enums 'n' such
###############################################################################

# damage, stances, & styles ###################################################


@unique
class DT(Enum):
    """Damage Type (DT) enumerator.
    Args:
        Enum (DT): Enumerator object.
    """

    # melee style class vars
    STAB = "stab"
    SLASH = "slash"
    CRUSH = "crush"

    # ranged style class vars
    RANGED = "ranged"

    # magic style class vars
    MAGIC = "magic"

    # typeless class vars
    TYPELESS = "typeless"


# I treat these uniformly as tuples, do as you see fit.
# I know not whether there are different classes of some of these
# Hey reader, check out the band Godspeed You! Black Emperor, they're gr!eat
MeleeDamageTypes = (DT.STAB, DT.SLASH, DT.CRUSH)
RangedDamageTypes = (DT.RANGED,)
MagicDamageTypes = (DT.MAGIC,)
TypelessDamageTypes = (DT.TYPELESS,)


@unique
class Stances(Enum):
    # type ambiguous class vars
    ACCURATE = "accurate"
    LONGRANGE = "longrange"
    DEFENSIVE = "defensive"
    NO_STYLE = "no style"
    # melee style class vars
    AGGRESSIVE = "aggressive"
    CONTROLLED = "controlled"
    # ranged style class vars
    RAPID = "rapid"
    # magic style class vars
    STANDARD = "standard"
    # npc stance
    NPC = "npc"


@unique
class Styles(Enum):
    # style names, flavor text as far as I can tell

    SLASH = "slash"
    STAB = "stab"
    ACCURATE = "accurate"
    RAPID = "rapid"
    LONGRANGE = "longrange"
    CHOP = "chop"
    SMASH = "smash"
    BLOCK = "block"
    HACK = "hack"
    LUNGE = "lunge"
    SWIPE = "swipe"
    POUND = "pound"
    PUMMEL = "pummel"
    SPIKE = "spike"
    IMPALE = "impale"
    JAB = "jab"
    FEND = "fend"
    BASH = "bash"
    REAP = "reap"
    PUNCH = "punch"
    KICK = "kick"
    FLICK = "flick"
    LASH = "lash"
    DEFLECT = "deflect"
    SHORT_FUSE = "short fuse"
    MEDIUM_FUSE = "medium fuse"
    LONG_FUSE = "long fuse"
    SPELL = "spell"
    FOCUS = "focus"
    STANDARD_SPELL = "standard spell"
    DEFENSIVE_SPELL = "defensive spell"

    NPC_MELEE = "monster melee"
    NPC_RANGED = "monster ranged"
    NPC_MAGIC = "monster magic"


MeleeStances = (
    Stances.ACCURATE,
    Stances.AGGRESSIVE,
    Stances.DEFENSIVE,
    Stances.CONTROLLED,
)
RangedStances = (Stances.ACCURATE, Stances.RAPID, Stances.LONGRANGE)
MagicStances = (Stances.ACCURATE, Stances.LONGRANGE, Stances.NO_STYLE, Stances.NO_STYLE)
SpellStylesNames = (Styles.STANDARD_SPELL, Styles.DEFENSIVE_SPELL)
ChinchompaStylesNames = (Styles.SHORT_FUSE, Styles.MEDIUM_FUSE, Styles.LONG_FUSE)


# skills & monsters ###########################################################


@unique
class Skills(Enum):
    ATTACK = "attack"
    STRENGTH = "strength"
    defence = "defence"
    RANGED = "ranged"
    PRAYER = "prayer"
    MAGIC = "magic"
    RUNECRAFT = "runecraft"
    HITPOINTS = "hitpoints"
    CRAFTING = "crafting"
    MINING = "mining"
    SMITHING = "smithing"
    FISHING = "fishing"
    COOKING = "cooking"
    FIREMAKING = "firemaking"
    WOODCUTTING = "woodcutting"
    AGILITY = "agility"
    HERBLORE = "herblore"
    THIEVING = "thieving"
    FLETCHING = "fletching"
    SLAYER = "slayer"
    FARMING = "farming"
    CONSTRUCTION = "construction"
    HUNTER = "hunter"


MonsterCombatSkills = (
    Skills.ATTACK,
    Skills.STRENGTH,
    Skills.defence,
    Skills.RANGED,
    Skills.MAGIC,
    Skills.HITPOINTS,
)


@unique
class MonsterTypes(Enum):
    DEMON = "demon"
    DRACONIC = "draconic"
    FIERY = "fiery"
    GOLEM = "golem"
    KALPHITE = "kalphite"
    LEAFY = "leafy"
    PENANCE = "penance"
    SHADE = "shade"
    SPECTRAL = "spectral"
    UNDEAD = "undead"
    VAMPYRE_TIER_1 = "vampyre - tier 1"
    VAMPYRE_TIER_2 = "vampyre - tier 2"
    VAMPYRE_TIER_3 = "vampyre - tier 3"
    XERICIAN = "xerician"
    WILDERNESS = "wilderness"


VampyreMonsterTypes = (
    MonsterTypes.VAMPYRE_TIER_1,
    MonsterTypes.VAMPYRE_TIER_2,
    MonsterTypes.VAMPYRE_TIER_3,
)


@unique
class MonsterLocations(Enum):
    WILDERNESS = "wilderness"
    TOB = "tob"
    COX = "cox"


###############################################################################
# tracked values
###############################################################################


@dataclass(eq=False, unsafe_hash=True)
class TrackedValue:
    _value: Any
    _value_type: type = field(init=False)
    _comment: str | None = None
    _comment_is_default: bool = field(init=False, default=False)

    def __post_init__(self):
        self._value_type = type(self.value)

        if self._comment is None:
            self._comment = str(self.value)
            self._comment_is_default = True

    # properties

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, x, /):
        if not isinstance(x, self._value_type):
            raise TypeError(x, self._value_type)

        self._value = x

    @property
    def comment(self) -> str:
        assert self._comment is not None
        return self._comment

    @comment.setter
    def comment(self, x, /):
        assert isinstance(x, str)
        self._comment = x

    # comparison

    # I know that @totalordering exists but I was getting strange errors with
    # comparisons so I decided to manually define them all.

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return self.value == other.value

    def __lt__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError

        return self.value < other.value

    def __le__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError

        return self.value <= other.value

    def __gt__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError

        return self.value > other.value

    def __ge__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            raise NotImplementedError

        return self.value >= other.value

    # operations

    def __str__(self):
        s = f"{self.__class__.__name__}({self.value})"

        if not self._comment_is_default:
            s = s[:-1] + f": {self.comment})"

        return s

    def __copy__(self):
        unpacked = (copy(getattr(self, field.name)) for field in fields(self))
        return self.__class__(*unpacked)

    def __add__(self, other) -> TrackedValue:
        if isinstance(other, TrackedValue):
            new_val = self.value + other.value
        elif isinstance(other, self._value_type):
            new_val = self.value + other
        else:
            raise NotImplementedError

        new_com = f"({self} + {other})"
        return self.__class__(new_val, new_com)

    def __sub__(self, other) -> TrackedValue:
        if isinstance(other, TrackedValue):
            new_val = self.value - other.value
        elif isinstance(other, self._value_type):
            new_val = self.value - other
        else:
            raise NotImplementedError

        new_com = f"({self} - {other})"
        return self.__class__(new_val, new_com)

    def __mul__(self, other) -> TrackedValue:
        if isinstance(other, self.__class__):
            new_val = self.value * other.value
        elif isinstance(other, self._value_type):
            new_val = self.value * other
        else:
            raise NotImplementedError

        new_com = f"({self} · {other})"
        return self.__class__(new_val, new_com)

    def __truediv__(self, other) -> float:
        if isinstance(other, TrackedValue):
            return self.value / other.value

        return self.value / other

    def __floordiv__(self, other) -> int:
        if isinstance(other, TrackedValue):
            return self.value // other.value

        return self.value // other


# generic subclasses ##########################################################


class TrackedInt(TrackedValue):

    # properties ##############################################################

    @property
    def value(self) -> int:
        return self._value

    def __int__(self):
        return self.value

    # operations ##############################################################

    def __sub__(self, other) -> TrackedInt:
        if isinstance(other, float):
            new_val = math.floor(self.value - other)
        elif isinstance(other, TrackedFloat):
            new_val = math.floor(self.value - other.value)
        else:
            super_val = super().__sub__(other)
            assert isinstance(super_val, self.__class__)
            return super_val

        new_com = f"⌊{self} - {other}⌋"
        new_tracked_int = self.__class__(new_val, new_com)
        assert isinstance(new_tracked_int, self.__class__)
        return new_tracked_int

    def __mul__(self, other) -> TrackedInt:
        if isinstance(other, float):
            new_val = math.floor(self.value * other)
        elif isinstance(other, TrackedFloat):
            new_val = math.floor(self.value * other.value)
        else:
            super_val = super().__mul__(other)
            assert isinstance(super_val, self.__class__)
            return super_val

        new_com = f"⌊{self} · {other}⌋"
        return self.__class__(new_val, new_com)


class TrackedFloat(TrackedValue):

    # properties

    @property
    def value(self) -> float:
        return self._value

    def __float__(self):
        return self.value

    # operations

    def __mul__(self, other):
        if isinstance(other, (float, TrackedFloat)):
            # I don't think you ever need to do this, delete this __mul__ if I
            # happen to be wrong in the future
            raise NotImplementedError


# subclasses ##################################################################

# common pairs
class Level(TrackedInt):
    ...


class LevelModifier(TrackedFloat):
    ...


class Roll(TrackedInt):
    ...


class RollModifier(TrackedFloat):
    ...


class DamageValue(TrackedInt):
    ...


class DamageModifier(TrackedFloat):
    ...


# misc. additional TrackedValues
class StyleBonus(TrackedInt):
    ...


CallableLevelsModifierType = Callable[[Level], tuple[Level]]


@dataclass
class CallableLevelsModifier:
    """Create a CallableLevelsModifier which takes skills as arguments
    and returns their modified values.

    skills must be a tuple of Skills enums. func must accept skills as
    an argument and return the modified values in the same tuple format.
    comment is optional.
    """

    skills: tuple[Skills]
    func: CallableLevelsModifierType
    comment: str | None

    def __post_init__(self):
        # TODO: Implement ParamSpec # TODO: Figure out ParamSpec
        if self.comment is None:
            self.comment = f"callable modifier: {self.skills}"


def create_modifier_pair(
    value: float | None = None, comment: str | None = None
) -> tuple[RollModifier, DamageModifier]:
    value = float(1) if value is None else value
    return RollModifier(value, comment), DamageModifier(value, comment)
