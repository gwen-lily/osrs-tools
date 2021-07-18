from main import *
import matplotlib.pyplot as plt
import cox_tools as ct

def main(party_size: int, challenge_mode: bool):
	def inner(xxx, yyy):
		shaman = CoxMonster.from_de0(
			name='lizardman shaman',
			party_size=xxx,
			challenge_mode=yyy
		)

		# On-task chin
		task_chinner = Player.on_task_chinchompa()
		task_chinner.pray(PlayerStats.StatPrayer.rigour())

		# Void chin
		void_chinner = Player.void_chinchompa()
		void_chinner.pray(PlayerStats.StatPrayer.rigour())

		# Arma chin
		arma_chinner = Player.arma_chinchompa()
		arma_chinner.pray(PlayerStats.StatPrayer.rigour())

		task_chinner.overload()
		void_chinner.overload()
		arma_chinner.overload()

		task_damage = task_chinner.damage_against_monster(shaman, distance=9)
		void_damage = void_chinner.damage_against_monster(shaman, distance=9)
		arma_damage = arma_chinner.damage_against_monster(shaman, distance=9)

		return 5*task_damage.per_second, 5*void_damage.per_second, 5*arma_damage.per_second

		# print('task: {:}\nvoid: {:}\narma: {:}'.format(task_damage.per_second,
		#                                                void_damage.per_second,
		#                                                arma_damage.per_second))

	cm = False

	ps_ary = np.arange(1, 61)
	x = ps_ary
	a = np.empty(x.shape)
	b = np.empty(x.shape)
	c = np.empty(x.shape)

	for i, ps in enumerate(ps_ary):
		a[i], b[i], c[i] = inner(ps, cm)

	plt.plot(x, a, x, b, x, c, )
	plt.title('Shaman dps w/ 6 shamans, overload, and rapid style')
	plt.xlabel('party size')
	plt.ylabel('dps')
	plt.legend(['task', 'void', 'arma'], loc='upper right')
	plt.show()

	d = np.empty(x.shape)
	e = np.empty(x.shape)

	for i, ps in enumerate(ps_ary):
		d[i], e[i] = rapid_vs_longrange(ps, cm)

	plt.plot(x, d, x, e)
	plt.title('Shaman dps w/ 6 shamans, task, and overload')
	plt.xlabel('party size')
	plt.ylabel('dps')
	plt.legend(['rapid', 'longrange'], loc='upper right')
	plt.show()

	kill_time_five(39, cm)


def rapid_vs_longrange(party_size: int, challenge_mode: bool):
	shaman = CoxMonster.from_de0(
		name='lizardman shaman',
		party_size=party_size,
		challenge_mode=challenge_mode
	)

	# On-task rapid
	rapid_chinner = Player.on_task_chinchompa()
	rapid_chinner.pray(PlayerStats.StatPrayer.rigour())

	# On-task longrange
	longrange_chinner = Player.on_task_chinchompa()
	longrange_chinner.pray(PlayerStats.StatPrayer.rigour())
	longrange_chinner.weapon.choose_style_by_name(PlayerStyle.long_fuse)

	rapid_chinner.overload()
	longrange_chinner.overload()

	rapid_damage = rapid_chinner.damage_against_monster(shaman, distance=9)
	longrange_damage = longrange_chinner.damage_against_monster(shaman, distance=9)

	return 5*rapid_damage.per_second, 5*longrange_damage.per_second


def kill_time_five(party_size: int, challenge_mode: bool):
	shaman = CoxMonster.from_de0(
		name='lizardman shaman',
		party_size=party_size,
		challenge_mode=challenge_mode
	)

	# On-task chin
	task_chinner = Player.on_task_chinchompa()
	task_chinner.pray(PlayerStats.StatPrayer.rigour())
	task_chinner.overload()
	task_damage = task_chinner.damage_against_monster(shaman, distance=9)
	dps_theory = task_damage.per_second * 5

	kill_times = []

	for i in range(5):
		shaman.reset_current_stats()
		ticks, _ = task_chinner.kill_monster(shaman, distance=9)
		kill_times.append(ticks)

	print(kill_times)
	longest_time = max(kill_times) * 0.6
	health = shaman.stats.combat.hitpoints
	dps_actual = 5*health / longest_time

	print('theory: {:.3f}'.format(dps_theory))
	print('actual: {:.3f}'.format(dps_actual))


def chin_decorator():
	shaman_name = 'lizardman shaman'

	task_chinner = Player.on_task_chinchompa()
	task_tbow = Player.on_task_tbow()
	void_tbow = Player.void_tbow()

	players = [task_chinner, task_tbow, void_tbow]

	for p in players:
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())

	attack_distance = 9

	csc = ct.plot_comparison(ct.cox_scale_comparison)
	csc(players, shaman_name, distance=attack_distance, bounds=(15, 39), additional_monsters_hit=4)



def shaman_decorator():
	shaman_name = 'lizardman shaman'

	task_chinner = Player.on_task_chinchompa()
	void_chin = Player.void_chinchompa()
	arma_chin = Player.arma_chinchompa()
	task_tbow = Player.on_task_tbow()
	void_tbow = Player.void_tbow()
	arma_tbow = Player.arma_tbow()

	players = [
		task_chinner,
		void_chin,
		arma_chin,
		task_tbow,
		void_tbow,
		arma_tbow
	]

	for p in players:
		p.overload()
		p.pray(PlayerStats.StatPrayer.rigour())

	attack_distance = 9
	additional_targets = 4

	csc = ct.plot_comparison(ct.cox_scale_comparison)
	# csc = ct.print_comparison(ct.cox_scale_comparison)
	csc(
		players,
		shaman_name,
		bounds=(15, 100),
		distance=attack_distance,
		additional_monsters_hit=additional_targets,
		plot_title="lizardman shaman (vulnerability)",
		cast_vulnerability=True
	)



if __name__ == '__main__':
	# main(7, False)
	shaman_decorator()
