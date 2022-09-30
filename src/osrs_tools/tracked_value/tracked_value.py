"""Definition of TrackedValue, TrackedInt, & TrackedFloat

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-03                                                         #
###############################################################################
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable

from numpy import float64, int64

###############################################################################
# abstract class                                                              #
###############################################################################


@dataclass(eq=False, unsafe_hash=True)
class TrackedValue:
    _value: Any
    _value_type: type = field(init=False)
    _comment: str | None = None
    _comment_is_default: bool = field(init=False, default=False)

    # dunder and helper methods ###############################################

    def __post_init__(self):
        self._value_type = type(self.value)

        if self._comment is None:
            self._comment = str(self.value)
            self._comment_is_default = True

    def _dunder_helper(self, other, func: Callable[[Any, Any], Any]) -> Any:
        """Performs a basic function on self and other.

        Parameters
        ----------
        other
            Must be either a TrackedValue or the same type as self._value_type.

        func : Callable[[Any, Any], Any]
            Takes self and other, yields Any.

        Raises
        ------

        TypeError

        Returns
        -------

        Any: Type return controlled by subclasses, with self taking precedence.
        """
        if isinstance(other, TrackedValue):
            _val = func(self.value, other.value)
        elif isinstance(other, self._value_type):
            _val = func(self.value, other)
        else:
            raise TypeError(other)

        return _val

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

    def __str__(self):
        _s = f"{self.__class__.__name__}({self.value})"

        if not self._comment_is_default:
            _s = _s[:-1] + f": {self.comment})"

        return _s

    # properties ##############################################################

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, __x, /):
        if not isinstance(__x, self._value_type):
            raise TypeError(__x, self._value_type)

        self._value = __x

    @property
    def comment(self) -> str:
        assert self._comment is not None
        return self._comment

    @comment.setter
    def comment(self, __x, /):
        assert isinstance(__x, str)
        self._comment = __x

    # arithmetic operations ###################################################
    # def __copy__(self) -> TrackedValue:
    #     unpacked = (copy(getattr(self, field.name)) for field in fields(self))
    #     return self.__class__(*unpacked)

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
        return self.__class__(new_val, new_com)

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


###############################################################################
# concrete classes                                                            #
###############################################################################


@dataclass(eq=False, unsafe_hash=True)
class TrackedInt(TrackedValue):
    _value: int | int64

    # properties

    @property
    def value(self) -> int | int64:
        return self._value

    def __int__(self):
        return int(self._value)

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
    def zero(cls) -> TrackedInt:
        return cls(0)

    @classmethod
    def one(cls) -> TrackedInt:
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
        new_val = self._dunder_helper(other, lambda x, y: x + y)

        val = self.__class__(new_val, new_com)
        return val

    def __radd__(self, other) -> TrackedFloat:
        return self._assert_subclass(super().__radd__(other))

    def __mul__(self, other) -> TrackedFloat:
        return self._assert_subclass(super().__mul__(other))

    # class methods

    @classmethod
    def zero(cls) -> TrackedFloat:
        return cls(0.0)

    @classmethod
    def one(cls) -> TrackedFloat:
        return cls(1.0)
