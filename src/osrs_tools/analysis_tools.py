import matplotlib.pyplot as plt
from functools import wraps
from itertools import product
from tabulate import tabulate
from typing import ParamSpec, TypeVar, Callable
from collections import namedtuple
from enum import Enum, unique
import numpy as np

from osrs_tools.character import Character, Player
from osrs_tools.stats import PlayerLevels, Boost
from osrs_tools.style import PlayerStyle
from osrs_tools.prayer import Prayer, PrayerCollection
from osrs_tools.equipment import Equipment
from osrs_tools.damage import Damage
from osrs_tools.exceptions import OsrsException
from copy import copy

# throwaway imports
from osrs_tools.style import BulwarkStyles
from osrs_tools.modifier import Styles

P = ParamSpec('P')
R = TypeVar('R')
datamode_type = namedtuple('datamode', ['key', 'dtype', 'attribute'])


class DataMode(Enum):
	DPT = datamode_type('damage per tick', float, 'per_tick')
	DPS = datamode_type('damage per second', float, 'per_second')
	DPM = datamode_type('damage per minute', float, 'per_minute')
	DPH = datamode_type('damage per hour', float, 'per_hour')
	MAX = datamode_type('max hit', int, 'max_hit')
	MIN = datamode_type('min hit', int, 'min_hit')
	MEAN = datamode_type('mean hit', float, 'mean')
	POSITIVE_DAMAGE = datamode_type('chance to deal positive damage', float, 'chance_to_deal_positive_damage')
	TICKS_TO_KILL = datamode_type('ticks to kill', float, None)
	SECONDS_TO_KILL = datamode_type('seconds to kill', float, None)
	MINUTES_TO_KILL = datamode_type('minutes to kill', float, None)
	HOURS_TO_KILL = datamode_type('hours to kill', float, None)
	DAMAGE_PER_TICK = DPT
	DAMAGE_PER_SECOND = DPS
	DAMAGE_PER_MINUTE = DPM
	DAMAGE_PER_HOUR = DPH
	MAX_HIT = MAX
	MIN_HIT = MIN
	MEAN_HIT = MEAN
	DWH_SUCCESS = POSITIVE_DAMAGE
	TTK = TICKS_TO_KILL
	STK = SECONDS_TO_KILL
	MTK = MINUTES_TO_KILL
	HTK = HOURS_TO_KILL


@unique
class DataAxes(Enum):
	players = 'players'
	targets = 'targets'
	levels = 'levels'
	prayers = 'prayers'
	boosts = 'boosts'
	equipment = 'equipment'
	active_style = 'active_style'


def tabulate_enhanced(data, col_labels: list, row_labels: list, meta_header: str = None, **kwargs):
	options = {
		'floatfmt': '.1f',
		'tablefmt': 'fancy',
	}
	options.update(kwargs)

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

	table_data = []
	for index, row in enumerate(data):
		try:
			labeled_row = [row_labels[index]] + list(row)
		except TypeError:
			labeled_row = [row_labels[index]]
			labeled_row.append(row)

		table_data.append(labeled_row)

	table = tabulate(table_data, headers=col_labels, floatfmt=options['floatfmt'], tablefmt=options['tablefmt'])

	if meta_header is not None:
		table = '\n'.join([meta_header, table])

	return table


def generic_player_damage_distribution(
	player: Player,
	target: Character,
    levels: PlayerLevels = None,
    prayers: PrayerCollection = None,
    boosts: Boost = None,
    equipment: Equipment = None,
    active_style: PlayerStyle = None,
    **kwargs
) -> Damage:
	"""Return a damage distribution from player & target, with optional modifiers.

	See the bedevere_the_wise method for more info on each of the parameters.

	Args:
		player (Player): A Player, a copy of which is modified within the method.
		target (Character): The target.
		levels (PlayerLevels, optional): Optional substitute for player.levels. Defaults to None.
		prayers (PrayerCollection, optional): Optional substitute for player.prayers_coll. Defaults to None.
		boost (Boost, optional): Optional substitute for active boosts, will reset all boosts per application. Defaults to None.
		equipment (Equipment, optional): Optional equipment to add, can include weapons with default styles. Defaults to None.
		active_style (PlayerStyle, optional): Optional style to specify non-gear-based style-swaps. Defaults to None.

	Returns:
		Damage: _description_
	"""

	play = copy(player) 	# make a copy of player
	play.active_style = player.active_style

	if levels is not None:
		play.base_levels = levels
		play.reset_stats()

	if prayers is not None:
		play.prayers_coll = prayers

	if boosts is not None:
		play.reset_stats()
		play.boost(boosts)

	if equipment is not None:		
		if active_style is not None:
			play.active_style = play.equipment.equip(*equipment.equipped_gear, style=active_style)
		else:
			return_style = play.equipment.equip(*equipment.equipped_gear)
			if return_style is not None:
				play.active_style = return_style

	elif active_style is not None:
		play.active_style = active_style

	assert play.equipment.full_set
	return play.damage_distribution(other=target, **kwargs)


def table_2d(f: Callable) -> Callable:
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

	@wraps(f)
	def inner(*args, **kwargs):

		transpose_key = 'transpose'
		if transpose_key in kwargs.keys():
			transpose = kwargs.pop(transpose_key)
		else:
			transpose = False

		retval = _, axes_dict, data_ary = f(*args, **kwargs)

		try:
			(row_label, row), (col_label, col) = axes_dict.items()
		except ValueError as exc:
			raise AnalysisError("axes aren't 2D") from exc



		col_labels = [str(c) for c in col]
		row_labels = [str(r) for r in row]
		meta_header = f'rows: {row_label.name}, cols: {col_label.name}'
		
		if transpose:
			table = tabulate_enhanced(
				data=data_ary.T, 
				col_labels=row_labels,
				row_labels=col_labels,
				meta_header=meta_header,
				**kwargs
			)
		else:
			table = tabulate_enhanced(
				data=data_ary, 
				col_labels=col_labels,
				row_labels=row_labels,
				meta_header=meta_header,
				**kwargs
			)

		return retval, table

	return inner


