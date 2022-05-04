"""Define StylesCollection, WeaponStyles, and MonsterStyles

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from dataclasses import dataclass
from typing import Any

from osrs_tools.data import DT, Stances, Styles

from .style import MonsterStyle, PlayerStyle, Style

###############################################################################
# abstract class                                                              #
###############################################################################


@dataclass
class StylesCollection:
    """Abstract StylesCollection from which others inherit


    Raises
    ------
    AttributeError
    ValueError
    TypeError
    DeprecationWarning
    StyleError
    """

    name: str
    styles: list[Style]
    default: Style

    def __iter__(self):
        yield from self.styles

    def __getitem__(self, __value: Styles | DT | Stances) -> Style:
        val = self.__getattribute__(__value)
        assert isinstance(val, Style)

        return val

    def __getattribute__(self, __name: str | Styles | DT | Stances) -> Any:
        """Direct lookup for Style, DT, & Stances.

        Parameters
        ----------
        __name : str | Styles | DT | Stances
            The attribute name.

        Returns
        -------
        Any
        """

        if isinstance(__name, str):
            return super().__getattribute__(__name)

        elif isinstance(__name, Styles):
            for _style in self.styles:
                if __name is _style.name:
                    return _style

            raise AttributeError(__name)

        elif isinstance(__name, DT):
            matches = [_s for _s in self.styles if _s.damage_type is __name]

            if (n := len(matches)) == 1:
                return matches[0]
            elif n == 0:
                raise ValueError(__name)
            else:
                raise ValueError(__name, matches)

        elif isinstance(__name, Stances):
            matches = [_s for _s in self.styles if _s.stance is __name]

            if (n := len(matches)) == 1:
                return matches[0]
            elif n == 0:
                raise ValueError(__name)
            else:
                raise ValueError(__name, matches)

        else:
            raise TypeError(__name)

    def get_by_style(self, style: Styles) -> Style:
        raise DeprecationWarning

    def get_by_dt(self, damage_type: DT) -> Style:
        raise DeprecationWarning

    def get_by_stance(self, stance: Stances) -> Style:
        raise DeprecationWarning


###############################################################################
# main classes                                                                #
###############################################################################


@dataclass
class WeaponStyles(StylesCollection):
    default: PlayerStyle

    def __getitem__(self, __value: Styles | DT | Stances, /) -> PlayerStyle:
        val = super().__getitem__(__value)
        assert isinstance(val, PlayerStyle)

        return val


@dataclass
class MonsterStyles(StylesCollection):
    default: MonsterStyle

    def __getitem__(self, __value: Styles | DT | Stances, /) -> MonsterStyle:
        val = super().__getitem__(__value)
        assert isinstance(val, MonsterStyle)

        return val
