from __future__ import annotations
from dataclasses import dataclass, field, fields
from enum import Enum, unique
import math
from typing import Callable
from functools import total_ordering
from copy import copy
import numpy as np

# enums 'n' such ###########################################################


@unique
class DT(Enum):
    """Damage Type (DT) enumerator.

    Args:
        Enum (DT): Enumerator object.
    """
    # melee style class vars
    stab = 'stab'
    slash = 'slash'
    crush = 'crush'
    # ranged style class vars
    ranged = 'ranged'
    # magic style class vars
    magic = 'magic'
    # typeless class vars
    typeless = 'typeless'


# I treat these uniformly as tuples, do as you see fit.
# I know not whether there are different classes of some of these
# Hey reader, check out the band Godspeed You! Black Emperor, they're gr!eat
MeleeDamageTypes = (DT.stab, DT.slash, DT.crush)
RangedDamageTypes = (DT.ranged,)
MagicDamageTypes = (DT.magic,)
TypelessDamageTypes = (DT.typeless,)


@unique
class Stances(Enum):
    # type ambiguous class vars
    accurate = 'accurate'
    longrange = 'longrange'
    defensive = 'defensive'
    no_style = 'no style'
    # melee style class vars
    aggressive = 'aggressive'
    controlled = 'controlled'
    # ranged style class vars
    rapid = 'rapid'
    # magic style class vars
    standard = 'standard'
    # npc stance
    npc = 'npc'


@unique
class Styles(Enum):
    # style names, flavor text as far as I can tell

    slash = 'slash'
    stab = 'stab'
    accurate = 'accurate'
    rapid = 'rapid'
    longrange = 'longrange'
    chop = 'chop'
    smash = 'smash'
    block = 'block'
    hack = 'hack'
    lunge = 'lunge'
    swipe = 'swipe'
    pound = 'pound'
    pummel = 'pummel'
    spike = 'spike'
    impale = 'impale'
    jab = 'jab'
    fend = 'fend'
    bash = 'bash'
    reap = 'reap'
    punch = 'punch'
    kick = 'kick'
    flick = 'flick'
    lash = 'lash'
    deflect = 'deflect'
    short_fuse = 'short fuse'
    medium_fuse = 'medium fuse'
    long_fuse = 'long fuse'
    spell = 'spell'
    focus = 'focus'
    standard_spell = 'standard spell'
    defensive_spell = 'defensive spell'

# Use case: if _ in XStances:
MeleeStances = (Stances.accurate, Stances.aggressive, Stances.defensive, Stances.controlled)
RangedStances = (Stances.accurate, Stances.rapid, Stances.longrange)
MagicStances = (Stances.accurate, Stances.longrange, Stances.no_style, Stances.no_style)
SpellStylesNames = (Styles.standard_spell, Styles.defensive_spell)
ChinchompaStylesNames = (Styles.short_fuse, Styles.medium_fuse, Styles.long_fuse)

@unique
class Skills(Enum):
    attack = "attack"
    strength = "strength"
    defence = "defence"
    ranged = "ranged"
    prayer = "prayer"
    magic = "magic"
    runecraft = "runecraft"
    hitpoints = "hitpoints"
    crafting = "crafting"
    mining = "mining"
    smithing = "smithing"
    fishing = "fishing"
    cooking = "cooking"
    firemaking = "firemaking"
    woodcutting = "woodcutting"
    agility = "agility"
    herblore = "herblore"
    thieving = "thieving"
    fletching = "fletching"
    slayer = "slayer"
    farming = "farming"
    construction = "construction"
    hunter = "hunter"


MonsterCombatSkills = (
    Skills.attack,
    Skills.strength,
    Skills.defence,
    Skills.ranged,
    Skills.magic,
    Skills.hitpoints,
)


@unique
class MonsterTypes(Enum):
    demon = 'demon'
    draconic = 'draconic'
    fiery = 'fiery'
    golem = 'golem'
    kalphite = 'kalphite'
    leafy = 'leafy'
    penance = 'penance'
    shade = 'shade'
    spectral = 'spectral'
    undead = 'undead'
    vampyre = 'vampyre'
    vampyre_tier_1 = 'vampyre - tier 1'
    vampyre_tier_2 = 'vampyre - tier 2'
    vampyre_tier_3 = 'vampyre - tier 3'
    xerician = 'xerician'
    wilderness = 'wilderness'


