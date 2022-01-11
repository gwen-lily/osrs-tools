from main import *
import matplotlib.pyplot as plt
import cox_tools as ct


def rope_decorator():
	# wtf is this function? hammers?
	mystic_name = 'skeletal mystic'

	tbow = Player.arma_tbow()
	zbow = Player.arma_zbow()
	fbow = Player.bowfa()
	blowpipe = Player.arma_bp()

	players = [tbow, zbow, fbow, blowpipe]

	# extra gear swaps
	salve = Gear.from_bitterkoekje_bedevere('salve amulet (ei)')
	brimstone = Gear.from_bitterkoekje_bedevere('brimstone ring')

	for p in players:
		p.equipment.equip(salve, brimstone)
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())

	hammer_range = np.arange(0 + 1)

	# csc = ct.plot_comparison(ct.cox_scale_comparison)
	csc = ct.print_comparison(ct.cox_scale_comparison)

	for lands in hammer_range:
		csc(players, mystic_name, bounds=(10,20), dwh_landed=lands,
		    plot_title='{:} ({:} hammers)'.format(mystic_name, lands)
		    )


def mystic_comparison():
	mystic_name = 'skeletal mystic'

	tbow = Player.arma_tbow()
	zbow = Player.arma_zbow()
	fbow = Player.bowfa()
	blowpipe = Player.arma_bp()

	players = [tbow, zbow, fbow, blowpipe]

	# extra reasonable gear swaps
	salve = Gear.from_bitterkoekje_bedevere('salve amulet (ei)')
	brimstone = Gear.from_bitterkoekje_bedevere('brimstone ring')

	for p in players:
		p.equipment.equip(salve, brimstone)
		p.pray(PlayerStats.StatPrayer.rigour())
		p.overload()

	scale_bounds = (1, 31)

	# csc = ct.plot_comparison(ct.cox_scale_comparison)
	csc = ct.print_comparison(ct.cox_scale_comparison)

	csc(players, mystic_name, bounds=scale_bounds, plot_title='{:}'.format(mystic_name))


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

	lad = Player.arma_zbow()
	salve = Gear.from_bitterkoekje_bedevere('salve amulet (ei)')
	players = [lad]

	for p in players:
		p.equipment.equip(salve)
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())

	dam = lad.damage_against_monster(mystic)

	print(dam.mean)
	print(dam.hitsplats[0].max_hit)

	for d, p in zip(dam.hitsplats[0].damage, dam.hitsplats[0].probability):
		print(d, p)


if __name__ == '__main__':
	# ruby_test()
	# level_comparison()
	# rope_decorator()
	mystic_comparison()
