from main import *
from scipy.optimize import fsolve, minimize, OptimizeResult, Bounds
import cox_tools as ct
import osrs_markov


def void_arma_scale():
	olm_name = OlmHead.get_name()

	arma_tbow = Player.arma_tbow()
	void_tbow = Player.void_tbow()
	players = [arma_tbow, void_tbow]

	for p in players:
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())

	csc = ct.plot_comparison(ct.cox_scale_comparison)
	# csc = ct.print_comparison(ct.cox_scale_comparison)

	csc(players, olm_name, bounds=(1, 100), plot_title='{:} (vulnerability)'.format(olm_name), cast_vulnerability=True)


def mage_dps_scale():
	olm_name = OlmMageHand.get_name()

	sang = Player.max_sang_brimstone()
	harm = Player.max_harm_fire_surge()
	shaun = Player.shaun_restricted_mage()

	# for gear_item in shaun.equipment.get_gear():
	# 	print(gear_item)
	#
	# print(shaun.equipment.aggressive_bonus())
	# print(shaun.equipment.defensive_bonus())

	players = [sang, harm, shaun]

	# overload and prayer

	for p in players:
		p.overload()
		p.pray(PlayerStats.StatPrayer.augury())

	shaun.pray(PlayerStats.StatPrayer.mystic_lore())

	# csc = ct.plot_comparison(ct.cox_scale_comparison)
	csc = ct.print_comparison(ct.cox_scale_comparison)

	csc(players, olm_name, bounds=(1, 100), plot_title='{:}'.format(olm_name))


def melee_dps_scale():
	olm_name = OlmMeleeHand.get_name()

	inquisitor_scythe = Player.max_scythe_inquisitor()
	bandos_scythe = Player.max_scythe_bandos()
	inquisitor_lance = Player.max_lance_inquisitor()
	bandos_lance = Player.max_lance_bandos()
	snowflake_shaun = Player.shaun_restricted_mage()

	players = [inquisitor_lance, bandos_lance, inquisitor_scythe, bandos_scythe, snowflake_shaun]

	for p in players:
		p.overload()
		p.pray(PlayerStats.StatPrayer.piety())

	# special
	snowflake_shaun.pray(PlayerStats.StatPrayer.improved_reflexes(), PlayerStats.StatPrayer.ultimate_strength())

	weapon = Weapon.from_bitterkoekje_bedevere("dragon scimitar")
	weapon.choose_style_by_name(PlayerStyle.slash)

	cape = Gear.from_osrsbox(name="fire cape")
	neck = Gear.from_osrsbox(name="amulet of fury")
	body = Gear.from_osrsbox(name="guthix d'hide body")
	legs = Gear.from_osrsbox(name="zamorak chaps")
	shield = Gear.from_osrsbox(name="rune defender")
	hands = Gear.from_osrsbox(name="barrows gloves")

	snowflake_shaun.equipment.equip(weapon, cape, neck, body, legs, shield, hands)


	csc = ct.print_comparison(ct.cox_scale_comparison)
	csc(
		players,
		olm_name,
		bounds=(15, 15),
		plot_title='{:} (0 def)'.format(olm_name),
		bgs_damage=1000,
		fifteen_sixteenths_scythe=True
	)

def melee_camp_scale():
	olm_name = OlmMeleeHand.get_name()

	inquisitor_scythe = Player.max_scythe_inquisitor()
	bandos_scythe = Player.max_scythe_bandos()
	justiciar_lance_ely = Player.max_lance_bandos()

	players = [inquisitor_scythe, bandos_scythe, justiciar_lance_ely]

	for p in players:
		p.overload()
		p.pray(PlayerStats.StatPrayer.piety())

	# special
	tank_gear = {
		"head": Gear.from_osrsbox(name='justiciar faceguard'),
		"body": Gear.from_osrsbox(name='justiciar chestguard'),
		"legs": Gear.from_osrsbox(name='justiciar legguards'),
		"neck": Gear.from_osrsbox(name="amulet of blood fury"),
		"shield": Gear.from_osrsbox(name="elysian spirit shield"),
		"hands": Gear.from_osrsbox(name="barrows gloves"),
		"feet": Gear.from_osrsbox(name="guardian boots"),
		"ring": Gear.from_osrsbox(name="ring of suffering (i)")
	}

	justiciar_lance_ely.equipment.equip(*tank_gear.values())

	csc = ct.print_comparison(ct.cox_scale_comparison)
	csc(
		players,
		olm_name,
		bounds=(15, 15),
		plot_title='{:} (0 def)'.format(olm_name),
		bgs_damage=1000,
		fifteen_sixteenths_scythe=False
	)


