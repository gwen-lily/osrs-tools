from __future__ import annotations

import math
from copy import copy
from dataclasses import dataclass, field, fields
from enum import Enum, unique
from functools import total_ordering
from typing import Callable

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


@total_ordering
@dataclass
class TrackedValue:
    value: int | float
    comment: str | None = None

    def __post_init__(self):
        if not isinstance(self.value, int):
            self.value = int(self.value)

        if self.comment is None:
            self.comment = str(self.value)

    def __floordiv__(self, other) -> int:
        return math.floor(self.value // other)

    def __lt__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.value < other.value
        else:
            return self.value < other

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        else:
            return self.value == other

    def __copy__(self):
        unpacked = tuple(copy(getattr(self, field.name)) for field in fields(self))
        return self.__class__(*unpacked)


# subclasses


@dataclass
class Level(TrackedValue):
    """A Level object which implements proper type security and modification tracking & representation.

    # TODO: Def smart __repr__ which implements PE(MD)(AS) to format pretty repr

    Raises:
        NotImplementedError: Raised with illegal arithmetic operations.
    """

    value: int
    comment: str | None = None

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: Level | StyleBonus | int) -> Level:
        if isinstance(other, Level) or isinstance(other, StyleBonus):
            new_value = self.value + other.value
            new_comment = f"({self.comment!s} + {other.comment!s})"
        elif isinstance(other, int):
            new_value = self.value + other
            new_comment = f"({self.comment!s} + {other!s})"
        else:
            raise NotImplementedError

        return Level(new_value, new_comment)

    def __radd__(self, other: StyleBonus | int) -> Level:
        if isinstance(other, StyleBonus) or isinstance(other, int):
            return self.__add__(other)
        else:
            raise NotImplementedError

    def __sub__(self, other: Level | StyleBonus | int) -> Level:
        if isinstance(other, Level) or isinstance(other, StyleBonus):
            new_value = self.value - other.value
            new_comment = f"({self.comment!s} - {other.comment!s})"
        elif isinstance(other, int):
            new_value = self.value - other
            new_comment = f"({self.comment!s} - {other!s})"
        elif isinstance(other, float):
            new_value = math.floor(self.value - other)
            new_comment = f"⌊{self.comment!s} - {other!s}⌋"
        else:
            raise NotImplementedError

        return Level(new_value, new_comment)

    def __rsub__(self, other: int):
        if isinstance(other, int):
            new_value = int(other) - int(self)
            new_comment = f"({other!s} - {self.comment!s})"
        else:
            raise NotImplementedError

        return Level(new_value, new_comment)

    def __mul__(self, other: LevelModifier | int) -> Level:
        if isinstance(other, LevelModifier):
            new_value = math.floor(int(self) * float(other))
            new_comment = f"⌊{self.comment!s} · {other.comment!s}⌋"
        elif isinstance(
            other, int
        ):  # TODO: Figure this out ->  or isinstance(other, np.int64):
            new_value = int(self) * int(other)
            new_comment = f"({self.comment!s} · {other!s})"
        else:
            raise NotImplementedError

        return Level(new_value, new_comment)

    def __rmul__(self, other: int) -> int:
        if isinstance(other, int):
            return int(self * other)

    def __truediv__(self, other: int | float | Level) -> int | float:
        if isinstance(other, Level):
            return int(self) / int(other)
        elif isinstance(other, int) or isinstance(other, float):
            return int(self) / other
        else:
            raise NotImplementedError

    def __floordiv__(self, other: float) -> int:
        if isinstance(other, float):
            val = math.floor(int(self) / other)
        else:
            raise NotImplementedError

        return val


