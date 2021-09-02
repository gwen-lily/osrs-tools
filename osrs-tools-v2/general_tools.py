from main import *
import matplotlib.pyplot as plt
import datetime as dt
from collections import abc

from boost_effects import *

# **KWARGS

# gear: A list of gear items which will all be equipped
# players: a list of player stats to cycle through
# potions: a list of potions to use, including divine/repot timer
# timer?
# prayers: a list of prayers to use
# additional targets
#   dps multiplier
#   actual additional targets (chins)
# scales
#   chambers scales (per 1 / per 8 / increment)
# plot title
# vulnerability
# int_format
# float_format
# filename

# challenge_mode
# max_combat_level
# max_hitpoints_level
# average_mining_level
# attributes
#   monster attributes

# level range
# training up, potions, etc, boost along the way

# special_attack
# distance

# dwh_range
# bgs_range
#   lower, upper bounds and union for each
# defence range

# tick_efficiency
# weapon (+ ammo pairs)

def dps_comparison(
		players: Union[Player, Iterable[Player]],
		boosts: Union[BoostEffect, Iterable[BoostEffect]],
		prayers: Union[PlayerStats.StatPrayer, Iterable[PlayerStats.StatPrayer]],
		equipment: Union[Equipment, Iterable[Equipment]],
		styles: Union[str, Iterable[str]],
		monster_names: Union[str, Iterable[str]],
		*args,
		**kwargs
):
	"""
	Extremely versatile function for any combination of stats, setups, gear, and more!

	:param players:
	:param boosts:
	:param prayers:
	:param equipment:
	:param styles:
	:param monster_names:
	:param args:
	:param kwargs:
	:return:
	"""

	optional_kwargs = (
		"additional_targets",
		"distance",
		"cox_cm",
		"cox_scale_bounds",
		"cox_max_combat_level",
		"cox_max_hitpoints_level",
		"cox_average_mining_level",
		"attributes",
		"train_skill",
		"train_skill_level_bounds",
		"special_attack",
		"vulnerability",
		"dwh_bounds",
		"bgs_bounds",
		"defence_bounds",
		"tick_efficiency",
		"fifteen_sixteenths_scythe"
	)

	iterable_kwargs = (
		"boosts",
		"prayers",
	)

	options = {key: None for key in optional_kwargs}
	options.update(kwargs)

	players = players if isinstance(players, Iterable) else [players]
	boosts = boosts if isinstance(boosts, Iterable) else [boosts]
	prayers = prayers if isinstance(prayers, Iterable) else [prayers]
	equipment = equipment if isinstance(equipment, Iterable) else [equipment]
	styles = styles if isinstance(styles, Iterable) else [styles]
	monster_names = monster_names if isinstance(monster_names, Iterable) else [monster_names]

	for player in players:
		for boost in boosts:
			player.apply_boost(boost)

			for prayer in prayers:
				player.pray(prayer)

				for loadout in equipment:
					player.equipment.equip(*loadout)

					for style in styles:
						try:
							player.equipment.weapon.choose_style_by_name(style)
						except PlayerStyle.StyleError:
							continue


				for monster_name in monster_names:

					if

					try:
						monster = CoxMonster.from_de0(
							monster_name,
						)






