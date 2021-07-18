from main import *
import matplotlib.pyplot as plt
import cox_tools as ct

# With ranging potion
# tbow void > bp void for rope rangers @ 21
# With overload
# tbow void > bp void for rope rangers @ 17


def main(party_size: int, challenge_mode: bool):
	ranger = CoxMonster.from_de0(
		name='deathly ranger',
		party_size=ps,
		challenge_mode=cm
	)
	mage = CoxMonster.from_de0(
		name='deathly mage',
		party_size=ps,
		challenge_mode=cm
	)

	# Void chin
	void_chinner = Player.void_chinchompa()
	void_chinner.overload()
	void_chinner.pray(PlayerStats.StatPrayer.rigour())

	# Arma chin
	arma_chinner = Player.arma_chinchompa()
	arma_chinner.overload()
	arma_chinner.pray(PlayerStats.StatPrayer.rigour())

	void_damage_ranger = void_chinner.damage_against_monster(ranger, distance=5)
	arma_damage_ranger = arma_chinner.damage_against_monster(ranger, distance=5)
	print('Chin damage against rangers and mages:\n\tvoid: {:}\n\tarma: {:}'.format(void_damage_ranger.per_second,
	                                                                                arma_damage_ranger.per_second))


def damage_steps(party_size: int, challenge_mode: bool):
	def inner(xxx, yyy):
		ranger = CoxMonster.from_de0(
			name='deathly ranger',
			party_size=xxx,
			challenge_mode=yyy
		)
		mage = CoxMonster.from_de0(
			name='deathly mage',
			party_size=xxx,
			challenge_mode=yyy
		)

		# Void bp
		void_bp = Player.void_bp()
		void_bp.pray(PlayerStats.StatPrayer.rigour())

		# Arma bp
		arma_bp = Player.arma_bp()
		arma_bp.pray(PlayerStats.StatPrayer.rigour())

		# Void tbow
		void_tbow = Player.void_tbow()
		void_tbow.pray(PlayerStats.StatPrayer.rigour())

		# Arma tbow
		arma_tbow = Player.arma_tbow()
		arma_tbow.pray(PlayerStats.StatPrayer.rigour())



		# pot
		void_bp.overload()
		arma_bp.overload()
		void_tbow.overload()
		arma_tbow.overload()


		void_damage_ranger = void_bp.damage_against_monster(ranger)
		arma_damage_ranger = arma_bp.damage_against_monster(ranger)
		void_tbow_damage_ranger = void_tbow.damage_against_monster(ranger)
		arma_tbow_damage_ranger = arma_tbow.damage_against_monster(ranger)

		return void_damage_ranger.per_second, arma_damage_ranger.per_second, void_tbow_damage_ranger.per_second, \
		       arma_tbow_damage_ranger.per_second

		# print('bp against rangers:\n\tvoid: {:}\n\tarma: {:}'.format(void_damage_ranger.per_second,
		#                                                              arma_damage_ranger.per_second))
		#
	# print('tbow against rangers:\n\tvoid: {:}'.format(void_tbow_damage_ranger.per_second))

	cm = False

	# print(dps_diff([16], cm))

	# ps0 = fsolve(dps_diff, [17], (cm,), band=(1, 50))
	# print(ps0)

	ps_ary = np.arange(1, 51)
	x = ps_ary
	a = np.empty(x.shape)
	b = np.empty(x.shape)
	c = np.empty(x.shape)
	d = np.empty(x.shape)

	for i, ps in enumerate(ps_ary):
		a[i], b[i], c[i], d[i] = inner(ps, cm)

	plt.plot(x, a, x, b, x, c, x, d)
	plt.title('Rope ranger dps in max gear w/ overload')
	plt.xlabel('party size')
	plt.ylabel('dps')
	plt.legend(['void bp', 'arma bp', 'void tbow', 'arma tbow'], loc='lower right')
	plt.show()


def dps_diff(party_size: np.ndarray, challenge_mode: bool):
	party_size_ind: int = party_size[0]

	ranger = CoxMonster.from_de0(
		name='deathly ranger',
		party_size=party_size_ind,
		challenge_mode=challenge_mode
	)
	mage = CoxMonster.from_de0(
		name='deathly mage',
		party_size=party_size_ind,
		challenge_mode=challenge_mode
	)

	# Void bp
	void_bp = Player.void_bp()
	void_bp.pray(PlayerStats.StatPrayer.rigour())

	# Void tbow
	void_tbow = Player.void_tbow()
	void_tbow.pray(PlayerStats.StatPrayer.rigour())

	# pot
	void_bp.overload()
	void_tbow.overload()
	# void_bp.bastion_potion()
	# arma_bp.bastion_potion()
	# void_tbow.bastion_potion()
	# arma_tbow.bastion_potion()

	void_damage_ranger = void_bp.damage_against_monster(ranger)
	void_tbow_damage_ranger = void_tbow.damage_against_monster(ranger)
	diff = void_damage_ranger.per_second - void_tbow_damage_ranger.per_second

	return diff


def rope_decorator():
	ranger_name = 'deathly ranger'
	mage_name = 'deathly mage'

	# void_bp = Player.void_bp()
	void_tbow = Player.void_tbow()
	arma_tbow = Player.arma_tbow()
	void_chin = Player.void_chinchompa()
	arma_chin = Player.arma_chinchompa()

	# players = [void_bp, void_tbow, arma_tbow, void_chin, arma_chin]
	players = [void_tbow, arma_tbow, void_chin, arma_chin]

	for p in players:
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())

	attack_distance = 5
	additional_targets = 3

	csc = ct.plot_comparison(ct.cox_scale_comparison)
	# csc = ct.print_comparison(ct.cox_scale_comparison)
	csc(players, ranger_name, bounds=(15, 100), distance=attack_distance, additional_monsters_hit=additional_targets, cast_vulnerability=True, plot_title="deathly ranger (vulnerability)")
	csc(players, mage_name, bounds=(15, 100), distance=attack_distance, additional_monsters_hit=additional_targets, cast_vulnerability=True, plot_title="deathly mage (vulnerability)")


if __name__ == '__main__':
	rope_decorator()


