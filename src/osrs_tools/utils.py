"""Utilities for the osrs-tools module

This code is a little old and jank, but it gets the job done.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""

import numpy as np
import pandas as pd

from osrs_tools.data import CSV_SEP, ITEMS_BITTER_BED, MONSTERS_BITTER, MONSTERS_DE0

###############################################################################
# load csvs                                                                   #
###############################################################################


def _load_de0():
    """Load chambers of xeric boss data from the de0 spreadsheet.

    Returns
    -------
    _type_
        _description_
    """
    cox_df = pd.read_csv(MONSTERS_DE0, sep=CSV_SEP)
    name_key = "name"

    # column headers lower case / name column to lower case
    cox_df.columns = cox_df.columns.str.lower()
    cox_df[name_key] = cox_df[name_key].str.lower()

    return cox_df


def _load_bitterkoekje_bedevere():
    ITEM_NAME = "name"
    NONE_VALUE = "none"
    STRING_COLUMNS = [0, 18, 23, 24]
    INT_COLUMNS = list(range(1, 13)) + [14] + list(range(19, 23))
    FLOAT_COLUMNS = [13] + list(range(15, 18))
    BOOL_COLUMNS = [25]

    gear_df: pd.DataFrame = pd.read_csv(ITEMS_BITTER_BED, sep=CSV_SEP)

    # empty header fill w/ name
    gear_df = gear_df.rename(columns={gear_df.columns[0]: ITEM_NAME})

    # column headers to lower case
    gear_df.columns = gear_df.columns.str.lower()

    # column operations #######################################################

    # convert string columns to lower() and strip() values
    string_columns = gear_df.columns[np.asarray(STRING_COLUMNS)]

    for sc in string_columns:
        gear_df[sc] = gear_df[sc].fillna("")
        gear_df[sc] = gear_df[sc].str.lower()
        gear_df[sc] = gear_df[sc].str.strip()

    # convert int columns to ints and fill NaN with 0
    integer_columns = gear_df.columns[np.asarray(INT_COLUMNS)]

    for ic in integer_columns:
        gear_df[ic] = gear_df[ic].fillna(0)

        try:
            gear_df[ic] = gear_df[ic].apply(int)
        except ValueError:
            # magic dart is listed as "mdart", only value I know to break this
            gear_df[ic] = 0

    # fill float NaNs with 0
    float_columns = gear_df.columns[np.asarray(FLOAT_COLUMNS)]

    for fc in float_columns:
        gear_df[fc] = gear_df[fc].fillna(0)

    # fill bool columns with FALSE
    bool_columns = gear_df.columns[np.asarray(BOOL_COLUMNS)]

    for bc in bool_columns:
        gear_df[bc] = gear_df[bc].fillna(False)

    # cleanup #################################################################

    # clear nones
    nones = gear_df.loc[gear_df[ITEM_NAME] == NONE_VALUE]
    gear_df = gear_df.drop(index=nones.index)

    # clear empty rows between weapon/gear/spell/ammo types
    gear_df = gear_df[gear_df[ITEM_NAME].notna()]

    return gear_df


def _load_bitterkoekje_npc():
    NPC_INDEX = "npc"
    STRING_COLUMNS = [0, 1, 10, 27]
    INT_COLUMNS = list(range(3, 10)) + list(range(11, 26)) + [29]
    FLOAT_COLUMNS = [2]

    npc_df = pd.read_csv(MONSTERS_BITTER, sep=CSV_SEP, header=1)
    npc_df.columns = npc_df.columns.str.lower()

    # column operations #######################################################
    string_columns = npc_df.columns[np.asarray(STRING_COLUMNS)]

    for sc in string_columns:
        npc_df[sc] = npc_df[sc].fillna("")
        npc_df[sc] = npc_df[sc].str.lower()
        npc_df[sc] = npc_df[sc].str.strip()

    int_columns = npc_df.columns[np.asarray(INT_COLUMNS)]

    for ic in int_columns:
        npc_df[ic] = npc_df[ic].fillna(0)
        npc_df[ic] = npc_df[ic].apply(int)

    # TODO: parse main attack style

    float_columns = npc_df.columns[np.asarray(FLOAT_COLUMNS)]

    # normally percent in the sheet, I manually changed presentation
    for fc in float_columns:
        npc_df[fc] = npc_df[fc].fillna(0)

    # cleanup #################################################################

    # clear nones and custom NPC
    nones = npc_df.loc[(npc_df[NPC_INDEX] == "") | (npc_df[NPC_INDEX] == "custom npc")]
    npc_df = npc_df.drop(index=nones.index)

    return npc_df


def lookup_monster(name: str, npc_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """

    :param name: Name of the npc
    :param npc_df: pd.DataFrame or the default one, allows for lookup chaining
    :return:
    """
    npc_index = "npc"
    df = npc_df if npc_df else NPC_DF
    return df.loc[df[npc_index] == name]


def lookup_normal_monster_by_name(
    name: str, npc_df: pd.DataFrame | None = None
) -> pd.DataFrame:
    npc_df = lookup_monster(name, npc_df)

    if len(npc_df) == 0:
        raise ValueError(name)
    elif len(npc_df) > 1:
        raise ValueError(name, npc_df)
    else:
        return npc_df


def get_cox_monster_base_stats_by_name(name: str) -> pd.DataFrame:
    mon_df = COX_DF.loc[COX_DF["name"] == name.lower()]

    if len(mon_df) == 0:
        raise ValueError(f"{name=} not found")
    elif len(mon_df) > 1:
        raise ValueError(f"{name=} yielded multiple {mon_df=}")
    else:
        return mon_df


def lookup_gear(name: str, gear_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """

    :param name: The name of the item
    :param gear_df: You can supply a dataframe to chain lookups or default to the whole list
    :return pd.DataFrame:
    """
    df = gear_df if gear_df else GEAR_DF
    return df.loc[df["name"] == name]


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

COX_DF = _load_de0()
GEAR_DF = _load_bitterkoekje_bedevere()
NPC_DF = _load_bitterkoekje_npc()
