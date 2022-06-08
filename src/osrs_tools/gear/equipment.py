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
from itertools import compress
from typing import Iterator

from osrs_tools.data import Slots
from osrs_tools.exceptions import OsrsException
from osrs_tools.stats import AggressiveStats, DefensiveStats, PlayerLevels
from osrs_tools.style import BowStyles, CrossbowStyles, ThrownStyles
from typing_extensions import Self

from . import common_gear as gear
from . import utils
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

    # dunder methods

    def __getitem__(self, __key: Slots, /) -> Gear:
        # access protected attribute of type Gear | None
        _gear = getattr(self, f"_{__key.value}")
        assert isinstance(_gear, Gear)
        return _gear

    def __setitem__(self, __key: Slots, __value: Gear | None, /) -> None:
        try:
            setattr(self, __key.value, __value)

        except AttributeError:
            setattr(self, f"_{__key.value}", __value)

    def __iter__(self) -> Iterator:
        yield from self.equipped_gear

    def __len__(self) -> int:
        return len(self.equipped_gear)

    def __bool__(self) -> bool:
        return len(self) > 0

    def __str__(self):
        _clsname = self.__class__.__name__

        if self.name is None:
            _joined = ", ".join([g.name for g in self.equipped_gear])
            message = f"{_clsname}({_joined})"
        else:
            message = f"{_clsname}({self.name})"

        return message

    def __add__(self, other: Gear | list[Gear] | Equipment) -> Equipment:
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

    def __radd__(self, other) -> Equipment:
        """radd pvm bro

        Parameters
        ----------
        other : _type_

        Returns
        -------
        Equipment
        """
        if isinstance(other, (Gear, list)):
            return self.__add__(other)

        raise TypeError(other)

    def __copy__(self):
        return Equipment().equip(*[copy(g) for g in self.equipped_gear])

    # properties: getters / setters

    @property
    def weapon(self) -> Weapon:
        assert isinstance(self._weapon, Weapon)
        return self._weapon

    @weapon.setter
    def weapon(self, __value: Weapon | None, /) -> None:
        if __value is None:
            self._weapon = None
            return

        assert isinstance(__value, Weapon)

        if __value.two_handed:
            self[Slots.SHIELD] = None
            return

    @property
    def shield(self) -> Gear | None:
        return self._shield

    @shield.setter
    def shield(self, __value: Gear | None, /) -> None:
        if __value is None:
            self._shield = None
            return

        self._shield = __value

        if self._weapon is None:
            return

        if self.weapon.two_handed:
            self._weapon = None
            return

    # well well well if it ain't a bug I just done found 'ere
    # there it is, if there's no weapon this is an error
    # if self[Slots.WEAPON].two_handed:
    #    self.unequip(Slots.WEAPON)

    # properties

    @property
    def aggressive_bonus(self) -> AggressiveStats:
        """Find the equipment set's aggressive bonus.

        This is the value before any relevant player modifiers are applied.

        Returns
        -------
        AggressiveStats
        """

        _val = sum(g.aggressive_bonus for g in self.equipped_gear)
        assert isinstance(_val, AggressiveStats)

        # Hey reader, it's me Joe from Family Guy here to explain why this
        # is necessary. See, the sum function starts with 0 and performs
        # successive sums on all the elements of an iterable. But, by the
        # definition of AggressiveStats, ...

        # Hey :b:eader, it's me Family Guy Peter Griffin to interrupt Joe,
        # see I actually consulted the documentation and it turns out I
        # retconned that, it's a much smarter system so this extra
        # coupling is completely unnecessary, carry on!

        # if isinstance(val, int) and val == 0:
        #     return AggressiveStats().no_bonus()

        return _val

    @property
    def defensive_bonus(self) -> DefensiveStats:
        """Find the equipment set's defensive bonus.

        Returns
        -------
        DefensiveStats
        """
        _val = sum(g.defensive_bonus for g in self.equipped_gear)
        assert isinstance(_val, DefensiveStats)

        return _val

    @property
    def prayer_bonus(self) -> int:
        """Find the equipment set's prayer bonus."""
        return sum(g.prayer_bonus for g in self.equipped_gear)

    @property
    def level_requirements(self) -> PlayerLevels:
        """Find the equipment set's level requirements."""
        indiv_reqs = [g.level_requirements for g in self.equipped_gear]

        if len(indiv_reqs) > 0:
            reqs = utils.get_minimum_reqs(*self.equipped_gear)
        else:
            reqs = PlayerLevels.starting_stats()

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

    def equip(self, *_gear: Gear, duplicates_allowed: bool = False) -> Self:
        """Equip the provided gear, also supports weapons."""

        # Catch duplicate error specification.
        if duplicates_allowed is False:
            slots_list = [g.slot for g in _gear]
            slots_set = set(slots_list)

            if len(slots_list) != len(slots_set):
                # create a list of the offending dupes
                dupe_gear = []

                for slot, count in Counter(slots_list).items():
                    if not count > 1:
                        continue

                    dupe_gear.append([g for g in _gear if g.slot is slot])

                raise ValueError(f"Duplicate gear: {', '.join(dupe_gear)}")

        for g in _gear:
            # type checking
            if not isinstance(g, Gear):
                raise TypeError(f"{type(g)} not allowed")

            self[g.slot] = g

        return self

    def unequip(self, *slots: Slots) -> Self:
        """Unequip any gear in the provided slots."""

        for slot in slots:
            if slot is Slots.WEAPON:
                self[Slots.WEAPON] = Weapon.empty_slot()
                continue

            self[slot] = None

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
        """Property which returns True if the Equipment slots are filled

        # TODO: implement osrsbox-db wrapper which eliminates the need for assume_2h parameter.

        Parameters
        ----------
        requires_ammo : bool | None
            If True, requires Ammunition to be equipped even for styles which
            don't make use of it, defaults to None

        Returns
        -------
        bool
        """
        if self._weapon is None:
            return False

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
                _ = self[slot]  # runs slot assertion

        return True

    @property
    def full_set(self) -> bool:
        """Return True if the equipment is a complete set, else False."""

        return self._full_set_method()

    @property
    def normal_void_set(self) -> bool:
        return self.wearing(
            gear.VoidKnightHelm,
            gear.VoidKnightTop,
            gear.VoidKnightRobe,
            gear.VoidKnightGloves,
        )

    @property
    def elite_void_set(self) -> bool:
        return self.wearing(
            gear.VoidKnightHelm,
            gear.EliteVoidTop,
            gear.EliteVoidRobe,
            gear.VoidKnightGloves,
        )

    @property
    def dharok_set(self) -> bool:
        return self.wearing(
            gear.DharoksGreataxe,
            gear.DharoksPlatebody,
            gear.DharoksPlatelegs,
            gear.DharoksGreataxe,
        )

    @property
    def bandos_set(self) -> bool:
        return self.wearing(
            gear.NeitiznotFaceguard,
            gear.BandosChestplate,
            gear.BandosTassets,
        )

    @property
    def inquisitor_set(self) -> bool:
        return self.wearing(
            gear.InquisitorsGreatHelm,
            gear.InquisitorsHauberk,
            gear.InquisitorsPlateskirt,
        )

    @property
    def torva_set(self) -> bool:
        return self.wearing(
            gear.TorvaFullHelm,
            gear.TorvaPlatebody,
            gear.TorvaPlatelegs,
        )

    @property
    def justiciar_set(self) -> bool:
        return self.wearing(
            gear.JusticiarFaceguard,
            gear.JusticiarChestguard,
            gear.JusticiarLegguard,
        )

    @property
    def obsidian_armor_set(self) -> bool:
        return self.wearing(
            gear.ObsidianHelm,
            gear.ObsidianPlatebody,
            gear.ObsidianPlatelegs,
        )

    @property
    def obsidian_weapon(self) -> bool:
        qualifying_weapons = [
            gear.ObsidianDagger,
            gear.ObsidianMace,
            gear.ObsidianMaul,
            gear.ObsidianSword,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

    @property
    def leafy_weapon(self) -> bool:
        qualifying_weapons = [
            gear.LeafBladedSpear,
            gear.LeafBladedSword,
            gear.LeafBladedBattleaxe,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

    @property
    def keris(self) -> bool:
        qualifying_weapons = [
            gear.Keris,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

    @property
    def crystal_armor_set(self) -> bool:
        return self.wearing(
            gear.CrystalHelm,
            gear.CrystalBody,
            gear.CrystalLegs,
        )

    @property
    def crystal_weapon(self) -> bool:
        qualifying_weapons = [
            gear.CrystalBow,
            gear.BowOfFaerdhinen,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

    @property
    def smoke_staff(self) -> bool:
        qualifying_weapons = [gear.MysticSmokeStaff, gear.SmokeBattlestaff]
        return self[Slots.WEAPON] in qualifying_weapons

    @property
    def graceful_set(self) -> bool:
        return self.wearing(
            gear.GracefulHood,
            gear.GracefulTop,
            gear.GracefulLegs,
            gear.GracefulGloves,
            gear.GracefulBoots,
            gear.GracefulCape,
        )

    @property
    def staff_of_the_dead(self) -> bool:
        qualifying_weapons = [
            gear.StaffOfLight,
            gear.StaffOfTheDead,
            gear.ToxicStaffOfTheDead,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

    @staticmethod
    def _is_crossbow(__wpn: Weapon | None, /) -> bool:
        """Return True if any form of crossbow is equipped.

        This generic property checks a few obvious values to ensure that other
        modules can interact with Crossbows simply.

        Returns:
            bool: True if any crossbow is equiped, otherwise False.
        """
        if __wpn is None:
            return False

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
            gear.DragonHunterCrossbow,
            gear.DragonHunterLance,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

    @property
    def salve(self) -> bool:
        """True if any form of salve amulet is equipped.

        Returns
        -------
        bool
        """
        qualifying_items = [
            gear.SalveAmuletI,
            gear.SalveAmuletEI,
        ]
        return self[Slots.NECK] in qualifying_items

    @property
    def wilderness_weapon(self) -> bool:
        """True if a wilderness / revenant weapon is equipped.

        Returns
        -------

        bool
        """
        qualifying_weapons = [
            gear.CrawsBow,
            gear.ViggorasChainmace,
            gear.ThammaronsSceptre,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

    @property
    def pickaxe(self) -> bool:
        """Returns true if the player is wielding a pickaxe.

        Returns:
            bool: _description_
        """
        try:
            assert isinstance(self[Slots.WEAPON], Weapon)
            return "pickaxe" in self[Slots.WEAPON].name
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
            gear.AbyssalDagger,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

    @property
    def dragon_dagger(self) -> bool:
        """Return True if equipment contains any form of dragon dagger.

        Returns
        -------
        bool
        """
        qualifying_weapons = [
            gear.DragonDagger,
        ]
        return self[Slots.WEAPON] in qualifying_weapons

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
        matching_ammunition = [gear.RubyDragonBoltsE, gear.RubyBoltsE]
        return self[Slots.AMMUNITION] in matching_ammunition

    @property
    def enchanted_diamond_bolts(self) -> bool:
        """True if enchanted diamond bolts are equipped."""
        matching_ammunition = [gear.DiamondDragonBoltsE, gear.DiamondBoltsE]
        return self[Slots.AMMUNITION] in matching_ammunition

    @property
    def enchanted_dragonstone_bolts(self) -> bool:
        """True if enchanted dragonstone bolts are equipped."""
        matching_ammunition = [gear.DragonstoneDragonBoltsE, gear.DragonstoneBoltsE]
        return self[Slots.AMMUNITION] in matching_ammunition

    @property
    def enchanted_onyx_bolts(self) -> bool:
        """True if enchanted onyx bolts are equipped."""
        matching_ammunition = [gear.OnyxDragonBoltsE, gear.OnyxBoltsE]
        return self[Slots.AMMUNITION] in matching_ammunition

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

        _gear: list[Gear] = []

        if torva_set:
            _gear.extend(gear.TorvaSet)

        gear_options = [
            gear.InfernalCape,
            gear.AmuletOfTorture,
            gear.FerociousGloves,
            gear.PrimordialBoots,
            gear.BerserkerRingI,
        ]
        gear_bools = [infernal, torture, ferocious, primordial, berserker]

        _gear.extend(compress(gear_options, gear_bools))

        return self.equip(*_gear)

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

        _gear: list[Gear] = []

        if arma_set:
            _gear.extend(gear.ArmadylSet)

        gear_options = [
            gear.AvasAssembler,
            gear.NecklaceOfAnguish,
            gear.ZaryteVambraces,
            gear.PegasianBoots,
        ]
        gear_bools = [avas, anguish, zaryte, pegasian]
        _gear.extend(compress(gear_options, gear_bools))

        return self.equip(*_gear)

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

        _gear: list[Gear] = []

        if ancestral_set:
            _gear.extend(gear.AncestralSet)

        gear_options = (
            gear.GodCapeI,
            gear.OccultNecklace,
            gear.ArcaneSpiritShield,
            gear.TormentedBracelet,
            gear.EternalBoots,
        )
        gear_bools = (god_cape, occult, arcane, tormented, eternal)
        _gear.extend(compress(gear_options, gear_bools))

        return self.equip(*_gear)
