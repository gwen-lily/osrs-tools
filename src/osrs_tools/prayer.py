from cached_property import cached_property
from osrsbox import prayers_api
from osrsbox.prayers_api import prayer_properties

from .stats import *
from src.osrs_tools.exceptions import *

Prayers = prayers_api.load()


# noinspection PyArgumentList
@define(order=True, frozen=True)
class Prayer:
	name: str
	drain_effect: int = 0
	attack: float = 1
	strength: float = 1
	defence: float = 1
	ranged_attack: float = 1
	ranged_strength: float = 1
	magic_attack: float = 1
	magic_strength: float = 1
	magic_defence: float = 1

	@classmethod
	def from_osrsbox(cls, name: str = None, prayer_id: int = None, **kwargs):
		options = {
			'drain_effect': 0,
			Skills.attack: 0,
			Skills.strength: 0,
			Skills.defence: 0,
			Skills.ranged: 0,
			'ranged_strength': 0,
			Skills.magic: 0,
			'magic_strength': 0,
			'magic_defence': 0
		}

		for pp in Prayers.all_prayers:
			if pp.name == name or pp.id == prayer_id:
				options.update(pp.bonuses)
				options.update(kwargs)

				return cls(
					name=pp.name,
					drain_effect=options['drain_effect'],
					attack=1 + 0.01*options[Skills.attack],
					strength=1 + 0.01*options[Skills.strength],
					defence=1 + 0.01*options[Skills.defence],
					ranged_attack=1 + 0.01*options[Skills.ranged],
					ranged_strength=1 + 0.01*options['ranged_strength'],
					magic_attack=1 + 0.01*options[Skills.magic],
					magic_strength=1 + 0.01*options['magic_strength'],
					magic_defence=1 + 0.01*options['magic_defence']
				)

		raise PrayerError(f'{name=}')

	@classmethod
	def augury(cls):
		# osrsbox version inaccurate
		return cls.from_osrsbox(prayer_id=29, defence=25, magic_defence=25, drain_effect=24)

	@classmethod
	def rigour(cls):
		return cls.from_osrsbox(prayer_id=28, drain_effect=24)

	@classmethod
	def piety(cls):
		return cls.from_osrsbox(prayer_id=27, drain_effect=24)

	@classmethod
	def protect_from_melee(cls):
		return cls.from_osrsbox(prayer_id=19, drain_effect=12)

	@classmethod
	def protect_from_missiles(cls):
		return cls.from_osrsbox(prayer_id=18, drain_effect=12)

	@classmethod
	def protect_from_magic(cls):
		return  cls.from_osrsbox(prayer_id=17, drain_effect=12)

	@classmethod
	def chivalry(cls):
		return cls.from_osrsbox(prayer_id=26, drain_effect=24)

	@classmethod
	def preserve(cls):
		return cls.from_osrsbox(prayer_id=25, drain_effect=2)

	@classmethod
	def smite(cls):
		return cls.from_osrsbox(prayer_id=24, drain_effect=18)

	@classmethod
	def redemption(cls):
		return cls.from_osrsbox(prayer_id=23, drain_effect=6)

	@classmethod
	def retribution(cls):
		return cls.from_osrsbox(prayer_id=22, drain_effect=3)

	@classmethod
	def mystic_might(cls):
		return cls.from_osrsbox(prayer_id=21, drain_effect=12)

	@classmethod
	def eagle_eye(cls):
		return cls.from_osrsbox(prayer_id=20, drain_effect=12)


def prayer_collection_validator(instance, attribute: str, value: tuple[Prayer, ...]):
	pass    # TODO: Create validators that handle better than the current system.


@define
class PrayerCollection:
	name: str = field(factory=str, converter=str)
	prayers: tuple[Prayer, ...] = field(factory=tuple)

	def pray(self, *prayers: Prayer):
		prayers_list = list(self.prayers)
		prayers_list.extend(prayers)
		self.prayers = tuple(prayers_list)

	def reset_prayers(self):
		self.prayers = tuple()

	@property
	def drain_effect(self):
		return sum([p.drain_effect for p in self.prayers])

	@classmethod
	def no_prayers(cls):
		return cls()

	def _get_prayer_collection_attribute(self, attribute: str):
		attribute_prayers = [p for p in self.prayers if not p.__getattribute__(attribute) == 1]
		if len(attribute_prayers) == 0:
			return 1
		elif len(attribute_prayers) == 1:
			return attribute_prayers[0].__getattribute__(attribute)
		else:
			raise PrayerError(f'{attribute=} with {attribute_prayers=}')

	@property
	def attack(self):
		return self._get_prayer_collection_attribute(Skills.attack)

	@property
	def strength(self):
		return self._get_prayer_collection_attribute(Skills.strength)

	@property
	def defence(self):
		return self._get_prayer_collection_attribute(Skills.defence)

	@property
	def ranged_attack(self):
		return self._get_prayer_collection_attribute('ranged_attack')

	@property
	def ranged_strength(self):
		return self._get_prayer_collection_attribute('ranged_strength')

	@property
	def magic_attack(self):
		return self._get_prayer_collection_attribute('magic_attack')

	@property
	def magic_strength(self):
		return self._get_prayer_collection_attribute('magic_strength')

	@property
	def magic_defence(self):
		return self._get_prayer_collection_attribute('magic_defence')

	def __iter__(self):
		for p in self.prayers:
			yield p

	def __next__(self):
		try:
			next(self.__iter__())
		except IndexError:
			raise StopIteration


class PrayerError(OsrsException):
	pass
