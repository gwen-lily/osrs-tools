"""Defines PvmAxes

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-06                                                         #
###############################################################################
"""

from __future__ import annotations

from dataclasses import Field, dataclass, field
from typing import Any

from osrs_tools.boost import Boost
from osrs_tools.character import Character
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.gear import Equipment
from osrs_tools.prayer import Prayer, Prayers
from osrs_tools.spell import Spell
from osrs_tools.stats import PlayerLevels
from osrs_tools.style import WeaponStyles

from .damage_axes import DamageAxes

###############################################################################
# main class                                                                  #
###############################################################################


@dataclass
class PvmAxes(DamageAxes):
    """Axes for a generic PvM damage calculation comparison

    Attributes
    ----------

    players : list[Player]
        A list of players

    targets : list[Character]
        A list of targets

    equipment : list[Equipment]
        A list of Equipment objects

    styles : list[WeaponStyles]
        A list of styles

    prayers : list[Prayers]
        A list of prayers

    boosts : list[Boost]
        A list of boosts

    levels : list[PlayerLevels]
        A list of levels

    distance : list[int]
        A list of distances between the attacker and target

    spells : list[Spell]
        A list of spells

    additional_targets_lsts : list[int | list[Character]]
        A list of additional target numbers or lists of characters

    """

    # characters axes
    player: list[Player]
    target: list[Character]
    # strategy parameters (interact with player)
    equipment: list[Equipment] = field(default_factory=list)
    style: list[WeaponStyles] = field(default_factory=list)
    prayers: list[Prayers] = field(default_factory=list)
    boosts: list[Boost] = field(default_factory=list)
    levels: list[PlayerLevels] = field(default_factory=list)
    # damage distribution parameters
    special_attack: list[bool] = field(default_factory=list)
    distance: list[int] = field(default_factory=list)
    spell: list[Spell] = field(default_factory=list)
    additional_targets: list[int | list[Character]] = field(default_factory=list)

    # properties

    @property
    def characters_axes(self) -> tuple[Field[Any], ...]:
        _field_names = [
            "player",
            "target",
        ]

        return tuple(axis for axis in self.axes if axis.name in _field_names)

    @property
    def strategy_axes(self) -> tuple[Field[Any], ...]:
        _field_names = [
            "equipment",
            "style",
            "prayers",
            "boosts",
            "levels",
        ]

        return tuple(axis for axis in self.axes if axis.name in _field_names)

    @property
    def pvm_calc_axes(self) -> tuple[Field[Any], ...]:
        _field_names = [
            "special_attack",
            "distance",
            "spell",
            "additional_targets",
        ]

        return tuple(axis for axis in self.axes if axis.name in _field_names)

    # class methods

    @classmethod
    def create(
        cls,
        player: Player | list[Player] | None = None,
        target: Monster | list[Monster] | None = None,
        *,
        equipment: Equipment | list[Equipment] | None = None,
        style: WeaponStyles | list[WeaponStyles] | None = None,
        prayers: Prayer | Prayers | list[Prayers] | None = None,
        boosts: Boost | list[Boost] | None = None,
        levels: PlayerLevels | list[PlayerLevels] | None = None,
        special_attack: bool | list[bool] | None = None,
        distance: int | list[int] | None = None,
        spell: Spell | list[Spell] | None = None,
        additional_targets: list[list[Character]] | list[int] | None = None,
    ) -> PvmAxes:
        """Create PvmAxes with converters and type validation

        see class docstrings

        Returns
        -------
        PvmAxes
        """

        def convert_to_axis(__value: Any | list[Any] | None, /) -> list[Any]:
            """Conform user values to the data structure"""
            if isinstance(__value, list):
                # argument properly formed
                return __value

            # non-list arguments
            return [__value]

        _axes_dict: dict[str, Any] = {
            "player": player,
            "target": target,
            "equipment": equipment,
            "style": style,
            "prayers": prayers,
            "boosts": boosts,
            "levels": levels,
            "special_attack": special_attack,
            "distance": distance,
            "spell": spell,
            "additional_targets": additional_targets,
        }
        axes_dict: dict[str, list[Any]] = {}

        for k, v in _axes_dict.items():
            if v is None:
                continue

            axes_dict[k] = convert_to_axis(v)

        return cls(**axes_dict)
