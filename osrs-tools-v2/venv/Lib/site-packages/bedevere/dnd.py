from bedevere import *
from bedevere.discrete_sums import *
from bedevere.matrix import *

advantage = 'advantage'
disadvantage = 'disadvantage'
trivantage = 'trivantage'

conditions = [advantage, disadvantage, trivantage]


class Die:

	def __init__(self, sides: int):
		self.rolls = np.arange(1, sides + 1)
		self.weights = (1/sides) * np.ones(sides)

		assert is_stochastic(self.weights)

	def roll(self, n: int = 1) -> list:
		return random.choices(self.rolls, weights=self.weights, k=n)

	def average_roll(self, n: int = 1) -> float:
		return np.average(self.rolls, weights=self.weights) * n

	def max_roll(self, n: int = 1) -> int:
		return n * max(self.rolls)


class WeightedDie(Die):

	def __init__(self, sides: int, weights: Union[np.ndarray, list]):
		super().__init__(sides)
		self.weights = weights

		assert is_stochastic(self.weights)


class GreatWeaponFightingDie(Die):

	def __init__(self, sides: int):
		super().__init__(sides)

	def roll(self, n: int = 1) -> list:
		first_rolls = super().roll(n)
		keep_rolls = list(filter(lambda x: x > 2, first_rolls))
		second_rolls = super().roll(n - len(keep_rolls))

		for roll in second_rolls:
			keep_rolls.append(roll)

		return keep_rolls

	def average_roll(self, n: int = 1) -> float:
		N = self.max_roll()
		mean_weights = list(map(lambda x: 2/N**2 + (1/N)*(x > 2), self.rolls))
		assert is_stochastic(np.asarray(mean_weights))

		return np.average(self.rolls, weights=mean_weights) * n


class Weapon:

	def __init__(self, attack_bonus: int, damage_bonus: int, damage_dice: Union[Die, List[Die]]):
		self.attack_bonus = attack_bonus
		self.damage_bonus = damage_bonus

		if type(damage_dice) == list:
			self.damage_dice = damage_dice

		else:
			self.damage_dice = [damage_dice]

	def attack(self, condition: str = None, extra_damage_dice: Union[Die, List[Die]] = None, extra_damage_bonus: int = 0) \
			-> Tuple[int, int, object]:

		if type(extra_damage_dice) == Die:
			extra_damage_dice = [extra_damage_dice]

		elif extra_damage_dice is None:
			extra_damage_dice = []

		main_damage = 0
		extra_damage = 0

		try:
			roll_to_hit = roll_d20(self.attack_bonus, condition)

		except CriticalHit as CH:
			main_damage = roll_dice(self.damage_dice, self.damage_bonus, is_critical=True)
			extra_damage = roll_dice(extra_damage_dice, extra_damage_bonus, is_critical=True)
			return main_damage, extra_damage, CH

		except CriticalFumble as CF:
			main_damage = roll_dice(self.damage_dice, self.damage_bonus)
			extra_damage = roll_dice(extra_damage_dice, extra_damage_bonus)
			return main_damage, extra_damage, CF

		main_damage = roll_dice(self.damage_dice, self.damage_bonus)
		extra_damage = roll_dice(extra_damage_dice, extra_damage_bonus)
		return main_damage, extra_damage, None


D4 = Die(4)
D6 = Die(6)
D8 = Die(8)
D10 = Die(10)
D12 = Die(12)
D20 = Die(20)
D100 = Die(100)


def roll_generic(die: Die, n: int = 1, bonus: int = 0) -> int:
	return sum(die.roll(n)) + bonus


def roll_dice(dice: Union[Die, List[Die]], bonus: int = 0, is_critical: bool = False) -> int:

	if type(dice) == Die:
		dice = [Die]

	dice_multiplier = 2 if is_critical else 1
	dice_rolls = []

	for die in dice:
		die_roll = die.roll(dice_multiplier)

		for dr in die_roll:
			dice_rolls.append(dr)

	return sum(dice_rolls) + bonus


def roll_d20(bonus: int = None, condition: str = None) -> int:

	if condition == advantage:
		roll = max(D20.roll(2))

	elif condition == disadvantage:
		roll = min(D20.roll(2))

	elif condition == trivantage:
		roll = max(D20.roll(3))

	else:
		roll = D20.roll()[0]

	if roll == 1:
		raise CriticalFumble(roll, roll + bonus)

	elif roll == 20:
		raise CriticalHit(roll, roll + bonus)

	else:
		return roll + bonus

# Legacy support
# Support until 1.0.0


def generic_roll(die: Die, n: int = 1, bonus: int = 0) -> int:
	warnings.warn("Method will change to roll_generic in 1.0.0", FutureWarning)
	return roll_generic(die, n, bonus)


def test():
	weapon = Weapon(5, 4, [D6, D6])

	for condition in conditions:
		main_damage, extra_damage, Crit = weapon.attack(condition, extra_damage_dice=[D6, D8, D8, D8])

		if type(Crit) == CriticalHit:
			print('crit', main_damage, extra_damage)

		elif type(Crit) == CriticalFumble:
			print('"fumble" - John Madden', main_damage, extra_damage)


if __name__ == '__main__':
	test()
