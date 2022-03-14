from __future__ import annotations
from numpy import isin
from osrsbox.items_api.modifier import Modifier
from dataclasses import dataclass
import math


class AttackRollModifier(Modifier):
    """Simple subclass for the Modifier object for type validation.
    """


class DamageModifier(Modifier):
    """Simple subclass for the Modifier object for type validation.
    """


@dataclass
class Roll:
    value: int

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: Roll) -> Roll:
        """Defines addition between OSRS Roll objects.

        Args:
            other (Roll): A Roll object.

        Raises:
            NotImplementedError: Raised with unsupported addition.

        Returns:
            Roll: Integer roll value.
        """
        if isinstance(other, Roll):
            self.value += other.value
            return self
        else:
            raise NotImplementedError
    
    def __mul__(self, other: Modifier) -> Roll:
        """Defines multiplication between OSRS Roll objects and Modifiers which act on them.

        OSRS Roll objects are modified by a variable amount of Modifiers, which are floored 
        between each successive multiplication. This class defines that behavior.

        Args:
            other (Modifier): A Modifier object which acts on the Roll.

        Raises:
            NotImplementedError: Raised with unsupported multiplication.

        Returns:
            Roll: Integer roll value.
        """
        if isinstance(other, Modifier):
            self.value = math.floor(int(self) * float(other))
            return self
        else:
            raise NotImplementedError


@dataclass
class MaxHit:
    value: int

    def __int__(self) -> int:
        return self.value

    def __add__(self, other: int | MaxHit) -> MaxHit:
        if isinstance(other, int):
            self.value += other
            return self
        elif isinstance(other, MaxHit):
            self.value += other.value
            return self
        else:
            raise NotImplementedError

    def __sub__(self, other: int | MaxHit) -> MaxHit:
        if isinstance(other, int):
            self.value -= other
            return self
        elif isinstance(other, MaxHit):
            self.value -= other.value
            return self
        else:
            raise NotImplementedError
    
    def __mul__(self, other: DamageModifier) -> MaxHit:
        if isinstance(other, DamageModifier):
            self.value = math.floor(int(self) * float(other))
            return self
        else:
            raise NotImplementedError
    



def create_modifier_pair(value: float = None, comment: str = None) -> tuple[AttackRollModifier, DamageModifier]:
    value = float(value) if value is not None else float(1)
    comment = str(comment) if comment is not None else None
    return AttackRollModifier(value, comment), DamageModifier(value, comment)