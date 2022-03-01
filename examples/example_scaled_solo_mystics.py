from osrs_tools.character import *
from osrs_tools import analysis_tools
from osrs_tools.analysis_tools import ComparisonMode, DataMode

from tabulate import tabulate


def room_estimates(scale: int, hammers: int = 0, thralls: bool = False, **kwargs):
	"""
	This is for a solo iron boosted raid, where only one or two accounts will be allowed to deal damage. I was curious
	about the use of thralls and dragon warhammers so I wrote this lil method to check it out. It needs work.
	"""

	mystics_count = min([3 + math.floor(scale / 3), 12])    # cap: party size 27 ~ 12 mystics

	lad = Player(name='lad')
	lad.boost(Overload.overload())
	lad.prayers.pray(Prayer.rigour(), Prayer.protect_from_magic())
	lad.equipment.equip_arma_set(zaryte=True)
	lad.equipment.equip_basic_ranged_gear(anguish=False)
	lad.equipment.equip_salve()
	lad.active_style = lad.equipment.equip_twisted_bow()

	mystic = SkeletalMystic.from_de0(scale)

	for _ in range(hammers):
		mystic.apply_dwh()

	dam = lad.damage_distribution(mystic)
	dpt = dam.per_tick + 0.625*thralls

	ticks_per_mystic = mystic.levels.hitpoints / dpt
	ticks_total = ticks_per_mystic * mystics_count
	minutes_total = ticks_total / 100

	pp_used_by_prayer = ticks_total / lad.ticks_per_pp_lost
	pp_user_per_summon = 6
	ticks_per_summon = 120
	pp_used_by_thralls = ticks_total / ticks_per_summon * pp_user_per_summon
	pp_used = pp_used_by_prayer + pp_used_by_thralls

	lad.active_levels.prayer = 0
	lad.boost(Boost.super_restore())
	pp_gained_per_restore = lad.active_levels.prayer * 4
	super_restore_used = np.ceil(pp_used / pp_gained_per_restore)

	table_data = [ticks_per_mystic, minutes_total, super_restore_used]
	return table_data


def dwh_setup(**kwargs):
	options = {
		'floatfmt': '.1f',
		'datamode': DataMode.DWH_SUCCESS,
		'scales': range(15, 32, 8),
		'strength_levels': None
	}
	options.update(kwargs)

	strength_levels = range(0, 99+1) if options['strength_levels'] is None else options['strength_levels']

	lad = Player(name='thwack lad')
	levels = [PlayerLevels(attack=99, strength=i) for i in strength_levels]

	boosts = [Boost.super_attack_potion()]
	lad.prayers.pray(Prayer.piety())

	lad.equipment.equip_basic_melee_gear()  # lots of overwrite
	lad.active_style = lad.equipment.equip_dwh(tyrannical=True)
	lad.equipment.equip_salve()
	lad.equipment.equip(mythical_cape)

	set_1 = Equipment()
	set_1.equip_bandos_set()
	set_1.equip(dwarven_helmet)
	assert set_1.wearing(head=dwarven_helmet)
	set_2 = Equipment()
	set_2.equip_inquisitor_set()
	set_3 = Equipment()
	set_3.equip_void_set(elite=True)

	equipments = [set_1, set_2]     # , set_3]

	mystics = [SkeletalMystic.from_de0(ps) for ps in options['scales']]

	indices, axes, data_ary = analysis_tools.generic_comparison_better(
		lad,
		levels=levels,
		boosts=boosts,
		equipment=equipments,
		target=mystics,
		comparison_mode=ComparisonMode.CARTESIAN,
		data_mode=options['datamode'],
		special_attack=True,
		**options,
	)

	slice_3d = data_ary[0, :, 0, 0, :, 0, :]

	# gear_by_monster_at_0_strength = slice_3d[0, :, :]
	gear_by_strength_at_1_scale = slice_3d[:, :, -1].T
	column_headers: list[str | int] = [DataMode.DWH_SUCCESS.name] + [lev.strength for lev in levels]

	print(analysis_tools.tabulate_wrapper(
		gear_by_strength_at_1_scale,
		column_headers,
		equipments,
		**options,
	))


if __name__ == '__main__':
	# my_scale = 31
	# my_hammers = 3
	# using_thralls = True
	#
	# data = []
	#
	# for i in range(my_hammers+1):
	# 	row = room_estimates(my_scale, i, using_thralls)
	# 	row_with_label = [i] + row
	# 	data.append(row_with_label)
	#
	# headers = ['num dwh', 'kill time per mystic (ticks)', 'room completion (minutes)', 'super restores']
	# table = tabulate(data, headers=headers, floatfmt='.0f')
	# print(
	# 	f'{"":-^38} {my_scale:>3} scale  {"":-^38}\n',
	# 	table
	# )
	dwarven_helmet = Gear.from_bb('dwarven helmet')
	mythical_cape = Gear.from_bb('mythical cape')

	float_fmts = ['5.3f', '5.0f']
	data_modes = [DataMode.DWH_SUCCESS, DataMode.MAX_HIT]

	for ff, dm in zip(float_fmts, data_modes):
		dwh_setup(scales=(1, ), strength_levels=range(0, 20+1), floatfmt=ff, datamode=dm)
