import matplotlib.pyplot as plt
from functools import wraps
from itertools import product
from tabulate import tabulate
from typing import Iterable, Any, ParamSpec, TypeVar, Concatenate, NamedTuple
from collections import namedtuple
import enum

from .character import *

P = ParamSpec('P')
R = TypeVar('R')
datamode_type = namedtuple('datamode', ['key', 'dtype', 'attribute'])


class DataMode(enum.Enum):
	DPS = datamode_type('damage per second', float, 'per_second')
	DAMAGE_PER_SECOND = DPS
	DPT = datamode_type('damage per tick', float, 'per_tick')
	DAMAGE_PER_TICK = DPT
	DPM = datamode_type('damage per minute', float, 'per_minute')
	DAMAGE_PER_MINUTE = DPM
	DPH = datamode_type('damage per hour', float, 'per_hour')
	DAMAGE_PER_HOUR = DPH
	MAX = datamode_type('max hit', int, 'max_hit')
	MAX_HIT = MAX
	MIN = datamode_type('min hit', int, 'min_hit')
	MIN_HIT = MIN
	MEAN = datamode_type('mean hit', float, 'mean')
	MEAN_HIT = MEAN


class ComparisonMode(enum.Enum):
	PARALLEL = 'parallel'       # (A | B) -> (A1, B1), (A2, B2)
	CARTESIAN = 'cartesian'     # (A x B) -> (A1, B1), (A1, B2), (A2, B1), (A2, B2)


def graph_wrapper(func: Callable[P, R]) -> Callable[P, R]:

	@wraps(func)
	def inner(*args: P.args, **kwargs: P.kwargs) -> R:
		input_ary, data_ary = func(*args, **kwargs)
		options = {
			'data': 'dps',
		}
		options.update(kwargs)
		m, n = data_ary.shape

		for i in range(m):
			y = data_ary[i, :]
			plt.plot(input_ary, y)

		plt.title(options['data'])
		plt.xlabel('scale')
		plt.ylabel(options['data'])
		plt.legend([p.name for p in options['players']])
		plt.show()

		return input_ary, data_ary

	return inner


def table_wrapper(func: Callable[P, R]) -> Callable[P, R]:

	@wraps(func)
	def wrapper_func(*args: P.args, **kwargs: P.kwargs) -> R:
		input_ary, data_ary = func(*args, **kwargs)
		options = {
			'headers': None,
			'floatfmt': '.1f',
			'tablefmt': 'simple'
		}
		options.update(kwargs)

		data = []
		for i, player in enumerate(options['players']):
			row = [player.name]
			row.extend(list(data_ary[i, :]))
			data.append(row)

		if headers := options['headers']:
			pass
		else:
			headers = [options['data']]
			headers.extend([str(x) for x in input_ary])

		table = tabulate(data, headers=headers, floatfmt=options['floatfmt'], tablefmt=options['tablefmt'])
		print(table)

		return input_ary, data_ary

	return wrapper_func


def scale_comparison(*, players: tuple[Player, ...], monster_name: str, **kwargs):
	options = {
		'scales': range(1, 100+1),
		'data': 'object'
	}
	options.update(kwargs)
	scales_ary = np.asarray(options['scales'])
	d_ary = np.empty(shape=(len(players), scales_ary.size), dtype=object)

	for j, scale in enumerate(scales_ary):
		monster = CoxMonster.from_de0(monster_name, scale)

		for i, player in enumerate(players):
			dam_ij = player.damage_distribution(monster)

			if options['data'] == 'object':
				d_ary[i, j] = dam_ij
			elif options['data'] == 'dps':
				d_ary[i, j] = dam_ij.per_second
			elif options['data'] == 'dpt':
				d_ary[i, j] = dam_ij.per_tick
			elif options['data'] == 'mean':
				d_ary[i, j] = dam_ij.mean
			elif options['data'] == 'max hit':
				d_ary[i, j] = dam_ij.max_hit
			else:
				raise NotImplementedError

	return scales_ary, d_ary


def variable_comparison(*, players: tuple[Player, ...], monster_name: str, skill_var: str, values: Iterable, **kwargs):
	options = {
		'data': 'object',
	}
	options.update(kwargs)
	values_ary = np.asarray(values)

	d_ary = np.empty(shape=(len(players), values_ary.size))
	monster = CoxMonster.from_de0(monster_name, 100)

	for j, value in enumerate(values):
		monster.active_levels.__setattr__(skill_var, value)

		for i, player in enumerate(players):
			dam_ij = player.damage_distribution(monster)

			if options['data'] == 'object':
				d_ary[i, j] = dam_ij
			elif options['data'] == 'dps':
				d_ary[i, j] = dam_ij.per_second
			elif options['data'] == 'dpt':
				d_ary[i, j] = dam_ij.per_tick
			elif options['data'] == 'mean':
				d_ary[i, j] = dam_ij.mean
			elif options['data'] == 'max hit':
				d_ary[i, j] = dam_ij.max_hit
			else:
				raise NotImplementedError

	return values_ary, d_ary


def equipment_comparison(
		*,
		players: tuple[Player, ...],
		equipments: tuple[Equipment, ...],
		data_func: Callable[P, R],
		target: Character | None,
		**kwargs
):
	"""

	:param players: A tuple containing Players.
	:param equipments: A tuple containing Equipments.
	:param data_func: A callable function which returns data. The first argument must accept Player. The second must
		accept Equipment. The third may accept Character or not exist.
	:param target: The Character
	:param kwargs:
	:return:
	"""
	if target:
		inputs = tuple(zip(equipments, (target, )*len(equipments)))
	else:
		inputs = equipments

	return generic_comparison(
		players=players,
		data_func=data_func,
		input_vals=inputs,
		**kwargs
	)


