from main import *
import matplotlib.pyplot as plt
import cox_tools as ct


def plot_decorator(magic_lvl: int = 99):
	ice_demon_name = IceDemon.get_name()

	kodai = Weapon.from_bitterkoekje_bedevere('kodai wand')
	kodai.choose_autocast(PlayerStyle.standard_spell, spells.fire_surge)

	sotd = Weapon.from_bitterkoekje_bedevere('staff of the dead')
	sotd.choose_autocast(PlayerStyle.standard_spell, spells.fire_surge)
	#
	# nightmare_staff = Weapon.from_bitterkoekje_bedevere('nightmare staff')
	# nightmare_staff.choose_autocast(PlayerStyle.standard_spell, spells.fire_surge)
	#
	# noob = Player.decihybrid_ice_demon()
	# noob.name = 'noob w/ smoke'
	#
	# noob_with_a_kodai = Player.decihybrid_ice_demon()
	# noob_with_a_kodai.equipment.equip(kodai)
	# noob_with_a_kodai.name = 'noob w/ kodai'
	#
	# noob_with_a_sotd = Player.decihybrid_ice_demon()
	# noob_with_a_sotd.equipment.equip(sotd)
	# noob_with_a_sotd.name = 'noob w/ sotd'
	#
	# noob_with_a_nightmare_staff = Player.decihybrid_ice_demon()
	# noob_with_a_nightmare_staff.equipment.equip(nightmare_staff)
	# noob_with_a_nightmare_staff.name = 'noob w/ nightmare staff'

	# mystic = Player.decihybrid_ice_demon()
	# mystic.name = '[mystic] fire surge (smoke)'
	# mystic.equipment.equip(
	# 	Gear.from_bitterkoekje_bedevere('tormented bracelet')
	# )
	#
	# mystic_sotd = Player.decihybrid_ice_demon()
	# mystic_sotd.name = '[mystic] fire surge (sotd)'
	# mystic_sotd.equipment.equip(
	# 	sotd,
	# 	Gear.from_bitterkoekje_bedevere('tormented bracelet')
	# )

	# chad = Player.decihybrid_ice_demon_chad_mode()
	# chad.name = '[ahrims] fire surge (smoke)'
	# chad.equipment.equip(
	# 	Gear.from_bitterkoekje_bedevere('infinity boots'),
	# 	# Gear.from_bitterkoekje_bedevere("ahrim's hood")
	# )

	chad_sotd = Player.decihybrid_ice_demon_chad_mode()
	chad_sotd.name = '[ahrims] fire surge (sotd)'
	chad_sotd.equipment.equip(
		sotd,
		# Gear.from_bitterkoekje_bedevere('infinity boots'),
		# Gear.from_bitterkoekje_bedevere("ahrim's hood")
	)

	chad_sotd_seers = Player.decihybrid_ice_demon_chad_mode()
	chad_sotd_seers.name = '[ahrims] fire surge (sotd) (seers (i))'
	chad_sotd_seers.equipment.equip(
		sotd,
		# Gear.from_bitterkoekje_bedevere('infinity boots'),
		Gear.from_bitterkoekje_bedevere('seers (i)')
		# Gear.from_bitterkoekje_bedevere("ahrim's hood")
	)


	# voider = Player.mage_void_ice_demon()
	#
	#
	# voider_sotd = Player.mage_void_ice_demon()
	# voider_sotd.equipment.equip(sotd)
	# voider_sotd.name = '[void] fire surge (sotd)'

	players = [chad_sotd, chad_sotd_seers]
	# players = [mystic, mystic_sotd, chad, chad_sotd, voider, voider_sotd]
	# players = [voider, voider_sotd]
	# players = [noob, noob_with_a_kodai, noob_with_a_sotd, noob_with_a_nightmare_staff]

	for p in players:
		p.stats.combat.magic = magic_lvl
		p.reset_current_stats()
		p.overload()
		p.pray(PlayerStats.StatPrayer.mystic_might())


	csc = ct.plot_comparison(ct.cox_scale_comparison)
	hammer_lands = np.arange(100)

	for lands in hammer_lands:
		csc(players, ice_demon_name, bounds=(1, 100), dwh_landed=lands,
		    plot_title='{:} ({:} hammers) ({:} magic lvl)'.format(ice_demon_name, lands, magic_lvl)
		    )

