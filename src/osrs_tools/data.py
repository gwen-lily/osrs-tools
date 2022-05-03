"""Basic data & classes ubiquitious to the program and OSRS.

All time values are in ticks unless otherwise noted.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

import math
from copy import copy
from dataclasses import dataclass, field, fields
from enum import Enum, auto, unique
from typing import Any, Callable

from numpy import float64, int64
from osrsbox import items_api, monsters_api, prayers_api

###############################################################################
# enums 'n' such
###############################################################################

# osrsbox-db load
ITEMS = items_api.load()
PRAYERS = prayers_api.load()
MONSTERS = monsters_api.load()

# misc ########################################################################

PLAYER_MAX_COMBAT_LEVEL = 126
PLAYER_MAX_SKILL_LEVEL = 99

# made these up
PARTY_AVERAGE_MINING_LEVEL = 42
PARTY_AVERAGE_THIEVING_LEVEL = 42
COX_POINTS_PER_HITPOINT = 4.15


CRYSTAL_PIECE_ARM = 0.06
CRYSTAL_PIECE_DM = 0.03
CRYSTAL_SET_ARM = 0.12
CRYSTAL_SET_DM = 0.06

INQUISITOR_PIECE_BONUS = 0.005
INQUISITOR_SET_BONUS = 0.01

ABYSSAL_BLUDGEON_DMG_MOD = 0.005

PVM_MAX_TARGETS = 11
PVP_MAX_TARGETS = 9

MUTTA_HP_RATIO_HEALED_PER_EAT = 0.60
MUTTA_EATS_PER_ROOM = 3

# made this up completely, #not true
TEKTON_HP_HEALED_PER_ANVIL_RATIO = 0.10

# time ########################################################################

SECONDS_PER_TICK = 0.6
TICKS_PER_SECOND = 1 / SECONDS_PER_TICK
TICKS_PER_MINUTE = 100
TICKS_PER_HOUR = 6000

HOURS_PER_SESSION = 6
TICKS_PER_SESSION = TICKS_PER_HOUR * HOURS_PER_SESSION

DEFAULT_EFFECT_INTERVAL = 25
UPDATE_STATS_INTERVAL = TICKS_PER_MINUTE
UPDATE_STATS_INTERVAL_PRESERVE = 150

OVERLOAD_DURATION = 500
DIVINE_DURATION = 500

# energy ######################################################################

RUN_ENERGY_MIN = 0
RUN_ENERGY_MAX = 10000

SPECIAL_ENERGY_MIN = 0
SPECIAL_ENERGY_MAX = 100
SPECIAL_ENERGY_INCREMENT = 10
SPECIAL_ENERGY_UPDATE_INTERVAL = 50
SPECIAL_ENERGY_DAMAGE = 10

# ammunition ##################################################################

BOLT_PROC = "bolt proc"

DIAMOND_BOLTS_PROC = 0.10
DIAMOND_BOLTS_DMG = 1.15

RUBY_BOLTS_PROC = 0.06
RUBY_BOLTS_HP_CAP = 500
RUBY_BOLTS_HP_RATIO = 0.20

# damage types ################################################################


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

# stance names ################################################################


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


# style names #################################################################


@unique
class Styles(Enum):
    """The name of every style in OSRS (that matters)."""

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

    # not official names
    NPC_MELEE = "monster melee"
    NPC_RANGED = "monster ranged"
    NPC_MAGIC = "monster magic"


MeleeStances = (
    Stances.ACCURATE,
    Stances.AGGRESSIVE,
    Stances.DEFENSIVE,
    Stances.CONTROLLED,
)
RangedStances = [Stances.ACCURATE, Stances.RAPID, Stances.LONGRANGE]
MagicStances = [Stances.ACCURATE, Stances.LONGRANGE, Stances.NO_STYLE, Stances.NO_STYLE]
SpellStylesNames = [Styles.STANDARD_SPELL, Styles.DEFENSIVE_SPELL]
ChinchompaStylesNames = [Styles.SHORT_FUSE, Styles.MEDIUM_FUSE, Styles.LONG_FUSE]


# skills & monster combat skills ##############################################


@unique
class Skills(Enum):
    ATTACK = "attack"
    STRENGTH = "strength"
    DEFENCE = "defence"
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
    Skills.DEFENCE,
    Skills.RANGED,
    Skills.MAGIC,
    Skills.HITPOINTS,
)

# monster types & locations ###################################################


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
    NONE = ""
    WILDERNESS = "wilderness"
    TOB = "tob"
    COX = "cox"


@unique
class Slayer(Enum):
    """An incomplete list of slayer assignment categories."""

    NONE = auto()

    ABERRANT_SPECTRES = auto()
    ABYSSAL_DEMONS = auto()
    ADAMANT_DRAGONS = auto()
    ANKOUS = auto()
    AVIANSIE = auto()
    BANDITS = auto()
    BANSHEES = auto()
    BASILISKS = auto()
    BATS = auto()
    BEARS = auto()
    BIRDS = auto()
    BLACK_DEMONS = auto()
    BLACK_DRAGONS = auto()
    BLACK_KNIGHTS = auto()
    BLOODVELDS = auto()
    BLUE_DRAGONS = auto()
    BRINE_RATS = auto()
    BRONZE_DRAGONS = auto()
    CATABLEPON = auto()
    CAVE_BUGS = auto()
    CAVE_CRAWLERS = auto()
    CAVE_HORRORS = auto()
    CAVE_SLIMES = auto()
    CAVE_KRAKEN = auto()
    CHAOS_DRUIDS = auto()
    COCKATRICES = auto()
    COWS = auto()
    DAGANNOTHS = auto()

    # done doing the bs ones for now

    DUST_DEVILS = auto()
    FOSSIL_ISLAND_WYVERNS = auto()
    GOBLINS = auto()
    GREATER_DEMONS = auto()
    GREEN_DRAGONS = auto()
    HELLHOUNDS = auto()
    HYDRAS = auto()
    JELLIES = auto()
    KALPHITES = auto()
    KURASKS = auto()
    LAVA_DRAGONS = auto()
    LIZARDMEN = auto()
    MITHRIL_DRAGONS = auto()
    NECHRYAEL = auto()
    RED_DRAGONS = auto()
    REVENANTS = auto()
    RUNE_DRAGONS = auto()
    SCORPIONS = auto()
    SHADES = auto()
    SKELETAL_WYVERNS = auto()
    SKELETONS = auto()
    SMOKE_DEVILS = auto()
    SUQAHS = auto()
    TROLLS = auto()
    VAMPYRES = auto()
    WYRMS = auto()


# slots ######################################################################


@unique
class Slots(Enum):
    """Complete list of gear slots in order from top to bottom, left to right."""

    HEAD = "head"
    CAPE = "cape"
    NECK = "neck"
    AMMUNITION = "ammunition"
    WEAPON = "weapon"
    BODY = "body"
    SHIELD = "shield"
    LEGS = "legs"
    HANDS = "hands"
    FEET = "feet"
    RING = "ring"


# effects #####################################################################


class Effect(Enum):
    """Enumerator of timed effect classifications."""

    # weapons
    STAFF_OF_THE_DEAD = auto()

    # potions
    STAMINA_POTION = auto()
    DIVINE_POTION = auto()
    OVERLOAD = auto()

    # character
    REGEN_SPECIAL_ENERGY = auto()
    UPDATE_STATS = auto()

    # olm phase specific effects
    OLM_BURN = auto()
    OLM_ACID = auto()
    OLM_FALLING_CRYSTAL = auto()

    # prayer
    PRAYER_DRAIN = auto()

    # misc
    FROZEN = auto()


###############################################################################
# tracked values                                                              #
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

    def _dunder_helper(self, other, func: Callable[[Any, Any], Any]) -> Any:
        """Performs a function on self and other with respect to TrackedValue datatypes.

        Args:
            other (_type_): Must be either a TrackedValue or the same type as
            self._value_type.

            func (Callable[[Any, Any], Any]): Takes self and other, yields Any.

        Raises:
            NotImplementedError:

        Returns:
            Any: Type return controlled by subclasses, with self taking precedence.
        """
        if isinstance(other, TrackedValue):
            new_val = func(self.value, other.value)
        elif isinstance(other, self._value_type):
            new_val = func(self.value, other)
        else:
            raise NotImplementedError

        return new_val

    def _assert_subclass(self, __value: TrackedValue, /) -> TrackedValue:
        """"""
        assert isinstance(__value, self.__class__)
        return __value

    # I know that @totalordering exists but I was getting strange errors with
    # comparisons so I decided to manually define them all.

    def __eq__(self, other) -> bool:
        return self._dunder_helper(other, lambda x, y: x == y)

    def __lt__(self, other) -> bool:
        return self._dunder_helper(other, lambda x, y: x < y)

    def __le__(self, other) -> bool:
        return self._dunder_helper(other, lambda x, y: x <= y)

    def __gt__(self, other) -> bool:
        return self._dunder_helper(other, lambda x, y: x > y)

    def __ge__(self, other) -> bool:
        return self._dunder_helper(other, lambda x, y: x >= y)

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
        new_val = self._dunder_helper(other, lambda x, y: x + y)
        new_com = f"({self} + {other})"
        return self.__class__(new_val, new_com)

    def __radd__(self, other) -> TrackedValue:
        val = self.__add__(other)
        return val

    def __sub__(self, other) -> TrackedValue:
        new_val = self._dunder_helper(other, lambda x, y: x - y)
        new_com = f"({self} - {other})"
        return self.__class__(new_val, new_com)

    def __mul__(self, other) -> Any:
        if isinstance(other, bool):
            if other is True:
                return self
            else:
                return 0

        new_val = self._dunder_helper(other, lambda x, y: x * y)
        new_com = f"({self} · {other})"
        return TrackedFloat(new_val, new_com)

    def __rmul__(self, other) -> Any:
        return self.__mul__(other)

    def __truediv__(self, other) -> float:
        if isinstance(other, TrackedValue):
            return self.value / other.value

        return self.value / other

    def __floordiv__(self, other) -> int:
        if isinstance(other, TrackedValue):
            return self.value // other.value

        return self.value // other


@dataclass(eq=False, unsafe_hash=True)
class TrackedInt(TrackedValue):
    _value: int | int64

    # properties

    @property
    def value(self) -> int | int64:
        return self._value

    def __int__(self):
        return int(self.value)

    # operations

    def __add__(self, other) -> TrackedInt:
        if isinstance(other, TrackedInt):
            new_com = f"({self} + {other}"
        else:
            new_com = f"⌊{self} + {other}⌋"

        new_val = self._dunder_helper(other, lambda x, y: math.floor(x + y))
        new_tracked_int = self.__class__(new_val, new_com)
        assert isinstance(new_tracked_int, self.__class__)
        return new_tracked_int

    def __sub__(self, other) -> TrackedInt:
        if isinstance(other, TrackedInt):
            new_com = f"({self} - {other}"
        else:
            new_com = f"⌊{self} - {other}⌋"

        new_val = self._dunder_helper(other, lambda x, y: math.floor(x - y))
        new_tracked_int = self.__class__(new_val, new_com)
        assert isinstance(new_tracked_int, self.__class__)
        return new_tracked_int

    def __mul__(self, other) -> TrackedInt:
        if isinstance(other, TrackedInt):
            new_com = f"({self} · {other})"
        else:
            new_com = f"⌊{self} · {other}⌋"

        new_val = self._dunder_helper(other, lambda x, y: math.floor(x * y))
        new_tracked_int = self.__class__(new_val, new_com)
        assert isinstance(new_tracked_int, self.__class__)
        return new_tracked_int

    def __rmul__(self, other) -> TrackedInt:
        return self.__mul__(other)

    # class methods

    @classmethod
    def zero(cls):
        return cls(0)

    @classmethod
    def one(cls):
        return cls(1)


@dataclass(eq=False, unsafe_hash=True)
class TrackedFloat(TrackedValue):
    _value: float | float64

    # properties

    @property
    def value(self) -> float | float64:
        return self._value

    def __float__(self) -> float:
        return float(self.value)

    # operations

    def _assert_subclass(self, __value: TrackedValue, /) -> TrackedFloat:
        val = super()._assert_subclass(__value)
        assert isinstance(val, self.__class__)

        return val

    def __add__(self, other) -> TrackedFloat:
        new_com = f"({self} + {other})"
        new_val = self._dunder_helper(other, lambda x, y: math.floor(x + y))

        val = self.__class__(new_val, new_com)
        return val

    def __radd__(self, other) -> TrackedFloat:
        return self._assert_subclass(super().__radd__(other))

    # class methods

    @classmethod
    def zero(cls) -> TrackedFloat:
        return cls(0.0)

    @classmethod
    def one(cls) -> TrackedFloat:
        return cls(1.0)


###############################################################################
# specific subclasses                                                         #
###############################################################################


class Level(TrackedInt):
    def _assert_subclass(self, __value: TrackedValue, /) -> Level:
        val = super()._assert_subclass(__value)
        assert isinstance(val, self.__class__)

        return val

    def __add__(self, other) -> Level:
        return self._assert_subclass(super().__add__(other))

    def __radd__(self, other) -> Level:
        return self._assert_subclass(super().__radd__(other))

    def __sub__(self, other) -> Level:
        return self._assert_subclass(super().__sub__(other))

    def __mul__(self, other) -> Level:
        return self._assert_subclass(super().__mul__(other))

    def __rmul__(self, other) -> Level:
        return self._assert_subclass(super().__rmul__(other))


class LevelModifier(TrackedFloat):
    ...


class Roll(TrackedInt):
    def _assert_subclass(self, __value: TrackedValue, /) -> Roll:
        val = super()._assert_subclass(__value)
        assert isinstance(val, self.__class__)

        return val

    def __sub__(self, other) -> Roll:
        return self._assert_subclass(super().__sub__(other))

    def __mul__(self, other) -> Roll:
        return self._assert_subclass(super().__mul__(other))


class RollModifier(TrackedFloat):
    ...


class DamageValue(TrackedInt):
    def _assert_subclass(self, __value: TrackedValue, /) -> DamageValue:
        val = super()._assert_subclass(__value)
        assert isinstance(val, self.__class__)

        return val

    def __add__(self, other) -> DamageValue:
        return self._assert_subclass(super().__add__(other))

    def __radd__(self, other) -> DamageValue:
        return self._assert_subclass(super().__radd__(other))

    def __mul__(self, other) -> DamageValue:
        return self._assert_subclass(super().__mul__(other))

    def __rmul__(self, other) -> DamageValue:
        return self._assert_subclass(super().__rmul__(other))


class DamageModifier(TrackedFloat):
    def _assert_subclass(self, __value: TrackedValue, /) -> DamageModifier:
        val = super()._assert_subclass(__value)
        assert isinstance(val, self.__class__)

        return val

    def __add__(self, other) -> DamageModifier:
        return self._assert_subclass(super().__add__(other))


class StyleBonus(TrackedInt):
    ...


class EquipmentStat(TrackedInt):
    """Stats for Equipment and related fields"""

    @staticmethod
    def _assert_subclass(__value: TrackedInt, /) -> EquipmentStat:
        assert isinstance(__value, EquipmentStat)
        return __value

    def __add__(self, other) -> EquipmentStat:
        return self._assert_subclass(super().__add__(other))

    def __sub__(self, other) -> EquipmentStat:
        return self._assert_subclass(super().__sub__(other))


ModifierPair = tuple[RollModifier, TrackedFloat]
VoidModifiers = tuple[LevelModifier, LevelModifier]

MinimumVisibleLevel = Level(0, "min visible lvl")
MaximumVisibleLevel = Level(120, "max visible lvl")


###############################################################################
# helper functions                                                            #
###############################################################################


def create_modifier_pair(
    value: float | None = None, comment: str | None = None
) -> tuple[RollModifier, DamageModifier]:
    """Create a RollModifier and DamageModifier with the same value/comment.

    Often (but not always) these two values are the same, this function
    simplifies the creation process.

    Parameters
    ----------
    value : float | None, optional
        The float value, by default None
    comment : str | None, optional
        A description of the modifier's source, by default None

    Returns
    -------
    tuple[RollModifier, DamageModifier]
    """
    value = float(1) if value is None else value
    return RollModifier(value, comment), DamageModifier(value, comment)
