import math
from typing import List


class Spell:

	def __init__(self, name: str, base_max_hit: int, attack_speed: int, max_targets_hit: int):
		self.name = name
		self._base_max_hit = base_max_hit
		self.attack_speed = attack_speed
		self.max_targets_hit = max_targets_hit

	def base_max_hit(self):
		return self._base_max_hit


class StandardSpell(Spell):

	def __init__(self, name: str, base_max_hit: int):
		attack_speed = 5
		max_targets_hit = 1
		super(StandardSpell, self).__init__(name, base_max_hit, attack_speed, max_targets_hit)


class GodSpell(StandardSpell):
	charge_bonus = 10

	def __init__(self, name: str):
		base_max_hit = 20
		super(GodSpell, self).__init__(name, base_max_hit)
		self._charged = False

	def base_max_hit(self, charged: bool = False):
		return self._base_max_hit + charged * self.charge_bonus


class AncientSpell(Spell):

	def __init__(self, name: str, base_max_hit: int, aoe: bool = False):
		attack_speed = 5
		max_targets_hit = 9 if aoe else 1
		super(AncientSpell, self).__init__(name, base_max_hit, attack_speed, max_targets_hit)


class PoweredSpell(Spell):

	def __init__(self, name: str, base_max_hit: int):
		attack_speed = 4
		max_targets_hit = 1
		super(PoweredSpell, self).__init__(name, base_max_hit, attack_speed, max_targets_hit)

	def base_max_hit(self, visible_magic_level: int = None):
		if not visible_magic_level:
			raise Exception('you must provide a visible magic level to spells.PoweredSpell.base_max_hit')
		minimum_visible_level = 75
		maximum_visible_level = 120
		stat = min([maximum_visible_level, max([minimum_visible_level, visible_magic_level])])
		scaled_base_max_hit = self._base_max_hit + math.floor((stat - minimum_visible_level) / 3)
		return scaled_base_max_hit


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

crumble_undead = StandardSpell('crumble undead', 15)
iban_blast = StandardSpell('iban blast', 25)

saradomin_strike = GodSpell('saradomin strike')
claws_of_guthix = GodSpell('claws of guthix')
flames_of_zamorak = GodSpell('flames of zamorak')

smoke_rush = AncientSpell('smoke rush', 13)
shadow_rush = AncientSpell('shadow rush', 14)
blood_rush = AncientSpell('blood rush', 15)
ice_rush = AncientSpell('ice rush', 16)
smoke_burst = AncientSpell('smoke burst', 17, True)
shadow_burst = AncientSpell('shadow burst', 18, True)
blood_burst = AncientSpell('blood burst', 21, True)
ice_burst = AncientSpell('ice burst', 22, True)
smoke_blitz = AncientSpell('smoke blitz', 23)
shadow_blitz = AncientSpell('shadow blitz', 24)
blood_blitz = AncientSpell('blood blitz', 25)
ice_blitz = AncientSpell('ice blitz', 26)
smoke_barrage = AncientSpell('smoke barrage', 27, True)
shadow_barrage = AncientSpell('shadow barrage', 28, True)
blood_barrage = AncientSpell('blood barrage', 29, True)
ice_barrage = AncientSpell('ice barrage', 30, True)


trident_of_the_seas = PoweredSpell('trident of the seas', 20)
trident_of_the_swamp = PoweredSpell('trident of the swamp', 23)
sanguinesti_staff = PoweredSpell('sanguinesti staff', 24)

spells: List[Spell] = [
	wind_strike,
	water_strike,
	earth_strike,
	fire_strike,
	wind_bolt,
	water_bolt,
	earth_bolt,
	fire_bolt,
	wind_blast,
	water_blast,
	earth_blast,
	fire_blast,
	wind_wave,
	water_wave,
	earth_wave,
	fire_wave,
	wind_surge,
	water_surge,
	earth_surge,
	fire_surge,
	crumble_undead,
	iban_blast,
	saradomin_strike,
	claws_of_guthix,
	flames_of_zamorak,
	smoke_rush,
	shadow_rush,
	blood_rush,
	ice_rush,
	smoke_burst,
	shadow_burst,
	blood_burst,
	ice_burst,
	smoke_blitz,
	shadow_blitz,
	blood_blitz,
	ice_blitz,
	smoke_barrage,
	shadow_barrage,
	blood_barrage,
	ice_barrage,
	trident_of_the_seas,
	trident_of_the_swamp,
	sanguinesti_staff,
]

fire_spells = [
	fire_strike,
	fire_bolt,
	fire_blast,
	fire_wave,
	fire_surge
]

bolt_spells = [
	wind_bolt,
	water_bolt,
	earth_bolt,
	fire_bolt
]

if __name__ == '__main__':
	pass
