from main import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import experience
from tabulate import tabulate


def dps_level_up(
		stat: str,
		start_level: int,
		end_level: int,
		target: Monster,
		special_attack: bool = False,
		distance: int = None,
		additional_targets: int = None,
		*players: Player
):

	assert start_level < end_level
	assert 1 <= start_level <= 99 and 1 <= end_level <= 99

	level_range = np.arange(start_level, end_level)

	m = len(players)
	n = level_range.size
	dps_matrix = np.zeros(shape=(m, n))

	for i, p in enumerate(players):
		try:
			p.stats.combat.__getattribute__(stat)
		except AttributeError as exc:
			raise exc

		if p.equipment.weapon.name == 'red chinchompa' or p.equipment.weapon.name == 'chinchompa':
			maximum_targets = 11    # includes the main target
		elif p.equipment.weapon.name == 'black chinchompa':
			maximum_targets = 12    # includes the main target
		else:
			maximum_targets = 1

		num_targets = min([1 + additional_targets, maximum_targets])

		for j, lvl in enumerate(level_range):
			p.stats.combat.__setattr__(stat, lvl)
			p.reset_current_stats()
			p.reset_potion_modifiers()
			p.ranging_potion()
			p.pray(PlayerStats.StatPrayer.rigour())
			dps_ij = p.damage_against_monster(other=target, special_attack=special_attack, distance=distance).per_second
			dps_ij_aoe = dps_ij * num_targets
			dps_matrix[i, j] = dps_ij_aoe

	for i in range(m):
		plt.plot(level_range, dps_matrix[i, :])

	plt.xlabel('{:} level'.format(stat))
	plt.ylabel('dps')
	plt.legend([p.name for p in players])
	plt.show()

	return dps_matrix


def level_test():
	weapon = Weapon.from_bitterkoekje_bedevere('red chinchompa')
	weapon.choose_style_by_name(PlayerStyle.medium_fuse)

	cape = Gear.from_osrsbox(name="ava's accumulator")
	# neck = Gear.from_osrsbox(name="amulet of glory")
	neck = Gear.from_osrsbox(name="salve amulet(ei)")
	feet = Gear.from_osrsbox(name="ranger boots")

	# void
	void_head = Gear.from_osrsbox(name="void ranger helm")
	void_hands = Gear.from_osrsbox(name="void knight gloves")

	void_body = Gear.from_osrsbox(name="void knight top")
	void_legs = Gear.from_osrsbox(name="void knight robe")

	elite_void_body = Gear.from_osrsbox(name="elite void top")
	elite_void_legs = Gear.from_osrsbox(name="elite void robe")

	# d'hide
	dhide_head = Gear.from_osrsbox(name="archer helm")

	dhide_body = Gear.from_osrsbox(name="bandos d'hide body")
	dhide_legs = Gear.from_osrsbox(name="bandos chaps")
	dhide_hands = Gear.from_osrsbox(name="bandos bracers")

	green_body = Gear.from_osrsbox(name="green d'hide body")
	green_legs = Gear.from_osrsbox(name="green d'hide chaps")
	green_hands = Gear.from_osrsbox(name="green d'hide vambraces")

	p0 = Player(
		name="green d'hide",
		stats=PlayerStats.max_player_stats(),
		equipment=Equipment(
			weapon,
			dhide_head,
			green_body,
			green_legs,
			green_hands,
			cape,
			neck,
			feet

		)
	)

	p1 = Player(
		name="black d'hide",
		stats=PlayerStats.max_player_stats(),
		equipment=Equipment(
			weapon,
			dhide_head,
			dhide_body,
			dhide_legs,
			dhide_hands,
			cape,
			neck,
			feet
		)
	)

	p2 = Player(
		name='normal void',
		stats=PlayerStats.max_player_stats(),
		equipment=Equipment(
			weapon,
			void_head,
			void_body,
			void_legs,
			void_hands,
			cape,
			neck,
			feet
		)
	)

	p2.equipment.equip_regular_void()

	p3 = Player(
		name='elite void',
		stats=PlayerStats.max_player_stats(),
		equipment=Equipment(
			weapon,
			void_head,
			elite_void_body,
			elite_void_legs,
			void_hands,
			cape,
			neck,
			feet
		)
	)

	p3.equipment.equip_elite_void()

	pp = [p0, p1, p2, p3]

	for p in pp:
		continue
		# p.pray(PlayerStats.StatPrayer.eagle_eye())

	monster = Monster.from_bitterkoekje("Skeleton (Ape Toll)")

	dps_level_up("ranged", 60, 98, monster, False, 1, *pp)


