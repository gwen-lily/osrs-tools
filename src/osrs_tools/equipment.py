from __future__ import annotations

from enum import Enum, unique
from functools import reduce

import pandas as pd
from attrs import astuple, define, field, validators
from osrsbox import items_api
from osrsbox.items_api.item_properties import ItemEquipment, ItemProperties, ItemWeapon

import osrs_tools.resource_reader as rr
from osrs_tools.exceptions import OsrsException
from osrs_tools.modifier import (
    DT,
    AttackRollModifier,
    DamageModifier,
    Level,
    Stances,
    Styles,
)
from osrs_tools.stats import (
    AggressiveStats,
    DefensiveStats,
    MonsterLevels,
    PlayerLevels,
)

# TODO: submodule for style imports
from osrs_tools.style import (
    AxesStyles,
    BladedStaffStyles,
    BludgeonStyles,
    BluntStyles,
    BowStyles,
    BulwarkStyles,
    ChinchompaStyles,
    ClawStyles,
    CrossbowStyles,
    PickaxeStyles,
    PlayerStyle,
    PolearmStyles,
    PoweredStaffStyles,
    ScytheStyles,
    SlashSwordStyles,
    SpearStyles,
    SpikedWeaponsStyles,
    StabSwordStyles,
    StaffStyles,
    Style,
    StyleError,
    StylesCollection,
    ThrownStyles,
    TwoHandedStyles,
    UnarmedStyles,
    WhipStyles,
)


class GearError(OsrsException):
    pass


class EquipableError(GearError):
    def __init__(self, message: str):
        super().__init__(message)


class GearNotFoundError(GearError):
    def __init__(self, gear_name: str = None):  # type: ignore
        self.message = (
            f"Item not found by name lookup: {gear_name=}" if gear_name else None
        )


class DuplicateGearError(GearError):
    def __init__(self, search_term: str = None, *matching_names: str):  # type: ignore
        if search_term and len(matching_names) > 0:
            self.message = f"{search_term=} yielded: " + ", ".join(matching_names)
        else:
            self.message = None


class WeaponError(GearError):
    pass


@unique
class Slots(Enum):
    head = "head"
    cape = "cape"
    neck = "neck"
    ammunition = "ammunition"
    weapon = "weapon"
    shield = "shield"
    body = "body"
    legs = "legs"
    hands = "hands"
    feet = "feet"
    ring = "ring"


Items = items_api.load()


def special_defence_roll_validator(instance: SpecialWeapon, attribute: str, value: DT):
    if value and value not in DT:
        raise WeaponError(f"{attribute=} with {value=} not in {DT}")


def lookup_gear_base_attributes_by_name(name: str, gear_df: pd.DataFrame = None):
    item_df = rr.lookup_gear(name, gear_df)

    if len(item_df) > 1:
        matching_names = tuple(item_df["name"].values)
        raise DuplicateGearError(name, *matching_names)
    elif len(item_df) == 0:
        raise GearNotFoundError(name)

    name = item_df["name"].values[0]

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
        mining=Level(item_df["mining level req"].values[0])
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


def lookup_weapon_attributes_by_name(name: str, gear_df: pd.DataFrame = None):
    item_df = rr.lookup_gear(name, gear_df)
    default_attack_range = 0
    comment = "bitter"

    if len(item_df) > 1:
        matching_names = tuple(item_df["name"].values)
        raise DuplicateGearError(name, *matching_names)
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
        special_accuracy_modifiers.append(AttackRollModifier(1 + raw_sarm, comment))
    if (raw_sdm1 := item_df["special damage 1"].values[0]) != 0:
        special_damage_modifiers.append(DamageModifier(1 + raw_sdm1, comment))
    if (raw_sdm2 := item_df["special damage 2"].values[0]) != 0:
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


