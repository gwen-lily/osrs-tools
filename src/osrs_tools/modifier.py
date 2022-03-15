from __future__ import annotations
from pydantic import validate_arguments, validator, ValidationError
from pydantic.dataclasses import dataclass
from attrs import define, field
from enum import Enum, unique
import math
from typing import Callable


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


MonsterCombatSkills = [
    Skills.attack,
    Skills.strength,
    Skills.defence,
    Skills.ranged,
    Skills.magic,
    Skills.hitpoints,
]


class DamageTypes(Enum):
    stab = "stab"
    slash = "slash"
    crush = "crush"
    ranged = "ranged"
    magic = "magic"


@dataclass
class TrackedValue:
    value: int | float
    comment: str | None

    def __post_init__(self):
        if self.comment is None:
            self.comment = str(self.value)


@dataclass
class Modifier(TrackedValue):
    """This class wraps a float with optional comment to describe the modifier application.
    """
    value: float
    comment: str | None

    @validator('value')
    def modifier_bounds(cls, v):
        if v < 0:
            raise ValueError(v)

    def __float__(self) -> float:
        return self.value


@validate_arguments
class AttackRollModifier(Modifier):
    """Simple subclass for the Modifier object for type validation.
    """


@validate_arguments
class DamageModifier(Modifier):
    """Simple subclass for the Modifier object for type validation.
    """


@validate_arguments
class LevelModifier(Modifier):
    """Simple subclass for the Modifier object for type validation.
    """


@validate_arguments
@dataclass
class StyleBonus(TrackedValue):
    value: int
    comment: str | None


@validate_arguments
@dataclass
class Roll(TrackedValue):
    value: int
    comment: str | None

    @validator('value')
    def roll_bounds(cls, v):
        if v < 0:
            raise ValueError(v)

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
            self.value += other.value
            self.comment = f'({self.comment!s} + {other.comment!s})'
        elif isinstance(other, int):
            self.value += other
            self.comment = f'({self.comment!s} + {other!s})'
        else:
            raise NotImplementedError

        return self

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
            self.value += other.value
            self.comment = f'({self.comment!s} - {other.comment!s})'
        elif isinstance(other, int):
            self.value += other
            self.comment = f'({self.comment!s} - {other!s})'
        else:
            raise NotImplementedError

        return self

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
            self.value = math.floor(int(self) * float(other))
            self.comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        elif isinstance(other, int):
            self.value = int(self) * other
            self.comment = f'({self.comment!s} · {other!s})'
        else:
            raise NotImplementedError

        return self


@validate_arguments
@dataclass
class Level(TrackedValue):
    """A Level object which implements proper type security and modification tracking & representation.

    # TODO: Def smart __repr__ which implements PE(MD)(AS) to format pretty repr

    Raises:
        NotImplementedError: Raised with illegal arithmetic operations.
    """
    value: int
    comment: str | None

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: Level | int) -> Level:
        """Defines addition between two Level objects.

        Args:
            other (Level, int): An integer-like object.

        Raises:
            NotImplementedError: Raised with unsupported addition.

        Returns:
            Level: The sum of both Levels.
        """
        if isinstance(other, Level):
            self.value += other.value
            self.comment = f'({self.comment!s} + {other.comment!s})'
        elif isinstance(other, int):
            self.value += other
            self.comment = f'({self.comment!s} + {other!s})'
        else:
            raise NotImplementedError

        return self

    def __sub__(self, other: Level | int) -> Level:
        """Defines subtraction between two Level objects.

        Args:
            other (Level, int): An integer-like object.

        Raises:
            NotImplementedError: Raised with unsupported subtraction.

        Returns:
            Level: Level (self) minus Level (other).
        """
        if isinstance(other, Level):
            self.value -= other.value
            self.comment = f'({self.comment!s} - {other.comment!s})'
        elif isinstance(other, int):
            self.value -= other
            self.comment += f'({self.comment!s} - {other!s})'
        else:
            raise NotImplementedError

        return self

    def __mul__(self, other: LevelModifier) -> Level:
        """Defines multiplication between Level objects and LevelModifiers which act on them.

        Level objects are modified by a variable amount of LevelModifiers, which are floored 
        between each successive multiplication. This method defines that behavior.

        Args:
            other (LevelModifier): A LevelModifier object which acts on the Level.

        Raises:
            NotImplementedError: Raised with unsupported multiplication.

        Returns:
            Level: A Level object, the result of floored multiplication by other.
        """
        if isinstance(other, LevelModifier):
            self.value = math.floor(int(self) * float(other))
            self.comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        else:
            raise NotImplementedError

        return self


CallableLevelsModifierType = Callable[[Level], tuple[Level]]


@validate_arguments
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


