from src.osrs_tools.character import *
from src.osrs_tools.analysis_tools import ComparisonMode, DataMode, generic_comparison_better, tabulate_wrapper
from scaled_solo_olm import olm_ticks_estimate
from src.osrs_tools.unique_loot_calculator import individual_point_cap

from itertools import product
from matplotlib import pyplot as plt
import math
from enum import Enum, auto


def guardian_estimates(scale: int, boost: Boost, **kwargs) -> (float, int):
	"""
	Simple guardian room estimate method at any scale or boost for scaled solos.

	This method initially had a lot more sugar and enums and procedures and trials going on, but then I realized if
	you're not chickening guardians or at the very least reducing its defence to zero for the whole kill you're trolling
	yourself.
	"""
	options = {
		'party_average_mining_level': 61*(15/31) + 85*(5/31) * 1*(11/31)    # hack math based on the alts I usually use
	}
	options.update(kwargs)

	guardian = Guardian.from_de0(scale, party_average_mining_level=options['party_average_mining_level'])
	lad = Player(name='guardians fit')

	# gear
	lad.equipment.equip_basic_melee_gear(torture=False, brimstone=True)
	lad.equipment.equip_fury(blood=True)
	lad.equipment.equip_torva_set()
	lad.active_style = lad.equipment.equip_dragon_pickaxe()

	# boosts
	lad.prayers.pray(Prayer.piety())
	lad.boost(boost)

	# dwh / bgs / zero defence assumed if you have enough alts
	guardian.active_levels.defence = 0

	dpt = lad.damage_distribution(guardian).per_tick
	ticks_per_guardian = guardian.levels.hitpoints / dpt
	damage_ticks = guardian.count_per_room() * ticks_per_guardian
	setup_ticks = 20*6 + 100    # 100 for inefficiency and jank
	total_ticks = setup_ticks + damage_ticks
	return total_ticks, guardian.points_per_room()


class MysticModes(Enum):
	tbow_thralls = auto()
	chin_six_by_two = auto()
	chin_ten = auto()


def mystics_estimates(scale: int, mode: MysticModes, **kwargs) -> (float, int):
	"""
	Simple mystic room estimate method for afk-tbow-thralling them as usual and chinning big stacks of large lads.

	Extended description.
	"""
	options = {
		'scale_at_load_time': scale,
		'dwh_attempts_per_mystic': 4,
		'dwh_specialist_equipment': None,
		'dwh_specialist_target_strength_level': 13
	}
	options.update(kwargs)
	trials = options['trials']

	mystic = SkeletalMystic.from_de0(scale)

	if mode is MysticModes.tbow_thralls:
		lad = Player(name='mystics fit')
		dwh_specialist = Player(name='dwh specialist')

		# gear
		lad.active_style = lad.equipment.equip_twisted_bow()
		lad.equipment.equip_arma_set(zaryte=True)
		lad.equipment.equip_basic_ranged_gear(anguish=False)
		lad.equipment.equip_salve()
		assert lad.equipment.full_set

		if options['dwh_specialist_equipment'] is None:
			dwh_specialist.equipment.equip_basic_melee_gear(torture=False, infernal=False, berserker=False)
			dwh_specialist.active_style = dwh_specialist.equipment.equip_dwh(inquisitor_set=True, avernic=True,
			                                                                 tyrannical=True)
			dwh_specialist.equipment.equip_salve()
			dwh_specialist.equipment.equip(mythical_cape)
			assert dwh_specialist.equipment.full_set

		# boosts
		lad.boost(Overload.overload())
		lad.prayers.pray(Prayer.rigour(), Prayer.protect_from_magic())

		dwh_specialist.active_levels.strength = options['dwh_specialist_target_strength_level']
		dwh_specialist.boost(Boost.super_attack_potion())
		dwh_specialist.prayers.pray(Prayer.piety(), Prayer.protect_from_magic())

		# debuffs
		data = np.empty(shape=(trials, ), dtype=int)

		for index in range(trials):
			mystic.reset_stats()

			for _ in range(options['dwh_attempts_per_mystic']):
				p = dwh_specialist.damage_distribution(mystic, special_attack=True).chance_to_deal_positive_damage
				if np.random.random() < p:
					mystic.apply_dwh()

			data[index] = mystic.active_levels.defence

		mean_defence_level = math.floor(data.mean())
		mystic.active_levels.defence = mean_defence_level

		thrall_dpt = 0.5
		dpt = lad.damage_distribution(mystic).per_tick + thrall_dpt
		kill_ticks = mystic.levels.hitpoints / dpt
		damage_ticks = kill_ticks * mystic.count_per_room(options['scale_at_load_time'])
		tank_ticks = 200
		jank_ticks = 6*options['dwh_attempts_per_mystic']
		total_ticks = damage_ticks + tank_ticks + jank_ticks


	elif mode is MysticModes.chin_six_by_two:
		pass
	elif mode is MysticModes.chin_ten:
		pass
	else:
		raise NotImplementedError

	return total_ticks, mystic.points_per_room(**options)


