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
    return (1 - capped_roll_chance) ** capped_rolls * (1 - uncapped_roll_chance)


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
    plt.ylabel("d[P(At least one unique)]/d[points] as % effective of initial roll")

    plt.show()


def ori_maths():
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
    chance_to_see_any_amount_of_drops = 1 - p_noloot

    expected_purples_per_raid = np.dot(np.arange(1, 2 + 1), [p_1loot, p_2loot])

    print(
        f"chance of a capped account getting a purple: {p_loot_on_capped_acc * 100:.1f}%"
    )
    print(
        f"chance of seeing at least one purple: {chance_to_see_any_amount_of_drops*100:.0f}%"
    )
    print(f"expected purples per raid: {expected_purples_per_raid:.2f}")


if __name__ == "__main__":
    # main()
    # print(two_cap_at_least_one())
    ori_maths()