@define(order=True, frozen=True)
class Gear:
    name: str
    slot: Slots = field(validator=validators.instance_of(Slots))
    aggressive_bonus: AggressiveStats = field(
        validator=validators.instance_of(AggressiveStats), repr=False
    )
    defensive_bonus: DefensiveStats = field(
        validator=validators.instance_of(DefensiveStats), repr=False
    )
    prayer_bonus: int = field(repr=False)
    level_requirements: PlayerLevels = field(
        validator=validators.instance_of(PlayerLevels), repr=False
    )

    def __str__(self):
        s = f"{self.__class__.__name__}({self.name!s})"
        return s

    def __repr__(self):
        return str(self)

    @classmethod
    def from_bb(cls, name: str):
        (
            name,
            slot,
            aggressive_bonus,
            defensive_bonus,
            prayer_bonus,
            level_requirements,
        ) = lookup_gear_base_attributes_by_name(name)

        return cls(
            name=name,
            slot=slot,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            prayer_bonus=prayer_bonus,
            level_requirements=level_requirements,
        )

    @classmethod
    def from_osrsbox(cls, name: str = None, item_id: int = None, **kwargs):

        if name:
            item = Items.lookup_by_item_name(name)
        elif item_id:
            item = Items.lookup_by_item_id(item_id)
        else:
            raise GearNotFoundError(f"{kwargs=}")

        if not item.equipable_by_player:
            raise EquipableError("attempt to create false gear")

        eqp = item.equipment
        name = item.name.lower()
        slot = None

        # slot validation & weapon / 2h validation
        for sl in Slots:
            # specific cases > general
            if eqp.slot == "ammo":
                slot = Slots.ammunition
            elif eqp.slot == "2h" or eqp.slot == Slots.weapon.name:
                raise WeaponError("Instance of weapon in Gear class.")
            elif eqp.slot == sl.name:
                slot = sl

        if slot is None:
            raise GearError(f"{eqp.slot}")

        ab = AggressiveStats(
            stab=eqp.attack_stab,
            slash=eqp.attack_slash,
            crush=eqp.attack_crush,
            magic_attack=eqp.attack_magic,
            ranged_attack=eqp.attack_ranged,
            melee_strength=eqp.melee_strength,
            ranged_strength=eqp.ranged_strength,
            magic_strength=eqp.magic_damage / 100,
        )
        db = DefensiveStats(
            stab=eqp.defence_stab,
            slash=eqp.defence_slash,
            crush=eqp.defence_crush,
            magic=eqp.defence_magic,
            ranged=eqp.defence_ranged,
        )
        pb = eqp.prayer

        if eqp.requirements is not None:
            combat_key = "combat"
            if combat_key in eqp.requirements:
                eqp.requirements.pop(combat_key)

            reqs = PlayerLevels(**{k: Level(v) for k, v in eqp.requirements.items()})
        else:
            reqs = PlayerLevels.no_requirements()

        return cls(name, slot, ab, db, pb, reqs)

    def empty_slot(cls, slot: str):
        return


class SpecialWeaponError(WeaponError):
    def __init__(self, gear: Gear):
        self.message = f"{gear=} {isinstance(gear, SpecialWeapon)=}"


class EquipmentError(OsrsException):
    pass


class TwoHandedError(EquipmentError):
    pass