def bedevere_the_wise(
	players: Player | list[Player],
	targets: Character | list[Character],
	*,
	levels: PlayerLevels | list[PlayerLevels] = None,
	prayers: Prayer | PrayerCollection | list[PrayerCollection] = None,
	boosts: Boost | list[Boost] = None,
	equipment: Equipment | list[Equipment] = None,
	active_style: PlayerStyle | list[PlayerStyle] = None,
	data_mode: DataMode = DataMode.DPT,
	**kwargs,
) -> tuple[dict[DataAxes, list], tuple[int], np.ndarray]:
	"""Smart comparison interface for a generic player damage method.

	# TODO: Make a **kwargs-heavy version of this method with priority ordering built into the way the user inputs these values

	Args:
		players (Player | list[Player]): Player objects, which all optional 
			parameters may modify by some method.
		targets (Character | list[Character]): Character objects against which to
			calculate the players' damage potential.
		levels (PlayerLevels | list[PlayerLevels], optional): PlayerLevels 
			objects which can modify the base_levels of players. May raise an 
			EquippableError if the provided levels are beneath that of equipment 
			requirements. Defaults to None.
		prayers (Prayer | PrayerCollection | list[PrayerCollection], optional): 
			PrayerCollection objects to be prayed by the players. Defaults to None.
		boosts (Boost | list[Boost], optional): Boosts objects to boost the 
			players. Defaults to None.
		equipment (Equipment | list[Equipment], optional): Equipment objects to 
			be equipped by the players. If the active_style parameter is specified, 
			it will override any default styles suggested by the equipment provided.
			Defaults to None.
		active_style (PlayerStyle | list[PlayerStyle] | None, optional): Styles 
			objects, will raise StyleErrors if the equipment provided does not have
			such styles. Defaults to None.
		data_mode (DataMode, optional): The data protocol to follow. See 
			DataModes for more information. Defaults to DataMode.DPT.
		**kwargs: 
			special_attack: bool, 
			distance: int, 
			spell: Spell, 
			additional_targets: int | Character | list[Character], 
		**additional_kwargs:

	Raises:
		NotImplementedError: Raised with unrecognized DataMode inputs.
		StyleError: Raised if the equipment provided does not have such styles.
		EquippableError: Raised if there is conflict between levels and
		equipment requirements.


	Returns:
		axes_dict (dict[DataAxes, tuple]): A dictionary for looking up axes indices. 
		indices (tuple[int]): An iterable list of all indices of the data array.
		data_ary (np.ndarray): The data array.
	"""
	# prepare all single instances as lists
	if isinstance(players, Player):
		players = [players]

	if isinstance(targets, Character):
		targets = [targets]

	if isinstance(levels, PlayerLevels):
		levels = [levels]

	if isinstance(prayers, PrayerCollection):
		prayers = [prayers]
	elif isinstance(prayers, Prayer):
		pc = PrayerCollection()
		pc.pray(prayers)
		prayers = [pc]

	if isinstance(boosts, Boost):
		boosts = [boosts]

	if isinstance(equipment, Equipment):
		equipment = [equipment]

	if isinstance(active_style, PlayerStyle):
		active_style = [active_style]

	# prepare kw and tuple axes, eliminate None values.
	axes_dict: dict[DataAxes, list]= {
		DataAxes.players: players,
		DataAxes.targets: targets,
		DataAxes.levels: levels,
		DataAxes.prayers: prayers,
		DataAxes.boosts: boosts,
		DataAxes.equipment: equipment,
		DataAxes.active_style: active_style
	}
	axes_dict = {k: v for k, v in axes_dict.items() if v is not None}
	axes = tuple(axes_dict.values())
	axes_dims = tuple(len(ax) for ax in axes)

	# get generated indices and a complete parameter space with itertools.product
	indices = tuple(product(*(range(n) for n in axes_dims)))
	# cartesian product of all parameter axes
	params_cart_prod = tuple(product(*axes))
	kwargs_params_cp = tuple({k.name: v for k, v in zip(axes_dict.keys(), p, strict=True)} for p in params_cart_prod)
	data_ary = np.empty(shape=axes_dims, dtype=data_mode.value.dtype)

	for index, kw_params in zip(indices, kwargs_params_cp, strict=True):
		pos_args = []
		player = kw_params.pop(DataAxes.players.name)
		pos_args.append(player)
		target = kw_params.pop(DataAxes.targets.name)
		pos_args.append(target)

		dam = generic_player_damage_distribution(*pos_args, **kw_params, **kwargs)

		if data_mode.value.attribute is not None:
			value = dam.__getattribute__(data_mode.value.attribute)
		else:
			target: Character = kw_params[DataAxes.targets.name]
			hp = target.levels.hitpoints

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
		
		data_ary[index] = value
	
	# final squeezing
	ary_squeezed = data_ary.squeeze()
	squeezed_axes_dict = {}

	for (k, v), dim in zip(axes_dict.items(), axes_dims, strict=True):
		if dim > 1:
			squeezed_axes_dict[k] = v

	# re-calculate these values for the squeezed array
	axes_dict = squeezed_axes_dict
	axes = tuple(axes_dict.values())
	axes_dims = tuple(len(ax) for ax in axes)
	indices = tuple(product(*(range(n) for n in axes_dims)))
	
	return indices, axes_dict, ary_squeezed

class AnalysisError(OsrsException):
	"""Raised at malformed requests.
	"""