def main(party_size: int, challenge_mode: bool):
	melee_hand = OlmMeleeHand(party_size=party_size, challenge_mode=challenge_mode)
	melee_hand.dwh_reduce()
	melee_hand.dwh_reduce()
	melee_hand.bgs_reduce(114)

	# Melee camp
	bandos_camp = Player.max_blood_fury_scythe_bandos()
	bandos_camp.overload()
	bandos_camp.pray(PlayerStats.StatPrayer.piety())

	# Melee flex (torture > blood fury, potentially inquisitor)
	bandos_flex = Player.max_scythe_bandos()
	bandos_flex.overload()
	bandos_flex.pray(PlayerStats.StatPrayer.piety())

	# Max mage

	players = [bandos_camp, bandos_flex]

	ct.cox_scale_comparison(players, OlmMeleeHand.get_name(), bounds=(15, 32))


def camp_vs_fifteen_sixteen_comp(party_size: int, challenge_mode: bool):
	melee_hand = OlmMeleeHand(party_size=party_size, challenge_mode=challenge_mode)
	melee_hand.bgs_reduce(melee_hand.stats.current_combat.defence)
	assert melee_hand.stats.current_combat.defence == 0

	bfury_camp = Player.max_blood_fury_scythe_bandos()
	bandos_flex = Player.max_scythe_bandos()
	inq_flex = Player.max_scythe_inquisitor()

	players = [bfury_camp, bandos_flex, inq_flex]
	damages = [[], [], []]

	for p in players:
		p.overload()
		p.pray(PlayerStats.StatPrayer.piety())

	# dps calcs
	std_bfury_camp_mean_hit = bfury_camp.damage_against_monster(melee_hand).mean
	bfury_camp.xerics_aid()
	brewed_down_bfury_camp_mean_hit = bfury_camp.damage_against_monster(melee_hand).mean

	std_bandos_flex_mean_hit = bandos_flex.damage_against_monster(melee_hand).mean
	std_inq_flex_mean_hit = inq_flex.damage_against_monster(melee_hand).mean

	tick_counter = 0

	while tick_counter < 800:
		five_cycle = tick_counter % 5
		sixteen_cycle = tick_counter % 16
		overload_cycle = tick_counter % 25
		brew_cycle = tick_counter % 32

		if five_cycle == 0:

			damages[0].append(bfury_camp.damage_against_monster(melee_hand).mean)

		if sixteen_cycle in [0, 5, 10]:
			damages[1].append(std_bandos_flex_mean_hit)
			damages[2].append(std_inq_flex_mean_hit)

		if brew_cycle == 0:
			bfury_camp.xerics_aid()

		if overload_cycle == 0:
			bfury_camp.overload()




		tick_counter += 1

	for p, d in zip(players, damages):
		print("{:40}{:.1f}".format(p.name, sum(d)))