# noinspection PyArgumentList
@define(order=True, frozen=True)
class Weapon(Gear):
    name: str
    slot: Slots = field(repr=False)
    aggressive_bonus: AggressiveStats = field(
        validator=validators.instance_of(AggressiveStats), repr=False
    )
    defensive_bonus: DefensiveStats = field(
        validator=validators.instance_of(DefensiveStats), repr=False
    )
    prayer_bonus: int = field(repr=False)
    level_requirements: PlayerLevels = field(
        validator=validators.instance_of(PlayerLevels), repr=False
    )
    styles_coll: StylesCollection = field(
        validator=validators.instance_of(StylesCollection)
    )
    attack_speed: int
    two_handed: bool = field(repr=False)

    @classmethod
    def empty_slot(cls):
        slot = Slots.weapon
        return cls(
            name="empty " + slot.name,
            slot=slot,
            aggressive_bonus=AggressiveStats.no_bonus(),
            defensive_bonus=DefensiveStats.no_bonus(),
            prayer_bonus=0,
            level_requirements=PlayerLevels.no_requirements(),
            styles_coll=UnarmedStyles,
            attack_speed=4,
            two_handed=False,
        )

    @classmethod
    def from_bb(cls, name: str):
        (
            name,
            slot,
            aggressive_bonus,
            defensive_bonus,
            prayer_bonus,
            level_requirements,
        ) = lookup_gear_base_attributes_by_name(name)
        (
            attack_speed,
            attack_range,
            two_handed,
            weapon_styles,
            _,
            _,
            _,
        ) = lookup_weapon_attributes_by_name(name)

        if not slot is Slots.weapon:
            raise WeaponError(slot)

        return cls(
            name=name,
            slot=slot,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            prayer_bonus=prayer_bonus,
            level_requirements=level_requirements,
            styles_coll=weapon_styles,
            attack_speed=attack_speed,
            two_handed=two_handed,
        )


@define(order=True, frozen=True)
class SpecialWeapon(Weapon):
    special_attack_roll_modifiers: list[AttackRollModifier] = field(
        factory=list, repr=False
    )
    special_damage_modifiers: list[DamageModifier] = field(factory=list, repr=False)
    special_defence_roll: DT | None = field(default=None, repr=False)

    @classmethod
    def from_bb(cls, name: str):
        (
            name,
            slot,
            aggressive_bonus,
            defensive_bonus,
            prayer_bonus,
            level_requirements,
        ) = lookup_gear_base_attributes_by_name(name)
        (
            attack_speed,
            attack_range,
            two_handed,
            weapon_styles,
            spec_arm_mods,
            spec_dmg_mods,
            sdr,
        ) = lookup_weapon_attributes_by_name(name)

        if not slot is Slots.weapon:
            raise WeaponError(slot)

        return cls(
            name=name,
            slot=slot,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            prayer_bonus=prayer_bonus,
            level_requirements=level_requirements,
            styles_coll=weapon_styles,
            attack_speed=attack_speed,
            two_handed=two_handed,
            special_attack_roll_modifiers=spec_arm_mods,
            special_damage_modifiers=spec_dmg_mods,
            special_defence_roll=sdr,
        )

    @classmethod
    def empty_slot(cls, slot: str = None):
        raise WeaponError(f"Attempt to create empty special weapon")


def equipment_weapon_validator(instance: Equipment, attribute: str, value: Weapon):
    if value is not None:
        if not isinstance(value, Weapon):
            raise WeaponError(f"Equipment.weapon was initialized as {value.__class__=}")

        if value.two_handed and instance.shield is not None:
            raise TwoHandedError(f"{value.name} equipped with {instance.shield.name}")


def equipment_shield_validator(instance: Equipment, attribute: str, value: Gear):
    if instance.weapon is not None and instance.weapon.two_handed and value is not None:
        raise TwoHandedError(f"{value.name} equipped with {instance.weapon.name}")


