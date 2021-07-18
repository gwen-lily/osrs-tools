# osrs-tools-v2\cox_tools.py
from main import *
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import datetime as dt


def plot_comparison(func):
	def inner(*args, **kwargs):
		ps, dps = func(*args, **kwargs)

		if 'players' in kwargs.keys():
			players_ref = kwargs['players']
		else:
			players_ref = args[0]
			assert isinstance(players_ref, list)

		if 'monster_name' in kwargs.keys():
			monster_name_ref = kwargs['monster_name']
		else:
			monster_name_ref = args[1]

		if 'plot_title' in kwargs.keys():
			plot_title = kwargs['plot_title']
		else:
			plot_title = monster_name_ref

		for j, p in enumerate(players_ref):
			plt.plot(ps, dps[:, j])

		# fig = plt.figure()
		# ax = fig.add_subplot(111)
		#

		plt.title(plot_title)
		plt.xlabel('party size')
		plt.ylabel('dps')
		legend_items = [p.name for p in players_ref]
		plt.legend(legend_items)
		plt.show()
	return inner


def print_comparison(func):
	def inner(*args, **kwargs):
		ps, dps = func(*args, **kwargs)

		if 'players' in kwargs.keys():
			players_ref = kwargs['players']
		else:
			players_ref = args[0]
			assert isinstance(players_ref, list)

		if 'monster_name' in kwargs.keys():
			monster_name_ref = kwargs['monster_name']
		else:
			monster_name_ref = args[1]

		cols = [p.name for p in players_ref]

		df = pd.DataFrame(
			data=dps,
			index=ps,
			columns=cols
		)

		print(df)
		now = int(dt.datetime.utcnow().timestamp())
		filename = 'osrs-tools-v2_{:}_{:}.tsv'.format(monster_name_ref, now)
		float_format = "%5.2f"
		df[cols] = df[cols].apply(pd.to_numeric, downcast='float').fillna(0)
		sanitized_filename = sanitize(filename)
		df.to_csv(sanitized_filename, sep='\t', float_format=float_format)

	return inner


def cox_scale_comparison(
		players: List[Player],
		monster_name: str,
		challenge_mode: bool = False,
		max_combat_level: int = None,
		max_hitpoints_level: int = None,
		average_mining_level: int = None,
		attribute: Union[List[str], str] = None,
		special_attack: bool = False,
		distance: int = None,
		bounds: Tuple[int, int] = None,
		additional_monsters_hit: int = None,
		dwh_landed: int = None,
		# dwh_range: Union[int, Tuple[int, int]] = None,
		bgs_damage: int = None,
		plot_title: str = None,
		fifteen_sixteenths_scythe: bool = False,
		cast_vulnerability: bool = False
):
	if bounds:
		lower_bound = max([1, bounds[0]])
		upper_bound = min([100, bounds[1]])
	else:
		lower_bound = 1
		upper_bound = 23

	additional_monsters_hit = additional_monsters_hit if additional_monsters_hit else 0
	dwh_landed = dwh_landed if dwh_landed else 0
	bgs_damage = bgs_damage if bgs_damage else 0

	ps_ary = np.arange(lower_bound, upper_bound + 1)
	dps_ary = np.empty(shape=(ps_ary.shape[0], len(players)))

	for i, ps in enumerate(ps_ary):
		try:
			monster_ps = CoxMonster.from_de0(monster_name, ps, challenge_mode, max_combat_level, max_hitpoints_level,
			                                 attribute)
		except CoxMonster.MonsterError as exc:
			if monster_name == Guardian.get_name():
				monster_ps = Guardian(ps, challenge_mode, max_combat_level, max_hitpoints_level, average_mining_level)
			elif monster_name == SkeletalMystic.get_name():
				monster_ps = SkeletalMystic(ps, challenge_mode, max_combat_level, max_hitpoints_level)
			elif monster_name == Tekton.get_name():
				monster_ps = Tekton(ps, challenge_mode, max_combat_level, max_hitpoints_level)
			elif monster_name == OlmHead.get_name():
				monster_ps = OlmHead(ps, challenge_mode, max_combat_level, max_hitpoints_level)
			elif monster_name == OlmMeleeHand.get_name():
				monster_ps = OlmMeleeHand(ps, challenge_mode, max_combat_level, max_hitpoints_level)
			elif monster_name == OlmMageHand.get_name():
				monster_ps = OlmMageHand(ps, challenge_mode, max_combat_level, max_hitpoints_level)
			elif monster_name == IceDemon.get_name():
				monster_ps = IceDemon(ps, challenge_mode, max_combat_level, max_hitpoints_level)
			else:
				raise exc

		if cast_vulnerability:
			monster_ps.vulnerability_reduce()

		for index in range(dwh_landed):
			monster_ps.dwh_reduce()

		monster_ps.bgs_reduce(bgs_damage)

		for j, p in enumerate(players):
			if fifteen_sixteenths_scythe and p.equipment.weapon.name == 'scythe of vitur':
				tick_efficiency_ratio = 15/16
			else:
				tick_efficiency_ratio = 1

			dam_ij = p.damage_against_monster(monster_ps, special_attack, distance,
			                                  tick_efficiency_ratio=tick_efficiency_ratio)
			dps_ij = dam_ij.per_second

			if p.equipment.weapon.active_style.name in PlayerStyle.chinchompa_style_names:
				dps_ij *= (1 + additional_monsters_hit)

			dps_ary[i, j] = round(dps_ij, 2)

	return ps_ary, dps_ary


# def defence_comparison(
# 		players: List[Player],
# 		monster_name: str,
# 		challenge_mode: bool = False,
# 		max_combat_level: int = None,
# 		max_hitpoints_level: int = None,
# 		average_mining_level: int = None,
# 		attribute: Union[List[str], str] = None,
# 		special_attack: bool = False,
# 		distance: int = None,
# 		bounds: Tuple[int, int] = None,
# 		additional_monsters_hit: int = None,
# 		dwh_landed: int = None,
# 		# dwh_range: Union[int, Tuple[int, int]] = None,
# 		bgs_damage: int = None,
# 		plot_title: str = None
# ):



def point_cap(list_of_list_of_monsters: List[list], party_size: int, challenge_mode: bool):
	for list_of_monsters in list_of_list_of_monsters:
		pass


def hello_rope():
	ranger_name = 'deathly ranger'
	mage_name = 'deathly mage'

	# Void bp
	void_bp = Player.void_bp()
	void_bp.pray(PlayerStats.StatPrayer.rigour())

	# Void tbow
	void_tbow = Player.void_tbow()
	void_tbow.pray(PlayerStats.StatPrayer.rigour())

	void_bp.overload()
	void_tbow.overload()

	players = [void_bp, void_tbow]

	cox_scale_comparison(players, ranger_name, bounds=(10, 23))


if __name__ == '__main__':
	hello_rope()