# def scaled_olm_estimate(party_size: int, dps_accounts: int, iron_whipper: bool = False):
# 	assert 3 <= dps_accounts <= 8   # TODO: general formula
#
# 	z = 1
# 	x = 1 if dps_accounts < 6 else 2
# 	y = dps_accounts - x - z
#
# 	X = Player.max_blood_fury_scythe_bandos()
# 	Y = Player.max_sang_brimstone()
# 	Z = Player.max_scythe_bandos()
#
# 	whip = Weapon.from_bitterkoekje_bedevere('abyssal whip')
# 	whip.choose_style_by_name(PlayerStyle.lash)
# 	W = Player.from_highscores(
# 		rsn='SirNargeth',
# 		equipment=Equipment(
# 			whip,
# 			Gear.from_bitterkoekje_bedevere('neitiznot'),
# 			Gear.from_bitterkoekje_bedevere('fire cape'),
# 			Gear.from_bitterkoekje_bedevere('amulet of fury'),
# 			Gear.from_bitterkoekje_bedevere('fighter torso'),
# 			Gear.from_bitterkoekje_bedevere('proselyte cuisse'),
# 			Gear.from_bitterkoekje_bedevere('dragon defender'),
# 			Gear.from_bitterkoekje_bedevere('barrows gloves'),
# 			Gear.from_bitterkoekje_bedevere('dragon boots'),
# 			Gear.from_bitterkoekje_bedevere('berserker (i)')
# 		)
# 	)
#
# 	R = Player.arma_tbow()
# 	R.equipment.equip(Gear.from_bitterkoekje_bedevere("brimstone ring"))
#
# 	players = [X, Y, Z, W, R]
#
# 	for p in players:
# 		p.overload()
#
# 		dt = p.weapon.active_style.damage_type
#
# 		if dt in PlayerStyle.melee_damage_types:
# 			p.pray('piety')
# 		elif dt in PlayerStyle.ranged_damage_types:
# 			p.pray('rigour')
# 		elif dt in PlayerStyle.magic_damage_types:
# 			p.pray('augury')
# 		else:
# 			continue
#
# 	melee_hand = OlmMeleeHand(party_size, challenge_mode=False)
# 	mage_hand = OlmMageHand(party_size, challenge_mode=False)
# 	melee_hand.stats.current_combat.defence = 0
# 	head = OlmHead(party_size, challenge_mode=False)
#
# 	DPSx = X.damage_against_monster(melee_hand).per_second
# 	DPSy = Y.damage_against_monster(mage_hand).per_second
# 	DPSz = (15/16) * Z.damage_against_monster(melee_hand).per_second
# 	DPSw = W.damage_against_monster(melee_hand).per_second
#
# 	c0 = x*DPSx + DPSw - (y+z)*DPSy
# 	c1 = z*(DPSz + DPSy)
# 	eta0 = -c0/c1
#
# 	d0 = x*DPSx + DPSw + (y+z)*DPSy
# 	d1 = z*(DPSz - DPSy)
# 	dps_total = d0 + d1*eta0
# 	kill_time_per_phase = (melee_hand.stats.combat.hitpoints + mage_hand.stats.combat.hitpoints) / dps_total
# 	phases = melee_hand.phases()
#
# 	DPSr = R.damage_against_monster(head).per_second
# 	kill_time_head = head.stats.combat.hitpoints / (dps_accounts * DPSr)
#
# 	intermission_time = 30      # seconds
# 	intermissions = phases - 1
#
# 	total_time = np.dot([phases, intermissions, 1],	[kill_time_per_phase, intermission_time, kill_time_head])
# 	total_time_minutes = total_time / 60
#
# 	print('Olm ({:} scale) with {:} DPS accounts'.format(party_size, dps_accounts))
# 	print('\t{:} phases, {:3.0f} seconds per phase'.format(phases, kill_time_per_phase))
# 	print('\tFlex should spend {:.0f}% melee'.format(eta0*100))
# 	print('\t{:} intermissions, {:} seconds per intermission'.format(intermissions, intermission_time))
# 	print('\t{:.0f} seconds for head phase'.format(kill_time_head))
# 	print('\n\t{:.0f} minutes to complete olm'.format(total_time_minutes))


