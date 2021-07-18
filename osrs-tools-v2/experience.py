import numpy as np
from typing import Union, List, Iterable


def compute_differential(levels: Union[int, Iterable[int]]):
	# returns an array of the XP needed to advance from LEVEL to LEVEL + 1

	try:
		_ = levels.__iter__()

	except AttributeError:
		levels_array = np.asarray([levels])
	else:
		levels_array = np.asarray(levels)

	differentials_array = np.floor((1/4) * np.floor((levels_array + 1 + 1) + 300*(2**(levels_array/7))))
	differentials_array = differentials_array.astype('int')
	return differentials_array


def display_levels(start: int, end: int):

	level_range = np.arange(start, end)     # no +1 because the target level does not need any experience
	differentials = compute_differential(level_range)

	for lvl, diff in zip(level_range, differentials):
		print(lvl, diff)


if __name__ == '__main__':
	s = 85
	e = 99
	display_levels(s, e)
