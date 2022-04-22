"""Gear & its subclasses, and Equipment.

Equipment is basically a very complicated and bloated Gear container, so it
needs some work to say the least.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field, fields
from functools import reduce
from typing import Any

from osrsbox import items_api
from osrsbox.items_api.item_properties import ItemEquipment
from typing_extensions import Self

import osrs_tools.resource_reader as rr
from osrs_tools.data import (
    DT,
    DamageModifier,
    Level,
    RollModifier,
    Slots,
    TrackedFloat,
    TrackedInt,
)
from osrs_tools.exceptions import OsrsException
from osrs_tools.stats import AggressiveStats, DefensiveStats, PlayerLevels
from osrs_tools.style import (
    BowStyles,
    CrossbowStyles,
    PlayerStyle,
    StylesCollection,
    ThrownStyles,
    UnarmedStyles,
    WeaponStyles,
)

###############################################################################
# errors n' such
###############################################################################

# gear ########################################################################


class GearError(OsrsException):
    pass


class EquipableError(GearError):
    pass


class GearNotFoundError(GearError):
    pass


# weapon ######################################################################


class WeaponError(GearError):
    pass


class SpecialWeaponError(WeaponError):
    ...


# equipment ###################################################################


class EquipmentError(OsrsException):
    ...


class TwoHandedError(EquipmentError):
    ...


###############################################################################
# enums n' helper functions                                                   #
###############################################################################


ITEMS = items_api.load()


def special_defence_roll_validator(_: SpecialWeapon, attribute: str, value: DT):
    if value and value not in DT:
        raise WeaponError(f"{attribute=} with {value=} not in {DT}")


def lookup_gear_bb_by_name(__name: str):
    item_df = rr.lookup_gear(__name)

    if len(item_df) > 1:
        matching_names = tuple(item_df["name"].values)
        raise GearError(matching_names)
    elif len(item_df) == 0:
        raise GearNotFoundError(__name)

    df_item = item_df["name"]
    name = df_item.values[0]
    assert isinstance(name, str)

    aggressive_bonus = AggressiveStats(
        stab=item_df["stab attack"].values[0],
        slash=item_df["slash attack"].values[0],
        crush=item_df["crush attack"].values[0],
        magic_attack=item_df["magic attack"].values[0],
        ranged_attack=item_df["ranged attack"].values[0],
        melee_strength=item_df["melee strength"].values[0],
        ranged_strength=item_df["ranged strength"].values[0],
        magic_strength=item_df["magic damage"].values[
            0
        ],  # stored as float in bitterkoekje's sheet
    )
    defensive_bonus = DefensiveStats(
        stab=item_df["stab defence"].values[0],
        slash=item_df["slash defence"].values[0],
        crush=item_df["crush defence"].values[0],
        magic=item_df["magic defence"].values[0],
        ranged=item_df["ranged defence"].values[0],
    )
    prayer_bonus = item_df["prayer"].values[0]
    level_requirements = PlayerLevels(
        _mining=Level(item_df["mining level req"].values[0])
    )

    slot_src = item_df["slot"].values[0]
    slot_enum = None

    for slot_e in Slots:
        if slot_e.name == slot_src:
            slot_enum = slot_e
            break

    if slot_enum is None:
        raise TypeError(slot_src)

    return (
        name,
        slot_enum,
        aggressive_bonus,
        defensive_bonus,
        prayer_bonus,
        level_requirements,
    )


def lookup_weapon_attrib_bb_by_name(name: str):
    item_df = rr.lookup_gear(name)
    default_attack_range = 0
    comment = "bitter"

    if len(item_df) > 1:
        matching_names = tuple(item_df["name"].values)
        raise GearError(matching_names)
    elif len(item_df) == 0:
        raise GearNotFoundError(name)

    attack_speed = item_df["attack speed"].values[0]
    attack_range = default_attack_range
    two_handed = item_df["two handed"].values[0]
    weapon_styles = StylesCollection.from_weapon_type(item_df["weapon type"].values[0])

    special_accuracy_modifiers = []
    special_damage_modifiers = []
    sdr_enum = None

    if (raw_sarm := item_df["special accuracy"].values[0]) != 0:
        assert raw_sarm is not None
        special_accuracy_modifiers.append(RollModifier(1 + raw_sarm, comment))

    if (raw_sdm1 := item_df["special damage 1"].values[0]) != 0:
        assert raw_sdm1 is not None
        special_damage_modifiers.append(DamageModifier(1 + raw_sdm1, comment))

    if (raw_sdm2 := item_df["special damage 2"].values[0]) != 0:
        assert raw_sdm2 is not None
        special_damage_modifiers.append(DamageModifier(1 + raw_sdm2, comment))

    if (raw_sdr := item_df["special defence roll"].values[0]) != "":
        for dt in DT:
            if dt.name == raw_sdr:
                sdr_enum = dt
                break

    return (
        attack_speed,
        attack_range,
        two_handed,
        weapon_styles,
        special_accuracy_modifiers,
        special_damage_modifiers,
        sdr_enum,
    )


###############################################################################
# gear and its subclasses                                                     #
###############################################################################


@dataclass(order=True, frozen=True)
class Gear:
    """An equippable item in osrs.

    Gear has subclasses Weapon & SpecialWeapon, which each have additional
    attributes. Gear can be created via resources or manually.

    # TODO: Manually / refactor gear to be pre-loaded

    Attributes
    ----------
    name : str
        The name of the gear.

    slot : Slots
        The gear's slot. Must be an enum.

    aggressive_bonus : AggressiveStats
        The aggressive bonuses of the gear.

    defensive_bonus : DefensiveStats
        The defensive bonuses of the gear.

    prayer_bonus : int
        The prayer bonus of the gear.

    level_requirements : PlayerLevels
        The requirements to wield or equip the gear.

    """

    name: str
    slot: Slots
    aggressive_bonus: AggressiveStats = field(repr=False)
    defensive_bonus: DefensiveStats = field(repr=False)
    prayer_bonus: int = field(repr=False)
    level_requirements: PlayerLevels = field(repr=False)

    # dunder methods

    def __str__(self):
        _s = f"{self.__class__.__name__}({self.name})"
        return _s

    # class methods

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

        return cls(
            name=name,
            slot=slot,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            prayer_bonus=prayer_bonus,
            level_requirements=level_requirements,
        )

    @classmethod
    def from_osrsbox(
        cls, name: str | None = None, item_id: int | None = None, **kwargs
    ):

        if name is not None and item_id is None:
            item = ITEMS.lookup_by_item_name(name)
        elif name is None and item_id is not None:
            item = ITEMS.lookup_by_item_id(item_id)
        else:
            raise GearNotFoundError(f"{name=}, {item_id=}")

        if not item.equipable_by_player:
            raise GearError(item.equipable_by_player)

        eqp = item.equipment
        assert isinstance(eqp, ItemEquipment)
        name = item.name.lower()
        slot = None

        # slot validation & weapon / 2h validation
        for slot_enum in Slots:
            if eqp.slot == "ammo":
                slot = Slots.AMMUNITION
                break
            elif eqp.slot in ["2h", Slots.WEAPON.value]:
                raise WeaponError("Instance of weapon in Gear class.")
            elif eqp.slot == slot_enum.value:
                slot = slot_enum
                break

        if slot is None:
            raise GearError(f"{eqp.slot}")

        aggressive_bonus = AggressiveStats(
            stab=TrackedInt(eqp.attack_stab),
            slash=TrackedInt(eqp.attack_slash),
            crush=TrackedInt(eqp.attack_crush),
            magic_attack=TrackedInt(eqp.attack_magic),
            ranged_attack=TrackedInt(eqp.attack_ranged),
            melee_strength=TrackedInt(eqp.melee_strength),
            ranged_strength=TrackedInt(eqp.ranged_strength),
            magic_strength=TrackedFloat(eqp.magic_damage / 100),
        )
        defensive_bonus = DefensiveStats(
            stab=TrackedInt(eqp.defence_stab),
            slash=TrackedInt(eqp.defence_slash),
            crush=TrackedInt(eqp.defence_crush),
            magic=TrackedInt(eqp.defence_magic),
            ranged=TrackedInt(eqp.defence_ranged),
        )
        prayer_bonus = eqp.prayer

        if eqp.requirements is not None:
            combat_key = "combat"
            if combat_key in eqp.requirements:
                eqp.requirements.pop(combat_key)

            reqs = PlayerLevels(**{k: Level(v) for k, v in eqp.requirements.items()})
        else:
            reqs = PlayerLevels.no_requirements()

        return cls(name, slot, aggressive_bonus, defensive_bonus, prayer_bonus, reqs)

    @classmethod
    def empty_slot(cls, slot: Slots):
        _name = f"empty {slot.value}"
        return cls(
            name=_name,
            slot=slot,
            aggressive_bonus=AggressiveStats.no_bonus(),
            defensive_bonus=DefensiveStats.no_bonus(),
            prayer_bonus=0,
            level_requirements=PlayerLevels.no_requirements(),
        )


@dataclass(order=True, frozen=False)
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

    # class methods

    @classmethod
    def empty_slot(cls):
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
    def unarmed(cls):
        """Simple wrapper for Weapon.empty_slot"""
        return cls.empty_slot()

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

    special_attack_roll_modifiers: list[RollModifier] = field(
        default_factory=list, repr=False
    )
    special_damage_modifiers: list[DamageModifier] = field(
        default_factory=list, repr=False
    )
    _special_defence_roll: DT | None = field(default=None, repr=False)

    @property
    def special_defence_roll(self) -> DT:
        """The damage type the defender uses to determine their defence roll."""
        assert isinstance(self._special_defence_roll, DT)
        return self._special_defence_roll

    @classmethod
    def from_bb(cls, name: str):
        # pylint: disable=unexpected-keyword-arg,no-value-for-parameter

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
    def empty_slot(cls):
        raise WeaponError("Attempt to create empty special weapon")


###############################################################################
# equipment                                                                   #
###############################################################################


@dataclass(order=True)
class Equipment:
    """Container class for tracking and manipulating Gear.

    Attributes
    ----------

    _head : Gear | None
        Protected attribute for the head slot, defaults to None.
    _cape : Gear | None
        Protected attribute for the cape slot, defaults to None.
    _neck : Gear | None
        Protected attribute for the neck slot, defaults to None.
    _ammunition : Gear | None
        Protected attribute for the ammunition slot, defaults to None.
    _weapon : Weapon | None
        Protected attribute for the weapon slot, defaults to None.
    _shield : Gear | None
        Protected attribute for the shield slot, defaults to None.
    _body : Gear | None
        Protected attribute for the body slot, defaults to None.
    _legs : Gear | None
        Protected attribute for the legs slot, defaults to None.
    _hands : Gear | None
        Protected attribute for the hands slot, defaults to None.
    _feet : Gear | None
        Protected attribute for the feet slot, defaults to None.
    _ring : Gear | None
        Protected attribute for the ring slot, defaults to None.
    """

    name: str = field(default_factory=str)
    _head: Gear | None = None
    _cape: Gear | None = None
    _neck: Gear | None = None
    _ammunition: Gear | None = None
    _weapon: Weapon | None = None
    _shield: Gear | None = None
    _body: Gear | None = None
    _legs: Gear | None = None
    _hands: Gear | None = None
    _feet: Gear | None = None
    _ring: Gear | None = None

    # dunder & access methods

    def __getattribute__(self, __name: str | Slots, /) -> Any:
        if isinstance(__name, str):
            return super().__getattribute__(__name)
        elif isinstance(__name, Slots):
            gear = super().__getattribute__(__name.value)
            assert isinstance(gear, Gear)
            return gear
        else:
            raise TypeError(__name)

    def __setattr__(self, __name: str | Slots, __value: Any, /) -> None:
        if isinstance(__name, str):
            super().__setattr__(__name, __value)
        elif isinstance(__name, Slots):
            if not isinstance(__value, Gear):
                raise TypeError(f"{__value} is not instance of {Gear}")

            super().__setattr__(__name.value, __value)
        else:
            raise TypeError(__name)

        return

    def _slot_getter(self, __slot: Slots, /) -> Gear:
        """Get a protected slot attribute and return the Gear object."""
        attribute_name = f"_{__slot.value}"
        gear = getattr(self, attribute_name)
        assert isinstance(gear, Gear)

        return gear

    def _slot_setter(self, __slot: Slots, __value: Gear, /):
        """Validate slot membership and set protected slot attribute."""
        assert __value.slot is __slot
        attribute_name = f"_{__slot.value}"
        setattr(self, attribute_name, __value)

    def __add__(self, other: Gear | Equipment) -> Equipment:
        """
        Directional addition, right-hand operand has priority except in the
        case of empty slots.

        :param other:
        :return:
        """
        if isinstance(other, Equipment):
            gear_list = other.equipped_gear
        elif isinstance(other, list):
            for elem in other:
                if not isinstance(elem, Gear):
                    raise TypeError(elem)

            gear_list = other

        elif isinstance(other, Gear):
            gear_list = [other]
        else:
            raise TypeError(other)

        return self.equip(*gear_list)

    def __str__(self):
        if self.name is None:
            message = f'{self.__class__.__name__}({", ".join([g.name for g in self.equipped_gear])})'
        else:
            message = f"{self.__class__.__name__}({self.name})"

        return message

    def __copy__(self):
        return Equipment.from_gear(*self.equipped_gear)

    # class methods

    @classmethod
    def from_gear(cls, *gear: Gear):
        raise DeprecationWarning

    @classmethod
    def no_equipment(cls):
        raise DeprecationWarning

    # access & type validation properties

    @property
    def head(self) -> Gear:
        return self._slot_getter(Slots.HEAD)

    @head.setter
    def head(self, __value: Gear):
        self._slot_setter(Slots.HEAD, __value)

    @property
    def cape(self) -> Gear:
        return self._slot_getter(Slots.CAPE)

    @cape.setter
    def cape(self, __value: Gear):
        self._slot_setter(Slots.CAPE, __value)

    @property
    def neck(self) -> Gear:
        return self._slot_getter(Slots.NECK)

    @neck.setter
    def neck(self, __value: Gear):
        self._slot_setter(Slots.NECK, __value)

    @property
    def ammunition(self) -> Gear:
        return self._slot_getter(Slots.AMMUNITION)

    @ammunition.setter
    def ammunition(self, __value: Gear):
        self._slot_setter(Slots.AMMUNITION, __value)

    @property
    def weapon(self) -> Weapon:
        wpn = self._slot_getter(Slots.WEAPON)
        assert isinstance(wpn, Weapon)

        return wpn

    @weapon.setter
    def weapon(self, __value: Weapon):
        self._slot_setter(Slots.WEAPON, __value)

        if __value.two_handed:
            self.unequip(Slots.SHIELD)

    @property
    def body(self) -> Gear:
        return self._slot_getter(Slots.BODY)

    @body.setter
    def body(self, __value: Gear):
        self._slot_setter(Slots.BODY, __value)

    @property
    def shield(self) -> Gear:
        return self._slot_getter(Slots.SHIELD)

    @shield.setter
    def shield(self, __value: Gear):
        self._slot_setter(Slots.SHIELD, __value)

        if self.weapon.two_handed:
            self.unequip(Slots.WEAPON)

    @property
    def legs(self) -> Gear:
        return self._slot_getter(Slots.LEGS)

    @legs.setter
    def legs(self, __value: Gear):
        self._slot_setter(Slots.LEGS, __value)

    @property
    def hands(self) -> Gear:
        return self._slot_getter(Slots.HANDS)

    @hands.setter
    def hands(self, __value: Gear):
        self._slot_setter(Slots.HANDS, __value)

    @property
    def feet(self) -> Gear:
        return self._slot_getter(Slots.FEET)

    @feet.setter
    def feet(self, __value: Gear):
        self._slot_setter(Slots.FEET, __value)

    @property
    def ring(self) -> Gear:
        return self._slot_getter(Slots.RING)

    @ring.setter
    def ring(self, __value: Gear):
        self._slot_setter(Slots.RING, __value)

    # Basic properties

    @property
    def aggressive_bonus(self) -> AggressiveStats:
        """Find the equipment set's aggressive bonus.

        The one edge case to look out for is the Dinh's Bulwark, which is
        handled via the Player class. Honestly, just use that one whenever
        able.

        Returns
        -------
        AggressiveStats
        """
        val = sum(g.aggressive_bonus for g in self.equipped_gear)

        if isinstance(val, int) and val == 0:
            return AggressiveStats.no_bonus()

        return val

    @property
    def defensive_bonus(self) -> DefensiveStats:
        """Find the equipment set's defensive bonus.

        Returns
        -------
        DefensiveStats
        """
        val = sum(g.defensive_bonus for g in self.equipped_gear)

        if isinstance(val, int) and val == 0:
            return DefensiveStats.no_bonus()

        return val

    @property
    def prayer_bonus(self) -> int:
        """Find the equipment set's prayer bonus."""
        return sum(g.prayer_bonus for g in self.equipped_gear)

    @property
    def level_requirements(self) -> PlayerLevels:
        """Find the equipment set's level requirements."""
        indiv_reqs = [g.level_requirements for g in self.equipped_gear]

        if len(indiv_reqs) > 0:
            reqs = reduce(lambda x, y: x.max_levels_per_skill(y), indiv_reqs)
        else:
            reqs = PlayerLevels.no_requirements()

        return reqs

        return reqs

    @property
    def equipped_gear(self) -> list[Gear]:
        """Return a list of all equipped gear, in class order."""
        gear_list: list[Gear] = []

        for f in fields(self):
            val: Gear = getattr(self, f.name)

            if isinstance(val, Weapon) and val != Weapon.empty_slot():
                gear_list.append(val)
            elif isinstance(val, Gear):
                gear_list.append(val)

        return gear_list

    # basic methods

    def equip(self, *gear: Gear, duplicates_allowed: bool = False) -> Self:
        """Equip the provided gear, also supports weapons."""

        # Catch duplicate error specification.
        if duplicates_allowed is False:
            slots_list = [g.slot for g in gear]
            slots_set = set(slots_list)

            if len(slots_list) != len(slots_set):
                # create a list of the offending dupes
                dupe_gear = []

                for slot, count in Counter(slots_list).items():
                    if not count > 1:
                        continue

                    dupe_gear.append([g for g in gear if g.slot is slot])

                raise ValueError(f"Duplicate gear: {', '.join(dupe_gear)}")

        for g in gear:

            # type checking
            if not isinstance(g, Gear):
                raise TypeError(f"{type(g)} not allowed")

            # attribute modification
            public_slot_name = g.slot.value
            protected_slot_name = f"_{g.slot.value}"

            # don't re-equip the same gear.
            if getattr(self, protected_slot_name) == g:
                continue

            setattr(self, public_slot_name, g)

        return self

    def unequip(self, *slots: Slots) -> Self:
        """Unequip any gear in the provided slots."""

        for slot in slots:
            if slot is Slots.WEAPON:
                setattr(self, Slots.WEAPON.name, Weapon.empty_slot())
                continue

            public_slot_name = slot.value
            setattr(self, public_slot_name, None)

        return self

    def wearing(self, *args, **kwargs) -> bool:
        """Return True if and only if all items are equipped."""

        m = len(args)
        n = len(kwargs)
        if m == 0 and n == 0:
            raise EquipmentError("Equipment.wearing call with no *args or **kwargs")

        if m > 0:
            if any(getattr(self, g.slot.value) != g for g in args):
                return False

        if n > 0:
            if any(getattr(self, k) != v for k, v in kwargs.items()):
                return False

        return True

    # Wearing Properties

    def _full_set_method(self, requires_ammo: bool | None = None) -> bool:
        """Property which returns True if the Equipment slots are fulfilled as needed to perform attacks.

        # TODO: implement osrsbox-db wrapper which eliminates the need for assume_2h parameter.

        Args:
            requires_ammo (bool, optional): If True, requires Ammunition to be equipped even for styles which don't make use
             of it. Defaults to None.
            assume_2h (bool, optional): If True, requires the Equipment.shield slot to be empty. Defaults to True.

        Returns:
            bool: True
        """
        wpn = self.weapon

        if requires_ammo is None:
            if wpn.styles in [BowStyles, CrossbowStyles, ThrownStyles]:
                requires_ammo = True
            else:
                requires_ammo = False

        if requires_ammo and self._ammunition is None:
            return False

        if not wpn.two_handed and self._shield is None:
            return False

        for slot in Slots:
            if slot in (Slots.AMMUNITION, Slots.SHIELD):
                continue
            elif slot is Slots.WEAPON:
                if wpn == Weapon.empty_slot():
                    return False
            else:
                _ = getattr(self, slot.value)  # runs slot assertion

        return True

    @property
    def full_set(self) -> bool:
        """Return True if the equipment is a complete set, else False."""

        return self._full_set_method()

    @property
    def normal_void_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("void knight helm"),
            body=Gear.from_bb("void knight top"),
            legs=Gear.from_bb("void knight robe"),
            hands=Gear.from_bb("void knight gloves"),
        )

    @property
    def elite_void_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("void knight helm"),
            body=Gear.from_bb("elite void top"),
            legs=Gear.from_bb("elite void robe"),
            hands=Gear.from_bb("void knight gloves"),
        )

    @property
    def dharok_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("dharok's greataxe"),
            body=Gear.from_bb("dharok's platebody"),
            legs=Gear.from_bb("dharok's platelegs"),
            weapon=Weapon.from_bb("dharok's greataxe"),
        )

    @property
    def bandos_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("neitiznot faceguard"),
            body=Gear.from_bb("bandos chestplate"),
            legs=Gear.from_bb("bandos tassets"),
        )

    @property
    def inquisitor_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("inquisitor's great helm"),
            body=Gear.from_bb("inquisitor's hauberk"),
            legs=Gear.from_bb("inquisitor's plateskirt"),
        )

    @property
    def torva_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("torva full helm"),
            body=Gear.from_bb("torva platebody"),
            legs=Gear.from_bb("torva platelegs"),
        )

    @property
    def justiciar_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("justiciar faceguard"),
            body=Gear.from_bb("justiciar chestguard"),
            legs=Gear.from_bb("justiciar legguard"),
        )

    @property
    def obsidian_armor_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("obsidian helm"),
            body=Gear.from_bb("obsidian platebody"),
            legs=Gear.from_bb("obsidian platelegs"),
        )

    @property
    def obsidian_weapon(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb("obsidian dagger"),
            Weapon.from_bb("obsidian mace"),
            Weapon.from_bb("obsidian maul"),
            Weapon.from_bb("obsidian sword"),
        )
        return self.weapon in qualifying_weapons

    @property
    def leafy_weapon(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb("leaf-bladed spear"),
            Weapon.from_bb("leaf-bladed sword"),
            Weapon.from_bb("leaf-bladed battleaxe"),
        )
        return self.weapon in qualifying_weapons

    @property
    def keris(self) -> bool:
        qualifying_weapons = (Weapon.from_bb("keris"),)
        return self.weapon in qualifying_weapons

    @property
    def crystal_armor_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("crystal helm"),
            body=Gear.from_bb("crystal body"),
            legs=Gear.from_bb("crystal legs"),
        )

    @property
    def crystal_weapon(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb("crystal bow"),
            Weapon.from_bb("bow of faerdhinen"),
        )
        return self.weapon in qualifying_weapons

    @property
    def smoke_staff(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb("mystic smoke staff"),
            Weapon.from_bb("smoke battlestaff"),
        )
        return self.weapon in qualifying_weapons

    @property
    def graceful_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("graceful hood"),
            body=Gear.from_bb("graceful top"),
            legs=Gear.from_bb("graceful legs"),
            hands=Gear.from_bb("graceful gloves"),
            feet=Gear.from_bb("graceful boots"),
            cape=Gear.from_bb("graceful cape"),
        )

    @property
    def armadyl_crossbow(self) -> bool:
        return self.wearing(weapon=SpecialWeapon.from_bb("armadyl crossbow"))

    @property
    def zaryte_crossbow(self) -> bool:
        return self.wearing(weapon=SpecialWeapon.from_bb("zaryte crossbow"))

    @property
    def scythe_of_vitur(self) -> bool:
        return self.wearing(weapon=Weapon.from_bb("scythe of vitur"))

    @property
    def chinchompas(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb("chinchompa"),
            Weapon.from_bb("red chinchompa"),
            Weapon.from_bb("black chinchompa"),
        )
        return self.weapon in qualifying_weapons

    @property
    def brimstone_ring(self) -> bool:
        return self.wearing(ring=Gear.from_bb("brimstone ring"))

    @property
    def tome_of_fire(self) -> bool:
        return self.wearing(shield=Gear.from_bb("tome of fire"))

    @property
    def tome_of_water(self) -> bool:
        return self.wearing(shield=Gear.from_bb("tome of water"))

    @property
    def staff_of_the_dead(self) -> bool:
        qualifying_weapons = (
            SpecialWeapon.from_bb("staff of light"),
            SpecialWeapon.from_bb("staff of the dead"),
            SpecialWeapon.from_bb("toxic staff of the dead"),
        )
        return self.weapon in qualifying_weapons

    @property
    def elysian_spirit_shield(self) -> bool:
        """Property representing whether or not an Elysian Spirit Shield Gear object is equipped.

        Returns:
            bool: True if the equipped shield slot is an Elysian Spirit Shield Gear object, False otherwise.
        """
        return self.wearing(shield=Gear.from_bb("elysian spirit shield"))

    @property
    def dinhs_bulwark(self) -> bool:
        """Property representing whether or not a Dinh's Bulwark SpecialWeapon is equipped.

        Returns:
            bool: True if the equipped Weapon is a Dinh's Bulwark SpecialWeapon, False otherwise.
        """
        return self.wearing(weapon=SpecialWeapon.from_bb("dinh's bulwark"))

    @property
    def blood_fury(self) -> bool:
        """Property representing whether or not an Amulet of Blood Fury is equipped.

        Returns:
            bool: True if the equipped Gear is an Amulet of Blood Fury Gear object, False otherwise.
        """
        return self.wearing(neck=Gear.from_bb("amulet of blood fury"))

    @property
    def dorgeshuun_special_weapon(self) -> bool:
        """Property representing whether or not an Equipment class weapon is a Bone Special Weapon.

        Bone Special Weapon is a term I created to include the Bone Dagger & Dorgeshuun Crossbow, both of
        which have similar accuracy behavior.

        Returns:
            bool: True if the equipped Weapon is a Bone Dagger or Crossbow SpecialWeapon object, False otherwise.
        """
        matching_weapons = [
            SpecialWeapon.from_bb("bone dagger"),
            SpecialWeapon.from_bb("dorgeshuun crossbow"),
        ]
        return self.weapon in matching_weapons

    @property
    def dragon_claws(self) -> bool:
        """Property representing whether or not a Dragon Claws SpecialWeapon is equipped.

        Returns:
            bool: True if the equipped Weapon is a Dragon Claws. SpecialWeapon, False otherwise.
        """
        return self.wearing(weapon=SpecialWeapon.from_bb("dragon claws"))

    @property
    def abyssal_bludgeon(self) -> bool:
        """Property representing whether or not an Abbysal Bludgeon SpecialWeapon is equipped.

        Returns:
            bool: True if the equipped Weapon is an Abyssal Bludgeon. SpecialWeapon, False otherwise.
        """
        return self.wearing(weapon=SpecialWeapon.from_bb("abyssal bludgeon"))

    @staticmethod
    def _is_crossbow(__wpn: Weapon, /) -> bool:
        """Return True if any form of crossbow is equipped.

        This generic property checks a few obvious values to ensure that other
        modules can interact with Crossbows simply.

        Returns:
            bool: True if any crossbow is equiped, otherwise False.
        """
        name_check = "crossbow" in __wpn.name
        styles_check = __wpn.styles == CrossbowStyles

        return name_check and styles_check

    @property
    def crossbow(self) -> bool:
        """Property representing whether or not any form of crossbow is equipped.

        Returns:
            bool: True if any crossbow is equiped, otherwise False.
        """
        return self._is_crossbow(self.weapon)

    @property
    def arclight(self) -> bool:
        """Property representing whether or not an arclight Special Weapon is equipped.

        Returns:
            bool: True if wielding, else False.
        """
        return self.wearing(weapon=SpecialWeapon.from_bb("arclight"))

    @property
    def dragonbane_weapon(self) -> bool:
        """Property representing whether a dragonbane weapon is equipped.

        There are currently two dragonbane weapons in the game: Dragon Hunter Crossbow &
        Dragon Hunter Lance. Returns True if either of these are equipped, else False.

        Returns:
            bool:
        """
        qualifying_weapons = (
            Weapon.from_bb("dragon hunter crossbow"),
            Weapon.from_bb("dragon hunter lance"),
        )
        return self.weapon in qualifying_weapons

    @property
    def salve(self) -> bool:
        """Property representing whether any form of salve amulet is equipped.

        Returns:
            bool:
        """
        qualifying_items = (
            Gear.from_bb("salve amulet (i)"),
            Gear.from_bb("salve amulet (ei)"),
        )
        return self.neck in qualifying_items

    @property
    def slayer(self) -> bool:
        """Property representing whether the black mask / slayer helm effect is active.

        # TODO: Implement black mask

        Returns:
            bool:
        """
        return self.wearing(head=Gear.from_bb("slayer helmet (i)"))

    @property
    def wilderness_weapon(self) -> bool:
        """Property representing whether the equipped weapon is one of the wilderness weapons.

        Currently, there are three wilderness weapons: Viggora's chain mace, Craw's bow, and
        Thammaron's sceptre.

        Returns:
            bool:
        """
        qualifying_weapons = (
            Weapon.from_bb("craw's bow"),
            Weapon.from_bb("viggora's chainmace"),
            Weapon.from_bb("thammaron's sceptre"),
        )
        return self.weapon in qualifying_weapons

    @property
    def twisted_bow(self) -> bool:
        return self.wearing(weapon=Weapon.from_bb("twisted bow"))

    @property
    def berserker_necklace(self) -> bool:
        return self.wearing(neck=Gear.from_bb("berserker necklace"))

    @property
    def chaos_gauntlets(self) -> bool:
        return self.wearing(hands=Gear.from_bb("chaos gauntlets"))

    @property
    def pickaxe(self) -> bool:
        """Returns true if the player is wielding a pickaxe.

        Returns:
            bool: _description_
        """
        try:
            assert isinstance(self.weapon, Weapon)
            return "pickaxe" in self.weapon.name
        except AssertionError:
            return False

    @property
    def abyssal_dagger(self) -> bool:
        qualifying_weapons = (SpecialWeapon.from_bb("abyssal dagger"),)
        return self.weapon in qualifying_weapons

    @property
    def dragon_dagger(self) -> bool:
        qualifying_weapons = (SpecialWeapon.from_bb("dragon dagger"),)
        return self.weapon in qualifying_weapons

    @property
    def seercull(self) -> bool:
        return self.wearing(weapon=SpecialWeapon.from_bb("seercull"))

    @property
    def dwh(self) -> bool:
        return self.weapon == SpecialWeapon.from_bb("dragon warhammer")

    # Ammunition / Bolts

    @property
    def enchanted_opal_bolts(self) -> bool:
        return NotImplemented

    @property
    def enchanted_jade_bolts(self) -> bool:
        return NotImplemented

    @property
    def enchanted_pearl_bolts(self) -> bool:
        return NotImplemented

    @property
    def enchanted_topaz_bolts(self) -> bool:
        return NotImplemented

    @property
    def enchanted_sapphire_bolts(self) -> bool:
        return NotImplemented

    @property
    def enchanted_emerald_bolts(self) -> bool:
        return NotImplemented

    @property
    def enchanted_ruby_bolts(self) -> bool:
        """Property representing whether or not any form of enchanted ruby bolts are equipped.

        Returns:
            bool: True if the equipped ammunition is either Ruby Dragon Bolts (e) or Ruby Bolts (e)
        """
        matching_ammunition = [
            Gear.from_bb("ruby dragon bolts (e)"),
            Gear.from_bb("ruby bolts (e)"),
        ]

        return self.ammunition in matching_ammunition

    @property
    def enchanted_diamond_bolts(self) -> bool:
        """Property representing whether or not any form of enchanted diamond bolts are equipped.

        Returns:
            bool: True if the equipped ammunition is either Diamond Dragon Bolts (e) or Diamond Bolts (e)
        """
        matching_ammunition = [
            Gear.from_bb("diamond dragon bolts (e)"),
            Gear.from_bb("diamond bolts (e)"),
        ]

        return self.ammunition in matching_ammunition

    @property
    def enchanted_dragonstone_bolts(self) -> bool:
        """Property representing whether or not any form of enchanted dragonstone bolts are equipped.

        Returns:
            bool: True if the equipped ammunition is either Dragonstone Dragon Bolts (e) or Dragonstone Bolts (e)
        """
        matching_ammunition = [
            Gear.from_bb("dragonstone dragon bolts (e)"),
            Gear.from_bb("dragonstone bolts (e)"),
        ]

        return self.ammunition in matching_ammunition

    @property
    def enchanted_onyx_bolts(self) -> bool:
        """Property representing whether or not any form of enchanted onyx bolts are equipped.

        Returns:
            bool: True if the equipped ammunition is either Onyx Dragon Bolts (e) or Onyx Bolts (e)
        """
        matching_ammunition = [
            Gear.from_bb("onyx dragon bolts (e)"),
            Gear.from_bb("onyx bolts (e)"),
        ]

        return self.ammunition in matching_ammunition

    @property
    def enchanted_bolts_equipped(self) -> bool:
        """Property representing whether or not any form of enchanted bolts are equipped.

        This generic property implements all of the ammunition / bolt properties and removes properties which return
        NotImplemented. Use in conjunction with specific properties to simplify decision trees in other modules.

        Returns:
            bool: True if any enchanted bolts are equipped, False otherwise.
        """
        properties = [
            self.enchanted_opal_bolts,
            self.enchanted_jade_bolts,
            self.enchanted_pearl_bolts,
            self.enchanted_topaz_bolts,
            self.enchanted_sapphire_bolts,
            self.enchanted_emerald_bolts,
            self.enchanted_ruby_bolts,
            self.enchanted_diamond_bolts,
            self.enchanted_dragonstone_bolts,
            self.enchanted_onyx_bolts,
        ]
        # Filter out NotImplemented properties
        implemented_properties = tuple(p for p in properties if isinstance(p, bool))
        return any(implemented_properties)

    # Equipment helpers

    def equip_basic_melee_gear(
        self,
        torture: bool = True,
        primordial: bool = True,
        infernal: bool = True,
        ferocious: bool = True,
        berserker: bool = True,
        brimstone: bool = False,
    ) -> Self:
        gear_options = [
            Gear.from_bb("amulet of torture"),
            Gear.from_bb("primordial boots"),
            Gear.from_bb("infernal cape"),
            Gear.from_bb("ferocious gloves"),
        ]
        gear_bools = [torture, primordial, infernal, ferocious]
        gear = [g for g, b in zip(gear_options, gear_bools) if b]

        # sus ordering again with the rings
        if brimstone:
            ring = Gear.from_bb("brimstone ring")
            gear.append(ring)
        elif berserker:
            ring = Gear.from_bb("berserker (i)")
            gear.append(ring)

        self.equip(*gear)
        return self

    def equip_basic_ranged_gear(
        self,
        avas: bool = True,
        anguish: bool = True,
        pegasian: bool = True,
        brimstone: bool = True,
        archers: bool = False,
    ) -> Self:
        gear_options = (
            Gear.from_bb("ava's assembler"),
            Gear.from_bb("necklace of anguish"),
            Gear.from_bb("pegasian boots"),
        )
        gear_bools = (avas, anguish, pegasian)
        gear = [g for g, b in zip(gear_options, gear_bools) if b]

        # sus ordering again with the rings
        if archers:
            ring = Gear.from_bb("archers (i)")
            gear.append(ring)
        elif brimstone:
            ring = Gear.from_bb("brimstone ring")
            gear.append(ring)

        self.equip(*gear)
        return self

    def equip_basic_magic_gear(
        self,
        ancestral_set: bool = True,
        god_cape: bool = True,
        occult: bool = True,
        arcane: bool = True,
        tormented: bool = True,
        eternal: bool = True,
        brimstone: bool = True,
        seers: bool = False,
    ) -> Self:
        if ancestral_set:
            self.equip_ancestral_set()

        gear_options = (
            Gear.from_bb("god cape (i)"),
            Gear.from_bb("occult necklace"),
            Gear.from_bb("arcane spirit shield"),
            Gear.from_bb("tormented bracelet"),
            Gear.from_bb("eternal boots"),
        )
        gear_bools = (god_cape, occult, arcane, tormented, eternal)
        gear = [g for g, b in zip(gear_options, gear_bools) if b]

        # sus ordering again with the rings
        if seers:
            ring = Gear.from_bb("seers (i)")
            gear.append(ring)
        elif brimstone:
            ring = Gear.from_bb("brimstone ring")
            gear.append(ring)

        self.equip(*gear)
        return self

    def equip_void_set(self, elite: bool = True) -> Self:
        """Equip an entire void set, either elite (default) or normal.

        Arguments
        ---------
            elite (bool, optional): If True, equip elite void components
            instead of normal ones. Defaults to True.
        """
        # TODO: Specific void items per style (with osrsbox-db implementation)
        # TODO: and provide parameter support.
        void_gear_names = ["void knight helm", "void knight gloves"]

        if elite:
            specific_void_gear_names = ["elite void top", "elite void robe"]
        else:
            specific_void_gear_names = ["void knight top", "void knight robe"]

        void_gear_names.extend(specific_void_gear_names)
        gear = [Gear.from_bb(name) for name in void_gear_names]
        self.equip(*gear)
        return self

    def equip_slayer_helm(self, imbued: bool = True) -> Self:
        if imbued is False:
            raise NotImplementedError

        self.equip(Gear.from_bb("slayer helmet (i)"))

        return self

    def equip_salve(self, e: bool = True, i: bool = True) -> Self:
        if e and i:
            self.equip(Gear.from_bb("salve amulet (ei)"))
        elif i:
            self.equip(Gear.from_bb("salve amulet (i)"))
        else:
            raise NotImplementedError

        return self

    def equip_fury(self, blood: bool = False) -> Self:
        fury = (
            Gear.from_bb("amulet of blood fury")
            if blood
            else Gear.from_bb("amulet of fury")
        )
        self.equip(fury)

        return self

    # melee gear helpers

    def equip_bandos_set(self) -> Self:
        self.equip(
            Gear.from_bb("neitiznot faceguard"),
            Gear.from_bb("bandos chestplate"),
            Gear.from_bb("bandos tassets"),
        )

        return self

    def equip_inquisitor_set(self) -> Self:
        self.equip(
            Gear.from_bb("inquisitor's great helm"),
            Gear.from_bb("inquisitor's hauberk"),
            Gear.from_bb("inquisitor's plateskirt"),
        )

        return self

    def equip_torva_set(self) -> Self:
        self.equip(
            Gear.from_bb("torva full helm"),
            Gear.from_bb("torva platebody"),
            Gear.from_bb("torva platelegs"),
        )

        return self

    def equip_justi_set(self) -> Self:
        self.equip(
            Gear.from_bb("justiciar faceguard"),
            Gear.from_bb("justiciar chestguard"),
            Gear.from_bb("justiciar legguard"),
        )

        return self

    def equip_dwh(
        self,
        *,
        inquisitor_set: bool = False,
        avernic: bool = True,
        brimstone: bool = True,
        tyrannical: bool = False,
    ) -> Self:

        if inquisitor_set:
            self.equip_inquisitor_set()

        gear: list[Gear] = [SpecialWeapon.from_bb("dragon warhammer")]

        if avernic:
            gear.append(Gear.from_bb("avernic defender"))

        # ordering a little sus here ngl
        if tyrannical:
            gear.append(Gear.from_bb("tyrannical (i)"))
        elif brimstone:
            gear.append(Gear.from_bb("brimstone ring"))

        return self.equip(*gear)

    def equip_bgs(self, berserker: bool = False) -> Self:
        gear: list[Gear] = [SpecialWeapon.from_bb("bandos godsword")]

        if berserker:
            gear.append(Gear.from_bb("berserker (i)"))

        return self.equip(*gear)

    def equip_scythe(self, berserker: bool = False) -> Self:
        gear: list[Gear] = [Weapon.from_bb("scythe of vitur")]

        if berserker:
            gear.append(Gear.from_bb("berserker (i)"))

        return self.equip(*gear)

    def equip_lance(self, avernic: bool = True, berserker: bool = False) -> Self:
        gear_bools = [avernic, berserker]
        gear_options = [
            Gear.from_bb("avernic defender"),
            Gear.from_bb("berserker (i)"),
        ]

        gear = [g for g, b in zip(gear_options, gear_bools) if b]
        gear.append(Weapon.from_bb("dragon hunter lance"))

        return self.equip(*gear)

    def equip_dragon_pickaxe(
        self, avernic: bool = True, berserker: bool = False
    ) -> Self:
        gear_bools = [avernic, berserker]
        gear_options = [Gear.from_bb("avernic defender"), Gear.from_bb("berserker (i)")]

        gear = [g for g, b in zip(gear_options, gear_bools) if b]
        gear.append(SpecialWeapon.from_bb("dragon pickaxe"))

        return self.equip(*gear)

    def equip_arclight(self) -> Self:
        self.weapon = SpecialWeapon.from_bb("arclight")
        return self

    def equip_dinhs(self) -> Self:
        self.weapon = SpecialWeapon.from_bb("dinh's bulwark")
        return self

    def equip_sotd(self) -> Self:
        self.weapon = SpecialWeapon.from_bb("staff of the dead")
        return self

    # ranged gear helpers

    def equip_arma_set(self, zaryte: bool = False, barrows: bool = False) -> Self:
        gear: list[Gear] = [
            Gear.from_bb("armadyl helmet"),
            Gear.from_bb("armadyl chestplate"),
            Gear.from_bb("armadyl chainskirt"),
        ]

        if zaryte:
            gear.append(Gear.from_bb("zaryte vambraces"))
        elif barrows:
            gear.append(Gear.from_bb("barrows gloves"))

        return self.equip(*gear)

    def equip_god_dhide(self) -> Self:
        gear: list[Gear] = [
            Gear.from_bb("god coif"),
            Gear.from_bb("god d'hide body"),
            Gear.from_bb("god d'hide chaps"),
            Gear.from_bb("god bracers"),
            Gear.from_bb("blessed d'hide boots"),
        ]

        return self.equip(*gear)

    def equip_crystal_set(self, zaryte: bool = False, barrows: bool = False) -> Self:
        gear: list[Gear] = [
            Gear.from_bb("crystal helm"),
            Gear.from_bb("crystal body"),
            Gear.from_bb("crystal legs"),
        ]

        if zaryte:
            gear.append(Gear.from_bb("zaryte vambraces"))
        elif barrows:
            gear.append(Gear.from_bb("barrows gloves"))

        return self.equip(*gear)

    def equip_twisted_bow(self, dragon_arrows: bool = True) -> Self:
        gear: list[Gear] = [Weapon.from_bb("twisted bow")]

        if dragon_arrows:
            gear.append(Gear.from_bb("dragon arrow"))

        return self.equip(*gear)

    def equip_blowpipe(self, dragon_darts: bool = True) -> Self:
        gear: list[Gear] = [SpecialWeapon.from_bb("toxic blowpipe")]

        if dragon_darts:
            gear.append(Gear.from_bb("dragon darts"))

        return self.equip(*gear)

    def equip_chins(
        self,
        buckler: bool = True,
        black: bool = False,
        red: bool = False,
        grey: bool = False,
    ) -> Self:

        chin_name = None
        if black:
            chin_name = "black chinchompa"
        elif red:
            chin_name = "red chinchompa"
        elif grey:
            chin_name = "grey chinchompa"
        else:
            raise AssertionError("no chins bruh")

        gear: list[Gear] = [Weapon.from_bb(chin_name)]

        if buckler:
            gear.append(Gear.from_bb("twisted buckler"))

        return self.equip(*gear)

    def equip_crossbow(
        self,
        crossbow: Weapon,
        buckler: bool = False,
        rubies: bool = False,
        diamonds: bool = False,
        ammunition: Gear | None = None,
    ) -> Self:
        """Equip any crossbow with options for the most common ammo.

        Parameters
        ----------
        crossbow : Weapon
            A crossbow Weapon.
        buckler : bool
            Set to True to equip a twisted buckler.
        rubies : bool, optional
            Set to True to equip ruby bolts, by default False
        diamonds : bool, optional
            Set to True to equip diamond bolts, by default False
        ammunition : Gear | None, optional
            Provide your own ammunition, by default None.

        Returns
        -------
        Self
        """
        assert self._is_crossbow(crossbow)
        gear: list[Gear] = [crossbow]

        if buckler:
            gear.append(Gear.from_bb("twisted buckler"))

        if rubies:
            ammo_name = "ruby dragon bolts (e)"
            gear.append(Gear.from_bb(ammo_name))
        elif diamonds:
            ammo_name = "diamond dragon bolts (e)"
            gear.append(Gear.from_bb(ammo_name))
        else:
            assert ammunition is not None
            assert ammunition.slot is Slots.AMMUNITION
            gear.append(ammunition)

        self.equip(*gear)
        return self

    def equip_zaryte_crossbow(
        self, buckler: bool = True, rubies: bool = False, diamonds: bool = False
    ) -> Self:
        raise DeprecationWarning

    def equip_dorgeshuun_crossbow(self, buckler: bool = True) -> Self:
        wpn = SpecialWeapon.from_bb("dorgeshuun crossbow")
        ammo = Gear.from_bb("bone bolts")

        return self.equip_crossbow(wpn, buckler=buckler, ammunition=ammo)

    def equip_crystal_bowfa(self, crystal_set: bool = True) -> Self:
        if crystal_set:
            self.equip_crystal_set()

        self.weapon = Weapon.from_bb("bow of faerdhinen")

        return self

    def equip_seercull(self, amethyst: bool = True) -> Self:
        gear: list[Gear] = [SpecialWeapon.from_bb("seercull")]

        if amethyst:
            gear.append(Gear.from_bb("amethyst arrow"))

        return self.equip(*gear)

    # magic gear helpers

    def equip_ancestral_set(self) -> Self:
        gear: list[Gear] = [
            Gear.from_bb("ancestral hat"),
            Gear.from_bb("ancestral robe top"),
            Gear.from_bb("ancestral robe bottoms"),
        ]

        return self.equip(*gear)

    def equip_sang(self, arcane: bool = False) -> Self:
        gear: list[Gear] = [Weapon.from_bb("sanguinesti staff")]

        if arcane:
            gear.append(Gear.from_bb("arcane spirit shield"))

        return self.equip(*gear)

    def equip_harm(self, tome: bool = True) -> Self:
        gear: list[Gear] = [Weapon.from_bb("harmonised staff")]

        if tome:
            gear.append(Gear.from_bb("tome of fire"))

        return self.equip(*gear)
