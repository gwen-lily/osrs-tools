import math
from abc import ABC, abstractmethod
from attrs import define, field, validators
from enum import Enum, unique


from osrs_tools.exceptions import OsrsException


@define(order=True, frozen=True)
class Spell(ABC):
    name: str = field(validator=validators.instance_of(str))
    base_max_hit: int = field(validator=validators.instance_of(int))
    attack_speed: int = field(validator=validators.instance_of(int))
    max_targets_hit: int = field(validator=validators.instance_of(int))

    @abstractmethod
    def max_hit(self):
        pass


@define(order=True, frozen=True)
class StandardSpell(Spell):
    attack_speed: int = field(validator=validators.instance_of(int), default=5, init=False)
    max_targets_hit: int = field(validator=validators.instance_of(int), default=1, init=False)

    def max_hit(self):
        return self.base_max_hit


@define(order=True, frozen=False)
class GodSpell(StandardSpell):
    base_max_hit: int = field(validator=validators.instance_of(int), default=20, init=False)
    charged: bool = field(validator=validators.instance_of(bool), default=False)
    charge_bonus: int = field(validator=validators.instance_of(int), default=10, init=False)

    def max_hit(self, charged: bool = False) -> int:
        return self.base_max_hit + charged*self.charge_bonus


@define(order=True, frozen=True)
class AncientSpell(Spell):
    attack_speed: int = field(validator=validators.instance_of(int), default=5, init=False)
    max_targets_hit: int = field(validator=validators.instance_of(int), default=1)

    def max_hit(self):
        return self.base_max_hit


@define(order=True, frozen=True)
class PoweredSpell(Spell):
    attack_speed: int = field(validator=validators.instance_of(int), default=4, init=False)
    max_targets_hit: int = field(validator=validators.instance_of(int), default=1, init=False)

    def max_hit(self, visible_magic_level: int = None) -> int:
        try:
            minimum_visible_level = 75
            maximum_visible_level = 120
            stat = min([max([minimum_visible_level, visible_magic_level]), maximum_visible_level])
            scaled_base_max_hit = self.base_max_hit + math.floor((stat - minimum_visible_level) / 3)
            return scaled_base_max_hit
        except TypeError:
            raise SpellError(f'{visible_magic_level=} must be an integer for {self.name=}')


@unique
class StandardSpells(Enum):
    wind_strike = StandardSpell('wind strike', 2)
    water_strike = StandardSpell('water strike', 4)
    earth_strike = StandardSpell('earth strike', 6)
    fire_strike = StandardSpell('fire strike', 8)
    wind_bolt = StandardSpell('wind bolt', 9)
    water_bolt = StandardSpell('water bolt', 10)
    earth_bolt = StandardSpell('earth bolt', 11)
    fire_bolt = StandardSpell('fire bolt', 12)
    wind_blast = StandardSpell('wind blast', 13)
    water_blast = StandardSpell('water blast', 14)
    earth_blast = StandardSpell('earth blast', 15)
    fire_blast = StandardSpell('fire blast', 16)
    wind_wave = StandardSpell('wind wave', 17)
    water_wave = StandardSpell('water wave', 18)
    earth_wave = StandardSpell('earth wave', 19)
    fire_wave = StandardSpell('fire wave', 20)
    wind_surge = StandardSpell('wind surge', 21)
    water_surge = StandardSpell('water surge', 22)
    earth_surge = StandardSpell('earth surge', 23)
    fire_surge = StandardSpell('fire surge', 24)

    # Unique StandardSpells
    crumble_undead = StandardSpell('crumble undead', 15)
    iban_blast = StandardSpell('iban blast', 25)

    # GodSpells
    saradomin_strike = GodSpell('saradomin strike')
    claws_of_guthix = GodSpell('claws of guthix')
    flames_of_zamorak = GodSpell('flames of zamorak')


FireSpells = (
    StandardSpells.fire_strike,
    StandardSpells.fire_bolt,
    StandardSpells.fire_blast,
    StandardSpells.fire_wave,
    StandardSpells.fire_surge,
)

BoltSpells = (
    StandardSpells.wind_bolt,
    StandardSpells.water_bolt,
    StandardSpells.earth_bolt,
    StandardSpells.fire_bolt,
)

GodSpells = (
    StandardSpells.saradomin_strike,
    StandardSpells.claws_of_guthix,
    StandardSpells.flames_of_zamorak,
)


@unique
class AncientSpells(Enum):
    smoke_rush = AncientSpell('smoke rush', 13)
    shadow_rush = AncientSpell('shadow rush', 14)
    blood_rush = AncientSpell('blood rush', 15)
    ice_rush = AncientSpell('ice rush', 16)
    smoke_burst = AncientSpell('smoke burst', 17, 9)
    shadow_burst = AncientSpell('shadow burst', 18, 9)
    blood_burst = AncientSpell('blood burst', 21, 9)
    ice_burst = AncientSpell('ice burst', 22, 9)
    smoke_blitz = AncientSpell('smoke blitz', 23)
    shadow_blitz = AncientSpell('shadow blitz', 24)
    blood_blitz = AncientSpell('blood blitz', 25)
    ice_blitz = AncientSpell('ice blitz', 26)
    smoke_barrage = AncientSpell('smoke barrage', 27, 9)
    shadow_barrage = AncientSpell('shadow barrage', 28, 9)
    blood_barrage = AncientSpell('blood barrage', 29, 9)
    ice_barrage = AncientSpell('ice barrage', 30, 9)


@unique
class PoweredSpells(Enum):
    trident_of_the_seas = PoweredSpell('trident of the seas', 20)
    trident_of_the_swamp = PoweredSpell('trident of the swamp', 23)
    sanguinesti_staff = PoweredSpell('sanguinesti staff', 24)


class SpellError(OsrsException):
    pass
