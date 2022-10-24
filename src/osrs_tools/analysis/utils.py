"""Basic analysis framework for osrs dps and such

All time values are in ticks unless otherwise noted.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from copy import copy
from dataclasses import Field
from functools import wraps
from itertools import combinations
from typing import Any, Callable, ParamSpec, TypeVar

import numpy as np
import pandas as pd
from osrs_tools.analysis.damage_axes import DamageAxes
from osrs_tools.analysis.pvm_axes import PvmAxes, PvmAxesEquipmentStyle, PvmAxesPlayerEquipmentStyle
from osrs_tools.boost import Boost, Overload
from osrs_tools.character import Character
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.combat import PvMCalc
from osrs_tools.data import DEFAULT_FLOAT_FMT, DEFAULT_TABLE_FMT
from osrs_tools.data import DataAxes
from osrs_tools.data import DataAxes as DA
from osrs_tools.data import DataMode, Slots
from osrs_tools.exceptions import OsrsException
from osrs_tools.gear import Equipment, Gear
from osrs_tools.prayer import Piety, Prayer, Prayers
from osrs_tools.strategy import CombatStrategy
from osrs_tools.style import PlayerStyle
from tabulate import tabulate

###############################################################################
# misc                                                                        #
###############################################################################

P = ParamSpec("P")
R = TypeVar("R")

###############################################################################
# main functions                                                              #
###############################################################################


def tabulate_enhanced(
    data,
    col_labels: list,
    row_labels: list,
    meta_header: str | None = None,
    floatfmt: str | None = None,
    tablefmt: str | None = None,
    **kwargs,
):
    # default values and error checking
    if floatfmt is None:
        floatfmt = DEFAULT_FLOAT_FMT
    if tablefmt is None:
        tablefmt = DEFAULT_TABLE_FMT

    if isinstance(data, np.ndarray):
        try:
            m, n = data.shape

        except ValueError as exc:
            if data.size == data.shape[0] and len(data.shape) == 1:
                m, n = (data.shape[0], 1)
            else:
                raise exc

        assert m == len(row_labels)
        assert n == len(col_labels) or n == len(col_labels) - 1

    # table prep
    table_data = []
    for index, row in enumerate(data):
        try:
            labeled_row = [row_labels[index]] + list(row)
        except TypeError:
            labeled_row = [row_labels[index]]
            labeled_row.append(row)

        table_data.append(labeled_row)

    table = tabulate(table_data, headers=col_labels, floatfmt=floatfmt, tablefmt=tablefmt)

    if meta_header is not None:
        line_length = len(table.split("\n")[0])
        header_basis = line_length * "-"
        # fmt the header
        fmtd_text = 2 * " " + meta_header + 2 * " "
        text_width = len(fmtd_text)
        start_idx = (line_length // 2) - (text_width // 2)
        end_idx = start_idx + text_width
        fmtd_header = header_basis[:start_idx] + fmtd_text + header_basis[end_idx:]

        table = "\n".join([fmtd_header, table])

    return table


def table_2d(func: Callable) -> Callable:
    """Creates a 2D table.

    # TODO: Figure out output additional types.
    Args:
            func (Callable[P, R]): Method that behaves like
                    bedevere_the_wise for I/O.

    Raises:
            AnalysisError: Raised if axes aren't 2D.

    Returns:
            Callable[P, R]:
    """

    def convert_to_df(data: np.ndarray, columns: list[str]) -> pd.DataFrame:
        if not isinstance(data, np.ndarray):
            raise TypeError(data)

        return pd.DataFrame(data, columns=columns, dtype=data.dtype)

    def convert_to_ndarray(df: pd.DataFrame) -> np.ndarray:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(df)

        return np.asarray(df)

    @wraps(func)
    def inner(
        *args,
        transpose: bool = False,
        sort_cols: bool = False,
        sort_rows: bool = False,
        ascending: bool = False,
        floatfmt: str = None,
        tablefmt: str = None,
        **kwargs,
    ):
        # optionals
        col_labels = None
        row_labels = None
        meta_header = None

        if (cl_k := "col_labels") in kwargs.keys():
            col_labels = kwargs.pop(cl_k)
        if (rl_k := "row_labels") in kwargs.keys():
            row_labels = kwargs.pop(rl_k)
        if (mh_k := "meta_header") in kwargs.keys():
            meta_header = kwargs.pop(mh_k)

        retval = axes_dict, data_ary = func(*args, **kwargs)

        if not isinstance(data_ary, np.ndarray):
            raise TypeError(data_ary)

        try:
            (row_label, row), (col_label, col) = axes_dict.items()
        except ValueError:
            try:
                row_label, row = list(axes_dict.items())[0]

                if (dm_key := "data_mode") in kwargs.keys():
                    col_label = kwargs.pop(dm_key)
                else:
                    col_label = ""

                col = [col_label]
            except ValueError as exc:
                raise AnalysisError("axes aren't 2D") from exc

        # swap rows and columns if specified
        if transpose:
            col_labels = [str(r) for r in row] if col_labels is None else col_labels
            row_labels = [str(c) for c in col] if row_labels is None else row_labels
            mov_label = row_label
            row_label = col_label
            col_label = mov_label
            data_ary = data_ary.T
        else:
            col_labels = [str(c) for c in col] if col_labels is None else col_labels
            row_labels = [str(r) for r in row] if row_labels is None else row_labels

        # data sorting
        # do row then col to prioritize col view.
        # TODO: Possible customize this? Or is this unnecessary since we are allowed to tranpose?
        data_df = None

        # sort by the first row
        if sort_rows:
            raise NotImplementedError
            # this is broken
            data_df = convert_to_df(data_ary, columns=col_labels)
            data_df = data_df.assign(**{"row_label": row_labels})
            data_df = data_df.sort_values(by=row_labels[0], axis=1, ascending=ascending)
            row_labels = list(data_df["row_label"])

        # sort by the first col
        if sort_cols:
            raise NotImplementedError
            # this is broken
            if data_df is None:
                data_df = convert_to_df(data_ary, columns=col_labels)
                data_df = data_df.assign(**{"row_label": row_labels})
                data_df = data_df.sort_values(by=col_labels[0], axis=0, ascending=ascending)

            data_df = data_df.sort_values(by=col_labels[0], ascending=ascending)
            row_labels = list(data_df["row_label"])

        if data_df is not None:
            data_ary = convert_to_ndarray(data_df)

        if meta_header is None:
            try:
                rl = row_label.name
            except AttributeError:
                rl = row_label

            try:
                cl = col_label.name
            except AttributeError:
                cl = col_label

            meta_header = f"rows: {rl}, cols: {cl}"

        table = tabulate_enhanced(
            data=data_ary,
            col_labels=col_labels,
            row_labels=row_labels,
            meta_header=meta_header,
            floatfmt=floatfmt,
            tablefmt=tablefmt,
            **kwargs,
        )

        return retval, table

    return inner


def bedevere_the_wise(
    axes_container: DamageAxes,
    data_mode: DataMode = DataMode.DPT,
) -> np.ndarray:
    """Smart comparison interface for a generic PvM damage calculation

    Parameters
    ----------
    axes_container : PvmAxes
        A datatype that contains information on the space of a PvMCalc

    data_mode : DataMode, optional
        The datatype of the values in the return data array, see the DataMode
        enum for more information, by default DataMode.DPT

    Returns
    -------
    tuple[Iterator[tuple[int]], dict[DataAxes, list], np.ndarray]
        Return an iterator of the complete series indices, a dictionary with
        DataAxes keys and axes values, and the data array.

    Raises
    ------
    NotImplementedError
    """

    # if isinstance(pvm_axes, PvmAxes):
    #     axes = pvm_axes.squeezed_axes
    #     dims = pvm_axes.squeezed_dims
    # elif isinstance(pvm_axes, PvmAxesEquipmentStyle):
    #     axes = pvm_axes.squeezed_axes
    #     dims = pvm_axes.squeezed_dims
    # elif isinstance(pvm_axes, PvmAxesPlayerEquipmentStyle):
    #     axes = pvm_axes.squeezed_axes
    #     dims = pvm_axes.squeezed_dims
    # else:
    #     raise ValueError(pvm_axes)

    wide_dims = axes_container.dims
    squeezed_dims = axes_container.squeezed_dims

    if len(squeezed_dims) > 2:
        raise ValueError(axes_container)

    data_ary = np.empty(shape=wide_dims, dtype=data_mode.value.dtype)

    for _indices in axes_container.indices:
        # iterate through all possible indices combinations
        params = axes_container[_indices]

        # TODO: Rework this shitty code
        if isinstance(axes_container, PvmAxesEquipmentStyle):
            ply, tgt, (eqp, sty), pry, bst, lvl, spc, dst, spl, adt = params
            assert isinstance(ply, Player)
            assert isinstance(tgt, Monster)

            strategy_params = (eqp, sty, pry, bst, lvl)
            pvm_calc_params = (spc, dst, spl, adt)

        elif isinstance(axes_container, PvmAxesPlayerEquipmentStyle):
            (ply, eqp, sty), tgt, pry, bst, lvl, spc, dst, spl, adt = params
            assert isinstance(ply, Player)
            assert isinstance(tgt, Monster)

            strategy_params = (eqp, sty, pry, bst, lvl)
            pvm_calc_params = (spc, dst, spl, adt)

        elif isinstance(axes_container, PvmAxes):
            ply, tgt = params[0:2]
            strategy_params = params[2:7]
            pvm_calc_params = params[7:11]

            assert isinstance(ply, Player)
            assert isinstance(tgt, Monster)

            eqp, sty, pry, bst, lvl = strategy_params
            spc, dst, spl, adt = pvm_calc_params

            if isinstance(sty, PlayerStyle):
                if isinstance(eqp, Equipment):
                    try:
                        weapon = eqp.weapon
                    except AssertionError:
                        weapon = ply.wpn
                else:
                    weapon = ply.wpn

                if sty not in weapon.styles:
                    data_ary[_indices] = 0
                    continue

        else:
            raise ValueError(axes_container)

        strat_kwargs = {
            DA.EQUIPMENT.value: eqp,
            DA.STYLE.value: sty,
            DA.PRAYERS.value: pry,
            DA.BOOSTS.value: bst,
            DA.LEVELS.value: lvl,
        }
        pvm_calc_kwargs = {
            DA.SPECIAL_ATTACK.value: spc,
            DA.DISTANCE.value: dst,
            DA.SPELL.value: spl,
            DA.ADDITIONAL_TARGETS.value: adt,
        }

        if any(_sp is not None for _sp in strat_kwargs.values()):
            # if the player must be modified directly
            old_eqp = copy(ply.eqp)
            old_sty = copy(ply.style)

            strat = CombatStrategy(ply, **strat_kwargs)
            dam = strat.activate().damage_distribution(tgt, **pvm_calc_kwargs)

            ply.eqp = old_eqp
            ply.style = old_sty
        else:
            # if the player does not need to be modified directly
            dam = PvMCalc(ply, tgt).get_damage(**pvm_calc_kwargs)

        if data_mode.value.attribute is not None:
            value = getattr(dam, data_mode.value.attribute)

        else:
            hp = tgt.levels.hitpoints

            if data_mode is DataMode.TICKS_TO_KILL:
                value = hp / dam.per_tick
            elif data_mode is DataMode.SECONDS_TO_KILL:
                value = hp / dam.per_second
            elif data_mode is DataMode.MINUTES_TO_KILL:
                value = hp / dam.per_minute
            elif data_mode is DataMode.HOURS_TO_KILL:
                value = hp / dam.per_hour
            else:
                raise NotImplementedError

        data_ary[_indices] = value

    # final squeezing
    ary_squeezed = data_ary.squeeze()

    return ary_squeezed


# bedevere_2d = table_2d(bedevere_the_wise)


def robin_the_brave(
    player: Player,
    target: Character,
    switches: Equipment | tuple[Gear],
    num_switches_allowed: int,
    *,
    prayers: Prayer | Prayers = Piety,
    boosts: Boost = Overload,
    active_style: PlayerStyle = None,  # type: ignore
    data_mode: DataMode = DataMode.DPT,
    **kwargs,
) -> tuple[dict[DataAxes, list], tuple[int], np.ndarray]:
    """Returns a 1-D data array comparing data_mode under every possible combination of gear in switches, limited to num_switches_allowed.

    Args:
            player (Player): Player performing the attack. Player should be initialized with as much gear as can be assumed. For example,
            if you know you're always bringing a torva set, equip it to the player.
            target (Character): Target of the attack.
            switches (Equipment | tuple[Gear]): An equipment or tuple[Gear] with the the optional switches.
            num_switches_allowed (int): The limit of Gear items in switches to use concurrently. The use case for this is in situations where
                    for inventory limitations you're only able to fit in a few switches, like Olm or TOB.
            prayers (Prayer | PrayerCollection, optional): Any prayers. Defaults to Piety.
            boosts (Boost, optional): Any boosts. Defaults to Overload.
            active_style (PlayerStyle, optional): Any style overrides. Defaults to None.
            data_mode (DataMode, optional): The statistic in question. Defaults to DataMode.DPT.

    Raises:
            TypeError: If some of the internal logic goes wrong with wrapper classes.
            AnalysisError: If you ask a question that doesn't make sense.

    Returns:
            axes_dict (dict[DataAxes, tuple]): A dictionary for looking up axes indices.
            indices (tuple[int]): An iterable list of all indices of the data array.
            data_ary (np.ndarray): The data array.
    """
    return NotImplemented

    # error checking
    if isinstance(switches, Equipment):
        switches_tup = switches.equipped_gear
    elif isinstance(switches, tuple):
        assert all(isinstance(g, Gear) for g in switches)
        switches_tup = switches
    else:
        raise TypeError(switches)

    if num_switches_allowed >= len(switches_tup):
        raise AnalysisError()

    # generate every combination of gear switches under the limitations
    switch_combos = []
    for combo in combinations(switches_tup, num_switches_allowed):
        switch_dict = {g.slot.name: g for g in combo}
        switch_combos.append(switch_dict)

    equipments = [Equipment(**switch_dict) for switch_dict in switch_combos]

    # return bedevere_the_wise(
    #     player,
    #     target,
    #     equipment=equipments,
    #     prayers=prayers,
    #     boosts=boosts,
    #     active_style=active_style,
    #     data_mode=data_mode,
    #     **kwargs,
    # )


class AnalysisError(OsrsException):
    """Raised at malformed requests."""
