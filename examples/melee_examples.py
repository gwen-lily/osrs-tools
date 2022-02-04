from copy import copy

from src.osrs_tools.character import *
from src.osrs_tools import analysis_tools


cvc = cox.graph_wrapper(cox.table_wrapper(cox.variable_comparison))
cec = cox.table_wrapper(cox.equipment_comparison)
# cvc = cox.graph_wrapper(cox.variable_comparison)


def olm_comparison(**kwargs):
	TorvaLad = Player(name='torva')
	InquisitorChopLad = Player(name='inquisitor (chop)')
	InquisitorJabLad = Player(name='inquisitor (jab)')
	BandosLad = Player(name='bandos')

	lads = (TorvaLad, InquisitorChopLad, InquisitorJabLad, BandosLad)
	styles = (ScytheStyles.get_style(x) for x in (PlayerStyle.chop, PlayerStyle.chop, PlayerStyle.jab, PlayerStyle.chop))

	for lad, style in zip(lads, styles):
		lad.active_style = lad.equipment.equip_scythe(style=style)
		lad.equipment.equip_basic_melee_gear()
		lad.boost(Overload.overload())
		lad.prayers.pray(Prayer.piety())

	TorvaLad.equipment.equip_torva_set()
	InquisitorChopLad.equipment.equip_inquisitor_set()
	InquisitorJabLad.equipment.equip_inquisitor_set()
	BandosLad.equipment.equip_bandos_set()

	big_olm = OlmMeleeHand.from_de0(1)

	cvc(
		players=lads,
		monster_name=big_olm.name,
		**kwargs
	)

#
# def brew_comparison(**kwargs):
# 	InquisitorLad = Player(name='inquisitor')
# 	BandosLad = Player(name='bandos')
#
# 	lads = (InquisitorLad, BandosLad)
# 	styles = (ScytheStyles.get_style(x) for x in (PlayerStyle.chop, PlayerStyle.chop, PlayerStyle.jab, PlayerStyle.chop))
#
# 	for lad, style in zip(lads, styles):
# 		lad.active_style = lad.equipment.equip_scythe(style=style)
# 		lad.equipment.equip_basic_melee_gear()
# 		lad.boost(Overload.overload())
# 		lad.prayers.pray(Prayer.piety())
#
# 	TorvaLad.equipment.equip_torva_set()
# 	InquisitorChopLad.equipment.equip_inquisitor_set()
# 	InquisitorLad.equipment.equip_inquisitor_set()
# 	BandosLad.equipment.equip_bandos_set()
#
# 	big_olm = OlmMeleeHand.from_de0(1)
#
# 	cvc(
# 		players=lads,
# 		monster_name=big_olm.name,
# 		skill_var=Skills.defence,
# 		values=np.arange(0, 30+1),
# 		**kwargs
# 	)


def torva_upgrade(**kwargs):
	OverLad = Player(name='overload')
	ScbLad = Player(name='scb')
	lads = (OverLad, ScbLad)
	boosts = (Overload.overload(), Boost.super_combat_potion())

	for lad, boost in zip(lads, boosts):
		lad.equipment.equip_basic_melee_gear()
		lad.equipment.equip_bandos_set()
		lad.active_style = lad.equipment.equip_scythe()
		lad.boost(boost)
		lad.prayers.pray(Prayer.piety())

	smolm = OlmMeleeHand.from_de0(1)

	head = Gear.from_bb('torva full helm')
	body = Gear.from_bb('torva platebody')
	legs = Gear.from_bb('torva platelegs')

	upgrades = (
		Equipment(head=head),
		Equipment(body=body),
		Equipment(legs=legs),
		Equipment(head=head, body=body),
		Equipment(head=head, legs=legs),
		Equipment(body=body, legs=legs),
		Equipment(head=head, body=body, legs=legs)
	)

	cec(players=lads, target=smolm, loadouts=upgrades, **kwargs)


def generic_relevant_type_bonus(**kwargs):

	def get_type_bonus(inner_player: Player, *args, **kwargs):
		assert len(args) == 1
		return inner_player.equipment.aggressive_bonus.__getattribute__(args[0])

	TorvaLad = Player(name='torva')
	DwhLad = Player(name='dwh')
	lads = (TorvaLad, DwhLad)

	for lad in lads:
		lad.equipment.equip_basic_melee_gear()
		lad.boost(Overload.overload())
		lad.prayers.pray(Prayer.piety())

	TorvaLad.equipment.equip_torva_set()
	TorvaLad.active_style = TorvaLad.equipment.equip_scythe()
	DwhLad.active_style = DwhLad.equipment.equip_dwh()

	generic_comp = cox.table_wrapper(cox.generic_comparison(
		players=lads,
		data_func=get_type_bonus,
		input_vals=((PlayerStyle.slash, ), (PlayerStyle.crush, )),
		data='dps',
		floatfmt='.1f'
	))


