from src.osrs_tools.character import *
from src.osrs_tools.analysis_tools import ComparisonMode, DataMode, generic_comparison_better, tabulate_wrapper

from itertools import product
import math
from enum import Enum, auto


def guardian_room_ticks_estimate(scale: int, boost: Boost, **kwargs) -> float:
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
	return total_ticks


class MysticModes(Enum):
	tbow_thralls = auto()
	chin_six_by_two = auto()
	chin_ten = auto()


def mystics_room_ticks_estimate(mode: MysticModes, **kwargs) -> float:
	"""
	Simple mystic room estimate method for chinning big stacks of large lads.

	There's only one real way to do shamans, same as guardians, so easy method.
	"""
	pass


def shamans_room_ticks_estimate(
		scale: int,
		boost: Boost,
		vulnerability: bool = False,
		bone_crossbow_specs: int = 0,
		**kwargs
) -> float:
	"""
	Simple shaman room estimate method for chinning big stacks of large lads.

	There's only one real way to do shamans, same as guardians, so easy method.
	"""
	options = {
		'trials': int(1e3),
	}
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
	total_ticks = damage_ticks + setup_ticks
	return total_ticks


class RopeModes(Enum):
	tbow_thralls = auto()
	chin_rangers = auto()
	chin_both = auto()


def rope_room_ticks_estimate(
		mode: RopeModes,
		scale: int,
		vulnerability: bool = False,
		bone_crossbow_specs: int = 0,
		**kwargs
):
	options = {
		'trials': int(1e1),
	}
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

	# combat
	if mode is RopeModes.tbow_thralls:
		thrall_dpt = 0.5    # (0+1+2+3+4)/5 damage / 4 ticks = 0.5 dpt
		lad.equipment.equip_void_set()
		lad.active_style = lad.equipment.equip_twisted_bow()
		mage_dpt = lad.damage_distribution(mage).per_tick + thrall_dpt
		ranger_dpt = lad.damage_distribution(ranger).per_tick + thrall_dpt

		mage_damage_ticks = mage.count_per_room() * mage.levels.hitpoints / mage_dpt
		ranger_damage_ticks = ranger.count_per_room() * ranger.levels.hitpoints / ranger_dpt
		setup_ticks = 0*vulnerability + 10*bone_crossbow_specs
		total_ticks = mage_damage_ticks + ranger_damage_ticks + setup_ticks

	elif mode is RopeModes.chin_rangers:
		raise NotImplementedError

	elif mode is RopeModes.chin_both:
		lad.equipment.equip_void_set()
		lad.active_style = lad.equipment.equip_black_chins()
		dpt = lad.damage_distribution(mage).per_tick

		damage_ticks = 2 * mage.levels.hitpoints / dpt  # one mager + one ranger's worth of HP / dpt
		setup_ticks = 20*vulnerability + 10*bone_crossbow_specs
		total_ticks = damage_ticks + setup_ticks

	return total_ticks


class CombatRotations(Enum):
	gms = auto()
	smg = auto()
	mutt_sham_myst = auto()
	myst_sham_mutt = auto()


class PuzzleRotations(Enum):
	thrope: auto()
	rice: auto()
	crope: auto()


def main(rotation: CombatRotations, scale: int, **kwargs):
	options = {
		'vulnerability': True,
		'bone_crossbow_specs': 0
	}
	options.update(kwargs)

	if rotation is CombatRotations.gms:
		guardians_ticks = guardian_room_ticks_estimate(
			scale=scale,
			boost=Boost.super_combat_potion(),
			**options,
		)
		shamans_ticks = shamans_room_ticks_estimate(
			scale=scale,
			boost=Overload.overload(),
			**options,
		)

	elif rotation is CombatRotations.smg:
		shamans_ticks = shamans_room_ticks_estimate(
			scale=scale,
			boost=Boost.bastion_potion(),
			**options,
		)
		guardians_ticks = guardian_room_ticks_estimate(
			scale=scale,
			boost=Overload.overload(),
			**options,
		)

	else:
		raise NotImplementedError

	rope_ticks = rope_room_ticks_estimate(
		mode=RopeModes.tbow_thralls,
		scale=scale,
		**options,
	)
	data = [guardians_ticks, 0, shamans_ticks, rope_ticks, 0]
	print(data)
	# col_labels = ['scale', Guardian.name, SkeletalMystic.name, LizardmanShaman.name, (DeathlyMage.name,
	#                                                                                   DeathlyRanger.name), 'foo']
	# row_labels = [scale]
	# table = tabulate_wrapper(data, col_labels, row_labels)
	# print(table)

if __name__ == '__main__':
	my_rot = CombatRotations.gms
	my_scale = 51
	my_trials = int(1e2)
	my_specs = 8

	main(rotation=my_rot, scale=my_scale, trials=my_trials, bone_crossbow_specs=my_specs)