def shamans_estimates(
		scale: int,
		boost: Boost,
		vulnerability: bool = False,
		bone_crossbow_specs: int = 0,
		**kwargs
) -> (float, int):
	"""
	Simple shaman room estimate method for chinning big stacks of large lads.

	There's only one real way to do shamans, same as guardians, so easy method.
	"""
	options = {}
	options.update(kwargs)

	shaman = LizardmanShaman.from_de0(scale)
	lad = Player(name='shamans fit')

	# gear
	lad.equipment.equip_basic_ranged_gear()
	lad.equipment.equip_arma_set(zaryte=True)
	lad.equipment.equip_slayer_helm()
	lad.task = True
	lad.active_style = lad.equipment.equip_black_chins()

	# boosts
	lad.prayers.pray(Prayer.rigour())
	lad.boost(boost)

	# def reduction
	if vulnerability:
		shaman.apply_vulnerability()

	if bone_crossbow_specs > 0:
		lad.active_style = lad.equipment.equip(
			SpecialWeapon.from_bb('dorgeshuun crossbow'),
			Gear.from_bb('bone bolts'),
			style=CrossbowStyles.get_style(PlayerStyle.longrange)
		)

		trials = options['trials']
		shaman_pre_boned_defence = shaman.active_levels.defence
		defence_level_data = np.empty(shape=(trials,), dtype=int)

		for index in range(trials):
			shaman.active_levels.defence = shaman_pre_boned_defence

			for _ in range(bone_crossbow_specs):
				dam = lad.damage_distribution(shaman, special_attack=True)
				damage_value = dam.random()[0]
				shaman.active_levels.defence = shaman.active_levels.defence - damage_value

			defence_level_data[index] = shaman.active_levels.defence

		# cleanup, also un-equips bone bolts
		lad.active_style = lad.equipment.equip_black_chins()

		mean_shaman_defence = int(np.floor(defence_level_data.mean()))
		shaman.active_levels.defence = mean_shaman_defence

	dpt = lad.damage_distribution(shaman).per_tick
	damage_ticks = shaman.levels.hitpoints / dpt
	setup_ticks = 200 + bone_crossbow_specs*10
	jank_ticks = 50     # cleanup n such
	total_ticks = damage_ticks + setup_ticks + jank_ticks
	return total_ticks, shaman.points_per_room()


class RopeModes(Enum):
	tbow_thralls = auto()
	chin_rangers = auto()
	chin_both = auto()


