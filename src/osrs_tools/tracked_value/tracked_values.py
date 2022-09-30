"""Definition of implementable TrackedValues 

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-03                                                         #
###############################################################################
"""
from __future__ import annotations

from .tracked_value import TrackedFloat, TrackedInt, TrackedValue

###############################################################################
# main classes & their modifiers                                              #
###############################################################################

# level #######################################################################


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

    # class methods

    @classmethod
    def zero(cls) -> Level:
        return Level(0)


class LevelModifier(TrackedFloat):
    ...


# roll ########################################################################


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


# damage value ################################################################


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

    @classmethod
    def zero(cls) -> DamageValue:
        return cls(0)

    @classmethod
    def one(cls) -> DamageValue:
        return cls(1)


class DamageModifier(TrackedFloat):
    def _assert_subclass(self, __value: TrackedValue, /) -> DamageModifier:
        val = super()._assert_subclass(__value)
        assert isinstance(val, self.__class__)

        return val

    def __add__(self, other) -> DamageModifier:
        return self._assert_subclass(super().__add__(other))


# misc #########################################################################


class StyleBonus(TrackedInt):

    # class methods

    @classmethod
    def zero(cls) -> StyleBonus:
        return StyleBonus(0)


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

    def __mul__(self, other: int) -> EquipmentStat:
        return self._assert_subclass(super().__mul__(other))

    # class methods

    @classmethod
    def zero(cls) -> EquipmentStat:
        return EquipmentStat(0)
