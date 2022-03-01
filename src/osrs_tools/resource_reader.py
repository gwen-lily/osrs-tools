import pandas as pd
import osrs_highscores
import numpy as np
from pathlib import Path

from osrs_tools.exceptions import *

RESOURCES_DIR = Path(__file__).absolute().parents[2].joinpath('resources')
de0_cox_bosses = RESOURCES_DIR.joinpath('cox_base_stats.csv')
bitterkoekje_items = RESOURCES_DIR.joinpath('bitterkoekje_items_bedevere_modified.csv')
bitterkoekje_npc = RESOURCES_DIR.joinpath('bitterkoekje_npcs.csv')
csv_separator = '\t'


class ResourceReaderError(OsrsException):
	pass


def _load_de0():
	cox_df = pd.read_csv(de0_cox_bosses, sep=csv_separator)
	cox_df.columns = map(str.lower, cox_df.columns)     # column headers lower case
	cox_df['name'] = cox_df['name'].str.lower()         # name column to lower case
	return cox_df


def _load_bitterkoekje_bedevere():
	# TODO: Define the ranges for column types more reliably, order will break this. It shouldn't be hard to fix though.
	item_name_header = 'name'
	none_value = 'none'

	gear_df: pd.DataFrame = pd.read_csv(bitterkoekje_items, sep=csv_separator)
	gear_df = gear_df.rename(columns={gear_df.columns[0]: item_name_header})        # empty header fill w/ name
	gear_df.columns = map(str.lower, gear_df.columns)                               # column headers to lower case

	# column operations ################################################################################################
	# convert string columns to lower() and strip() values
	# string columns are 0, 18, 31:32
	string_columns_range = np.asarray([0, 18, 23, 24])
	string_columns = gear_df.columns[string_columns_range]

	for sc in string_columns:
		gear_df[sc] = gear_df[sc].fillna('')
		gear_df[sc] = gear_df[sc].str.lower()
		gear_df[sc] = gear_df[sc].str.strip()

	# convert int columns to ints and fill NaN with 0
	# int columns are 1:12, 14, 19:22
	integer_columns_range = np.append(np.arange(1, 12+1), 14)
	integer_columns_range = np.append(integer_columns_range, np.arange(19, 22+1))
	integer_columns = gear_df.columns[integer_columns_range]

	for ic in integer_columns:
		gear_df[ic] = gear_df[ic].fillna(0)

		try:
			gear_df[ic] = gear_df[ic].apply(int)
		except ValueError:
			gear_df[ic] = 0     # magic dart is listed as "mdart", only value I know to break this

	# fill float NaNs with 0
	# float columns are 15:17
	float_columns_range = np.append(13, np.arange(15, 17+1))
	float_columns = gear_df.columns[float_columns_range]

	for fc in float_columns:
		gear_df[fc] = gear_df[fc].fillna(0)

	# fill bool columns with FALSE
	# bool columns are 33:35
	bool_columns_range = np.arange(25, 25+1)
	bool_columns = gear_df.columns[bool_columns_range]

	for bc in bool_columns:
		gear_df[bc] = gear_df[bc].fillna(False)

	# cleanup ##########################################################################################################
	# clear nones except the first which is for the unarmed weapon
	nones = gear_df.loc[gear_df[item_name_header] == none_value]
	gear_df = gear_df.drop(index=nones.index[1:])

	# clear empty rows between weapon/gear/spell/ammo types
	gear_df = gear_df[gear_df[item_name_header].notna()]

	return gear_df


def _load_bitterkoekje_npc():
	npc_index = 'npc'

	npc_df = pd.read_csv(bitterkoekje_npc, sep=csv_separator, header=1)
	npc_df.columns = map(str.lower, npc_df.columns)     # column headers lower case

	# column operations ################################################################################################
	string_columns_range = np.asarray([0, 1, 10, 27])
	string_columns = npc_df.columns[string_columns_range]

	for sc in string_columns:
		npc_df[sc] = npc_df[sc].fillna('')
		npc_df[sc] = npc_df[sc].str.lower()
		npc_df[sc] = npc_df[sc].str.strip()

	int_columns_range = np.append(
		np.append(np.arange(3, 9+1), np.arange(11, 25+1)),
		np.arange(29, 29+1))
	int_columns = npc_df.columns[int_columns_range]

	for ic in int_columns:
		npc_df[ic] = npc_df[ic].fillna(0)
		npc_df[ic] = npc_df[ic].apply(int)

	# TODO: parse main attack style

	float_columns_range = np.asarray([2])
	float_columns = npc_df.columns[float_columns_range]

	# normally percent in the sheet, I manually changed presentation
	for fc in float_columns:
		npc_df[fc] = npc_df[fc].fillna(0)

	# cleanup ##########################################################################################################
	# clear nones and custom NPC
	nones = npc_df.loc[(npc_df[npc_index] == '') | (npc_df[npc_index] == 'custom npc')]
	npc_df = npc_df.drop(index=nones.index)

	return npc_df