def rope_estimates(
		mode: RopeModes,
		scale: int,
		vulnerability: bool = False,
		bone_crossbow_specs: int = 0,
		**kwargs
) -> (float, int):
	options = {}
	options.update(kwargs)

	# characters
	mage = DeathlyMage.from_de0(scale)
	ranger = DeathlyRanger.from_de0(scale)
	monsters = [mage, ranger]

	lad = Player(name='rope fit')

	# gear
	lad.equipment.equip_basic_ranged_gear()

	# boosts / debuffs
	lad.prayers.pray(Prayer.rigour())
	lad.boost(Overload.overload())

	if vulnerability:
		for mon in monsters:
			mon.apply_vulnerability()

	# combat
	if mode is RopeModes.tbow_thralls:
		thrall_dpt = 0.5    # (0+1+2+3+4)/5 damage / 4 ticks = 0.5 dpt
		lad.equipment.equip_arma_set(zaryte=True)
		lad.active_style = lad.equipment.equip_twisted_bow()
		assert lad.equipment.full_set

		mage_dpt = lad.damage_distribution(mage).per_tick + thrall_dpt
		ranger_dpt = lad.damage_distribution(ranger).per_tick + thrall_dpt

		mage_damage_ticks = mage.count_per_room() * mage.levels.hitpoints / mage_dpt
		ranger_damage_ticks = ranger.count_per_room() * ranger.levels.hitpoints / ranger_dpt
		setup_ticks = 6 + 0*vulnerability   # 10*bone_crossbow_specs    # lure ticks + nonsense
		total_ticks = mage_damage_ticks + ranger_damage_ticks + setup_ticks
	else:
		# TODO: Redo placement of this
		if bone_crossbow_specs > 0:     # mages and rangers have the same defence stats so just run one set of sims
			lad.equipment.equip_arma_set(zaryte=True)
			lad.active_style = lad.equipment.equip_dorgeshuun_crossbow()

			trials = options['trials']
			mage_pre_boned_defence = mage.active_levels.defence
			defence_level_data = np.empty(shape=(trials,), dtype=int)

			for index in range(trials):
				mage.active_levels.defence = mage_pre_boned_defence

				for _ in range(bone_crossbow_specs):
					dam = lad.damage_distribution(mage, special_attack=True)
					damage_value = dam.random()[0]
					mage.active_levels.defence = mage.active_levels.defence - damage_value

				defence_level_data[index] = mage.active_levels.defence

			# cleanup
			lad.equipment.unequip(GearSlots.weapon, GearSlots.shield, GearSlots.ammunition)

			mean_mage_defence = int(np.floor(defence_level_data.mean()))

			mage.active_levels.defence = mean_mage_defence
			ranger.active_levels.defence = mean_mage_defence

		if mode is RopeModes.chin_rangers:
			total_ticks = None
			raise NotImplementedError
		elif mode is RopeModes.chin_both:
			lad.equipment.equip_void_set()
			lad.active_style = lad.equipment.equip_black_chins()
			dpt = lad.damage_distribution(mage).per_tick

			damage_ticks = 2 * mage.levels.hitpoints / dpt  # one mager + one ranger's worth of HP / dpt
			setup_ticks = 20*vulnerability + 10*bone_crossbow_specs
			total_ticks = damage_ticks + setup_ticks
		else:
			raise NotImplementedError

	total_points = mage.points_per_room() + ranger.points_per_room()

	return total_ticks, total_points


def thieving_estimates(scale: int, **kwargs) -> (float, int):
	options = {
		'ticks_per_grub': 5,
	}
	options.update(kwargs)

	def flat_grub_estimate(inner_scale: int) -> int:
		return 16*inner_scale - 1

	def jank_grub_estimate(modifier: float = None):
		modifier = 268 / flat_grub_estimate(28) if modifier is None else modifier   # my one data point
		return math.floor(flat_grub_estimate(scale) * modifier)

	grub_estimate = jank_grub_estimate()
	points_per_grub = 100
	ticks_per_grub = options['ticks_per_grub']

	ticks_estimate = ticks_per_grub * grub_estimate
	points_estimate = points_per_grub * grub_estimate
	return ticks_estimate, points_estimate


class CombatRotations(Enum):
	gms = auto()
	smg = auto()
	mutt_sham_myst = auto()
	myst_sham_mutt = auto()


class PuzzleRotations(Enum):
	thrope: auto()
	rice: auto()
	crope: auto()


