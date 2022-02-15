from src.osrs_tools.character import *
from src.osrs_tools import analysis_tools
from src.osrs_tools.analysis_tools import ComparisonMode, DataMode

from tabulate import tabulate


def room_estimates(scale: int, hammers: int = 0, thralls: bool = False, **kwargs):
	"""
	This is for a solo iron boosted raid, where only one or two accounts will be allowed to deal damage. I was curious
	about the use of thralls and dragon warhammers so I wrote this lil method to check it out. It needs work.
	"""

	if scale >= 19:
		mystics_count = 12
	else:
		raise NotImplementedError

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


if __name__ == '__main__':
	my_scale = 31
	my_hammers = 3
	using_thralls = True

	data = []

	for i in range(my_hammers+1):
		row = room_estimates(my_scale, i, using_thralls)
		row_with_label = [i] + row
		data.append(row_with_label)

	headers = ['num dwh', 'kill time per mystic (ticks)', 'room completion (minutes)', 'super restores']
	table = tabulate(data, headers=headers, floatfmt='.0f')
	print(
		f'{"":-^38} {my_scale:>3} scale  {"":-^38}\n',
		table
	)
