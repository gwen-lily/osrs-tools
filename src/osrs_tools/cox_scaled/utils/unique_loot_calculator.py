import matplotlib.pyplot as plt
import numpy as np

loot_roll_point_cap = int(570e3)
individual_point_cap = 131071
chance_per_one_percent = 8676
points_per_purple = chance_per_one_percent * 100
capped_roll_chance = loot_roll_point_cap / points_per_purple
max_rolls = 6


def zero_purple_chance(points: int) -> float:
    capped_rolls, remaining_points = divmod(points, loot_roll_point_cap)

    if capped_rolls >= max_rolls:
        return (1 - capped_roll_chance) ** max_rolls

    uncapped_roll_chance = remaining_points / points_per_purple
    zero_chance = (1 - capped_roll_chance) ** capped_rolls * \
        (1 - uncapped_roll_chance)

    return zero_chance


def purple_chance(points: int, number: int) -> float:
    capped_rolls, remaining_points = divmod(points, loot_roll_point_cap)

    if capped_rolls + 1 * (remaining_points > 0) < number:
        return 0

    else:
        raise NotImplementedError


def two_cap_at_least_one() -> float:
    total_points = loot_roll_point_cap * 2
    return 1 - zero_purple_chance(total_points)


def main(**kwargs):
    options = {
        "dx": int(1e4),
    }
    options.update(kwargs)

    x = np.arange(0, max_rolls * loot_roll_point_cap + 1, options["dx"])
    y = np.asarray([1 - zero_purple_chance(xx) for xx in x])
    x_thousand = x * 1e-3

    x_thousand_diff = np.diff(x_thousand)
    y_diff = np.diff(y)
    dy_dx_thousand = [dy / dx for dx, dy in zip(x_thousand_diff, y_diff)]
    dy_dx_thousand_as_percentage = np.asarray(dy_dx_thousand) * (
        1 / max(dy_dx_thousand)
    )

    plt.plot(x_thousand, y)
    plt.xlabel("points (K)")
    plt.ylabel("Probability of rolling at least one unique")
    plt.show()

    plt.plot(x_thousand[:-1], dy_dx_thousand_as_percentage)
    plt.xlabel("points (K)")
    plt.ylabel(
        "d[P(At least one unique)]/d[points] as % effective of initial roll"
    )

    plt.show()


def ori_31_scale_maths():
    # assume four accounts that cap with some extra dps alts
    # the fraction could be estimated better with data, but I'm
    # assuming it's low because of how many points Olm gives.
    team_points = int(800e3)
    b = individual_point_cap
    fraction_of_leftover_points_on_dps_alts = 0.25

    # sum of individual points accounting for cap
    capped_acc_points = 4 * b
    dps_alt_points = (
        team_points - capped_acc_points
    ) * fraction_of_leftover_points_on_dps_alts
    sigma = capped_acc_points + dps_alt_points  # sum of individ pts

    # chances of successfully rolling a purple
    p1 = capped_roll_chance
    p2 = (team_points - loot_roll_point_cap) * 0.01 / chance_per_one_percent
    # failure
    q1 = 1 - p1
    q2 = 1 - p2

    # chances of seeing 1 loot & 2 loots
    p_noloot = zero_purple_chance(team_points)
    p_1loot = p1 * q2 + p2 * q1
    p_2loot = p1 * p2

    # sum of two events
    # 1: Chance that player gets the loot given 1 loot
    # 2: Chance that there are two loots and then either
    # 	a: The first roll is the player's (B / Σ)
    # 	b: The first roll fails and the second roll is the player's
    # 	   	(1 - B)/Σ * B/(Σ - B) assume that if the first roll happened
    # 		it went to a capped player (pretty safe assumption).
    p_event_1 = p_1loot * (b / sigma)
    p_event_2 = p_2loot * (b / sigma + b * (1 - b) / (sigma * (sigma - b)))
    p_loot_on_capped_acc = p_event_1 + p_event_2

    # overall loot chance
    _chance_any_drop = 1 - p_noloot

    expected_purples_per_raid = np.dot(np.arange(1, 2 + 1), [p_1loot, p_2loot])

    print(
        "chance of a capped account getting a purple: " +
        f"{p_loot_on_capped_acc * 100:.1f}%"
    )
    print(
        f"chance of seeing at least one purple: {_chance_any_drop*100:.0f}%"
    )
    print(f"expected purples per raid: {expected_purples_per_raid:.2f}")


def ori_three_plus_twelve_overcap(iron_points: int) -> float:

    # clamp iron points to the individual cap
    if iron_points <= individual_point_cap:
        excess_points = 0
    else:
        excess_points = iron_points - individual_point_cap
        iron_points = individual_point_cap

    # deduct from the assignment pool
    sum_of_individual_points = total_pts_estimate - excess_points

    # the points that determine whether or not a purple is rolled
    # re-add the excess points into the total pool
    _purple_chance = 1 - zero_purple_chance(total_pts_estimate)

    # the chance for the iron to get the purple, once a purple has been rolled
    iron_point_share = iron_points / sum_of_individual_points
    iron_purple_chance = _purple_chance * iron_point_share

    return iron_purple_chance


if __name__ == "__main__":
    total_points_data = [
        342589,
        341693,
        339492,
        325621,
        320835,
        313269,
        325721,
        320762,
        330708,
        314555,
    ]

    total_pts_estimate = sum(total_points_data) // len(total_points_data)
    print(total_pts_estimate)

    iron_pts_ary = np.arange(120000, 150000, int(1e3))
    iron_purp_ary = np.empty(shape=iron_pts_ary.shape, dtype=float)

    for idx, ep in enumerate(iron_pts_ary):
        iron_purp_ary[idx] = ori_three_plus_twelve_overcap(ep)

    plt.plot(iron_pts_ary, iron_purp_ary)
    plt.xlabel('points over cap')
    plt.ylabel('iron purple chance')

    plt.show()
