"""Equipment, a Gear container with some validation and ease of access.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from collections import Counter
from copy import copy
from dataclasses import dataclass, field, fields
from functools import reduce
from itertools import compress
from typing import Any

from osrs_tools.data import Slots
from osrs_tools.exceptions import OsrsException
from osrs_tools.stats.stats import AggressiveStats, DefensiveStats, PlayerLevels
from osrs_tools.style.style import BowStyles, CrossbowStyles, ThrownStyles
from typing_extensions import Self

from . import common_gear as cg
from .gear import Gear
from .weapon import Weapon

###############################################################################
# errors 'n such                                                              #
###############################################################################


class EquipmentError(OsrsException):
    ...


###############################################################################
# main class                                                                  #
###############################################################################


@dataclass(order=True, frozen=False)
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

    def __iter__(self):
        yield from self.equipped_gear

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

    def __getitem__(self, __value: Slots, /) -> Gear:
        gear = super().__getattribute__(__value.value)
        assert isinstance(gear, Gear)
        return gear

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
        _clsname = self.__class__.__name__

        if self.name is None:
            _joined = ", ".join([g.name for g in self.equipped_gear])
            message = f"{_clsname}({_joined})"
        else:
            message = f"{_clsname}({self.name})"

        return message

    def __copy__(self):
        return Equipment().equip(*[copy(g) for g in self.equipped_gear])

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
            cg.VoidKnightHelm,
            cg.VoidKnightTop,
            cg.VoidKnightRobe,
            cg.VoidKnightGloves,
        )

    @property
    def elite_void_set(self) -> bool:
        return self.wearing(
            cg.VoidKnightHelm,
            cg.EliteVoidTop,
            cg.EliteVoidRobe,
            cg.VoidKnightGloves,
        )

    @property
    def dharok_set(self) -> bool:
        return self.wearing(
            cg.DharoksGreataxe,
            cg.DharoksPlatebody,
            cg.DharoksPlatelegs,
            cg.DharoksGreataxe,
        )

    @property
    def bandos_set(self) -> bool:
        return self.wearing(
            cg.NeitiznotFaceguard,
            cg.BandosChestplate,
            cg.BandosTassets,
        )

    @property
    def inquisitor_set(self) -> bool:
        return self.wearing(
            cg.InquisitorsGreatHelm,
            cg.InquisitorsHauberk,
            cg.InquisitorsPlateskirt,
        )

    @property
    def torva_set(self) -> bool:
        return self.wearing(
            cg.TorvaFullHelm,
            cg.TorvaPlatebody,
            cg.TorvaPlatelegs,
        )

    @property
    def justiciar_set(self) -> bool:
        return self.wearing(
            cg.JusticiarFaceguard,
            cg.JusticiarChestguard,
            cg.JusticiarLegguard,
        )

    @property
    def obsidian_armor_set(self) -> bool:
        return self.wearing(
            cg.ObsidianHelm,
            cg.ObsidianPlatebody,
            cg.ObsidianPlatelegs,
        )

    @property
    def obsidian_weapon(self) -> bool:
        qualifying_weapons = [
            cg.ObsidianDagger,
            cg.ObsidianMace,
            cg.ObsidianMaul,
            cg.ObsidianSword,
        ]
        return self.weapon in qualifying_weapons

    @property
    def leafy_weapon(self) -> bool:
        qualifying_weapons = [
            cg.LeafBladedSpear,
            cg.LeafBladedSword,
            cg.LeafBladedBattleaxe,
        ]
        return self.weapon in qualifying_weapons

    @property
    def keris(self) -> bool:
        qualifying_weapons = [
            cg.Keris,
        ]
        return self.weapon in qualifying_weapons

    @property
    def crystal_armor_set(self) -> bool:
        return self.wearing(
            cg.CrystalHelm,
            cg.CrystalBody,
            cg.CrystalLegs,
        )

    @property
    def crystal_weapon(self) -> bool:
        qualifying_weapons = [
            cg.CrystalBow,
            cg.BowOfFaerdhinen,
        ]
        return self.weapon in qualifying_weapons

    @property
    def smoke_staff(self) -> bool:
        qualifying_weapons = [cg.MysticSmokeStaff, cg.SmokeBattlestaff]
        return self.weapon in qualifying_weapons

    @property
    def graceful_set(self) -> bool:
        return self.wearing(
            cg.GracefulHood,
            cg.GracefulTop,
            cg.GracefulLegs,
            cg.GracefulGloves,
            cg.GracefulBoots,
            cg.GracefulCape,
        )

    @property
    def staff_of_the_dead(self) -> bool:
        qualifying_weapons = [
            cg.StaffOfLight,
            cg.StaffOfTheDead,
            cg.ToxicStaffOfTheDead,
        ]
        return self.weapon in qualifying_weapons

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
    def dragonbane_weapon(self) -> bool:
        """True if a dragonbane weapon is equipped.

        There are currently two dragonbane weapons in the game:
            Dragon Hunter Crossbow
            Dragon Hunter Lance

        Returns
        -------
        bool
        """
        qualifying_weapons = [
            cg.DragonHunterCrossbow,
            cg.DragonHunterLance,
        ]
        return self.weapon in qualifying_weapons

    @property
    def salve(self) -> bool:
        """True if any form of salve amulet is equipped.

        Returns
        -------
        bool
        """
        qualifying_items = [
            cg.SalveAmuletI,
            cg.SalveAmuletEI,
        ]
        return self.neck in qualifying_items

    @property
    def wilderness_weapon(self) -> bool:
        """True if a wilderness / revenant weapon is equipped.

        Returns
        -------

        bool
        """
        qualifying_weapons = [
            cg.CrawsBow,
            cg.ViggorasChainmace,
            cg.ThammaronsSceptre,
        ]
        return self.weapon in qualifying_weapons

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
        """Return True if equipment contains any form of abyssal dagger.

        Returns
        -------
        bool
        """
        qualifying_weapons = [
            cg.AbyssalDagger,
        ]
        return self.weapon in qualifying_weapons

    @property
    def dragon_dagger(self) -> bool:
        """Return True if equipment contains any form of dragon dagger.

        Returns
        -------
        bool
        """
        qualifying_weapons = [
            cg.DragonDagger,
        ]
        return self.weapon in qualifying_weapons

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
        """True if enchanted ruby bolts are equipped."""
        matching_ammunition = [cg.RubyDragonBoltsE, cg.RubyBoltsE]
        return self.ammunition in matching_ammunition

    @property
    def enchanted_diamond_bolts(self) -> bool:
        """True if enchanted diamond bolts are equipped."""
        matching_ammunition = [cg.DiamondDragonBoltsE, cg.DiamondBoltsE]
        return self.ammunition in matching_ammunition

    @property
    def enchanted_dragonstone_bolts(self) -> bool:
        """True if enchanted dragonstone bolts are equipped."""
        matching_ammunition = [cg.DragonstoneDragonBoltsE, cg.DragonstoneBoltsE]
        return self.ammunition in matching_ammunition

    @property
    def enchanted_onyx_bolts(self) -> bool:
        """True if enchanted onyx bolts are equipped."""
        matching_ammunition = [cg.OnyxDragonBoltsE, cg.OnyxBoltsE]
        return self.ammunition in matching_ammunition

    @property
    def enchanted_bolts_equipped(self) -> bool:
        """True if any form of enchanted bolts are equipped.

        This generic property implements all of the ammunition / bolt
        properties and removes properties which return NotImplemented. Use in
        conjunction with specific properties to simplify decision trees in
        other modules.

        Returns
        -------
        bool
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
        implemented_properties = (p for p in properties if isinstance(p, bool))
        return any(implemented_properties)

    # Equipment helpers

    def equip_bis_melee(
        self,
        torva_set: bool = True,
        infernal: bool = True,
        torture: bool = True,
        ferocious: bool = True,
        primordial: bool = True,
        berserker: bool = True,
    ) -> Self:
        """Equip some basic best-in-slot melee gear by default.

        Parameters
        ----------
        torva_set : bool, optional
            True to equip a Torva helm, body, and legs, by default True
        infernal : bool, optional
            True to equip an infernal cape, by default True
        torture : bool, optional
            True to equipo an amulet of torture, by default True
        ferocious : bool, optional
            True to equip ferocious gloves, by default True
        primordial : bool, optional
            True to equip primordial boots, by default True
        berserker : bool, optional
            True to equip a berserker ring (i), by default True

        Returns
        -------
        Self
        """

        gear: list[Gear] = []

        if torva_set:
            gear.extend(cg.TorvaSet)

        gear_options = [
            cg.InfernalCape,
            cg.AmuletOfTorture,
            cg.FerociousGloves,
            cg.PrimordialBoots,
            cg.BerserkerRingI,
        ]
        gear_bools = [infernal, torture, ferocious, primordial, berserker]

        gear.extend(compress(gear_options, gear_bools))

        return self.equip(*gear)

    def equip_bis_ranged(
        self,
        arma_set: bool = True,
        avas: bool = True,
        anguish: bool = True,
        zaryte: bool = True,
        pegasian: bool = True,
    ) -> Self:
        """Equip some basic best-in-slot ranged gear by default.

        Parameters
        ----------
        arma_set : bool, optional
            True to equip an armadyl helm, body, & legs, by default True
        avas : bool, optional
            True to equip an ava's assembler (vorkath one), by default True
        anguish : bool, optional
            True to equip a necklace of anguish, by default True
        zaryte : bool, optional
            True to equip zaryte vambraces, by default True
        pegasian : bool, optional
            True to equip pegasian boots, by default True

        Returns
        -------
        Self
        """

        gear: list[Gear] = []

        if arma_set:
            gear.extend(cg.ArmadylSet)

        gear_options = [
            cg.AvasAssembler,
            cg.NecklaceOfAnguish,
            cg.ZaryteVambraces,
            cg.PegasianBoots,
        ]
        gear_bools = [avas, anguish, zaryte, pegasian]
        gear.extend(compress(gear_options, gear_bools))

        return self.equip(*gear)

    def equip_bis_mage(
        self,
        ancestral_set: bool = True,
        god_cape: bool = True,
        occult: bool = True,
        arcane: bool = True,
        tormented: bool = True,
        eternal: bool = True,
    ) -> Self:
        """Equip some basic best-in-slot mage gear by default.

        Parameters
        ----------
        ancestral_set : bool, optional
            True to equip an ancestral hat, top, & legs, by default True
        god_cape : bool, optional
            True to equip a god cape (i), by default True
        occult : bool, optional
            True to equip an occult necklace, by default True
        arcane : bool, optional
            True to equip an arcane spirit shield, by default True
        tormented : bool, optional
            True to equip a tormented bracelet, by default True
        eternal : bool, optional
            True to equip eternal boots, by default True

        Returns
        -------
        Self
        """

        gear: list[Gear] = []

        if ancestral_set:
            gear.extend(cg.AncestralSet)

        gear_options = (
            cg.GodCapeI,
            cg.OccultNecklace,
            cg.ArcaneSpiritShield,
            cg.TormentedBracelet,
            cg.EternalBoots,
        )
        gear_bools = [god_cape, occult, arcane, tormented, eternal]
        gear.extend(compress(gear_options, gear_bools))

        return self.equip(*gear)