def lookup_monster(name: str, npc_df: pd.DataFrame = None) -> pd.DataFrame:
	"""

	:param name: Name of the npc
	:param npc_df: pd.DataFrame or the default one, allows for lookup chaining
	:return:
	"""
	npc_index = 'npc'
	df = npc_df if npc_df else NPC_DF
	return df.loc[df[npc_index] == name]


def lookup_normal_monster_by_name(name: str, npc_df: pd.DataFrame = None) -> pd.DataFrame:
	npc_df = lookup_monster(name, npc_df)

	if len(npc_df) == 0:
		raise ResourceReaderError(f'{name=} not found')
	elif len(npc_df) > 1:
		raise ResourceReaderError(f'{name=} yielded {npc_df=}')
	else:
		return npc_df


def lookup_npcs_by_type(npc_type: str, npc_df: pd.DataFrame = None) -> pd.DataFrame:
	"""

	:param npc_type: The type of an npc such as: undead, demon, dragon. Not fully supported for xerician, draconic...
	:param npc_df: pd.DataFrame or the default one, allows for lookup chaining
	:return:
	"""
	df = npc_df if npc_df else NPC_DF
	return df.loc[df['type'] == npc_type]


def get_cox_monster_base_stats_by_name(name: str) -> pd.DataFrame:
	mon_df = COX_DF.loc[COX_DF['name'] == name.lower()]

	if len(mon_df) == 0:
		raise ResourceReaderError(f'{name=} not found')
	elif len(mon_df) > 1:
		raise ResourceReaderError(f'{name=} yielded multiple {mon_df=}')
	else:
		return mon_df


def lookup_gear(name: str, gear_df: pd.DataFrame = None) -> pd.DataFrame:
	"""

	:param name: The name of the item
	:param gear_df: You can supply a dataframe to chain lookups or default to the whole list
	:return pd.DataFrame:
	"""
	df = gear_df if gear_df else GEAR_DF
	return df.loc[df['name'] == name]


# def lookup_slot_table(slot: str, gear_df: pd.DataFrame = None) -> pd.DataFrame:
# 	"""
#
# 	:param slot:
# 	:param gear_df: You can supply a dataframe to chain lookups or default to the whole list
# 	:return pd.DataFrame:
# 	"""
# 	df = gear_df if gear_df else GEAR_DF
# 	return df.loc[df['slot'] == slot]
#
#
# def lookup_weapon_type_table(weapon_type: str, gear_df: pd.DataFrame = None) -> pd.DataFrame:
# 	"""
#
# 	:param weapon_type: The type of weapon such as 'two-handed swords', 'stab swords', 'spiked weapons', ...
# 	:param gear_df: You can supply a dataframe to chain lookups or default to the whole list
# 	:return pd.DataFrame:
# 	"""
# 	df = gear_df if gear_df else GEAR_DF
# 	return df.loc[(df['weapon type'] == weapon_type) & (df['slot'] == 'weapon')]
#
#
# def lookup_accessible_gear_table(stats: stats.PlayerLevels, gear_df: pd.DataFrame = None) -> pd.DataFrame:
# 	"""
#
# 	:param stats: PlayerStatsDeprecated.PlayerCombat object
# 	:param gear_df: You can supply a dataframe to chain lookups or default to the whole list
# 	:return pd.DataFrame:
# 	"""
# 	df = gear_df if gear_df else GEAR_DF
# 	return df.loc[
# 		(df['hitpoints level req'] <= stats.hitpoints) &
# 		(df['attack level req'] <= stats.attack) &
# 		(df['strength level req'] <= stats.strength) &
# 		(df['defence level req'] <= stats.defence) &
# 		(df['ranged level req'] <= stats.ranged) &
# 		(df['magic level req'] <= stats.magic) &
# 		(df['slayer level req'] <= stats.slayer) &
# 		(df['agility level req'] <= stats.agility)
# 	]
#
#
# def lookup_gear_min_max(index: str, gear_df: pd.DataFrame = None) -> (pd.DataFrame, pd.DataFrame):
# 	"""
#
# 	:param index: Name of the index / attribute / aspect you want to check, such as: 'melee strength', 'stab defence'
# 	:param gear_df: A pd.DataFrame, or the default one. Allows for lookup chaining.
# 	:return: pd.DataFrame for min, pd.DataFrame for max.
# 	"""
# 	df = gear_df if gear_df is not None else GEAR_DF
# 	gear_min = df.loc[df[index] == df[index].min()]
# 	gear_max = df.loc[df[index] == df[index].max()]
#
# 	return gear_min, gear_max
#

def lookup_player_highscores(rsn: str) -> osrs_highscores.highscores.Highscores:
	"""

	:param rsn: A player's RSN
	:return osrs_highscores.highscores.Highscores:
	"""
	return osrs_highscores.Highscores(rsn)


COX_DF = _load_de0()
GEAR_DF = _load_bitterkoekje_bedevere()
NPC_DF = _load_bitterkoekje_npc()