@validate_arguments
@dataclass
class PlayerLevel(Level):
    @validator('value')
    def player_level_bounds(cls, v):
        if v not in range(1, 99+1):
            raise ValueError(v)

    def __add__(self, other: PlayerLevel | StyleBonus | int) -> ModifiedPlayerLevel:
        if isinstance(other, PlayerLevel):
            new_value = self.value + other.value
            new_comment = f'({self.comment!s} + {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value + other
            new_comment = f'({self.comment!s} + {other!s})'
        elif isinstance(other, StyleBonus):
            new_value = self.value + other.value
            new_comment = f'({self.comment!s} + {other.comment!s})'
        else:
            raise NotImplementedError

        return ModifiedPlayerLevel(new_value, new_comment)

    def __sub__(self, other: PlayerLevel | StyleBonus | int) -> ModifiedPlayerLevel:
        if isinstance(other, PlayerLevel):
            new_value = self.value - other.value
            new_comment = f'({self.comment!s} - {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value - other
            new_comment = f'({self.comment!s} - {other!s})'
        elif isinstance(other, StyleBonus):
            new_value = self.value - other.value
            new_comment = f'({self.comment!s} - {other.comment!s})'
        else:
            raise NotImplementedError

        return ModifiedPlayerLevel(new_value, new_comment)

    def __mul__(self, other: LevelModifier) -> ModifiedPlayerLevel:
        if isinstance(other, LevelModifier):
            new_value = math.floor(int(self) * float(other))
            new_comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        else:
            raise NotImplementedError

        return ModifiedPlayerLevel(new_value, new_comment)


@validate_arguments
class ModifiedPlayerLevel(PlayerLevel):
    @validator('value')
    def player_level_bounds(cls, v):
        if v < 0:
            raise ValueError(v)

    def __mul__(self, other: LevelModifier) -> ModifiedPlayerLevel:
        """Overrides PlayerLevel.__mul__ in order to avoid unnecessary object creation.

        Args:
            other (LevelModifier): A LevelModifier object.

        Raises:
            NotImplementedError: Raised under illegal arithmetic.

        Returns:
            ModifiedPlayerLevel: 
        """
        if isinstance(other, LevelModifier):
            self.value = math.floor(int(self) * float(other))
            self.comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        else:
            raise NotImplementedError

        return self


@validate_arguments
class MonsterLevel(Level):
    """Simple wrapper for Level which is fine for Monsters with mostly unbound levels.

    Raises:
        NotImplementedError: Raised under illegal arithmetic operations.
    """
    @validator('value')
    def monster_level_bounds(cls, v):
        if v < 0:
            raise ValueError(v)

    def __add__(self, other: MonsterLevel | StyleBonus | int) -> ModifiedMonsterLevel:
        if isinstance(other, MonsterLevel):
            new_value = self.value + other.value
            new_comment = f'({self.comment!s} + {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value + other
            new_comment = f'({self.comment!s} + {other!s})'
        elif isinstance(other, StyleBonus):
            new_value = self.value + other.value
            new_comment = f'({self.comment!s} + {other.comment!s})'
        else:
            raise NotImplementedError

        return ModifiedMonsterLevel(new_value, new_comment)

    def __sub__(self, other: MonsterLevel | int) -> ModifiedMonsterLevel:
        if isinstance(other, MonsterLevel):
            new_value = self.value - other.value
            new_comment = f'({self.comment!s} - {other.comment!s})'
        elif isinstance(other, int):
            new_value = self.value - other
            new_comment = f'({self.comment!s} - {other!s})'
        elif isinstance(other, StyleBonus):
            new_value = self.value - other.value
            new_comment = f'({self.comment!s} - {other.comment!s})'
        else:
            raise NotImplementedError

        return ModifiedMonsterLevel(new_value, new_comment)

    def __mul__(self, other: LevelModifier) -> ModifiedMonsterLevel:
        if isinstance(other, LevelModifier):
            new_value = math.floor(int(self) * float(other))
            new_comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        else:
            raise NotImplementedError

        return ModifiedMonsterLevel(new_value, new_comment)


@validate_arguments
class ModifiedMonsterLevel(MonsterLevel):
    @validator('value')
    def monster_level_bounds(cls, v):
        if v < 0:
            raise ValueError(v)

    def __mul__(self, other: LevelModifier) -> ModifiedMonsterLevel:
        """Overrides MonsterLevel.__mul__ in order to avoid unnecessary object creation.

        Args:
            other (LevelModifier): A LevelModifier object.

        Raises:
            NotImplementedError: Raised under illegal arithmetic.

        Returns:
            ModifiedMonsterLevel: 
        """
        if isinstance(other, LevelModifier):
            self.value = math.floor(int(self) * float(other))
            self.comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
        else:
            raise NotImplementedError

        return self


@validate_arguments
@dataclass
class DamageValue(TrackedValue):
    value: int
    comment: str | None

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: DamageValue | int) -> DamageValue:
        if isinstance(other, DamageValue):
            self.value += other.value
            self.comment = f'({self.comment!s} + {other.comment!s})'
        elif isinstance(other, int):
            self.value += other
            self.comment = f'({self.comment!s} + {other!s})'
        else:
            raise NotImplementedError

        return self

    def __sub__(self, other: DamageValue | int) -> DamageValue:
        if isinstance(other, DamageValue):
            self.value -= other.value
            self.comment = f'({self.comment!s} - {other.comment!s})'
        elif isinstance(other, int):
            self.value -= other
            self.comment = f'({self.comment!s} - {other!s})'
        else:
            raise NotImplementedError

        return self

    def __mul__(self, other: DamageModifier) -> DamageValue:
        if isinstance(other, DamageModifier):
            self.value = math.floor(int(self) * float(other))
            self.comment = f'⌊{self.comment!s} · {other.comment!s}⌋'
            return self
        else:
            raise NotImplementedError


def create_modifier_pair(value: float = None, comment: str = None) -> tuple[AttackRollModifier, DamageModifier]:
    value = float(value) if value is not None else float(1)
    comment = str(comment) if comment is not None else None
    return AttackRollModifier(value, comment), DamageModifier(value, comment)
