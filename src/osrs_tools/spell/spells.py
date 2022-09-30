"""Definition of all spells in OSRS

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-                                                             #
###############################################################################
"""

from enum import Enum, unique

from osrs_tools.tracked_value import DamageValue

from .spell import AncientSpell, GodSpell, PoweredSpell, StandardSpell, TumekenPoweredSpell

# standard spells #############################################################


@unique
class StandardSpells(Enum):
    WIND_STRIKE = StandardSpell(name="wind strike", base_max_hit=DamageValue(2))
    WATER_STRIKE = StandardSpell(name="water strike", base_max_hit=DamageValue(4))
    EARTH_STRIKE = StandardSpell(name="earth strike", base_max_hit=DamageValue(6))
    FIRE_STRIKE = StandardSpell(name="fire strike", base_max_hit=DamageValue(8))
    WIND_BOLT = StandardSpell(name="wind bolt", base_max_hit=DamageValue(9))
    WATER_BOLT = StandardSpell(name="water bolt", base_max_hit=DamageValue(10))
    EARTH_BOLT = StandardSpell(name="earth bolt", base_max_hit=DamageValue(11))
    FIRE_BOLT = StandardSpell(name="fire bolt", base_max_hit=DamageValue(12))
    WIND_BLAST = StandardSpell(name="wind blast", base_max_hit=DamageValue(13))
    WATER_BLAST = StandardSpell(name="water blast", base_max_hit=DamageValue(14))
    EARTH_BLAST = StandardSpell(name="earth blast", base_max_hit=DamageValue(15))
    FIRE_BLAST = StandardSpell(name="fire blast", base_max_hit=DamageValue(16))
    WIND_WAVE = StandardSpell(name="wind wave", base_max_hit=DamageValue(17))
    WATER_WAVE = StandardSpell(name="water wave", base_max_hit=DamageValue(18))
    EARTH_WAVE = StandardSpell(name="earth wave", base_max_hit=DamageValue(19))
    FIRE_WAVE = StandardSpell(name="fire wave", base_max_hit=DamageValue(20))
    WIND_SURGE = StandardSpell(name="wind surge", base_max_hit=DamageValue(21))
    WATER_SURGE = StandardSpell(name="water surge", base_max_hit=DamageValue(22))
    EARTH_SURGE = StandardSpell(name="earth surge", base_max_hit=DamageValue(23))
    FIRE_SURGE = StandardSpell(name="fire surge", base_max_hit=DamageValue(24))

    # Unique StandardSpells
    CRUMBLE_UNDEAD = StandardSpell(name="crumble undead", base_max_hit=DamageValue(15))
    IBAN_BLAST = StandardSpell(name="iban blast", base_max_hit=DamageValue(25))

    # GodSpells
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
    SMOKE_RUSH = AncientSpell(name="smoke rush", base_max_hit=DamageValue(13))
    SHADOW_RUSH = AncientSpell(name="shadow rush", base_max_hit=DamageValue(14))
    BLOOD_RUSH = AncientSpell(name="blood rush", base_max_hit=DamageValue(15))
    ICE_RUSH = AncientSpell(name="ice rush", base_max_hit=DamageValue(16))
    SMOKE_BURST = AncientSpell(name="smoke burst", base_max_hit=DamageValue(17), max_targets_hit=9)
    SHADOW_BURST = AncientSpell(name="shadow burst", base_max_hit=DamageValue(18), max_targets_hit=9)
    BLOOD_BURST = AncientSpell(name="blood burst", base_max_hit=DamageValue(21), max_targets_hit=9)
    ICE_BURST = AncientSpell(name="ice burst", base_max_hit=DamageValue(22), max_targets_hit=9)
    SMOKE_BLITZ = AncientSpell(name="smoke blitz", base_max_hit=DamageValue(23))
    SHADOW_BLITZ = AncientSpell(name="shadow blitz", base_max_hit=DamageValue(24))
    BLOOD_BLITZ = AncientSpell(name="blood blitz", base_max_hit=DamageValue(25))
    ICE_BLITZ = AncientSpell(name="ice blitz", base_max_hit=DamageValue(26))
    SMOKE_BARRAGE = AncientSpell(name="smoke barrage", base_max_hit=DamageValue(27), max_targets_hit=9)
    SHADOW_BARRAGE = AncientSpell(name="shadow barrage", base_max_hit=DamageValue(28), max_targets_hit=9)
    BLOOD_BARRAGE = AncientSpell(name="blood barrage", base_max_hit=DamageValue(29), max_targets_hit=9)
    ICE_BARRAGE = AncientSpell(name="ice barrage", base_max_hit=DamageValue(30), max_targets_hit=9)


# powered spells ##############################################################


@unique
class PoweredSpells(Enum):
    TRIDENT_OF_THE_SEAS = PoweredSpell(name="trident of the seas", base_max_hit=DamageValue(20))
    TRIDENT_OF_THE_SWAMP = PoweredSpell(name="trident of the swamp", base_max_hit=DamageValue(23))
    SANGUINESTI_STAFF = PoweredSpell(name="sanguinesti staff", base_max_hit=DamageValue(24))
    TUMEKENS_SHADOW = TumekenPoweredSpell()
