"""Defines DamageAxes

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-06                                                         #
###############################################################################
"""

from dataclasses import Field, dataclass, fields
from itertools import product
from typing import Any

###############################################################################
# main class                                                                  #
###############################################################################


@dataclass(frozen=True)
class DamageAxes:
    """Basic Axes class which defines __getitem__"""

    # properties ##############################################################

    # normal

    @property
    def axes(self) -> tuple[Field[Any], ...]:
        return tuple(_f for _f in fields(self) if _f.init is True)

    @property
    def dims(self) -> tuple[int, ...]:
        dims: list[int] = []

        for axis in self.axes:
            val = len(getattr(self, axis.name))
            val = 1 if val == 0 else val  # no 0-dim axes
            dims.append(val)

        return tuple(dims)

    @property
    def indices(self):
        return product(*(range(n) for n in self.dims))

    # squeezed

    @property
    def squeezed_axes(self) -> tuple[Field[Any], ...]:
        return tuple(_axis for _axis in self.axes if len(getattr(self, _axis.name)) > 1)

    @property
    def squeezed_dims(self) -> tuple[int, ...]:
        return tuple(_d for _d in self.dims if _d > 1)

    @property
    def squeezed_indices(self) -> product:
        return product(*(range(n) for n in self.squeezed_dims))

    # dunder methods

    def __getitem__(self, __key: tuple[int, ...]) -> tuple[Any, ...]:
        """Get parameter values from indices"""

        if len(__key) == len(self.axes):
            axes = self.axes
        elif len(__key) == len(self.squeezed_axes):
            axes = self.squeezed_axes
        else:
            raise ValueError(__key)

        # _values_dict: dict[str, Any] = {}

        # for axis, idx in zip(axes, __key, strict=True):
        #     _values_dict[axis.name] = getattr(self, axis.name)[idx]

        # return _values_dict

        _values: list[Any] = []

        for axis, idx in zip(axes, __key, strict=True):
            try:
                _values.append(getattr(self, axis.name)[idx])
            except IndexError:
                _values.append(None)

        return tuple(_values)
