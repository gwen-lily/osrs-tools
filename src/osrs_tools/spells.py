"""Spells and definition of all OSRS spells.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, unique

from osrs_tools.character import Player
from osrs_tools.data import Level
from osrs_tools.exceptions import OsrsException

###############################################################################
# errors 'n such                                                              #
###############################################################################


class SpellError(OsrsException):
    pass


###############################################################################
# Spell                                                                       #
###############################################################################


@dataclass(frozen=True, kw_only=True)
class Spell(ABC):
    """An abstract Spell from which concrete spells inherit.

    Attributes
    ----------

    name : str
        The name of the spell.

    base_max_hit : int
        A parameter, check the wiki.

    attack_speed : int
        The time between casts (in ticks).

    max_targets_hit : int
        The maximum number of targets hit by a spell.

    """

    name: str
    base_max_hit: int
    attack_speed: int = field(default=5, init=False)
    max_targets_hit: int = field(default=1, init=False)

    @abstractmethod
    def max_hit(self, lad: Player, /) -> int:
        pass


class StandardSpell(Spell):
    def max_hit(self, /) -> int:
        return self.base_max_hit


@dataclass(frozen=True)
class GodSpell(StandardSpell):
    base_max_hit: int = field(default=20, init=False)
    charge_bonus: int = field(default=10, init=False)

    def max_hit(self, lad: Player, /) -> int:
        return self.base_max_hit + lad.charged * self.charge_bonus


@dataclass(frozen=True)
class AncientSpell(Spell):
    max_targets_hit: int = field(default=1)

    def max_hit(self, /) -> int:
        return self.base_max_hit


@dataclass(frozen=True)
class PoweredSpell(Spell):
    attack_speed: int = field(default=4, init=False)

    def max_hit(self, lad: Player, /) -> int:
        vis_lvl = lad.visible_magic
        min_vis_lvl = Level(75, "minimum PoweredSpell visible level")
        max_vis_lvl = Level(120, "maximum PoweredSpell visible level")

        vis_lvl_clamped = min(max(min_vis_lvl, vis_lvl), max_vis_lvl)
        max_hit = self.base_max_hit + (vis_lvl_clamped - min_vis_lvl) // 3

        return max_hit


###############################################################################
# define spells and member groups                                             #
###############################################################################

# standard spells #############################################################


@unique
class StandardSpells(Enum):
    WIND_STRIKE = StandardSpell(name="wind strike", base_max_hit=2)
    WATER_STRIKE = StandardSpell(name="water strike", base_max_hit=4)
    EARTH_STRIKE = StandardSpell(name="earth strike", base_max_hit=6)
    FIRE_STRIKE = StandardSpell(name="fire strike", base_max_hit=8)
    WIND_BOLT = StandardSpell(name="wind bolt", base_max_hit=9)
    WATER_BOLT = StandardSpell(name="water bolt", base_max_hit=10)
    EARTH_BOLT = StandardSpell(name="earth bolt", base_max_hit=11)
    FIRE_BOLT = StandardSpell(name="fire bolt", base_max_hit=12)
    WIND_BLAST = StandardSpell(name="wind blast", base_max_hit=13)
    WATER_BLAST = StandardSpell(name="water blast", base_max_hit=14)
    EARTH_BLAST = StandardSpell(name="earth blast", base_max_hit=15)
    FIRE_BLAST = StandardSpell(name="fire blast", base_max_hit=16)
    WIND_WAVE = StandardSpell(name="wind wave", base_max_hit=17)
    WATER_WAVE = StandardSpell(name="water wave", base_max_hit=18)
    EARTH_WAVE = StandardSpell(name="earth wave", base_max_hit=19)
    FIRE_WAVE = StandardSpell(name="fire wave", base_max_hit=20)
    WIND_SURGE = StandardSpell(name="wind surge", base_max_hit=21)
    WATER_SURGE = StandardSpell(name="water surge", base_max_hit=22)
    EARTH_SURGE = StandardSpell(name="earth surge", base_max_hit=23)
    FIRE_SURGE = StandardSpell(name="fire surge", base_max_hit=24)

    # Unique StandardSpells
    CRUMBLE_UNDEAD = StandardSpell(name="crumble undead", base_max_hit=15)
    IBAN_BLAST = StandardSpell(name="iban blast", base_max_hit=25)

    # GodSpells
    # for some reason, only GodSpells make pylint throw an phantom error
    # pylint: disable=no-value-for-parameter
    SARADOMIN_STRIKE = GodSpell(name="saradomin strike")
    CLAWS_OF_GUTHIX = GodSpell(name="claws of guthix")
    FLAMES_OF_ZAMORAK = GodSpell(name="flames of zamorak")


FireSpells = (
    StandardSpells.FIRE_STRIKE,
    StandardSpells.FIRE_BOLT,
    StandardSpells.FIRE_BLAST,
    StandardSpells.FIRE_WAVE,
    StandardSpells.FIRE_SURGE,
)

BoltSpells = (
    StandardSpells.WIND_BOLT,
    StandardSpells.WATER_BOLT,
    StandardSpells.EARTH_BOLT,
    StandardSpells.FIRE_BOLT,
)

GodSpells = (
    StandardSpells.SARADOMIN_STRIKE,
    StandardSpells.CLAWS_OF_GUTHIX,
    StandardSpells.FLAMES_OF_ZAMORAK,
)

# ancient spells ##############################################################


@unique
class AncientSpells(Enum):
    SMOKE_RUSH = AncientSpell(name="smoke rush", base_max_hit=13)
    SHADOW_RUSH = AncientSpell(name="shadow rush", base_max_hit=14)
    BLOOD_RUSH = AncientSpell(name="blood rush", base_max_hit=15)
    ICE_RUSH = AncientSpell(name="ice rush", base_max_hit=16)
    SMOKE_BURST = AncientSpell(name="smoke burst", base_max_hit=17, max_targets_hit=9)
    SHADOW_BURST = AncientSpell(name="shadow burst", base_max_hit=18, max_targets_hit=9)
    BLOOD_BURST = AncientSpell(name="blood burst", base_max_hit=21, max_targets_hit=9)
    ICE_BURST = AncientSpell(name="ice burst", base_max_hit=22, max_targets_hit=9)
    SMOKE_BLITZ = AncientSpell(name="smoke blitz", base_max_hit=23)
    SHADOW_BLITZ = AncientSpell(name="shadow blitz", base_max_hit=24)
    BLOOD_BLITZ = AncientSpell(name="blood blitz", base_max_hit=25)
    ICE_BLITZ = AncientSpell(name="ice blitz", base_max_hit=26)
    SMOKE_BARRAGE = AncientSpell(
        name="smoke barrage", base_max_hit=27, max_targets_hit=9
    )
    SHADOW_BARRAGE = AncientSpell(
        name="shadow barrage", base_max_hit=28, max_targets_hit=9
    )
    BLOOD_BARRAGE = AncientSpell(
        name="blood barrage", base_max_hit=29, max_targets_hit=9
    )
    ICE_BARRAGE = AncientSpell(name="ice barrage", base_max_hit=30, max_targets_hit=9)


# powered spells ##############################################################


@unique
class PoweredSpells(Enum):
    TRIDENT_OF_THE_SEAS = PoweredSpell(name="trident of the seas", base_max_hit=20)
    TRIDENT_OF_THE_SWAMP = PoweredSpell(name="trident of the swamp", base_max_hit=23)
    SANGUINESTI_STAFF = PoweredSpell(name="sanguinesti staff", base_max_hit=24)