def main(rotation: CombatRotations, scale: int, **kwargs) -> float:
	options = {
		'vulnerability': True,
		'bone_crossbow_specs': 0,
		'trials': int(1e3),
		'setup_ticks_meta': 30 * 100,   # 30 minutes to wrangle a scale, the lads, and gear
	}
	options.update(kwargs)

	if rotation is CombatRotations.gms:
		guardian_boost = Boost.super_combat_potion()
		shamans_boost = Overload.overload()
	elif rotation is CombatRotations.smg:
		guardian_boost = Overload.overload()
		shamans_boost = Boost.bastion_potion()
	else:
		raise NotImplementedError

	guardians_ticks, guardian_points = guardian_estimates(
		scale=scale,
		boost=guardian_boost,
		**options,
	)
	mystics_ticks, mystics_points = mystics_estimates(
		scale=scale,
		mode=MysticModes.tbow_thralls,
		**options,
	)
	shamans_ticks, shamans_points = shamans_estimates(
		scale=scale,
		boost=shamans_boost,
		**options,
	)

	rope_ticks, rope_points = rope_estimates(
		mode=RopeModes.tbow_thralls,
		scale=scale,
		**options,
	)
	thieving_ticks, thieving_points = thieving_estimates(
		scale=scale,
		**options,
	)

	olm_ticks, olm_points = olm_ticks_estimate(
		scale=scale,
		**options,
	)

	# 1 stam * (4 doses / 1 stam) * (4 minutes / 1 dose) * (100 ticks / 1 minute)
	minimum_stams_needed = math.ceil(olm_ticks / (1 * 4 * 4 * 100))

	# ticks ############################################################################################################
	tick_data = [guardians_ticks, mystics_ticks, shamans_ticks, rope_ticks, thieving_ticks, olm_ticks]
	tick_data.insert(0, sum(tick_data[:]) + options['setup_ticks_meta'])
	tick_data.append(minimum_stams_needed)

	data_minutes = [d/100 for d in tick_data[:-1]]
	data_hours = [d/6000 for d in tick_data[:-1]]
	col_labels = ['time unit', 'total', 'guardians', 'mystics', 'shamans', 'rope', 'thieving', 'olm',
	              'minimum stamina pots']
	row_labels = ['ticks', 'minutes', 'hours']

	list_of_data = [tick_data, data_minutes, data_hours]
	table_line = '-'*107
	header_line = copy(table_line)
	header_title = f'  scale:  {scale:3.0f}  '
	chop_index = (len(table_line) - len(header_title))//2
	title_line = header_line[:chop_index] + header_title + header_line[chop_index + len(header_title):]
	time_table = tabulate_wrapper(list_of_data, col_labels=col_labels, row_labels=row_labels, meta_header=title_line,
	                         floatfmt='.1f')

	# points ###########################################################################################################
	pt_data = [guardian_points, mystics_points, shamans_points, rope_points, thieving_points, olm_points]
	pt_data.insert(0, sum(pt_data) - individual_point_cap)
	col_labels = [''] + col_labels[1:-1]
	row_labels = ['points']
	list_of_data = [pt_data]
	points_table = tabulate_wrapper(list_of_data, col_labels, row_labels)

	# points per hour ##################################################################################################
	adjusted_total_points = pt_data[0]
	points_per_hour = adjusted_total_points / data_hours[0]

	print('\n'.join(['\n', time_table, '\n', points_table, '\n', f'points per hr: {points_per_hour}']))
	return points_per_hour


if __name__ == '__main__':
	my_rot = CombatRotations.gms
	my_scales = list(range(15, 52, 4))
	my_scales = list(range(15, 52, 1))
	my_specs_list = [0] * len(my_scales)
	# my_specs_list = [*(0, )*4, *(0, )*6]     # bone crossbow only worth the jank in 31+ imo
	my_trials = int(5e1)

	my_setup_ticks = 30 * 100   # 30 minutes to wrangle a reasonable scale + scalers + gear the lads

	mythical_cape = Gear.from_bb('mythical cape')
	dwh_specialist_strength_level = 13

	scales_ary = np.asarray(my_scales)
	pph_data = np.empty(shape=scales_ary.shape, dtype=float)

	for index, (my_scale, my_specs) in enumerate(zip(my_scales, my_specs_list)):
		pph_data[index] = main(
			rotation=my_rot,
			scale=my_scale,
			trials=my_trials,
			bone_crossbow_specs=my_specs,
			dwh_specialist_strength_level=dwh_specialist_strength_level,
			setup_ticks_meta=my_setup_ticks
		)

	plt.plot(scales_ary, pph_data)
	plt.xlabel('scale')
	plt.ylabel('points per hr (pph)')
	plot_title = 'PPH vs. scale for scaled iron gimmick solos'
	plt.title(plot_title)
	plt.show()
	plt.savefig(plot_title + '.png')
