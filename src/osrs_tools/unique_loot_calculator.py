import numpy as np
import matplotlib.pyplot as plt

loot_roll_point_cap = int(570e3)
individual_point_cap = 131071
chance_per_one_percent = 8676
points_per_purple = chance_per_one_percent*100
capped_roll_chance = loot_roll_point_cap / points_per_purple
max_rolls = 6


def zero_purple_chance(points: int) -> float:
	capped_rolls, remaining_points = divmod(points, loot_roll_point_cap)

	if capped_rolls < max_rolls:
		uncapped_roll_chance = remaining_points/points_per_purple
		return (1-capped_roll_chance)**capped_rolls * (1-uncapped_roll_chance)
	else:
		return (1-capped_roll_chance)**max_rolls


def purple_chance(points: int, number: int) -> float:
	capped_rolls, remaining_points = divmod(points, loot_roll_point_cap)

	if capped_rolls + 1*(remaining_points > 0) < number:
		return 0

	else:
		raise NotImplementedError


def two_cap_at_least_one() -> float:
	total_points = loot_roll_point_cap * 2
	return 1 - zero_purple_chance(total_points)



def main(**kwargs):
	options = {
		'dx': int(1e4),
	}
	options.update(kwargs)

	x = np.arange(0, max_rolls*loot_roll_point_cap+1, options['dx'])
	y = np.asarray([1 - zero_purple_chance(xx) for xx in x])
	x_thousand = x * 1e-3

	x_thousand_diff = np.diff(x_thousand)
	y_diff = np.diff(y)
	dy_dx_thousand = [dy/dx for dx, dy in zip(x_thousand_diff, y_diff)]
	dy_dx_thousand_as_percentage = np.asarray(dy_dx_thousand) * (1/max(dy_dx_thousand))

	plt.plot(x_thousand, y)
	plt.xlabel('points (K)')
	plt.ylabel('Probability of rolling at least one unique')
	plt.show()

	plt.plot(x_thousand[:-1], dy_dx_thousand_as_percentage)
	plt.xlabel('points (K)')
	plt.ylabel('d[P(At least one unique)]/d[points] as % effective of initial roll')

	plt.show()


if __name__ == '__main__':
	# main()
	print(two_cap_at_least_one())