def scaled_olm_iron_estimate(party_size: int, dps_accounts: int):
	assert 3 <= dps_accounts <= 8   # TODO: general formula

	n_u = 1 if dps_accounts < 6 else 2
	n_w = 1
	n_v = dps_accounts - n_u - n_w

	U = Player.max_blood_fury_scythe_bandos()
	V = Player.max_sang_brimstone()

	whip = Weapon.from_bitterkoekje_bedevere('abyssal whip')
	whip.choose_style_by_name(PlayerStyle.lash)
	UW = Player.from_highscores(
		rsn='SirNargeth',
		equipment=Equipment(
			whip,
			Gear.from_bitterkoekje_bedevere('neitiznot'),
			Gear.from_bitterkoekje_bedevere('fire cape'),
			Gear.from_bitterkoekje_bedevere('amulet of fury'),
			Gear.from_bitterkoekje_bedevere('fighter torso'),
			Gear.from_bitterkoekje_bedevere('proselyte cuisse'),
			Gear.from_bitterkoekje_bedevere('dragon defender'),
			Gear.from_bitterkoekje_bedevere('barrows gloves'),
			Gear.from_bitterkoekje_bedevere('dragon boots'),
			Gear.from_bitterkoekje_bedevere('berserker (i)')
		)
	)
	trident = Weapon.from_bitterkoekje_bedevere('trident of the swamp')
	trident.choose_autocast(PlayerStyle.accurate, spells.trident_of_the_swamp)
	VW = Player.from_highscores(
		rsn='SirNargeth',
		equipment=Equipment(
			trident,
			Gear.from_bitterkoekje_bedevere('ancestral hat'),
			Gear.from_bitterkoekje_bedevere('god cape (i)'),
			Gear.from_bitterkoekje_bedevere('amulet of fury'),
			Gear.from_bitterkoekje_bedevere('ancestral robe top'),
			Gear.from_bitterkoekje_bedevere("ahrim's robeskirt"),
			Gear.from_bitterkoekje_bedevere('tome of fire'),
			Gear.from_bitterkoekje_bedevere('barrows gloves'),
			Gear.from_bitterkoekje_bedevere('infinity boots')
		)
	)

	X = Player.arma_tbow()
	X.equipment.equip(Gear.from_bitterkoekje_bedevere('brimstone ring'))
	# XZ = X      # TODO: Iron and ruby calcs

	players = [U, V, UW, VW, X]

	for p in players:
		p.overload()
		dt = p.weapon.active_style.damage_type

		if dt in PlayerStyle.melee_damage_types:
			p.pray(PlayerStats.StatPrayer.piety())
		elif dt in PlayerStyle.ranged_damage_types:
			p.pray(PlayerStats.StatPrayer.rigour())
		elif dt in PlayerStyle.magic_damage_types:
			p.pray(PlayerStats.StatPrayer.augury())
		else:
			raise PlayerStyle.StyleError('damage type not recognized')

	melee_hand = OlmMeleeHand(party_size, challenge_mode=False)
	melee_hand.stats.current_combat.defence = 0
	mage_hand = OlmMageHand(party_size, challenge_mode=False)
	head = OlmHead(party_size, challenge_mode=False)

	d_u = U.damage_against_monster(melee_hand).per_second
	d_v = V.damage_against_monster(mage_hand).per_second
	d_uw = UW.damage_against_monster(melee_hand).per_second
	d_vw = VW.damage_against_monster(mage_hand).per_second
	d_x = X.damage_against_monster(head).per_second

	# fudge factors
	f_u = 0.95
	f_v = 0.90
	f_uw = 0.99
	f_vw = 0.99

	# define n_v_prime to handle multiple mage camps (one skipper that suffers vs runners that don't)
	n_v_prime = n_v - 1 + f_v

	c_0 = n_u*f_u*d_u - n_v_prime*d_v - n_w*d_vw*f_vw
	c_1 = n_w*(d_uw*f_uw + d_vw*f_vw)
	epsilon_0 = -1*(c_0/c_1)

	b_0 = n_u*f_u*d_u + n_v_prime*d_v + n_w*d_vw*f_vw
	b_1 = n_w*(d_uw*f_uw - d_vw*f_vw)
	total_dps = b_0 + epsilon_0*b_1
	total_health = melee_hand.stats.combat.hitpoints + mage_hand.stats.combat.hitpoints
	kill_time_per_phase = total_health / total_dps
	phases = melee_hand.phases()

	kill_time_head = head.stats.combat.hitpoints / (dps_accounts * d_x)

	intermission_time = 30      # seconds
	intermissions = phases - 1

	total_time = np.dot([phases, intermissions, 1],	[kill_time_per_phase, intermission_time, kill_time_head])
	total_time_minutes = total_time / 60

	print('Olm ({:} scale) with {:} DPS accounts'.format(party_size, dps_accounts))
	print('\t{:} phases, {:3.0f} seconds per phase'.format(phases, kill_time_per_phase))
	print('\t{:} intermissions, {:} seconds per intermission'.format(intermissions, intermission_time))
	print('\t{:.0f} seconds for head phase'.format(kill_time_head))
	print('\n\t{:.0f} minutes to complete olm'.format(total_time_minutes))



