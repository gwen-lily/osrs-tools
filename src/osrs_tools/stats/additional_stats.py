"""Definition of Style

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022                                                              #
###############################################################################
"""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field, fields

from osrs_tools import utils
from osrs_tools.data import DT, MagicDamageTypes, MeleeDamageTypes, RangedDamageTypes
from osrs_tools.tracked_value import EquipmentStat, StyleBonus, TrackedFloat

from .data import StatBonusPair
from .stats import Stats

###############################################################################
# main classes                                                                #
###############################################################################


@dataclass
class StyleStats(Stats):
    """Integer container class for validation, security, and logging."""

    melee_attack: StyleBonus = field(default_factory=StyleBonus.zero)
    melee_strength: StyleBonus = field(default_factory=StyleBonus.zero)
    defence: StyleBonus = field(default_factory=StyleBonus.zero)
    ranged_attack: StyleBonus = field(default_factory=StyleBonus.zero)
    ranged_strength: StyleBonus = field(default_factory=StyleBonus.zero)
    magic_attack: StyleBonus = field(default_factory=StyleBonus.zero)

    # class methods

    @classmethod
    def melee_shared_bonus(cls):
        value = 1
        comment = "shared style"
        return cls(
            melee_attack=StyleBonus(value, comment),
            melee_strength=StyleBonus(value, comment),
            defence=StyleBonus(value, comment),
        )

    @classmethod
    def melee_accurate_bonuses(cls):
        value = 3
        comment = "accurate style"
        return cls(melee_attack=StyleBonus(value, comment))

    @classmethod
    def melee_strength_bonuses(cls):
        value = 3
        comment = "aggressive style"
        return cls(melee_strength=StyleBonus(value, comment))

    @classmethod
    def defensive_bonuses(cls):
        value = 3
        comment = "defensive style"
        return cls(defence=StyleBonus(value, comment))

    @classmethod
    def ranged_bonus(cls):
        value = 3
        comment = "ranged (accurate) style"
        return cls(
            ranged_attack=StyleBonus(value, comment),
            ranged_strength=StyleBonus(value, comment),
        )

    @classmethod
    def magic_bonus(cls):
        value = 3
        comment = "magic (accurate) style"
        return cls(magic_attack=StyleBonus(value, comment))

    @classmethod
    def npc_bonus(cls):
        bonus = StyleBonus(1, "npc style")
        return cls(
            melee_attack=bonus,
            melee_strength=bonus,
            defence=bonus,
            ranged_attack=bonus,
            magic_attack=bonus,
        )


