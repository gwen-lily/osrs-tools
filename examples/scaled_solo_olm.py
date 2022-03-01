from src.osrs_tools.character import *
from src.osrs_tools import analysis_tools
from src.osrs_tools.analysis_tools import ComparisonMode, DataMode

from itertools import product
import math
from tabulate import tabulate

ring_of_endurance = Gear(
	name='ring of endurance',
	slot=GearSlots.ring,
	aggressive_bonus=AggressiveStats.no_bonus(),
	defensive_bonus=DefensiveStats.no_bonus(),
	prayer_bonus=0,
	level_requirements=PlayerLevels.no_requirements()
)

book_of_the_dead = Gear(
	name='book of the dead',
	slot=GearSlots.shield,
	aggressive_bonus=AggressiveStats(magic=6),
	defensive_bonus=DefensiveStats.no_bonus(),
	prayer_bonus=3,
	level_requirements=PlayerLevels.no_requirements()
)


def magic_shield_comparison(**kwargs):

	options = {
		'floatfmt': '.1f',
	}
	options.update(kwargs)

	lad = Player(name='lad')
	lad.boost(Overload.overload())
	lad.prayers.pray(Prayer.augury())

	lad.equipment.equip_basic_magic_gear(arcane=False, brimstone=False)
	lad.active_style = lad.equipment.equip(ring_of_endurance, Weapon.from_bb('sanguinesti staff'))

	equipment = [
		Equipment(shield=Gear.from_bb('arcane spirit shield')),
		Equipment(shield=book_of_the_dead)
	]

	olms = [OlmMageHand.from_de0(ps) for ps in range(15, 32, 8)]

	indices, axes, data_ary = analysis_tools.generic_comparison_better(
		players=lad,
		equipment=equipment,
		target=olms,
		comparison_mode=ComparisonMode.CARTESIAN,
		data_mode=DataMode.DPS,
	)

	row_axis = 4
	col_axis = 6

	data = data_ary[0, 0, 0, 0, :, 0, :]
	table_data = []

	for index, row in enumerate(data):
		row_with_label = [axes[row_axis][index]] + list(row)
		table_data.append(row_with_label)

	headers = [f'Olm Mage Hand ({ps:.0f})' for ps in range(15, 32, 8)]
	table = tabulate(table_data, headers=headers, floatfmt=options['floatfmt'])
	print(table)


def olm_ticks_estimate(scale: int, **kwargs):

	options = {
		'floatfmt': '.1f',
		'thrall_dpt': 0.5,
		'melee_hand_defence': 0
	}
	options.update(kwargs)

	# MAGIC HAND #######################################################################################################
	mage_lad = Player(name='mage lad')
	mage_lad.boost(Overload.overload())
	mage_lad.prayers.pray(Prayer.augury())
	mage_lad.equipment.equip_basic_magic_gear(arcane=False, brimstone=False)
	mage_lad.active_style = mage_lad.equipment.equip(ring_of_endurance, book_of_the_dead,
	                                                 Weapon.from_bb('sanguinesti staff'))
	assert mage_lad.equipment.full_set

	magic_hand = OlmMageHand.from_de0(scale)
	dpt = mage_lad.damage_distribution(magic_hand).per_tick + options['thrall_dpt']
	magic_damage_ticks_per_phase = magic_hand.levels.hitpoints / dpt
	specs_before_melee_starts = int(np.round(2 + magic_damage_ticks_per_phase/250))

	magic_ticks = magic_hand.count_per_room() * magic_damage_ticks_per_phase
	magic_hand_points = magic_hand.points_per_room()

	# MELEE HAND #######################################################################################################
	melee_lad = Player(name='melee lad')
	melee_lad.boost(Overload.overload())
	melee_lad.prayers.pray(Prayer.piety())
	melee_lad.equipment.equip_basic_melee_gear(berserker=False, torture=False)
	melee_lad.equipment.equip_fury(blood=True)
	melee_lad.equipment.equip_torva_set()
	melee_lad.active_style = melee_lad.equipment.equip_lance(berserker=False)
	melee_lad.equipment.equip(ring_of_endurance)
	assert melee_lad.equipment.full_set

	melee_hand = OlmMeleeHand.from_de0(scale)
	melee_hand.active_levels.defence = options['melee_hand_defence']

	dpt = melee_lad.damage_distribution(melee_hand).per_tick + options['thrall_dpt']
	melee_damage_ticks_per_phase = melee_hand.levels.hitpoints / dpt

	melee_ticks = melee_hand.count_per_room() * melee_damage_ticks_per_phase
	melee_hand_points = melee_hand.points_per_room()


	# HEAD PHASE #######################################################################################################
	ranger_lad = Player(name='ranger lad')
	ranger_lad.boost(Overload.overload())
	ranger_lad.prayers.pray(Prayer.rigour())
	ranger_lad.equipment.equip_basic_ranged_gear(brimstone=False)
	ranger_lad.equipment.equip_arma_set(zaryte=True)
	ranger_lad.equipment.equip(ring_of_endurance)
	ranger_lad.active_style = ranger_lad.equipment.equip_twisted_bow()
	assert ranger_lad.equipment.full_set

	olm_head = OlmHead.from_de0(scale)
	dpt = ranger_lad.damage_distribution(olm_head).per_tick + options['thrall_dpt']
	ranged_ticks = olm_head.levels.hitpoints / dpt

	ranged_points = olm_head.points_per_room()

	total_ticks = magic_ticks + melee_ticks + ranged_ticks
	total_points = magic_hand_points + melee_hand_points + ranged_points
	return total_ticks, total_points