def scaled_olm_iron_whipper_competent_team_with_flex(party_size: int, dps_accounts: int):
	assert 3 <= dps_accounts <= 6   # TODO: general formula

	n_u = 1
	n_w = 1
	n_x = 1
	n_v = dps_accounts - n_u - n_x
	n_z = dps_accounts

	U = Player.max_blood_fury_scythe_bandos()
	V = Player.max_sang_brimstone()

	whip = Weapon.from_bitterkoekje_bedevere('abyssal whip')
	whip.choose_style_by_name(PlayerStyle.lash)
	W = Player.from_highscores(
		rsn='SirNargeth',
		equipment=Equipment(
			whip,
			Gear.from_bitterkoekje_bedevere('neitiznot'),
			Gear.from_bitterkoekje_bedevere('fire cape'),
			Gear.from_bitterkoekje_bedevere('amulet of fury'),
			Gear.from_bitterkoekje_bedevere('fighter torso'),
			Gear.from_bitterkoekje_bedevere('proselyte cuisse'),
			Gear.from_bitterkoekje_bedevere('dragon defender'),
			Gear.from_bitterkoekje_bedevere('barrows gloves'),
			Gear.from_bitterkoekje_bedevere('dragon boots'),
			Gear.from_bitterkoekje_bedevere('berserker (i)')
		)
	)

	Z = Player.arma_tbow()
	Z.equipment.equip(Gear.from_bitterkoekje_bedevere('brimstone ring'))
	# XZ = X      # TODO: Iron and ruby calcs

	players = [U, V, W, Z]

	for p in players:
		p.overload()
		dt = p.weapon.active_style.damage_type

		if dt in PlayerStyle.melee_damage_types:
			p.pray(PlayerStats.StatPrayer.piety())
		elif dt in PlayerStyle.ranged_damage_types:
			p.pray(PlayerStats.StatPrayer.rigour())
		elif dt in PlayerStyle.magic_damage_types:
			p.pray(PlayerStats.StatPrayer.augury())
		else:
			raise PlayerStyle.StyleError('damage type not recognized')

	melee_hand = OlmMeleeHand(party_size, challenge_mode=False)
	melee_hand.stats.current_combat.defence = 0
	mage_hand = OlmMageHand(party_size, challenge_mode=False)
	head = OlmHead(party_size, challenge_mode=False)

	d_u = U.damage_against_monster(melee_hand).per_second
	d_v = V.damage_against_monster(mage_hand).per_second
	d_w = W.damage_against_monster(melee_hand).per_second
	d_x = d_u
	d_y = d_v
	d_z = Z.damage_against_monster(head).per_second

	# fudge factors
	f_u = 0.95
	f_v = 0.90
	f_w = 0.99
	f_x = f_u
	f_y = f_v
	f_z = 0.90

	# define n_v_prime to handle multiple mage camps (one skipper that suffers vs runners that don't)
	n_v_prime = n_v - 1 + f_v
	n_z_prime = n_z + 2*(f_z - 1)

	def melee_dps(epsilon):
		return n_u*f_u*d_u + n_w*f_w*d_w + epsilon*n_x*d_x*f_x

	def magic_dps(epsilon):
		return n_v_prime*d_v + (1 - epsilon)*n_x*d_y*f_y

	def ranged_dps():
		return n_z_prime*d_z

	def dps_difference(epsilon):
		return melee_dps(epsilon) - magic_dps(epsilon)

	solution = fsolve(dps_difference, np.asarray([0.5]), band=(0, 1))
	epsilon_0 = solution[0]
	total_dps = melee_dps(epsilon_0) + magic_dps(epsilon_0)
	total_health = melee_hand.stats.combat.hitpoints + mage_hand.stats.combat.hitpoints
	kill_time_per_phase = total_health / total_dps
	phases = melee_hand.phases()

	kill_time_head = head.stats.combat.hitpoints / ranged_dps()

	intermission_time = 30      # seconds
	intermissions = phases - 1

	total_time = np.dot([phases, intermissions, 1],	[kill_time_per_phase, intermission_time, kill_time_head])
	total_time_minutes = total_time / 60

	print('Olm ({:} scale) with {:} DPS accounts'.format(party_size, dps_accounts))
	print('\t{:} phases, {:3.0f} seconds per phase'.format(phases, kill_time_per_phase))
	print('\tFlex should spend {:.0f}% melee'.format(epsilon_0*100))
	print('\t{:} intermissions, {:} seconds per intermission'.format(intermissions, intermission_time))
	print('\t{:.0f} seconds for head phase'.format(kill_time_head))
	print('\n\t{:.0f} minutes to complete olm'.format(total_time_minutes))