def dwh_land_comparison(**kwargs):

	def get_nonzero_damage_chance_per_olm(inner_player: Player, party_size: int, **inner_kwargs) -> float:
		olm = OlmMeleeHand.from_de0(party_size=party_size, **inner_kwargs)
		return inner_player.damage_distribution(olm, special_attack=True, **inner_kwargs).chance_to_deal_positive_damage

	TorvaDwh = Player(name='torva')
	InquisitorDwh = Player(name='inquisitor')
	BandosDwh = Player(name='bandos')
	lads = (TorvaDwh, InquisitorDwh, BandosDwh)

	for lad in lads:
		lad.equipment.equip_basic_melee_gear(berserker=False)
		lad.equipment.equip_dwh()
		lad.boost(Overload.overload())
		lad.prayers.pray(Prayer.piety())

	TorvaDwh.equipment.equip_torva_set()
	BandosDwh.equipment.equip_bandos_set()

	scales = np.arange(15, 55+1, 8)
	headers = list(scales)

	table_comp = cox.table_wrapper(cox.generic_comparison)
	table_comp(
		players=lads,
		data_func=get_nonzero_damage_chance_per_olm,
		input_vals=scales,
		shared_input=True,
		headers=headers,
		floatfmt='.2f',
		**kwargs
	)


def example_choob_gear_upgrade(**kwargs):

	def dps_func(inner_player: Player, inner_equipment: Equipment, inner_target: Character, **inner_kwargs) -> float:
		default_equipment = copy(inner_player.equipment)
		default_active_style = inner_player.active_style
		new_equipment_tuple = astuple(inner_equipment, recurse=False)
		style = kwargs['style'] if 'style' in kwargs else None
		style = inner_player.equipment.equip(*new_equipment_tuple, style=style)

		if style:
			inner_player.active_style = style

		dam = inner_player.damage_distribution(inner_target, **inner_kwargs)
		inner_player.equipment = default_equipment
		inner_player.active_style = default_active_style

		return dam.per_second

	Choob = Player(name='choob')
	Choob.levels.attack = 95
	Choob.levels.strength = 98
	Choob.reset_stats()
	Choob.active_style = Choob.equipment.equip(
		Gear.from_bb('neitiznot'),
		Gear.from_bb('fire cape'),
		Gear.from_bb('amulet of torture'),
		Weapon.from_bb('dragon hunter lance'),
		Gear.from_bb('fighter torso'),
		Gear.from_bb('dragon defender'),
		Gear.from_bb('obsidian platelegs'),
		Gear.from_bb('barrows gloves'),
		Gear.from_bb('dragon boots'),
		Gear.from_bb('berserker (i)'),
	)
	Choob.prayers.pray(Prayer.piety())
	Choob.boost(Overload.overload())

	possible_upgrades = (
		None,
		Gear.from_bb('neitiznot faceguard'),
		Weapon.from_bb('scythe of vitur'),
		Gear.from_bb('bandos chestplate'),
		Gear.from_bb('avernic defender'),
		Gear.from_bb('bandos tassets'),
		Gear.from_bb('ferocious gloves'),
		Gear.from_bb('primordial boots'),
	)
	possible_upgrades = [Equipment.from_unordered(g) for g in possible_upgrades]

	low_def_olm = OlmMeleeHand.from_de0(5)
	low_def_olm.active_levels.defence = 0

	headers = ['dps']
	headers.extend((str(e) for e in possible_upgrades))

	foo, bar = cec(
		players=(Choob, ),
		equipments=possible_upgrades,
		data_func=dps_func,
		target=low_def_olm,
		headers=headers,
		**kwargs,
	)




def main():
	# olm_comparison(skill_var=Skills.defence, values=np.arange(0, 30+1), data='dps', floatfmt='.2f')
	# torva_upgrade(data='dps', floatfmt='.1f', mode='comparison')
	# generic_relevant_type_bonus()
	# dwh_land_comparison()
	example_choob_gear_upgrade()


if __name__ == '__main__':
	main()





