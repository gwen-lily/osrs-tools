from main import *
import matplotlib.pyplot as plt
import cox_tools as ct


def rope_decorator():
	mystic_name = 'skeletal mystic'

	arma_tbow = Player.arma_tbow()
	arma_bp_dragon_darts = Player.arma_bp()
	arma_bp_dragon_darts.name = '[arma] bp (dragon darts)'

	arma_bp_rune_darts = Player.arma_bp()
	arma_bp_rune_darts.equipment.equip(Gear.from_bitterkoekje_bedevere('rune dart'))
	arma_bp_rune_darts.name = '[arma] bp (rune darts)'

	void_tbow = Player.void_tbow()
	# void_bp = Player.void_bp()
	arma_dhcb_ruby = Player.arma_dhcb_ruby()

	#players = [arma_tbow, arma_bp_dragon_darts, arma_bp_rune_darts, arma_dhcb_ruby, void_tbow]

	# players = [arma_tbow, void_tbow]
	players = [arma_tbow, arma_bp_dragon_darts]

	for p in players:
		p.equipment.equip(Gear.from_bitterkoekje_bedevere('salve amulet (ei)'))
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())
		p.equipment.equip(Gear.from_bitterkoekje_bedevere('brimstone ring'))

	hammer_range = np.arange(0 + 1)

	# csc = ct.plot_comparison(ct.cox_scale_comparison)
	csc = ct.print_comparison(ct.cox_scale_comparison)

	for lands in hammer_range:
		csc(players, mystic_name, bounds=(10,20), dwh_landed=lands,
		    plot_title='{:} ({:} hammers)'.format(mystic_name, lands)
		    )


def level_comparison():
	mystic_name = 'skeletal mystic'

	level_range = np.arange(85, 99 + 1)
	players = []

	for level in level_range:
		p = Player.void_tbow()
		# p.equipment.equip_elite_void()
		p.name = '{:} ({:} ranged)'.format(p.name, level)
		p.equipment.equip(Gear.from_bitterkoekje_bedevere("salve amulet (ei)"))
		p.stats.combat.ranged = level
		p.reset_current_stats()
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())
		players.append(p)

	hammer_range = np.arange(2 + 1)
	csc = ct.plot_comparison(ct.cox_scale_comparison)

	for lands in hammer_range:
		csc(players, mystic_name, bounds=(1, 100), dwh_landed=lands,
		    plot_title='{:} ({:} hammers)'.format(mystic_name, lands)
		    )


def ruby_test():
	mystic = SkeletalMystic(7, False)

	arma_dhcb_ruby = Player.arma_dhcb_ruby()

	players = [arma_dhcb_ruby]

	for p in players:
		p.equipment.equip(Gear.from_bitterkoekje_bedevere('salve amulet (ei)'))
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())

	dam = arma_dhcb_ruby.damage_against_monster(mystic)

	print(dam.mean)
	print(dam.hitsplats[0].max_hit)

	for d, p in zip(dam.hitsplats[0].damage, dam.hitsplats[0].probability):
		print(d, p)



if __name__ == '__main__':
	# ruby_test()
	# level_comparison()
	rope_decorator()
