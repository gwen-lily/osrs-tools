from main import *
from scipy.optimize import fsolve
import cox_tools

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

	cox_tools.cox_scale_comparison(players, OlmMeleeHand.get_name(), bounds=(15, 32))


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


def scaled_olm_estimate(party_size: int, dps_accounts: int, iron_whipper: bool = False):
	assert 3 <= dps_accounts <= 8   # TODO: general formula

	z = 1
	x = 1 if dps_accounts < 6 else 2
	y = dps_accounts - x - z

	X = Player.max_blood_fury_scythe_bandos()
	Y = Player.max_sang_brimstone()
	Z = Player.max_scythe_bandos()

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

	R = Player.arma_tbow()
	R.equipment.equip(Gear.from_bitterkoekje_bedevere("brimstone ring"))

	players = [X, Y, Z, W, R]

	for p in players:
		p.overload()

		dt = p.weapon.active_style.damage_type

		if dt in PlayerStyle.melee_damage_types:
			p.pray('piety')
		elif dt in PlayerStyle.ranged_damage_types:
			p.pray('rigour')
		elif dt in PlayerStyle.magic_damage_types:
			p.pray('augury')
		else:
			continue

	melee_hand = OlmMeleeHand(party_size, challenge_mode=False)
	mage_hand = OlmMageHand(party_size, challenge_mode=False)
	melee_hand.stats.current_combat.defence = 0
	head = OlmHead(party_size, challenge_mode=False)

	DPSx = X.damage_against_monster(melee_hand).per_second
	DPSy = Y.damage_against_monster(mage_hand).per_second
	DPSz = (15/16) * Z.damage_against_monster(melee_hand).per_second
	DPSw = W.damage_against_monster(melee_hand).per_second

	c0 = x*DPSx + DPSw - (y+z)*DPSy
	c1 = z*(DPSz + DPSy)
	eta0 = -c0/c1

	d0 = x*DPSx + DPSw + (y+z)*DPSy
	d1 = z*(DPSz - DPSy)
	dps_total = d0 + d1*eta0
	kill_time_per_phase = (melee_hand.stats.combat.hitpoints + mage_hand.stats.combat.hitpoints) / dps_total
	phases = melee_hand.phases()

	DPSr = R.damage_against_monster(head).per_second
	kill_time_head = head.stats.combat.hitpoints / (dps_accounts * DPSr)

	intermission_time = 30      # seconds
	intermissions = phases - 1

	total_time = np.dot([phases, intermissions, 1],	[kill_time_per_phase, intermission_time, kill_time_head])
	total_time_minutes = total_time / 60

	print('Olm ({:} scale) with {:} DPS accounts'.format(party_size, dps_accounts))
	print('\t{:} phases, {:3.0f} seconds per phase'.format(phases, kill_time_per_phase))
	print('\tFlex should spend {:.0f}% melee'.format(eta0*100))
	print('\t{:} intermissions, {:} seconds per intermission'.format(intermissions, intermission_time))
	print('\t{:.0f} seconds for head phase'.format(kill_time_head))
	print('\n\t{:.0f} minutes to complete olm'.format(total_time_minutes))


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


if __name__ == '__main__':
	ps = 31
	cm = False

	# main(ps, cm)
	# camp_vs_fifteen_sixteen_comp(ps, cm)
	# scaled_olm_estimate(41, 4)
	# scaled_olm_estimate(15, 3)
	# scaled_olm_estimate(23, 4)
	# scaled_olm_estimate(31, 6)
	scaled_olm_iron_whipper_competent_team_with_flex(39, 5)
