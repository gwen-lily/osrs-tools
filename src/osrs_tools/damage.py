import functools

import numpy as np
import random
from cached_property import cached_property

from src.osrs_tools.exceptions import *


class Hitsplat:     # TODO: Dataclass/attrs
    _tolerance = 1e-6    # for ensuring complete probability spaces / sums

    def __init__(self, damage: np.ndarray, probability: np.ndarray, hitpoints_cap: int = None):
        """
        Construct a Hitsplat object from exact damage and probability information.

        :param damage:  Array-like of possible damage values.
        :param probability: Exact probabilities of corresponding damage values occurring.
        :param hitpoints_cap: If the Monster's current HP is less than the max hit, smoosh all such values into cap HP.
        """
        assert damage.size == probability.size
        assert self._tolerance > np.abs(np.sum(probability) - 1)     # complete probability space

        if not hitpoints_cap or damage.max() <= hitpoints_cap:
            self.damage = damage
            self.probability = probability

        else:
            self.damage = damage[:hitpoints_cap+1]
            self.probability = np.zeros(self.damage.shape)
            self.probability[:hitpoints_cap] = probability[:hitpoints_cap]
            self.probability[hitpoints_cap] = sum(probability[hitpoints_cap:])

        self.min_hit = self.damage.min()
        self.max_hit = self.damage.max()
        self.mean = np.dot(self.damage, self.probability)



    def random(self, attempts: int = 1) -> list[int]:
        return random.choices(self.damage, self.probability, k=attempts)

    def asdict(self):
        return {d: p for d, p in zip(self.damage, self.probability)}

    @classmethod
    def from_max_hit_acc(cls, max_hit: int, accuracy: float, hitpoints_cap: int = None):
        """
        Simple constructor for normal hit distributions with equal chance of all damage values from 0 to max_hit.
        :param max_hit: The highest damage value that can be dealt.
        :param accuracy: The chance an attack has to be successful, not to be confused with the chance to deal damage.
        :param hitpoints_cap: The hitpoints of the target, disallows damage values over the cap and shifts distribution.
        :return: A Hitsplat object.
        """
        damage = np.arange(0, max_hit+1)
        probability = np.asarray([accuracy * (1 / (max_hit+1)) for _ in damage])
        probability[0] = probability[0] + (1 - accuracy)
        return cls(
            damage=damage,
            probability=probability,
            hitpoints_cap=hitpoints_cap
        )

    @classmethod
    def from_dict(cls, d: dict):
        assert all(type(k) == int and type(v) == float for k, v in d.items())

        max_hit = max(d.keys())
        damage = np.arange(0, max_hit+1)
        probability = np.zeros(damage.shape)

        for i, dam in enumerate(damage):
            try:
                probability[i] = d[dam]
            except KeyError:
                probability[i] = 0

        return cls(damage=damage, probability=probability)

    def __str__(self):
        message = f'{self.__class__.__name__}(min={self.min_hit}, max={self.max_hit}, mean={self.mean:.1f}'
        return message

    def __copy__(self):
        return self.__class__(damage=self.damage[:], probability=self.probability[:])


class Damage:
    _seconds_per_tick = 0.6
    _ticks_per_second = 1 / _seconds_per_tick
    _ticks_per_minute = 100
    _ticks_per_hour = 6000

    def __init__(self, attack_speed: int, *hitsplats: Hitsplat, **kwargs):
        # TODO: Make the default __iter__ behavior of this class yield hitsplats
        # KWARGS
        tick_efficiency_key = 'tick_efficiency_ratio'

        options = {
            tick_efficiency_key: 1
        }
        options.update(kwargs)

        self.tick_efficiency_ratio = options[tick_efficiency_key]

        # INIT
        self._attack_speed = attack_speed
        assert len(hitsplats) > 0
        self.hitsplats = hitsplats
        self.mean = sum(hs.mean for hs in self.hitsplats)
        self.min_hit = sum(hs.min_hit for hs in self.hitsplats)
        self.max_hit = sum(hs.max_hit for hs in self.hitsplats)
        self.per_tick = self.mean / self.attack_speed
        self.per_second = self.per_tick * Damage._ticks_per_second
        self.per_minute = self.per_tick * Damage._ticks_per_minute
        self.per_hour = self.per_tick * Damage._ticks_per_hour

    @property
    def attack_speed(self) -> float:
        return self._attack_speed / self.tick_efficiency_ratio

    @property
    def chance_to_deal_positive_damage(self) -> float:
        zero_chances = (hs.probability[0] for hs in self.hitsplats)
        return 1 - functools.reduce(lambda x, y: x*y, zero_chances)

    def random(self, attempts: int = 1) -> list[int]:
        hits = []
        for hs in self.hitsplats:
            hits.extend(hs.random(attempts))

        return hits

    @classmethod
    def from_max_hit_acc(cls, max_hit: int, accuracy: float, attack_speed: int, hitpoints_cap: int = None, **kwargs):
        hs = Hitsplat.from_max_hit_acc(max_hit=max_hit, accuracy=accuracy, hitpoints_cap=hitpoints_cap)
        return cls(attack_speed, hs, **kwargs)

    def __iter__(self):
        return iter(self.hitsplats)

    def __next__(self):
        try:
            return next(self.__iter__())
        except IndexError:
            raise StopIteration

    def __str__(self):
        message = f'{self.__class__.__name__}({self.hitsplats})'
        return message


class DamageError(OsrsException):
    pass