def level_test_unrestricted(starting_level: int, ending_level: int, fuse: str):
	grey_chins = Weapon.from_bitterkoekje_bedevere('chinchompa')
	grey_chins.choose_style_by_name(fuse)

	red_chins = Weapon.from_bitterkoekje_bedevere('red chinchompa')
	red_chins.choose_style_by_name(fuse)

	black_chins = Weapon.from_bitterkoekje_bedevere('black chinchompa')
	black_chins.choose_style_by_name(fuse)

	cape = Gear.from_osrsbox(name="ava's assembler")
	neck = Gear.from_osrsbox(name="bonecrusher necklace")
	feet = Gear.from_osrsbox(name="pegasian boots")
	hands = Gear.from_osrsbox(name="twisted buckler")

	# void
	void_head = Gear.from_osrsbox(name="void ranger helm")
	void_hands = Gear.from_osrsbox(name="void knight gloves")

	elite_void_body = Gear.from_osrsbox(name="elite void top")
	elite_void_legs = Gear.from_osrsbox(name="elite void robe")

	p0 = Player(
		name="grey chins",
		stats=PlayerStats.max_player_stats(),
		equipment=Equipment(
			grey_chins,
			void_head,
			elite_void_body,
			elite_void_legs,
			void_hands,
			cape,
			neck,
			feet,
			hands
		)
	)

	p1 = Player(
		name="red chins",
		stats=PlayerStats.max_player_stats(),
		equipment=Equipment(
			red_chins,
			void_head,
			elite_void_body,
			elite_void_legs,
			void_hands,
			cape,
			neck,
			feet,
			hands
		)
	)

	p2 = Player(
		name='black chins',
		stats=PlayerStats.max_player_stats(),
		equipment=Equipment(
			black_chins,
			void_head,
			elite_void_body,
			elite_void_legs,
			void_hands,
			cape,
			neck,
			feet,
			hands
		)
	)

	pp = [p0, p1, p2]

	for p in pp:
		p.equipment.equip_elite_void()

	monster = Monster.from_bitterkoekje("maniacal monkey")
	dps_matr = dps_level_up("ranged", starting_level, ending_level, monster, False, 1, 20, *pp)
	# m (players) by n (levels) matrix

	levels = np.arange(starting_level, ending_level)
	xp_needed_per_level = experience.compute_differential(levels)

	# hard-coded values
	damage_per_hitpoints_xp = 3 / 4
	seconds_per_hour = 3600
	seconds_per_tick = 0.6
	ticks_per_hour = seconds_per_hour * (1 / seconds_per_tick)

	attack_speed = p0.equipment.weapon.attack_speed

	if p0.equipment.weapon.active_style.name in [PlayerStyle.short_fuse, PlayerStyle.medium_fuse]:
		damage_per_ranged_xp = 1 / 4
		damage_per_defence_xp = 0
	elif p0.equipment.weapon.active_style.name == PlayerStyle.long_fuse:
		damage_per_ranged_xp = 1 / 2
		damage_per_defence_xp = 1 / 2
	else:
		raise PlayerStyle.StyleError(p0.equipment.weapon.active_style.name)

	damage_per_hour_matrix = dps_matr * seconds_per_hour
	damage_per_tick_matrix = dps_matr * seconds_per_tick
	damage_per_chinchompa = damage_per_tick_matrix * attack_speed

	ranged_experience_per_hour_matrix = damage_per_hour_matrix * (1 / damage_per_ranged_xp)
	ranged_experience_per_chinchompa = damage_per_chinchompa * (1 / damage_per_ranged_xp)

	chinchompas_per_level = np.empty(dps_matr.shape)

	try:
		defence_experience_per_chinchompa = damage_per_chinchompa * (1 / damage_per_defence_xp)
		defence_experience_per_hour_matrix = damage_per_hour_matrix * (1 / damage_per_defence_xp)

	except ZeroDivisionError:
		defence_experience_per_hour_matrix = np.zeros(dps_matr.shape)
		defence_experience_per_chinchompa = np.zeros(dps_matr.shape)

	for i, p in enumerate(pp):
		chinchompas_per_level[i, :] = (1 / ranged_experience_per_chinchompa[i, :]) * xp_needed_per_level

	ranged_experience_per_monkey = monster.stats.combat.hitpoints / damage_per_ranged_xp
	bonecrusher_charges_per_level = xp_needed_per_level / ranged_experience_per_monkey

	ranged_xph_k = (ranged_experience_per_hour_matrix / 1e3).astype('int').tolist()
	defence_xph_k = (defence_experience_per_hour_matrix / 1e3).astype('int').tolist()

	dps_table = tabulate(dps_matr.astype('float').tolist(), headers=levels)
	ranged_xph_table = tabulate(ranged_xph_k, headers=levels)
	defence_xph_table = tabulate(defence_xph_k, headers=levels)
	cpl_table = tabulate(chinchompas_per_level.astype('int').tolist(), headers=levels)
	bonecrusher_table = tabulate([bonecrusher_charges_per_level.astype('int').tolist()], headers=levels)

	print(dps_table, '\n')
	print(ranged_xph_table, '\n')
	print(defence_xph_table, '\n')
	print(cpl_table, '\n')
	print(bonecrusher_table)

	chins_needed = np.sum(chinchompas_per_level, axis=1)
	chins_needed = chins_needed.astype('int')

	time_needed_hours = chins_needed * attack_speed * (1 / ticks_per_hour)
	time_needed_hours = time_needed_hours.astype('int')

	bonecrusher_charges_needed = np.sum(bonecrusher_charges_per_level).astype('int')
	chins_costs = np.asarray([np.mean([731, 787]), np.mean([1032, 1007]), np.mean([2009, 2012])])

	gp_needed = (chins_needed * chins_costs) / 1e6
	gp_needed = gp_needed.astype('int')

	# important_table = tabulate([
	# 	['grey chins needed', chins_needed[0], gp_needed[0]],
	# 	['red chins needed', chins_needed[1], gp_needed[1]],
	# 	['black chins needed', chins_needed[2], gp_needed[2]],
	# 	['bonecrusher charges needed', bonecrusher_charges_needed]
	# ],
	# headers=['attribute', 'amount', 'cost (Million GP)'])

	main_table = tabulate(
		[
			['chins needed', *chins_needed],
			['GP (Million)', *gp_needed],
			['Time (hours)', *time_needed_hours],
			['Bonecrusher charges', *(3 * [bonecrusher_charges_needed, ])]
		],
		headers=['attribute', 'grey chins', 'red chins', 'black chins']
	)

	print('\n', main_table)


def main():
	medium_fuse = PlayerStyle.medium_fuse
	long_fuse = PlayerStyle.long_fuse
	level_test_unrestricted(85, 99, medium_fuse)

	# with open('chins.tsv', 'w+') as f:
	# 	df = pd.

	dps = 5


if __name__ == '__main__':
	main()

