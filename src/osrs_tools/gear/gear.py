"""Gear, the most basic gear class.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""
from __future__ import annotations

from dataclasses import dataclass, field

from osrs_tools.data import ITEMS, EquipmentStat, Level, Slots, TrackedFloat
from osrs_tools.exceptions import OsrsException
from osrs_tools.gear.utils import lookup_gear_bb_by_name
from osrs_tools.stats.stats import AggressiveStats, DefensiveStats, PlayerLevels
from osrsbox.items_api.item_equipment import ItemEquipment

###############################################################################
# errors 'n such                                                              #
###############################################################################


class GearError(OsrsException):
    pass


class EquipableError(GearError):
    pass


###############################################################################
# main class                                                                  #
###############################################################################


@dataclass(order=True, frozen=True)
class Gear:
    """An equippable item in osrs.

    Gear has subclasses Weapon & SpecialWeapon, which each have additional
    attributes. Gear can be created via resources or manually.

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
            raise ValueError(f"{name=}, {item_id=}")

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
                raise TypeError(type(cls))
            elif eqp.slot == slot_enum.value:
                slot = slot_enum
                break

        if slot is None:
            raise GearError(f"{eqp.slot}")

        aggressive_bonus = AggressiveStats(
            stab=EquipmentStat(eqp.attack_stab),
            slash=EquipmentStat(eqp.attack_slash),
            crush=EquipmentStat(eqp.attack_crush),
            magic_attack=EquipmentStat(eqp.attack_magic),
            ranged_attack=EquipmentStat(eqp.attack_ranged),
            melee_strength=EquipmentStat(eqp.melee_strength),
            ranged_strength=EquipmentStat(eqp.ranged_strength),
            magic_strength=TrackedFloat(eqp.magic_damage / 100),
        )
        defensive_bonus = DefensiveStats(
            stab=EquipmentStat(eqp.defence_stab),
            slash=EquipmentStat(eqp.defence_slash),
            crush=EquipmentStat(eqp.defence_crush),
            magic=EquipmentStat(eqp.defence_magic),
            ranged=EquipmentStat(eqp.defence_ranged),
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