def generic_damage_method(
		player: Player,
		levels: PlayerLevels | None,
		prayers: PrayerCollection | None,
		boosts: BoostCollection | None,
		equipment: Equipment | None,
		active_style: PlayerStyle | None,
		target: Character,
		*args,
		**kwargs
) -> Damage:
	if levels is not None:
		player.levels = levels
		player.reset_stats()

	if prayers is not None:
		player.prayers = prayers

	if boosts is not None:
		player.reset_stats()
		player.boost(boosts)

	if equip_reset := (equipment is not None):
		base_equip = copy(player.equipment)
		base_style = player.active_style

		return_style = player.equipment.equip(*astuple(equipment, recurse=False), style=active_style)

		if return_style is not None:
			player.active_style = return_style

	else:
		base_equip, base_style = (None, )*2

	# not redundant, style may change without gear changing.
	if active_style is not None:
		player.active_style = active_style

	dam = player.damage_distribution(other=target, *args, **kwargs)

	# cleanup
	if equip_reset:
		player.equipment.equip(*astuple(base_equip, recurse=False))
		player.active_style = base_style

	return dam


def generic_comparison_better(
		players: Player | list[Player, ...],
		*,
		levels: PlayerLevels | list[PlayerLevels, ...] = None,
		prayers: Prayer | PrayerCollection | list[Prayer | PrayerCollection, ...] = None,
		boosts: Boost | BoostCollection | list[Boost | BoostCollection, ...] = None,
		equipment: Equipment | list[Equipment, ...] = None,
		active_style: PlayerStyle | list[PlayerStyle, ...] = None,
		target: Character | list[Character, ...] = None,
		comparison_mode: ComparisonMode.PARALLEL,
		data_mode: DataMode = DataMode.DPS,
		**kwargs,
) -> (tuple[int, ...], list[list, ...], np.ndarray):
	if isinstance(players, Player):
		players = [players]

	if levels is None:
		levels = [None]
	elif isinstance(levels, PlayerLevels):
		levels = [levels]

	if prayers is None:
		prayers = [None]
	elif isinstance(prayers, Prayer):
		prayers = [PrayerCollection(prayers=(prayers, ))]
	elif isinstance(prayers, PrayerCollection):
		prayers = [prayers]
	elif isinstance(prayers, list):
		for index, e in enumerate(prayers[:]):
			if isinstance(e, Prayer):
				prayers[index] = PrayerCollection(prayers=(e, ))

	if boosts is None:
		boosts = [None]
	elif isinstance(boosts, Boost):
		boosts = [BoostCollection(boosts=(boosts, ))]
	elif isinstance(boosts, BoostCollection):
		boosts = [boosts]
	elif isinstance(boosts, list):
		for index, e in enumerate(boosts[:]):
			if isinstance(e, Boost):
				boosts[index] = BoostCollection(boosts=(e, ))

	if equipment is None:
		equipment = [None]
	elif isinstance(equipment, Equipment):
		equipment = [equipment]

	if active_style is None:
		active_style = [None]
	elif isinstance(active_style, PlayerStyle):
		active_style = [active_style]

	if target is None:
		target = [None]
	elif isinstance(target, Character):
		target = [target]

	axes = [players, levels, prayers, boosts, equipment, active_style, target]
	axes_dims = tuple(len(ax) for ax in axes)

	if comparison_mode == ComparisonMode.PARALLEL:
		max_dim = max(axes_dims)
		indices = tuple(range(max_dim))
		data_ary = np.empty(shape=(max_dim, ), dtype=data_mode.value.dtype)

		for index, axis in enumerate(axes[:]):
			if len(axis) == 1:
				axes[index] = axis * max_dim

		for index, params in enumerate(zip(*axes, strict=True)):
			dam = generic_damage_method(*params, **kwargs)
			data_ary[index] = dam.__getattribute__(data_mode.value.attribute)

	elif comparison_mode == ComparisonMode.CARTESIAN:
		indices = tuple(product(*(range(n) for n in axes_dims)))
		cartesian_product = product(*axes)
		data_ary = np.empty(shape=axes_dims, dtype=data_mode.value.dtype)

		for index, params in zip(indices, cartesian_product):
			dam = generic_damage_method(*params, **kwargs)
			data_ary[index] = dam.__getattribute__(data_mode.value.attribute)

	else:
		raise NotImplementedError

	return indices, axes, data_ary



def generic_comparison(
		*,
		players: list[Player, ...],
		data_func: Callable[P, R],
		input_vals: Iterable,
		**kwargs
):
	"""

	:param players: A tuple containing Players.
	:param data_func: A callable function which returns data. The first argument must accept Player.
	:param input_vals: An Iterable whose elements are passed to data_func. If different Players require different params
		input_vals must be an Iterable of Iterables.
	:param kwargs:
	:return:
	"""
	input_ary = np.asarray([str(v) for v in input_vals], dtype=str)
	data_ary = np.empty(shape=(len(players), input_ary.size))

	for i, player in enumerate(players):
		for j, input_j in enumerate(input_vals):
			try:
				data_ary[i, j] = data_func(player, *input_j, **kwargs)
			except TypeError:
				data_ary[i, j] = data_func(player, input_j, **kwargs)

	return input_ary, data_ary





