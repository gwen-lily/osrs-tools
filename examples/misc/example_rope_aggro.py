import numpy as np

from osrs_tools.character import *
from osrs_tools import analysis_tools
from osrs_tools.analysis_tools import ComparisonMode, DataMode

from itertools import product
import math
from tabulate import tabulate


def aggro_check(**kwargs):
	options = {
		'floatfmt': '.2f',
		'scales': range(15, 32, 8)
	}
	options.update(kwargs)

	lad = Player(name='hybrid tank')
	lad.boost(Overload.overload())
	lad.prayers_coll.pray(Prayer.augury())

	lad.active_style = lad.equipment.equip(
		Gear.from_osrsbox('bearhead'),
		Gear.from_osrsbox('imbued zamorak cape'),
		Gear.from_osrsbox('amulet of fury'),
		Gear.from_osrsbox('bone bolts'),
		Weapon.from_bb('trident of the seas'),
		Gear.from_osrsbox("Karil's leathertop"),
		Gear.from_osrsbox('twisted buckler'),
		Gear.from_osrsbox("Karil's leatherskirt"),
		Gear.from_osrsbox('saradomin bracers'),
		Gear.from_osrsbox('eternal boots'),
		Gear.from_osrsbox('seers ring (i)'),
	)

	monster_classes = [DeathlyMage, DeathlyRanger]
	monsters = []

	for mc in monster_classes:
		for scale in options['scales']:
			monsters.append(mc.from_de0(scale))

	indices, axes, data_ary = analysis_tools.bedevere_the_wise(
		lad,
		target=monsters,
		comparison_mode=ComparisonMode.PARALLEL,
		data_mode=DataMode.POSITIVE_DAMAGE
	)

	print(data_ary)


def hybrid_tank(**kwargs):
	options = {
		'floatfmt': '.1f',
		'scales': range(15, 32, 8)
	}
	options.update(kwargs)

	player_names = [
		'void tank',
		'mage tank',
		'range tank',
	]

	lads = tuple(Player(name=name) for name in player_names)
	void_tank, mage_tank, range_tank = lads

	for lad in lads:
		print('foo')
		lad.active_style = lad.equipment.equip(
			imbued_god_cape,
			fury,
			bone_bolts,
			trident,
			buckler,
			eternals,
			suffering
		)
		lad.boost(Overload.overload())
		lad.prayers_coll.pray(Prayer.augury())

	void_tank.equipment.equip_void_set()


def chin_estimate(**kwargs):
	options = {
		'floatfmt': '.1f',
		'scales': range(15, 32, 8),
	}
	options.update(kwargs)
	scales = options['scales']

	greys = Weapon.from_bb('chinchompa')
	reds = Weapon.from_bb('red chinchompa')
	blacks = Weapon.from_bb('black chinchompa')

	lad = Player(name='chinner')
	lad.equipment.equip_basic_ranged_gear()
	lad.equipment.equip_arma_set(zaryte=True)
	lad.active_style = lad.equipment.equip_black_chins(buckler=True)
	lad.boost(Overload.overload())
	lad.prayers_coll.pray(Prayer.rigour())

	equipments = [
		Equipment(weapon=greys),
		Equipment(weapon=reds),
		Equipment(weapon=blacks),
	]

	monster_classes = [DeathlyMage, DeathlyRanger]
	monsters = [mc.from_de0(ps) for ps in scales for mc in monster_classes]

	indices, axes, data_ary = analysis_tools.bedevere_the_wise(
		lad,
		equipment=equipments,
		target=monsters,
		comparison_mode=ComparisonMode.CARTESIAN,
		data_mode=DataMode.TICKS_TO_KILL,
	)
	slice = data_ary[0, 0, 0, 0, :, 0, :]

	col_labels = axes[6][:]
	row_labels = axes[4][:]
	print(analysis_tools.tabulate_enhanced(slice, col_labels, row_labels, **options))


def shaman_estimate(**kwargs):
	options = {
		'floatfmt': '.1f',
		'scales': range(15, 32, 8),
	}
	options.update(kwargs)
	scales = options['scales']

	greys = Weapon.from_bb('chinchompa')
	reds = Weapon.from_bb('red chinchompa')
	blacks = Weapon.from_bb('black chinchompa')

	lad = Player(name='chinner')
	lad.equipment.equip_basic_ranged_gear()
	lad.equipment.equip_arma_set(zaryte=True)
	lad.equipment.equip_slayer_helm()
	lad.active_style = lad.equipment.equip_black_chins(buckler=True)
	lad.boost(Overload.overload())
	lad.prayers_coll.pray(Prayer.rigour())

	equipments = [
		Equipment(weapon=greys),
		Equipment(weapon=reds),
		Equipment(weapon=blacks),
	]

	monster_classes = [LizardmanShaman]
	monsters = [mc.from_de0(ps) for ps in scales for mc in monster_classes]

	indices, axes, data_ary = analysis_tools.bedevere_the_wise(
		lad,
		equipment=equipments,
		target=monsters,
		comparison_mode=ComparisonMode.CARTESIAN,
		data_mode=DataMode.TICKS_TO_KILL,
	)
	slice = data_ary[0, 0, 0, 0, :, 0, :]

	col_labels = axes[6][:]
	row_labels = axes[4][:]
	print(analysis_tools.tabulate_enhanced(slice, col_labels, row_labels, **options))


def mystic_estimates(**kwargs):
	options = {
		'floatfmt': '.1f',
		'scales': range(15, 32, 8),
	}
	options.update(kwargs)
	scales = options['scales']

	lad = Player(name='chinner')
	lad.equipment.equip_basic_ranged_gear(anguish=False)
	lad.equipment.equip_salve()
	lad.equipment.equip_arma_set(zaryte=True)
	lad.active_style = lad.equipment.equip_black_chins(buckler=True)
	lad.boost(Overload.overload())
	lad.prayers_coll.pray(Prayer.rigour())

	monster_classes = [SkeletalMystic]
	monsters = [mc.from_de0(ps) for ps in scales for mc in monster_classes]

	indices, axes, data_ary = analysis_tools.bedevere_the_wise(
		lad,
		target=monsters,
		comparison_mode=ComparisonMode.CARTESIAN,
		data_mode=DataMode.TICKS_TO_KILL,
	)
	slice = data_ary[0, 0, 0, 0, 0, 0, :]

	col_labels = axes[6][:]
	row_labels = axes[0][:]
	print(analysis_tools.tabulate_enhanced(slice, col_labels, row_labels, **options))




if __name__ == '__main__':
	fury = Gear.from_osrsbox('amulet of fury')
	bone_bolts = Gear.from_osrsbox('bone bolts')
	trident = Weapon.from_bb('trident of the seas')
	suffering = Gear.from_osrsbox('suffering (i)')
	bearhead = Gear.from_osrsbox('bearhead')  # magic only from here
	imbued_god_cape = Gear.from_osrsbox('imbued zamorak cape')
	karils_top = Gear.from_osrsbox("Karil's leathertop")
	buckler = Gear.from_osrsbox('twisted buckler')
	karils_skirt = Gear.from_osrsbox("Karil's leatherskirt")
	god_bracers = Gear.from_osrsbox('saradomin bracers')
	eternals = Gear.from_osrsbox('eternal boots')


	# aggro_check(scales=(31,) )
	# chin_estimate(scales=(31,) )
	# shaman_estimate(scales=(31,) )
	mystic_estimates(scales=(23, 31))