def scaled_olm_defence_means(
		players_bounds: Union[int, Tuple[int, int]],
		challenge_mode: bool = False,
		max_combat_level: int = None,
		max_hitpoints_level: int = None,
		scale_bounds: Tuple[int, int] = (15, 100),
		trials: int = int(1e6)
):
	dwh_target = 3

	assert players_bounds[0] <= players_bounds[1]
	assert scale_bounds[0] <= scale_bounds[1]
	players_ary = np.arange(players_bounds[0], players_bounds[1] + 1)
	scales_ary = np.arange(scale_bounds[0], scale_bounds[1] + 1)
	m = len(players_ary)
	n = len(scales_ary)

	mean_defence_mx = np.zeros(shape=(m, n, trials))

	dwh = Player.dwh_inquisitor_brimstone()
	bgs = Player.bgs_bandos()
	pp = (dwh, bgs)

	for p in pp:
		p.overload()
		p.pray(PlayerStats.StatPrayer.piety())

	biggest_olm = OlmMeleeHand(party_size=scales_ary.max(),
	                           challenge_mode=challenge_mode,
	                           max_combat_level=max_combat_level,
	                           max_hitpoints_level=max_hitpoints_level
	                           )
	defence_max = biggest_olm.stats.combat.defence
	amc_dwh = osrs_markov.defence_matrix_dwh_generator(dwh, biggest_olm)

	biggest_olm = OlmMeleeHand(party_size=scales_ary.max(),
	                           challenge_mode=challenge_mode,
	                           max_combat_level=max_combat_level,
	                           max_hitpoints_level=max_hitpoints_level
	                           )

	amc_bgs = osrs_markov.defence_matrix_bgs_generator(bgs, biggest_olm)

	for iter in np.arange(trials):

		for i, players in enumerate(players_ary):
			specs_available = 2 * players

			for j, scale in enumerate(scales_ary):
				pass


def hundred_scale_dps_balance(melee_mage, total_raiders: int, tank_dps_ratio: float = None, thralls: bool = False):
	thrall_dps = 0.625 if thralls else 0

	melee, mage = melee_mage
	melee_dps = 11.94 + thrall_dps
	mage_dps = 6.31 + thrall_dps
	tank_dps = 9.84
	tank_dps_ratio = tank_dps_ratio if tank_dps_ratio else 1

	melee_dps = melee_dps * melee + tank_dps * tank_dps_ratio
	mage_dps = mage_dps * mage
	dps_diff = melee_dps - mage_dps
	player_diff = total_raiders - (melee + mage)
	return dps_diff, player_diff