@define(order=True)
class Equipment:
    """
    The Equipment class has attributes for each piece of Gear a player can use as well as methods to query and change
    the gear.
    """

    head: Gear | None = None
    cape: Gear | None = None
    neck: Gear | None = None
    ammunition: Gear | None = None
    weapon: Weapon | None = field(validator=equipment_weapon_validator, default=None)
    shield: Gear | None = field(validator=equipment_shield_validator, default=None)
    body: Gear | None = None
    legs: Gear | None = None
    hands: Gear | None = None
    feet: Gear | None = None
    ring: Gear | None = None
    set_name: str | None = None

    # Basic properties and methods for manipulating Equipment objects ######################################################
    @property
    def aggressive_bonus(self) -> AggressiveStats:
        # Notably does not account for Dinh's strength bonus, which is handled via Player._dinhs_modifier()
        val = sum(g.aggressive_bonus for g in self.equipped_gear)

        if isinstance(val, int) and val == 0:
            return AggressiveStats.no_bonus()

        return val

    @property
    def defensive_bonus(self) -> DefensiveStats:
        val = sum(g.defensive_bonus for g in self.equipped_gear)

        if isinstance(val, int) and val == 0:
            return DefensiveStats.no_bonus()

        return val

    @property
    def prayer_bonus(self) -> int:
        return sum(g.prayer_bonus for g in self.equipped_gear)

    @property
    def level_requirements(self) -> PlayerLevels:
        # PlayerLevels.__mul__(self, other) handles the behavior of aggregating level requirements.
        individual_level_reqs = [g.level_requirements for g in self.equipped_gear]

        if len(individual_level_reqs) != 0:
            comb_reqs = reduce(
                lambda x, y: x.max_levels_per_skill(y), individual_level_reqs
            )
            return comb_reqs
        else:
            return PlayerLevels.no_requirements()

    @property
    def equipped_gear(self) -> list[Gear]:
        return [g for g in astuple(self, recurse=False) if isinstance(g, Gear)]

    def equip(self, *gear: Gear, style: PlayerStyle = None) -> PlayerStyle | None:  # type: ignore
        weapon_style = style if style is not None else None

        for g in gear:
            if self.__getattribute__(g.slot.name) == g:
                continue
            else:
                if isinstance(g, Weapon):
                    weapon_style = style if style is not None else g.styles_coll.default

                    if weapon_style not in g.styles_coll.styles:
                        raise StyleError(str(weapon_style))

                    try:
                        self.weapon = g
                    except TwoHandedError:
                        self.shield = None
                        self.weapon = g

                else:
                    try:
                        self.__setattr__(g.slot.name, g)
                    except TwoHandedError:
                        assert g.slot is Slots.shield
                        self.weapon = Weapon.empty_slot()
                        self.shield = g

        if weapon_style is not None:
            assert isinstance(weapon_style, PlayerStyle)
            return weapon_style

    def unequip(self, *slots: Slots, style: PlayerStyle = None) -> PlayerStyle | None:  # type: ignore
        return_style = None

        for slot in slots:
            if slot is Slots.weapon:
                return_style = style if style else UnarmedStyles.default
                assert isinstance(return_style, PlayerStyle)
                self.weapon = Weapon.empty_slot()
            else:
                self.__setattr__(slot.name, None)

        if return_style is not None:
            assert isinstance(return_style, PlayerStyle)
            return return_style

    def wearing(self, *args, **kwargs) -> bool:
        m = len(args)
        n = len(kwargs)
        if m == 0 and n == 0:
            raise EquipmentError(f"Equipment.wearing call with no *args or **kwargs")

        if m > 0:
            if any(self.__getattribute__(g.slot.name) != g for g in args):
                return False

        if n > 0:
            if any(self.__getattribute__(k) != v for k, v in kwargs.items()):
                return False

        return True

    def __add__(self, other: Gear | Equipment) -> Equipment:
        """
        Directional addition, right-hand operand has priority except in the
        case of empty slots.

        :param other:
        :return:
        """
        if isinstance(other, Equipment):
            self.equip(*other.equipped_gear)
        elif isinstance(other, Gear):
            self.equip(other)
        else:
            raise NotImplementedError

        return self

    def __sub__(self, other: Gear | Equipment) -> Equipment:
        """
        Directional subtraction, remove right-hand gear if and only if it
        exists in the left-hand set. Pass otherwise.

        :param other:
        :return:
        """
        if isinstance(other, Equipment):
            for gear in other.equipped_gear:
                if self.__getattribute__(gear.slot.name) == gear:
                    self.unequip(gear.slot)
        elif isinstance(other, Gear):
            if self.__getattribute__(other.slot.name) == other:
                self.unequip(other.slot)
        else:
            raise NotImplementedError

        return self

    def __str__(self):
        if self.set_name is None:
            message = f'{self.__class__.__name__}({", ".join([g.name for g in self.equipped_gear])})'
        else:
            message = f"{self.__class__.__name__}({self.set_name})"

        return message

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        return Equipment.from_gear(*self.equipped_gear)

    # class methods ########################################################################################################

    @classmethod
    def from_gear(cls, *gear: Gear):
        eqp = cls()
        eqp.equip(*gear)
        return eqp

    @classmethod
    def no_equipment(cls):
        return cls()

    # Wearing Properties ###################################################################################################
    def full_set_method(self, requires_ammo: bool = None) -> bool:  # type: ignore
        """Property which returns True if the Equipment slots are fulfilled as needed to perform attacks.

        # TODO: implement osrsbox-db wrapper which eliminates the need for assume_2h parameter.

        Args:
            requires_ammo (bool, optional): If True, requires Ammunition to be equipped even for styles which don't make use
             of it. Defaults to None.
            assume_2h (bool, optional): If True, requires the Equipment.shield slot to be empty. Defaults to True.

        Returns:
            bool: True
        """
        assert isinstance(self.weapon, Weapon)

        if requires_ammo is None:
            if self.weapon.styles_coll in [BowStyles, CrossbowStyles, ThrownStyles]:
                requires_ammo = True
            else:
                requires_ammo = False

        if requires_ammo and self.ammunition is None:
            return False

        if not self.weapon.two_handed and self.shield is None:
            return False

        for slot in Slots:
            if slot is Slots.ammunition or slot is Slots.shield:
                continue
            elif slot is Slots.weapon:
                if self.weapon == Weapon.empty_slot():
                    return False

            else:
                if self.__getattribute__(slot.name) is None:
                    return False

        return True

    @property
    def full_set(self) -> bool:
        return self.full_set_method()

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

    @property
    def crossbow(self) -> bool:
        """Property representing whether or not any form of crossbow is equipped.

        This generic property checks a few obvious values to ensure that other modules can interact with Crossbows simply.

        Returns:
            bool: True if any crossbow is equiped, otherwise False.
        """
        # use names because crossbows may be SpecialWeapon or Weapon.
        # TODO: Re-assess whether using name search is still valid.
        try:
            assert isinstance(self.weapon, Weapon)
            return (
                "crossbow" in self.weapon.name
                and self.weapon.styles_coll == CrossbowStyles
            )
        except AssertionError:
            return False

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

    # Ammunition / Bolts ###################################################################################################

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

    ########################################################################################################################
    # Equipment helpers ####################################################################################################
    ########################################################################################################################

    def equip_basic_melee_gear(
        self,
        torture: bool = True,
        primordial: bool = True,
        infernal: bool = True,
        ferocious: bool = True,
        berserker: bool = True,
        brimstone: bool = False,
    ):
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

    def equip_basic_ranged_gear(
        self,
        avas: bool = True,
        anguish: bool = True,
        pegasian: bool = True,
        brimstone: bool = True,
        archers: bool = False,
    ):
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
    ):
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

    def equip_void_set(self, elite: bool = True):
        """Equip an entire void set, either elite (default) or normal.

        # TODO: Specific void items per style (with osrsbox-db implementation) & provide parameter support.
        Args:
            elite (bool, optional): If True, equip elite void components instead of normal ones. Defaults to True.
        """
        void_gear_names = ["void knight helm", "void knight gloves"]

        if elite:
            specific_void_gear_names = ["elite void top", "elite void robe"]
        else:
            specific_void_gear_names = ["void knight top", "void knight robe"]

        void_gear_names.extend(specific_void_gear_names)
        gear = [Gear.from_bb(name) for name in void_gear_names]
        self.equip(*gear)

    def equip_slayer_helm(self, imbued: bool = True):
        if imbued is False:
            raise NotImplementedError

        self.equip(Gear.from_bb("slayer helmet (i)"))

    def equip_salve(self, e: bool = True, i: bool = True):
        if e and i:
            self.equip(Gear.from_bb("salve amulet (ei)"))
        elif i:
            self.equip(Gear.from_bb("salve amulet (i)"))
        else:
            raise NotImplementedError

    def equip_fury(self, blood: bool = False):
        fury = (
            Gear.from_bb("amulet of blood fury")
            if blood
            else Gear.from_bb("amulet of fury")
        )
        self.equip(fury)

    # melee gear helpers ###################################################################################################
    def equip_bandos_set(self):
        self.equip(
            Gear.from_bb("neitiznot faceguard"),
            Gear.from_bb("bandos chestplate"),
            Gear.from_bb("bandos tassets"),
        )

    def equip_inquisitor_set(self):
        self.equip(
            Gear.from_bb("inquisitor's great helm"),
            Gear.from_bb("inquisitor's hauberk"),
            Gear.from_bb("inquisitor's plateskirt"),
        )

    def equip_torva_set(self):
        self.equip(
            Gear.from_bb("torva full helm"),
            Gear.from_bb("torva platebody"),
            Gear.from_bb("torva platelegs"),
        )

    def equip_justi_set(self):
        self.equip(
            Gear.from_bb("justiciar faceguard"),
            Gear.from_bb("justiciar chestguard"),
            Gear.from_bb("justiciar legguard"),
        )

    def equip_dwh(
        self,
        *,
        inquisitor_set: bool = False,
        avernic: bool = True,
        brimstone: bool = True,
        tyrannical: bool = False,
        style: Style = None,  # type: ignore
    ) -> PlayerStyle:

        if inquisitor_set:
            self.equip_inquisitor_set()

        gear = []

        if avernic:
            gear.append(Gear.from_bb("avernic defender"))

        # ordering a little sus here ngl
        if tyrannical:
            gear.append(Gear.from_bb("tyrannical (i)"))
        elif brimstone:
            gear.append(Gear.from_bb("brimstone ring"))

        weapon_style = style if style is not None else BluntStyles.default
        assert isinstance(style, PlayerStyle)

        return_style = self.equip(
            SpecialWeapon.from_bb("dragon warhammer"), *gear, style=weapon_style
        )
        assert isinstance(return_style, PlayerStyle)
        return return_style

    def equip_bgs(self, style: PlayerStyle = None) -> PlayerStyle:  # type: ignore
        if style is not None:
            weapon_style = style
        elif self.inquisitor_set:
            weapon_style = TwoHandedStyles.get_by_style(Styles.SMASH)
        else:
            weapon_style = TwoHandedStyles.default

        assert isinstance(weapon_style, PlayerStyle)
        return_val = self.equip(
            SpecialWeapon.from_bb("bandos godsword"), style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_scythe(
        self, berserker: bool = False, style: PlayerStyle = None  # type: ignore
    ) -> PlayerStyle:

        if style is not None:
            weapon_style = style
        else:
            if self.inquisitor_set:
                weapon_style = ScytheStyles.get_by_style(Styles.JAB)
            else:
                weapon_style = ScytheStyles.default

        assert isinstance(weapon_style, PlayerStyle)
        gear = [Gear.from_bb("berserker (i)")] if berserker else []
        return_val = self.equip(
            Weapon.from_bb("scythe of vitur"), *gear, style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_lance(
        self, avernic: bool = True, berserker: bool = False, style: PlayerStyle = None  # type: ignore
    ) -> PlayerStyle:
        if style is not None:
            weapon_style = style
        elif self.inquisitor_set:
            weapon_style = SpearStyles.get_by_style(Styles.POUND)
        else:
            weapon_style = SpearStyles.default

        gear_options = (
            Gear.from_bb("avernic defender"),
            Gear.from_bb("berserker (i)"),
        )
        gear_bools = (avernic, berserker)
        gear = (g for g, b in zip(gear_options, gear_bools) if b)
        assert isinstance(weapon_style, PlayerStyle)
        return_val = self.equip(
            Weapon.from_bb("dragon hunter lance"), *gear, style=weapon_style
        )

        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_dragon_pickaxe(
        self, avernic: bool = True, berserker: bool = False, style: PlayerStyle = None  # type: ignore
    ) -> PlayerStyle:
        weapon_style = style if style is not None else PickaxeStyles.default
        assert isinstance(weapon_style, PlayerStyle)
        gear_options = [Gear.from_bb("avernic defender"), Gear.from_bb("berserker (i)")]
        gear_bools = (avernic, berserker)

        gear = (g for g, b in zip(gear_options, gear_bools) if b)
        return_val = self.equip(
            Weapon.from_bb("dragon pickaxe"), *gear, style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_arclight(self, style: PlayerStyle = None) -> PlayerStyle:  # type: ignore
        weapon_style = style if style is not None else SlashSwordStyles.default
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(SpecialWeapon.from_bb("arclight"), style=weapon_style)
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_dinhs(self, style: PlayerStyle = None) -> PlayerStyle:  # type: ignore
        weapon_style = BulwarkStyles.default if style is None else style
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(
            SpecialWeapon.from_bb("dinh's bulwark"), style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_sotd(self, style: PlayerStyle = None) -> PlayerStyle:  # type: ignore
        weapon_style = BladedStaffStyles.default if style is None else style
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(SpecialWeapon.from_bb("staff of the dead"), style=style)
        assert isinstance(return_val, PlayerStyle)
        return return_val

    # ranged gear helpers ##################################################################################################
    def equip_arma_set(self, zaryte: bool = False, barrows: bool = False):
        if zaryte:
            gear = (Gear.from_bb("zaryte vambraces"),)
        elif barrows:
            gear = (Gear.from_bb("barrows gloves"),)
        else:
            gear = tuple()

        self.equip(
            Gear.from_bb("armadyl helmet"),
            Gear.from_bb("armadyl chestplate"),
            Gear.from_bb("armadyl chainskirt"),
            *gear,
        )

    def equip_god_dhide(self):
        self.equip(
            Gear.from_bb("god coif"),
            Gear.from_bb("god d'hide body"),
            Gear.from_bb("god d'hide chaps"),
            Gear.from_bb("god bracers"),
            Gear.from_bb("blessed d'hide boots"),
        )

    def equip_crystal_set(self, zaryte: bool = False, barrows: bool = False):
        if zaryte:
            gear = (Gear.from_bb("zaryte vambraces"),)
        elif barrows:
            gear = (Gear.from_bb("barrows gloves"),)
        else:
            gear = tuple()

        self.equip(
            Gear.from_bb("crystal helm"),
            Gear.from_bb("crystal body"),
            Gear.from_bb("crystal legs"),
            *gear,
        )

    def equip_twisted_bow(
        self, dragon_arrows: bool = True, style: PlayerStyle = None  # type: ignore
    ) -> PlayerStyle:
        gear = [Gear.from_bb("dragon arrow")] if dragon_arrows else []
        weapon_style = style if style else BowStyles.default
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(
            Weapon.from_bb("twisted bow"), *gear, style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_blowpipe(
        self, dragon_darts: bool = True, style: PlayerStyle = None  # type: ignore
    ) -> PlayerStyle:
        gear = (
            [
                Gear.from_bb("dragon darts"),
            ]
            if dragon_darts
            else []
        )
        weapon_style = style if style else ThrownStyles.default
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(
            SpecialWeapon.from_bb("toxic blowpipe"), *gear, style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_black_chins(
        self, buckler: bool = True, style: PlayerStyle = None  # type: ignore
    ) -> PlayerStyle:
        """legacy function, see @equip_chins"""
        raise DeprecationWarning("Equipment.equip_chins")

    def equip_chins(
        self,
        buckler: bool = True,
        black: bool = False,
        red: bool = False,
        grey: bool = False,
        style: PlayerStyle = None,  # type: ignore
    ) -> PlayerStyle:
        chin_name = None
        if black:
            chin_name = "black chinchompa"
        elif red:
            chin_name = "red chinchompa"
        elif grey:
            chin_name = "grey chinchompa"
        else:
            raise WeaponError(f"no chins bruh")

        chins = Weapon.from_bb(chin_name)
        gear = (Gear.from_bb("twisted buckler"),) if buckler else tuple()
        weapon_style = style if style else ChinchompaStyles.default
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(chins, *gear, style=weapon_style)
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_zaryte_crossbow(
        self,
        buckler: bool = True,
        rubies: bool = False,
        diamonds: bool = False,
        style: PlayerStyle = None,  # type: ignore
    ) -> PlayerStyle:
        gear = []

        if rubies:
            gear.append(Gear.from_bb("ruby dragon bolts (e)"))
        elif diamonds:
            gear.append(Gear.from_bb("diamond dragon bolts (e)"))

        if buckler:
            gear.append(Gear.from_bb("twisted buckler"))

        weapon_style = style if style else CrossbowStyles.default
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(
            SpecialWeapon.from_bb("zaryte crossbow"),
            *gear,
            style=weapon_style,
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_dorgeshuun_crossbow(
        self, buckler: bool = True, bone_bolts: bool = True, style: PlayerStyle = None  # type: ignore
    ) -> PlayerStyle:
        if style is not None:
            weapon_style = style
        else:
            weapon_style = CrossbowStyles.get_by_style(Styles.ACCURATE)

        assert isinstance(weapon_style, PlayerStyle)

        gear_options = (Gear.from_bb("twisted buckler"), Gear.from_bb("bone bolts"))
        gear_bools = (buckler, bone_bolts)
        gear = [g for g, b in zip(gear_options, gear_bools) if b]

        return_val = self.equip(
            SpecialWeapon.from_bb("dorgeshuun crossbow"), *gear, style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_crystal_bowfa(
        self, crystal_set: bool = True, style: PlayerStyle = None  # type: ignore
    ) -> PlayerStyle:
        if crystal_set:
            self.equip_crystal_set()

        weapon_style = style if style else BowStyles.default
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(Weapon.from_bb("bow of faerdhinen"), style=weapon_style)
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_seercull(self, style: PlayerStyle = None) -> PlayerStyle:  # type: ignore
        seercull = SpecialWeapon.from_bb("seercull")
        weapon_style = style if style else BowStyles.get_by_stance(Stances.ACCURATE)
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(seercull, style=weapon_style)
        assert isinstance(return_val, PlayerStyle)
        return return_val

    # magic gear helpers ###################################################################################################
    def equip_ancestral_set(self):
        self.equip(
            Gear.from_bb("ancestral hat"),
            Gear.from_bb("ancestral robe top"),
            Gear.from_bb("ancestral robe bottoms"),
        )

    def equip_sang(self, arcane: bool = True, style: PlayerStyle = None) -> PlayerStyle:  # type: ignore
        gear = [Gear.from_bb("arcane spirit shield")] if arcane else []
        weapon_style = (
            style if style else PoweredStaffStyles.get_by_stance(Stances.ACCURATE)
        )
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(
            Weapon.from_bb("sanguinesti staff"), *gear, style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val

    def equip_harm(self, tome: bool = True, style: PlayerStyle = None) -> PlayerStyle:  # type: ignore
        gear = [Gear.from_bb("tome of fire")] if tome else []
        weapon_style = style if style else StaffStyles.default
        assert isinstance(weapon_style, PlayerStyle)

        return_val = self.equip(
            Weapon.from_bb("harmonised staff"), *gear, style=weapon_style
        )
        assert isinstance(return_val, PlayerStyle)
        return return_val
