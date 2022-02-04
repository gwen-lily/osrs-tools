from src.osrs_tools.character import *
from src.osrs_tools import analysis_tools
from tabulate import tabulate

csc = cox.graph_wrapper(cox.table_wrapper(cox.scale_comparison))


def crossbow_comparison(scales, **kwargs):
	dcb = Player(name='dragon crossbow')
	acb = Player(name='armadyl crossbow')
	zcb = Player(name='zaryte crossbow')
	lads = (dcb, acb, zcb,)
	weapons = (
		SpecialWeapon.from_bb('dragon crossbow'),
		SpecialWeapon.from_bb('armadyl crossbow'),
		SpecialWeapon.from_bb('zaryte crossbow'),
	)
	styles = (CrossbowStyles.get_style(PlayerStyle.rapid), )*3
	ammos = (Gear.from_bb('ruby dragon bolts (e)'), )*3

	for lad, weapon, style, ammo in zip(lads, weapons, styles, ammos):
		lad.prayers.pray(Prayer.rigour())
		lad.boost(Overload.overload())
		lad.active_style = lad.equipment.equip(weapon, ammo, style=style)
		lad.equipment.equip_basic_ranged_gear(anguish=False)
		lad.equipment.equip_salve()

	csc(players=lads, monster_name='skeletal mystic', scales=scales, **kwargs)


def example_mystics_comparison(**kwargs):

	def dps_func(inner_player: Player, inner_equipment: Equipment, inner_target: Character, **inner_kwargs) -> float:
		default_equipment = copy(inner_player.equipment)
		default_active_style = inner_player.active_style
		new_equipment_tuple = astuple(inner_equipment, recurse=False)
		inner_style = kwargs['style'] if 'style' in kwargs else None
		inner_style = inner_player.equipment.equip(*new_equipment_tuple, style=inner_style)

		if inner_style:
			inner_player.active_style = inner_style

		dam = inner_player.damage_distribution(inner_target, **inner_kwargs)
		inner_player.equipment = default_equipment
		inner_player.active_style = default_active_style

		return dam.per_second

	Lad = Player(name='Ladd Russo')
	lads = (Lad, )

	Lad.equipment.equip_basic_ranged_gear(anguish=False)
	Lad.equipment.equip_salve()
	Lad.equipment.equip_arma_set(zaryte=True)
	Lad.boost(Overload.overload())
	Lad.prayers.pray(Prayer.rigour())

	tbow = Weapon.from_bb('twisted bow')
	fbow = Weapon.from_bb('bow of faerdhinen')
	dcb = SpecialWeapon.from_bb('dragon crossbow')
	acb = SpecialWeapon.from_bb('armadyl crossbow')
	zcb = SpecialWeapon.from_bb('zaryte crossbow')
	buckler = Gear.from_bb('twisted buckler')

	d_arrows = Gear.from_bb('dragon arrow')
	dr_bolts = Gear.from_bb('ruby dragon bolts (e)')

	crys_helm = Gear.from_bb('crystal helm')
	crys_body = Gear.from_bb('crystal body')
	crys_legs = Gear.from_bb('crystal legs')

	equipments = [
		Equipment(weapon=tbow, ammunition=d_arrows),
		Equipment(weapon=fbow, head=crys_helm, body=crys_body, legs=crys_legs),
		Equipment(weapon=dcb, shield=buckler, ammunition=dr_bolts),
		Equipment(weapon=acb, shield=buckler, ammunition=dr_bolts),
		Equipment(weapon=zcb, shield=buckler, ammunition=dr_bolts),
	]

	mystic = SkeletalMystic.from_de0(kwargs['scale'])
	headers = [str(e.weapon.name) for e in equipments]

	tabulator = cox.table_wrapper(cox.equipment_comparison)
	tabulator(
		players=lads,
		equipments=equipments,
		data_func=dps_func,
		target=mystic,
		headers=headers
	)


def crystal_armour_comparison(scales, **kwargs):
	arma_tbow = Player(name='arma tbow')
	crystal_tbow = Player(name='crystal tbow')
	lads = [arma_tbow, crystal_tbow]

	for lad in lads:
		lad.equipment.equip_basic_ranged_gear()
		lad.equipment.equip_salve()
		lad.active_style = lad.equipment.equip_twisted_bow()
		lad.prayers.pray(Prayer.rigour(), Prayer.protect_from_magic())
		lad.boost(Overload.overload())

	arma_tbow.equipment.equip_arma_set(zaryte=True)
	crystal_tbow.equipment.equip_crystal_set(zaryte=True)
	csc(players=lads, monster_name='skeletal mystic', scales=scales, **kwargs)
	csc(players=lads, monster_name='great olm', scales=scales, **kwargs)

	data = [[p.name, p.ticks_per_pp_lost, math.floor(1/p.ticks_per_pp_lost * 100)] for p in lads]
	header = ['player', 'ticks per pp lost', 'pp lost per minute']
	table = tabulate(data, header, tablefmt='pretty')
	print(table)


