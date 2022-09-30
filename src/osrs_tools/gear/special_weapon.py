"""SpecialWeapon, a subclass of Weapon with some extra functionality.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from dataclasses import dataclass, field

from osrs_tools.data import DT, Slots
from osrs_tools.gear.utils import (
    lookup_gear_bb_by_name,
    lookup_weapon_attrib_bb_by_name,
)
from osrs_tools.tracked_value import DamageModifier, RollModifier

from .weapon import Weapon, WeaponError

###############################################################################
# errors 'n such                                                              #
###############################################################################


class SpecialWeaponError(WeaponError):
    ...


###############################################################################
# main class                                                                  #
###############################################################################


@dataclass(order=True, frozen=True)
class SpecialWeapon(Weapon):
    """An equippable special weapon in osrs.

    special weapon has all of the attributes of Gear and more, including some optional
    attributes.

    Attributes
    ----------
    name : str
        The name of the special weapon.

    aggressive_bonus : AggressiveStats
        The aggressive bonuses of the special weapon.

    defensive_bonus : DefensiveStats
        The defensive bonuses of the special weapon.

    prayer_bonus : int
        The prayer bonus of the special weapon.

    level_requirements : PlayerLevels
        The requirements to wield the special weapon.

    styles : WeaponStyles
        The style options for the special weapon.

    attack_speed : int
        The base speed (in ticks) between special weapon attacks.

    two_handed : bool
        True if the special weapon is two-handed, else False.

    special_attack_roll_modifiers : list[RollModifier]
        A list of attack roll modifiers which act on the player's attack roll.
        Defaults to empty list.

    special_damage_modifiers : list[DamageModifier]
        A list of damage modifiers which act on the player's damage values.
        Defaults to empty list.

    _special_defence_roll : DT | None
        The damage type the defender uses to determine their defence roll.
        Defaults to None.

    """

    special_attack_roll_modifiers: list[RollModifier] = field(default_factory=list)
    special_damage_modifiers: list[DamageModifier] = field(default_factory=list)
    _special_defence_roll: DT | None = None

    @property
    def special_defence_roll(self) -> DT:
        """The damage type the defender uses to determine their defence roll."""
        assert isinstance(self._special_defence_roll, DT)
        return self._special_defence_roll

    @classmethod
    def from_bb(cls, name: str):

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
            spec_arm_mods,
            spec_dmg_mods,
            sdr,
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
            special_attack_roll_modifiers=spec_arm_mods,
            special_damage_modifiers=spec_dmg_mods,
            _special_defence_roll=sdr,
        )

    @classmethod
    def empty_slot(cls) -> None:
        raise TypeError(type(cls))
