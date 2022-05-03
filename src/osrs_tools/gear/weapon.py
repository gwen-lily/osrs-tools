"""Weapon, a subclass of Gear with some extra functionality.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""
from __future__ import annotations

from dataclasses import dataclass, field

from osrs_tools.data import Slots
from osrs_tools.gear.utils import (
    lookup_gear_bb_by_name,
    lookup_weapon_attrib_bb_by_name,
)
from osrs_tools.stats import AggressiveStats, DefensiveStats, PlayerLevels
from osrs_tools.style import PlayerStyle, UnarmedStyles, WeaponStyles

from .gear import Gear, GearError

###############################################################################
# errors 'n such                                                              #
###############################################################################


class WeaponError(GearError):
    pass


###############################################################################
# main class                                                                  #
###############################################################################


@dataclass(order=True, frozen=True)
class Weapon(Gear):
    """An equippable weapon in osrs.

    Weapon has all of the attributes of Gear and more, including some optional
    attributes.

    Attributes
    ----------
    name : str
        The name of the weapon.

    aggressive_bonus : AggressiveStats
        The aggressive bonuses of the weapon.

    defensive_bonus : DefensiveStats
        The defensive bonuses of the weapon.

    prayer_bonus : int
        The prayer bonus of the weapon.

    level_requirements : PlayerLevels
        The requirements to wield the weapon.

    styles : WeaponStyles
        The style options for the weapon.

    attack_speed : int
        The base speed (in ticks) between weapon attacks.

    two_handed : bool
        True if the weapon is two-handed, else False.


    """

    name: str
    aggressive_bonus: AggressiveStats
    defensive_bonus: DefensiveStats
    prayer_bonus: int
    level_requirements: PlayerLevels
    styles: WeaponStyles
    attack_speed: int
    two_handed: bool
    slot: Slots = field(repr=False, init=False, default=Slots.WEAPON)

    # properties

    @property
    def default_style(self) -> PlayerStyle:
        return self.styles.default

    @property
    def reqs(self) -> PlayerLevels:
        return self.level_requirements

    # class methods

    @classmethod
    def empty_slot(cls) -> Weapon:
        name = f"empty {Slots.WEAPON.name}"
        return cls(
            name=name,
            aggressive_bonus=AggressiveStats.no_bonus(),
            defensive_bonus=DefensiveStats.no_bonus(),
            prayer_bonus=0,
            level_requirements=PlayerLevels.no_requirements(),
            styles=UnarmedStyles,
            attack_speed=4,
            two_handed=False,
        )

    @classmethod
    def unarmed(cls) -> Weapon:
        """Simple wrapper for Weapon.empty_slot"""
        return cls.empty_slot()

    @classmethod
    def from_bb(cls, name: str) -> Weapon:
        (
            name,
            slot,
            aggressive_bonus,
            defensive_bonus,
            prayer_bonus,
            level_requirements,
        ) = lookup_gear_bb_by_name(name)
        (
            attack_speed,
            _attack_range,
            two_handed,
            weapon_styles,
            _,
            _,
            _,
        ) = lookup_weapon_attrib_bb_by_name(name)

        if slot is not Slots.WEAPON:
            raise ValueError(slot)

        return cls(
            name=name,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            prayer_bonus=prayer_bonus,
            level_requirements=level_requirements,
            styles=weapon_styles,
            attack_speed=attack_speed,
            two_handed=two_handed,
        )