def scaled_olm_time_estimate(num_raiders: int, party_size: int, tank_dps_ratio: float = None, thralls: bool = False):
	num_available_raiders = num_raiders - 2     # tanks
	x0 = np.asarray([(1/3)*num_available_raiders, (2/3)*num_available_raiders])

	res = fsolve(
		hundred_scale_dps_balance,
		x0,
		(num_available_raiders, tank_dps_ratio, thralls),
	)
	print(res)
	num_melee, num_mage = res

	thrall_dps = 0.625 if thralls else 0

	dps_melee = 11.94 + thrall_dps
	dps_sang = 6.31 + thrall_dps
	dps_head = 8.5      # low fudge number

	head = OlmHead(party_size, False)

	melee_hp = OlmMeleeHand(party_size, False).stats.combat.hitpoints
	mage_hp = OlmMageHand(party_size, False).stats.combat.hitpoints
	head_hp = OlmHead(party_size, False).stats.combat.hitpoints

	phases = head.phases()

	melee_kill_time = melee_hp / (num_melee * dps_melee)    # seconds for all
	mage_kill_time = mage_hp / (num_mage * dps_sang)
	head_kill_time = head_hp / ((num_melee+num_mage)*dps_head)
	intermission_time = 30

	hands_kill_time = max([melee_kill_time, mage_kill_time])

	seconds_to_kill = hands_kill_time*phases + intermission_time*(phases - 1) + head_kill_time
	minutes_to_kill = seconds_to_kill / 60
	hours_to_kill = minutes_to_kill / 60

	seconds_per_overload_dose = 300
	overload_dose_per_potion = 4
	overload_doses_needed_per_person = seconds_to_kill / seconds_per_overload_dose
	overload_potions_needed_per_person = overload_doses_needed_per_person / overload_dose_per_potion

	seconds_per_stamina_dose = 120
	stamina_dose_per_potion = 4
	stamina_doses_needed_per_phase = melee_kill_time / seconds_per_stamina_dose
	stamina_doses_needed_per_olm = stamina_doses_needed_per_phase * phases
	stamina_potions_needed_per_olm = stamina_doses_needed_per_olm / stamina_dose_per_potion

	header = ['attribute', 'value']
	table = [
		["kill time (minutes)", math.ceil(minutes_to_kill)],
		["Full overload potions needed per person", math.ceil(overload_potions_needed_per_person)],
		["Full stamina potions needed per person", math.ceil(stamina_potions_needed_per_olm)]
	]
	table = tabulate(table, headers=header)
	# print(table)

	return num_melee, num_mage, minutes_to_kill, overload_potions_needed_per_person, stamina_potions_needed_per_olm


def assignment_table_hundred_scale(lb: int, ub: int, thralls: bool = False):
	rows = []
	headers = ["# Raiders", "# Lance 4:0", "# Sang", "Kill time (min)", "Ovl. per Raider", "Stam. per Lancer"]

	for i in range(lb, ub+1):
		num_mel, num_mag, kill_time, opnpp, spnpp = scaled_olm_time_estimate(i, 100, thralls=thralls)
		rows.append([i, num_mel, num_mag, kill_time, opnpp, spnpp])

	table = tabulate(rows, headers=headers, floatfmt=".1f")
	print(table)


def melee_comparison(*players):
	pass    # lmao there's no need torva >>>>>>>>>>>>>>>>>>>



if __name__ == '__main__':
	bandos_scythe = Player.max_scythe_bandos()
	inq_scythe = Player.max_scythe_inquisitor()
	torva_scythe = Player.max_scythe_torva()

	# main(ps, cm)
	# camp_vs_fifteen_sixteen_comp(ps, cm)
	# scaled_olm_estimate(41, 4)
	# scaled_olm_estimate(15, 3)
	# scaled_olm_estimate(23, 4)
	# scaled_olm_estimate(31, 6)
	# scaled_olm_iron_whipper_competent_team_with_flex(39, 5)
	# void_arma_scale()
	# mage_dps_scale()
	# mage_dps_scale()
	# melee_dps_scale()
	# melee_camp_scale()
	# scaled_olm_time_estimate(15, 100)
	# assignment_table_hundred_scale(7, 30, thralls=True)



