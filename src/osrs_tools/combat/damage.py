"""The basis of all damage calculation.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

import functools
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from osrs_tools.data import TICKS_PER_HOUR, TICKS_PER_MINUTE, TICKS_PER_SECOND
from osrs_tools.exceptions import OsrsException
from osrs_tools.tracked_value import DamageValue, Level

###############################################################################
# errors 'n such                                                              #
###############################################################################

HS_TOLERANCE = 1e-6


class DamageError(OsrsException):
    pass


###############################################################################
# Hitsplat & Damage classes                                                   #
###############################################################################


@dataclass
class Hitsplat:
    damage: NDArray[np.int_] = field(repr=False)
    probability: NDArray[np.float_] = field(repr=False)
    min_hit: int = field(init=False)
    max_hit: int = field(init=False)
    mean_hit: float = field(init=False)
    probability_nonzero_damage: float = field(init=False, repr=False)

    def __post_init__(self):
        try:
            assert self.damage.size == self.probability.size
            assert HS_TOLERANCE > np.abs(self.probability.sum() - 1)
        except AssertionError as exc:
            raise ValueError from exc

        self.min_hit = self.damage.min()
        self.max_hit = self.damage.max()
        self.mean_hit = np.dot(self.damage, self.probability)
        self.probability_nonzero_damage = 1 - self.probability[0]

    def random_hit(self, k: int = 1) -> NDArray[np.int_]:
        """Return a 1D array of random hits.

        Parameters
        ----------

        k : int, optional
            Attempts made by the attacker, Defaults to 1

        Returns
        -------

        NDArray[np.int_]
        """
        return np.random.choice(
            self.damage, size=(k,), replace=False, p=self.probability
        )

    @classmethod
    def basic_constructor(
        cls,
        max_hit: DamageValue | int,
        accuracy: float,
        hitpoints_cap: int | Level | None = None,
    ):
        """Hit distribution with a uniform damage range from 0 to max_hit.

        Parameters
        ----------
        max_hit : MaxHit | int
            An integer-like object that denotes the maximum damage value.
        accuracy : float
            The probability an attack will succeed, not to be confused with
            the probability to deal positive damage.
        hitpoints_cap : int, optional
            Optionally specify a hitpoints cap to accurately simulate
            overkill hitsplats. Excess damage is aggregated in the largest
            allowed damage value, Defaults to None.

        Returns
        -------
        Hitsplat
        """
        damage = np.arange(0, int(max_hit) + 1)
        probability = np.asarray([accuracy * (1 / (int(max_hit) + 1)) for _ in damage])
        probability[0] += 1 - accuracy

        if hitpoints_cap is not None and hitpoints_cap < damage.max():
            return cls.clamp_to_hitpoints_cap(damage, probability, hitpoints_cap)
        else:
            return cls(damage, probability)

    @classmethod
    def clamp_to_hitpoints_cap(
        cls, damage: np.ndarray, probability: np.ndarray, hitpoints_cap: int | Level
    ):
        hp_cap = int(hitpoints_cap)
        dmg_adj = damage[: hp_cap + 1]
        prb_adj = np.zeros(dmg_adj.shape)
        prb_adj[:hp_cap] = probability[:hp_cap]
        prb_adj[hp_cap] = probability[hp_cap:].sum()
        return cls(dmg_adj, prb_adj)

    @classmethod
    def thrall(cls):
        """Returns a thrall Hitsplat object.

        Returns
        -------
        Hitsplat
            Thrall Hitsplat object.
        """
        dmg = np.arange(0, 4 + 1)
        prb = (1 / dmg.size) * np.ones(shape=dmg.shape)
        return cls(dmg, prb)


@dataclass
class Damage:
    attack_speed: int
    hitsplats: list[Hitsplat] = field(repr=False)
    min_hit: int = field(init=False)
    max_hit: int = field(init=False)
    mean_hit: float = field(init=False)
    probability_nonzero_damage: float = field(init=False, repr=False)
    per_tick: float = field(init=False)
    per_second: float = field(init=False, repr=False)
    per_minute: float = field(init=False, repr=False)
    per_hour: float = field(init=False, repr=False)

    def __post_init__(self):
        self.min_hit = sum(hs.min_hit for hs in self.hitsplats)
        self.max_hit = sum(hs.max_hit for hs in self.hitsplats)
        self.mean_hit = sum(hs.mean_hit for hs in self.hitsplats)
        zero_probs = (hs.probability[0] for hs in self.hitsplats)
        self.probability_nonzero_damage = 1 - functools.reduce(
            lambda x, y: x * y, zero_probs
        )
        self.per_tick = self.mean_hit / self.attack_speed
        self.per_second = self.per_tick * TICKS_PER_SECOND
        self.per_minute = self.per_tick * TICKS_PER_MINUTE
        self.per_hour = self.per_tick * TICKS_PER_HOUR

    def __iter__(self):
        return iter(self.hitsplats)

    def random_hit(self, k: int = 1) -> NDArray[np.int_]:
        """Return a 1D array representing a random hit from the Damage object.

        Parameters
        ----------

        k : int, optional
            Attack attempts, Defaults to 1.

        Returns
        -------

        NDArray[np.int_]
        """

        n = len(self.hitsplats)
        hits = np.empty(shape=(k, n), dtype=int)

        for idx, hs in enumerate(self.hitsplats):
            hits[:, idx] = hs.random_hit(k)

        hits: NDArray[np.int_] = hits.reshape(k * n)
        return hits

    @classmethod
    def basic_constructor(
        cls,
        attack_speed: int,
        max_hit: DamageValue | int,
        accuracy: float,
        hitpoints_cap: int | Level | None = None,
    ):
        """Basic constructor for a uniform damage distribution from 0 to max_hit.

        Parameters
        ----------
        attack_speed : int
            The attack speed in ticks.
        max_hit : (MaxHit | int): An integer-like object that denotes the maximum damage value.
        accuracy (float): The probability an attack will succeed, not to be confused with the
        probability to deal positive damage.
        hitpoints_cap (int, optional): Optionally specify a hitpoints cap to accurately simulate
        overkill hitsplats. Excess damage is aggregated in the largest allowed damage value.
        Defaults to None.

        Returns:
            Damage: A Damage object
        """
        hs = Hitsplat.basic_constructor(max_hit, accuracy, hitpoints_cap)
        return cls(attack_speed, [hs])

    @classmethod
    def thrall(cls):
        """Constructs a thrall Damage object.

        Returns:
            Damage: Thrall Damage object.
        """
        attack_speed = 4
        hs = Hitsplat.thrall()
        return cls(attack_speed, [hs])


# for clean reference
ThrallDamage = Damage.thrall()
