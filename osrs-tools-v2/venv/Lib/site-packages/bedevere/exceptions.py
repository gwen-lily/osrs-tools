from bedevere import *


class Critical(Exception):

	def __init__(self, rolls: list, value: int, message: str = 'You rolled a critical value.'):
		self.rolls = rolls
		self.value = value
		self.message = message
		super().__init__(self.message)


class CriticalHit(Critical):

	def __init__(self, rolls: list, value: int, message: str = 'You scored a critical hit!', damage: int = 0):
		self._damage = damage
		super().__init__(rolls, value, message)

	@property
	def damage(self) -> int:
		return self.damage

	@damage.setter
	def damage(self, value: int):
		self.damage = value


class CriticalFumble(Critical):

	def __init__(self, rolls: list, value: int, message: str = 'You scored a critical fumble!'):
		super().__init__(rolls, value, message)
