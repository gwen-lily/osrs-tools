from main import *

def defence_matrix_dwh_generator(player: Player, monster: Monster):
	max_defence_level = monster.stats.combat.defence
	defence_states = np.arange(max_defence_level, -1, -1)
	r = 4   # [3 and 2 and 1 and 0]
	t = (max_defence_level + 1) - r

	Q = np.zeros(shape=(t, t))
	R = np.zeros(shape=(t, r))

	for i, def_lvl in enumerate(defence_states):
		if def_lvl <= 3:
			break

		monster.stats.combat.defence = def_lvl
		monster.reset_current_stats()

		on_hit_def_lvl = monster.dwh_reduce(damage_dealt=True)
		monster.reset_current_stats()

		on_miss_def_lvl = monster.dwh_reduce(damage_dealt=False)
		monster.reset_current_stats()

		dam = player.damage_against_monster(monster, special_attack=True)
		chance_to_deal_zero_damage = dam.hitsplats[0].damage_dict[0]

		j0 = max_defence_level - on_hit_def_lvl
		j1 = max_defence_level - on_miss_def_lvl

		try:
			Q[i, j0] = 1 - chance_to_deal_zero_damage
		except IndexError as exc:
			R[i, 0] = 1 - chance_to_deal_zero_damage

		try:
			Q[i, j1] = Q[i, j1] + chance_to_deal_zero_damage
		except IndexError:
			R[i, 0] = R[i, 0] + chance_to_deal_zero_damage

	amc = markov.AbsorbingMarkovChain(Q, R, defence_states)

	return amc


def defence_matrix_bgs_generator(player: Player, monster: Monster):
	max_defence_level = monster.stats.combat.defence
	defence_states = np.arange(max_defence_level, -1, -1)
	r = 1  # [0]
	t = (max_defence_level + 1) - r

	Q = np.zeros(shape=(t, t))
	R = np.zeros(shape=(t, r))

	for i, def_lvl in enumerate(defence_states):

		if def_lvl == 0:
			continue

		monster.stats.combat.defence = def_lvl
		monster.reset_current_stats()

		dam = player.damage_against_monster(monster, special_attack=True)

		for j, reduced_def_lvl in enumerate(defence_states):
			damage_dealt = def_lvl - reduced_def_lvl

			if not 0 <= damage_dealt <= dam.hitsplats[0].damage.max():
				continue

			try:
				Q[i, j] = dam.hitsplats[0].damage_dict[damage_dealt]
			except IndexError:
				R[i, 0] = 1 - sum(Q[i, :])

	amc = markov.AbsorbingMarkovChain(Q, R, defence_states)
	return amc


def zero_question():
	d = Player.dwh_inquisitor_brimstone()
	b = Player.bgs_bandos()

	for p in (d, b):
		p.overload()
		p.pray(PlayerStats.StatPrayer.piety())

	o = OlmMeleeHand(15, False)
	amc_dwh = defence_matrix_dwh_generator(d, o)

	o = OlmMeleeHand(15, False)
	amc_bgs = defence_matrix_bgs_generator(b, o)

	print('suh')


if __name__ == '__main__':
	zero_question()