def main(party_size: int, challenge_mode: bool):
	ice_demon = IceDemon(party_size, challenge_mode)

	noob = Player.decihybrid_ice_demon()
	chad = Player.decihybrid_ice_demon_chad_mode()
	giga_chad = Player.max_kodai_fire_surge()
	arma_tbow = Player.arma_tbow()
	void_tbow = Player.void_tbow()

	players = [noob, chad, giga_chad, arma_tbow, void_tbow]

	for p in players:
		p.overload()

	noob.pray(PlayerStats.StatPrayer.mystic_might())
	chad.pray(PlayerStats.StatPrayer.augury())
	giga_chad.pray(PlayerStats.StatPrayer.augury())
	arma_tbow.pray(PlayerStats.StatPrayer.rigour())
	void_tbow.pray(PlayerStats.StatPrayer.rigour())

	x = np.arange(ice_demon.stats.combat.defence + 1)
	y1 = np.zeros(x.shape)
	y2 = np.zeros(x.shape)
	y3 = np.zeros(x.shape)
	# a1 = np.zeros(x.shape)
	# a2 = np.zeros(x.shape)
	z1 = np.zeros(x.shape)
	z2 = np.zeros(x.shape)

	for i in x:
		ice_demon.stats.current_combat.defence = i

		noob_dam = noob.damage_against_monster(ice_demon)
		chad_dam = chad.damage_against_monster(ice_demon)
		giga_chad_dam = giga_chad.damage_against_monster(ice_demon)

		y1[i] = noob_dam.per_second # * 5
		y2[i] = chad_dam.per_second # * 5
		y3[i] = giga_chad_dam.per_second
		# a1[i] = 1 - noob_dam.hitsplats[0].probability[0]
		# a2[i] = 1 - chad_dam.hitsplats[0].probability[0]
		z1[i] = arma_tbow.damage_against_monster(ice_demon).per_second
		z2[i] = void_tbow.damage_against_monster(ice_demon).per_second

	hammers_hit = np.arange(1, 9)
	defence_milestones = np.zeros(hammers_hit.shape)
	ice_demon.stats.current_combat.defence = ice_demon.stats.combat.defence

	for index, hits in enumerate(hammers_hit):
		ice_demon.dwh_reduce()
		defence_milestones[index] = ice_demon.stats.current_combat.defence

	height = 12

	# plt.subplots(2, 1)

	# plt.subplot(211)
	# fig = plt.figure()
	# ax = fig.add_subplot(111)
	# ax.set(xlim=[0, 200], ylim=[0, 12])
	#
	# plt.vlines(defence_milestones, 0, height, linewidth=0.5, colors='k', ls='--')
	# plt.plot(x, y1, x, y2, x, z1, x, z2)  # , x, z1, x, z2)
	# plt.legend(['smoke (current)', 'smoke (chad setup)', 'arma tbow', 'void tbow'])
	# plt.title('DPS')
	# plt.xlabel('defence')
	# plt.xticks(np.arange(0, 201, 25))
	# plt.ylabel('dps')
	# plt.yticks(np.arange(13))
	#
	# plt.tight_layout()
	#
	# del fig, ax


	csc = ct.plot_comparison(ct.cox_scale_comparison)

	for lands in range(5):
		csc(players, ice_demon.name, bounds=(1, 100), dwh_landed=lands,
		    plot_title='{:} ({:} hammers)'.format(ice_demon.name, lands)
		    )


	# plt.subplot(212)
	# plt.plot(x, a1, x, a2)
	# plt.legend(['smoke', 'chad smoke'])
	# plt.title('hybrid gang (current) vs eventual chad endgame')
	# plt.xlabel('defence')
	# plt.ylabel('chance to not hit zero')

	plt.show()



if __name__ == '__main__':
	plot_decorator(99)
	# main(23, False)
