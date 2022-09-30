from osrs_tools.character import *
from osrs_tools import analysis_tools
from osrs_tools.analysis_tools import ComparisonMode, DataMode

from itertools import product
import math
from tabulate import tabulate


def example_cartesian_comparison(data_mode: DataMode, **kwargs):
	"""
	Hello world example for the generic comparison method.

	The data spit out by generic_comparison are not obviously usable unless you're familiar with numpy. TODO: # Make
	user-friendly access methods that wrap generic_comparison along some classic (row, column) -> data questions like
	(equipment, monster) -> dps.

	:param data_mode: see DataMode for options.
	:param kwargs:
	:return:
	"""
	options = {
		'floatfmt': '.1f',
	}
	options.update(kwargs)

	Lad = Player(name='Big Lad')
	lads = [Lad]

	default_levels = PlayerLevels.maxed_player()
	levels = []
	for lvl in range(90, 99+1, 3):
		pl = copy(default_levels)
		pl.ranged = lvl
		levels.append(pl)

	prayers = Prayer.rigour()
	boosts = Overload.overload()

	# take care of basic equipment up front
	Lad.equipment.equip_basic_ranged_gear()
	Lad.equipment.equip_arma_set(barrows=False)
	Lad.active_style = Lad.equipment.equip_twisted_bow()

	equipment = [
		Equipment(hands=Gear.from_bb('barrows gloves')),
		Equipment(hands=Gear.from_bb('zaryte vambraces')),
		Equipment(
			head=Gear.from_bb('void knight helm'),
			body=Gear.from_bb('elite void top'),
			legs=Gear.from_bb('elite void robe'),
			hands=Gear.from_bb('void knight gloves'),
		)
	]

	monsters = []
	monster_names = [
		'deathly mage',
		'deathly ranger',
		'muttadile (big)',
		'vasa nistirio',
		'great olm',
	]

	for mn in monster_names:
		for scale in range(23, 23+1, 8):
			monsters.append(CoxMonster.from_de0(mn, scale))

	indices, axes, data = analysis_tools.generic_comparison_better(
		lads,
		levels=levels,
		prayers=prayers,
		boosts=boosts,
		equipment=equipment,
		target=monsters,
		comparison_mode=ComparisonMode.CARTESIAN,
		data_mode=data_mode,
		**kwargs
	)

	# we can grab slices, flatten dimensions, etc. for ease of viewing and as-needed for tabulation or data processing

	# this slice explores the relationship between (equipment, target) -> data
	rows_axis = 4
	row_vals = axes[rows_axis]
	columns_axis = 6
	columns_vals = axes[columns_axis]
	data_slice = data[0, -1, 0, 0, :, 0, :]
	data_as_lol = []

	for display, row_data in zip(row_vals, data_slice, strict=True):
		row_data = [display] + list(row_data)
		data_as_lol.append(row_data)

	table = tabulate(data_as_lol, headers=columns_vals, floatfmt=options['floatfmt'])
	print(table)

	# if we wanted to see ((equipment, level), target) -> data we could do this too
	rows_axes = (1, 4)
	rows_axes_dims = [len(axes[ax]) for ax in rows_axes]
	row_vals = list(product(*[axes[index] for index in rows_axes]))
	column_axis = 6
	column_axis_dim = len(axes[column_axis])
	columns_vals = axes[columns_axis]

	data_slice = data[0, :, 0, 0, :, 0, :]
	data_slice = data_slice.reshape(math.prod(rows_axes_dims), column_axis_dim)
	data_as_lol = []

	for display, row_data in zip(row_vals, data_slice, strict=True):
		row_data = [display] + list(row_data)
		data_as_lol.append(row_data)

	table = tabulate(data_as_lol, headers=columns_vals, floatfmt=options['floatfmt'])
	print(table)



def shamans_dps(data_mode: DataMode, comparison_mode: ComparisonMode, **kwargs):
	"""
	I'm curious about bone crossbows.

	:param data_mode: see DataMode for options.
	:param kwargs:
	:return:
	"""
	options = {
		'scale': 31,
		'floatfmt': '.1f',
		'special_attack': True,
	}
	options.update(kwargs)

	Lad = Player(name='Big Lad')
	Hybrid = Player(name='hybrid', levels=PlayerLevels.from_rsn('decihybrid'))
	Hybrid.prayers.pray(Prayer.rigour())
	boosts = [Overload.overload(), Boost.ranging_potion()]

	# take care of basic equipment up front
	Hybrid.equipment.equip_basic_ranged_gear(avas=False, pegasian=False)
	Hybrid.equipment.equip_god_dhide()
	Hybrid.active_style = Lad.equipment.equip(
		SpecialWeapon.from_bb('dorgeshuun crossbow'),
		Gear.from_bb('robin hood hat'),
		Gear.from_bb("ava's accumulator"),
		Gear.from_bb('bone bolts'),
		Gear.from_bb('twisted buckler'),
		style=CrossbowStyles.get_style(PlayerStyle.longrange)
	)

	monsters = CoxMonster.from_de0('lizardman shaman', options['scale'])
	monsters.apply_vulnerability()

	indices, axes, data = analysis_tools.generic_comparison_better(
		Hybrid,
		boosts=boosts,
		target=monsters,
		comparison_mode=comparison_mode,
		data_mode=data_mode,
		**kwargs
	)

	for i, a, d in zip(indices, axes, data):
		print(i, a, data)


if __name__ == '__main__':
	# example_cartesian_comparison(data_mode=DataMode.DPS, floatfmt='.1f')
	my_scale = 31
	shamans_dps(data_mode=DataMode.MAX_HIT, comparison_mode=ComparisonMode.PARALLEL, floatfmt='.1f', scale=my_scale)