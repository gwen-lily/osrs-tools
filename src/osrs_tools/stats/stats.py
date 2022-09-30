"""Definition of Stats and StatsOptional

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass, fields
from functools import total_ordering, wraps
from typing import Any, Callable

from osrs_tools.data import Skills
from osrs_tools.exceptions import OsrsException
from osrs_tools.tracked_value import Level

###############################################################################
# errors 'n such                                                              #
###############################################################################


class StatsError(OsrsException):
    pass


###############################################################################
# abstract classes                                                            #
###############################################################################


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