def olm_damage_estimate(**kwargs):
	options = {
		'floatfmt': '.1f',
		'scales': range(15, 32, 8),
	}
	options.update(kwargs)

	melee_lad = Player(name='melee_lad')
	melee_lad.boost(Overload.overload())
	melee_lad.prayers.pray(Prayer.piety())
	melee_lad.equipment.equip_basic_melee_gear(berserker=False, torture=False)
	melee_lad.equipment.equip_torva_set()
	melee_lad.active_style = melee_lad.equipment.equip_lance(avernic=False)
	melee_lad.equipment.equip(amulet_of_fury, ring_of_endurance)

	equipments = [Equipment(shield=x) for x in (avernic_defender, elysian_spirit_shield)]
	olms = [OlmHead.from_de0(ps) for ps in options['scales']]

	olm = OlmHead.from_de0(1)
	melee_lad.equipment.equip(avernic_defender)
	dam_1 = olm.damage_distribution(melee_lad)
	melee_lad.equipment.equip(elysian_spirit_shield)
	dam_2 = olm.damage_distribution(melee_lad)

	print(dam_1, dam_2)


def melee_hand_mean_defence(scale: int, total_specs: int, hammers_first: int, **kwargs):
	options = {
		'trials': 1e3,
	}
	options.update(kwargs)
	trials = int(options['trials'])

	lad_1 = Player(name='lad 1')
	lad_2 = Player(name='lad 2')
	lads = [lad_1, lad_2]

	for lad in lads:
		lad.boost(Overload.overload())
		lad.prayers.pray(Prayer.piety())

		lad.equipment.equip_basic_melee_gear(berserker=False, torture=False)
		lad.equipment.equip_torva_set()
		lad.equipment.equip(Gear.from_bb('amulet of fury'))

	lad_1.active_style = lad_1.equipment.equip_dwh(inquisitor_set=False, avernic=True, brimstone=False)
	lad_2.active_style = lad_2.equipment.equip(SpecialWeapon.from_bb('bandos godsword'))

	defence_data = np.empty(shape=(trials,), dtype=int)
	olm = OlmMeleeHand.from_de0(party_size=scale)

	defence_range = np.arange(0, olm.levels.defence + 1)
	dwh_p_ary = np.empty(shape=defence_range.shape, dtype=float)
	bgs_dam_ary = np.empty(shape=defence_range.shape, dtype=Damage)

	for index, defence in enumerate(defence_range):
		olm.active_levels.defence = defence
		dwh_p_ary[index] = lad_1.damage_distribution(olm, special_attack=True).chance_to_deal_positive_damage
		bgs_dam_ary[index] = lad_2.damage_distribution(olm, special_attack=True)

	for index in range(trials):
		olm.reset_stats()
		dwh_landed = 0

		for _ in range(total_specs):
			if dwh_landed < hammers_first:
				p = dwh_p_ary[olm.active_levels.defence]

				if np.random.random() < p:
					dwh_landed += 1
					olm.apply_dwh()
			else:
				bgs_dam: Damage = bgs_dam_ary[olm.active_levels.defence]
				olm.apply_bgs(bgs_dam.random()[0])

		defence_data[index] = olm.active_levels.defence

	return defence_data.mean()


def melee_hand_estimate(**kwargs):
	pass


def olm_max_hits(**kwargs):
	options = {
		'scales': range(1, 101),
	}
	options.update(kwargs)
	lad = Player(name='dummy')
	data = []
	headers = ['scale', 'normal', 'crippled', 'enraged', 'head phase']

	for ps in options['scales']:
		olm = OlmHead.from_de0(ps)
		row = [
			olm.party_size,
			olm.max_hit(lad),
			olm.max_hit(lad, crippled=True),
			olm.max_hit(lad, enraged=True),
			olm.max_hit(lad, head_phase=True)
		]
		data.append(row)

	df = pd.DataFrame(data, columns=headers, dtype=int)
	df.to_csv('olm max hits.csv', sep='\t')

	table = tabulate(data, headers, floatfmt='.0f')
	print(table)


if __name__ == '__main__':


	elysian_spirit_shield = Gear.from_bb('elysian spirit shield')

	# magic_shield_comparison(floatfmt='.2f')
	# olm_ticks_estimate(scales=(31, ))
	olm_max_hits()
	# olm_damage_estimate(scales=(31, ))