def mystics_comparison(scales, **kwargs):
	tbow = Player(name='tbow')
	acb = Player(name='acb')
	bp = Player(name='bp (dd)')
	lads = (tbow, acb, bp)
	weapons = (
		Weapon.from_bb('twisted bow'),
		SpecialWeapon.from_bb('armadyl crossbow'),
		SpecialWeapon.from_bb('toxic blowpipe'),
	)
	styles = (
		BowStyles.get_style(PlayerStyle.rapid),
		CrossbowStyles.get_style(PlayerStyle.rapid),
		ThrownStyles.get_style(PlayerStyle.rapid),
	)
	ammos = (
		Gear.from_bb('dragon arrow'),
		Gear.from_bb('ruby dragon bolts (e)'),
		Gear.from_bb('dragon dart')
	)

	for lad, weapon, style, ammo in zip(lads, weapons, styles, ammos):
		lad.prayers.pray(Prayer.rigour())
		lad.boost(Overload.overload())
		lad.active_style = lad.equipment.equip(weapon, ammo, style=style)
		lad.equipment.equip_basic_ranged_gear(anguish=False)
		lad.equipment.equip_salve()
		lad.equipment.equip_arma_set(zaryte=True)

	csc(players=lads, monster_name='skeletal mystic', scales=scales, **kwargs)


def skill_by_monsters(
		base_player: Player,
		boosts: Boost | list[Boost, ...],
		prayers: Prayer | PrayerCollection,
		skill: str,
		skill_values: int | list[int, ...],
		monsters: Monster | list[Monster, ...],
		**kwargs
):

	lads = []
	boosts = [boosts,] if isinstance(boosts, Boost) else boosts
	prayers = PrayerCollection(prayers=(prayers, )) if isinstance(prayers, Prayer) else prayers
	skill_values = [skill_values, ] if isinstance(skill_values, int) else skill_values
	monsters = [monsters, ] if isinstance(monsters, Monster) else monsters

	options = {
		'data': 'dps',
	}
	options.update(kwargs)


	for sv in skill_values:
		base_stats = copy(base_player.levels)
		base_equip = copy(base_player.equipment)
		base_stats.__setattr__(skill, sv)
		lads.append(Player(name=f'{skill}: {sv}', levels=base_stats, prayers=prayers, equipment=base_equip))

	for lad in lads:
		lad.boost(*boosts)

	def dps_func(inner_player: Player, inner_target: Monster, **inner_kwargs) -> float:
		dam = inner_player.damage_distribution(inner_target, **inner_kwargs)

		if (data_key := inner_kwargs['data']) == 'object':
			return dam
		elif data_key == 'dps':
			return dam.per_second
		elif data_key == 'dpt':
			return dam.per_tick
		elif data_key == 'max hit':
			return dam.max_hit
		else:
			return dam

	tabulator = cox.table_wrapper(cox.generic_comparison)

	return tabulator(
		players=lads,
		data_func=dps_func,
		input_vals=monsters,
		**options
	)
	# tabulator = cox.table_wrapper(cox.generic_comparison)
	# tabulator(
	# 	players=lads,
	# 	data_func=dps_func,
	# 	input_vals=monsters,
	# 	**options
	# )


def main(**kwargs):
	# scales = range(15, 32, 1)
	# crossbow_comparison(scales, data='dps', floatfmt='.1f')
	# crystal_armour_comparison(scales, data='dps', floatfmt='.1f')
	# for scale in range(15, 55, 8):
	# 	example_mystics_comparison(scale=scale)

	Lad = Player(name='template lad')
	Lad.equipment.equip_basic_ranged_gear()
	Lad.equipment.equip_arma_set(zaryte=True)
	Lad.active_style = Lad.equipment.equip_black_chins()

	boosts = Overload.overload()
	prayers = Prayer.rigour()
	skill = Skills.ranged
	skill_values = list(range(80, 99+1))
	monster_names = [
		'deathly mage',
		'deathly ranger',
		'lizardman shaman',
	]
	scales = kwargs['scales'] if 'scales' in kwargs else range(15, 31+1, 8)
	monsters = 	[CoxMonster.from_de0(mn, scale) for scale in scales for mn in monster_names]
	# for scale in scales:
	# 	for mn in monster_names:
	# 		monsters.append(CoxMonster.from_de0(name=mn, party_size=scale))



	skill_by_monsters(Lad, boosts, prayers, skill, skill_values, monsters, **kwargs)


if __name__ == '__main__':
	scales = range(15, 31+1, 8)
	distance = 9
	additional_targets = 0
	floatfmt = '.2f'

	main(scales=scales, distance=distance, additional_targets=additional_targets, floatfmt=floatfmt, data='dps')