@unique
class MonsterLocations(Enum):
    wilderness = 'wilderness'
    tob = 'tob'
    cox = 'cox'


# tracked values ###########################################################


@total_ordering
@dataclass
class TrackedValue:
    value: int | float
    comment: str | None = None

    def __post_init__(self):
        if self.comment is None:
            self.comment = str(self.value)

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
        new_value = copy(self.value)
        new_comment = copy(self.comment)
        return self.__class__(new_value, new_comment)

    def __copy__(self):
        unpacked = tuple(getattr(self, field.name) for field in fields(self))
        return self.__class__(*(copy(x) for x in unpacked))

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
            new_comment = f'({self.comment!s} + {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value + other
            new_comment = f'({self.comment!s} + {other!s})'
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
            new_comment = f'({self.comment!s} - {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value - other
            new_comment = f'({self.comment!s} - {other!s})'
        else:
            raise NotImplementedError

        return Level(new_value, new_comment)

    def __mul__(self, other: LevelModifier) -> Level:
        if isinstance(other, LevelModifier):
            new_value = math.floor(int(self) * float(other))
            new_comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        elif isinstance(other, int) or isinstance(other, np.int64):
            new_value = int(self) * int(other)
            new_comment = f'({self.comment!s} · {other!s})'
        else:
            raise NotImplementedError

        return Level(new_value, new_comment)

    def __div__(self, other: int) -> int:
        if isinstance(other, int):
            return int(self) / other
        else:
            raise NotImplementedError


@dataclass
class Roll(TrackedValue):
    """Roll value.
    """
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
            new_comment = f'({self.comment!s} + {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value + other
            new_comment = f'({self.comment!s} + {other!s})'
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
            new_comment = f'({self.comment!s} - {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value - other
            new_comment = f'({self.comment!s} - {other!s})'
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
            new_comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        elif isinstance(other, int):
            new_value = int(self) * other
            new_comment = f'({self.comment!s} · {other!s})'
        else:
            raise NotImplementedError

        return Roll(new_value, new_comment)

    def __div__(self, other: int) -> int:
        if isinstance(other, int):
            return int(self) / other
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
            new_comment = f'({self.comment!s} + {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value + other
            new_comment = f'({self.comment!s} + {other!s})'
        else:
            raise NotImplementedError

        return DamageValue(new_value, new_comment)

    def __sub__(self, other: DamageValue | int) -> DamageValue:
        if isinstance(other, DamageValue):
            new_value = self.value - other.value
            new_comment = f'({self.comment!s} - {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value - other
            new_comment = f'({self.comment!s} - {other!s})'
        else:
            raise NotImplementedError

        return DamageValue(new_value, new_comment)

    def __mul__(self, other: DamageModifier) -> DamageValue:
        if isinstance(other, DamageModifier):
            new_value = math.floor(int(self) * float(other))
            new_comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        else:
            raise NotImplementedError

        return DamageValue(new_value, new_comment)

    def __div__(self, other: int) -> int:
        if isinstance(other, int):
            return int(self) / other
        else:
            raise NotImplementedError

# modifiers


@dataclass
class Modifier(TrackedValue):
    """This class wraps a float with optional comment to describe the modifier application.
    """
    value: float
    comment: str | None = None

    def __float__(self) -> float:
        return self.value


# subclasses
class LevelModifier(Modifier):
    """Simple subclass for the Modifier object for type validation.
    """


class AttackRollModifier(Modifier):
    """Simple subclass for the Modifier object for type validation.
    """


class DamageModifier(Modifier):
    """Simple subclass for the Modifier object for type validation.
    """


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
            self.comment = f'callable modifier: {self.skills}'


def create_modifier_pair(value: float = None, comment: str = None) -> tuple[AttackRollModifier, DamageModifier]:
    value = float(value) if value is not None else float(1)
    comment = str(comment) if comment is not None else None
    return AttackRollModifier(value, comment), DamageModifier(value, comment)


@dataclass
class StyleBonus(TrackedValue):
    """Style Bonus. :3
    """
    value: int
    comment: str | None = None