@dataclass
class Roll(TrackedValue):
    """Roll value."""

    value: int
    comment: str | None = None

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: Roll | int) -> Roll:
        """Defines addition between integer-like objects.

        Args:
            other (Roll): An object which supports __int__

        Raises:
            NotImplementedError: Raised with unsupported addition.

        Returns:
            Roll: Summed roll.
        """
        if isinstance(other, Roll):
            new_value = self.value + other.value
            new_comment = f"({self.comment!s} + {other.comment!s})"
        elif isinstance(other, int):
            new_value = self.value + other
            new_comment = f"({self.comment!s} + {other!s})"
        else:
            raise NotImplementedError

        return Roll(new_value, new_comment)

    def __sub__(self, other: Roll | int) -> Roll:
        """Defines subtraction between integer-like objects.

        Args:
            other (Roll): An object which supports __int__

        Raises:
            NotImplementedError: Raised with unsupported subtraction.

        Returns:
            Roll: roll (self)) - roll (other).
        """
        if isinstance(other, Roll):
            new_value = self.value - other.value
            new_comment = f"({self.comment!s} - {other.comment!s})"
        elif isinstance(other, int):
            new_value = self.value - other
            new_comment = f"({self.comment!s} - {other!s})"
        elif isinstance(other, float):
            new_value = math.floor(self.value - other)
            new_comment = f"⌊{self.comment!s} - {other!s}⌋"
        else:
            raise NotImplementedError

        return Roll(new_value, new_comment)

    def __mul__(self, other: AttackRollModifier | int) -> Roll:
        """Defines multiplication between Roll objects and Modifiers which act on them.

        OSRS Roll objects are modified by a variable amount of Modifiers, which are floored
        between each successive multiplication. This class defines that behavior.

        Args:
            other (Modifier): A Modifier object which acts on the Roll.

        Raises:
            NotImplementedError: Raised with unsupported multiplication.

        Returns:
            Roll: Integer roll value.
        """
        if isinstance(other, AttackRollModifier):
            new_value = math.floor(int(self) * float(other))
            new_comment = f"⌊{self.comment!s} · {other.comment!s}⌋"
        elif isinstance(other, int):
            new_value = int(self) * other
            new_comment = f"({self.comment!s} · {other!s})"
        else:
            raise NotImplementedError

        return Roll(new_value, new_comment)

    def __div__(self, other: int) -> int:
        if isinstance(other, int):
            return int(self) // other
        else:
            raise NotImplementedError


@dataclass
class DamageValue(TrackedValue):
    value: int
    comment: str | None = None

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: DamageValue | int) -> DamageValue:
        if isinstance(other, DamageValue):
            new_value = self.value + other.value
            new_comment = f"({self.comment!s} + {other.comment!s})"
        elif isinstance(other, int):
            new_value = self.value + other
            new_comment = f"({self.comment!s} + {other!s})"
        else:
            raise NotImplementedError

        return DamageValue(new_value, new_comment)

    def __sub__(self, other: DamageValue | int) -> DamageValue:
        if isinstance(other, DamageValue):
            new_value = self.value - other.value
            new_comment = f"({self.comment!s} - {other.comment!s})"
        elif isinstance(other, int):
            new_value = self.value - other
            new_comment = f"({self.comment!s} - {other!s})"
        else:
            raise NotImplementedError

        return DamageValue(new_value, new_comment)

    def __mul__(self, other: DamageModifier) -> DamageValue:
        if isinstance(other, DamageModifier):
            new_value = math.floor(int(self) * float(other))
            new_comment = f"⌊{self.comment!s} · {other.comment!s}⌋"
        else:
            raise NotImplementedError

        return DamageValue(new_value, new_comment)

    def __div__(self, other: int) -> int:
        if isinstance(other, int):
            return int(self) // other
        else:
            raise NotImplementedError


# modifiers


@dataclass
class Modifier(TrackedValue):
    """This class wraps a float with optional comment to describe the modifier application."""

    value: float
    comment: str | None = None

    def __post_init__(self):
        if not isinstance(self.value, float):
            self.value = float(self.value)

        if self.comment is None:
            self.comment = str(self.value)

    def __float__(self) -> float:
        return self.value


# subclasses
class LevelModifier(Modifier):
    """Simple subclass for the Modifier object for type validation."""


class AttackRollModifier(Modifier):
    """Simple subclass for the Modifier object for type validation."""


class DamageModifier(Modifier):
    """Simple subclass for the Modifier object for type validation."""


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
) -> tuple[AttackRollModifier, DamageModifier]:
    value = float(value) if value is not None else float(1)
    comment = str(comment) if comment is not None else None
    return AttackRollModifier(value, comment), DamageModifier(value, comment)


@dataclass
class StyleBonus(TrackedValue):
    """Style Bonus. :3"""

    value: int
    comment: str | None = None