@dataclass
class AggressiveStats(Stats):
    """Class with information relevant to offensive damage calculation.

    Included attributes are attack bonus values: stab, slash, crush, magic
    attack, ranged attack, melee strength, ranged strength, and magic strength
    (not to be confused with magic damage).

    Attributes
    ----------

    stab : TrackedInt
        Accuracy bonus for stab damage type. Defaults to 0.
    slash : TrackedInt
        Accuracy bonus for slash damage type. Defaults to 0.
    crush : TrackedInt
        Accuracy bonus for crush damage type. Defaults to 0.
    magic_attack : TrackedInt
        Accuracy bonus for magic damage type. Defaults to 0.
    ranged_attack : TrackedInt
        Accuracy bonus for ranged damage type. Defaults to 0.
    melee_strength : TrackedInt
        Strength bonus for melee damage types. Defaults to 0.
    ranged_strength : TrackedInt
        Strength bonus for ranged damage type. Defaults to 0.
    magic_strength : TrackedFloat
        Strength bonus for magic damage type. Uniquely expressed as a float
        as opposed to a straight bonus. Defaults to 0.
    """

    stab: EquipmentStat = field(default_factory=EquipmentStat.zero)
    slash: EquipmentStat = field(default_factory=EquipmentStat.zero)
    crush: EquipmentStat = field(default_factory=EquipmentStat.zero)
    magic_attack: EquipmentStat = field(default_factory=EquipmentStat.zero)
    ranged_attack: EquipmentStat = field(default_factory=EquipmentStat.zero)
    melee_strength: EquipmentStat = field(default_factory=EquipmentStat.zero)
    ranged_strength: EquipmentStat = field(default_factory=EquipmentStat.zero)
    magic_strength: TrackedFloat = field(default_factory=TrackedFloat.zero)

    # dunder and helper methods

    def __getitem__(self, __value: DT, /) -> StatBonusPair:
        if __value in MeleeDamageTypes:
            _atk = self.__getattribute__(__value.value)
            assert isinstance(_atk, EquipmentStat)
            _str = self.melee_strength
        elif __value in RangedDamageTypes:
            _atk = self.ranged_attack
            _str = self.ranged_strength
        elif __value in MagicDamageTypes:
            _atk = self.magic_attack
            _str = self.magic_strength
        else:
            raise ValueError(__value)

        return _atk, _str

    def __add__(self, other: int | AggressiveStats) -> AggressiveStats:
        if isinstance(other, int):
            if other == 0:
                return copy(self)
            else:
                raise ValueError(other)

        elif isinstance(other, AggressiveStats):
            new_vals = {}

            for f in fields(self):
                self_val = getattr(self, f.name)
                other_val = getattr(other, f.name)
                new_vals[f.name] = self_val + other_val
        else:
            raise TypeError(other)

        return AggressiveStats(**new_vals)

    @classmethod  # TODO: Look into bitterkoekje's general attack stat and see where it matters
    def from_bb(cls, name: str):
        mon_df = utils.lookup_normal_monster_by_name(name)

        general_attack_bonus = mon_df["attack bonus"]
        val = general_attack_bonus.values[0]
        assert val is not None

        if val > 0:
            stab_attack, slash_attack, crush_attack = 3 * (general_attack_bonus,)
        else:
            stab_attack = mon_df["stab attack"].values[0]
            slash_attack = mon_df["slash attack"].values[0]
            crush_attack = mon_df["crush attack"].values[0]

        return cls(
            stab_attack,
            slash_attack,
            crush_attack,
            mon_df["magic attack"].values[0],
            mon_df["ranged attack"].values[0],
            mon_df["melee strength"].values[0],
            mon_df["ranged strength"].values[0],
            mon_df["magic strength"].values[0],
        )

    @classmethod
    def from_osrsbox(cls, name: str):
        raise NotImplementedError


@dataclass
class DefensiveStats(Stats):
    """Class with information relevant to defensive damage calculation.

    Attributes
    ----------

    stab : TrackedInt
        Defence bonus for stab damage type.
    slash : TrackedInt
        Defence bonus for slash damage type.
    crush : TrackedInt
        Defence bonus for crush damage type.
    magic : TrackedInt
        Defence bonus for magic damage type.
    ranged : TrackedInt
        Defence bonus for ranged damage type.
    """

    stab: EquipmentStat = field(default_factory=EquipmentStat.zero)
    slash: EquipmentStat = field(default_factory=EquipmentStat.zero)
    crush: EquipmentStat = field(default_factory=EquipmentStat.zero)
    magic: EquipmentStat = field(default_factory=EquipmentStat.zero)
    ranged: EquipmentStat = field(default_factory=EquipmentStat.zero)

    # dunder and helper methods

    def __getitem__(self, __value: DT, /) -> EquipmentStat:
        _def = self.__getattribute__(__value.value)
        assert isinstance(_def, EquipmentStat)

        return _def

    def __add__(self, other: int | DefensiveStats) -> DefensiveStats:
        if isinstance(other, int):
            if other == 0:
                return copy(self)
            else:
                raise ValueError(other)

        elif isinstance(other, DefensiveStats):
            new_vals = {}

            for f in fields(self):
                self_val = getattr(self, f.name)
                other_val = getattr(other, f.name)
                new_vals[f.name] = self_val + other_val
        else:
            raise TypeError(other)

        return DefensiveStats(**new_vals)

    @classmethod
    def from_bb(cls, name: str):
        mon_df = utils.lookup_normal_monster_by_name(name)

        return cls(
            mon_df["stab defence"].values[0],
            mon_df["slash defence"].values[0],
            mon_df["crush defence"].values[0],
            mon_df["magic defence"].values[0],
            mon_df["ranged defence"].values[0],
        )

    @classmethod
    def from_osrsbox(cls, name: str):
        raise NotImplementedError
