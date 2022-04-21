import functools

import numpy as np
from attrs import define, field

from osrs_tools.exceptions import OsrsException
from osrs_tools.modifier import DamageValue, Level

# helpful constants
HS_TOLERANCE = 1e-6
SECONDS_PER_TICK = 0.6
TICKS_PER_SECOND = 1 / SECONDS_PER_TICK
TICKS_PER_MINUTE = 100
TICKS_PER_HOUR = 6000


@define
class Hitsplat:
    damage: np.ndarray = field(repr=False, converter=np.asarray)
    probability: np.ndarray = field(repr=False, converter=np.asarray)
    min_hit: int = field(init=False)
    max_hit: int = field(init=False)
    mean_hit: float = field(init=False)
    probability_nonzero_damage: float = field(init=False, repr=False)

    def __attrs_post_init__(self):
        try:
            assert self.damage.size == self.probability.size
            assert HS_TOLERANCE > np.abs(self.probability.sum() - 1)
        except AssertionError as exc:
            raise DamageError from exc

        self.min_hit = self.damage.min()
        self.max_hit = self.damage.max()
        self.mean_hit = np.dot(self.damage, self.probability)
        self.probability_nonzero_damage = 1 - self.probability[0]

    def random_hit(self, k: int = 1) -> int | np.ndarray:
        """Return a hit or 1D array of hits that are randomly chosen from the Hitsplat distribution.

        Args:
            k (int, optional): Attempts made by the attacker. Defaults to 1.

        Returns:
            int | np.ndarray[int]: Return int if only one attempt, else an ndarray[int].
        """
        if k == 1:
            return np.random.choice(
                self.damage, size=1, replace=False, p=self.probability
            )
        else:
            return np.random.choice(
                self.damage, size=(k,), replace=False, p=self.probability
            )

    @classmethod
    def basic_constructor(
        cls,
        max_hit: DamageValue | int,
        accuracy: float,
        hitpoints_cap: int | Level = None,
    ):
        """Basic constructor for a hit distribution with a uniform damage value from 0 to max_hit.

        Args:
            max_hit (MaxHit | int): An integer-like object that denotes the maximum damage value.
            accuracy (float): The probability an attack will succeed, not to be confused with the
            probability to deal positive damage.
            hitpoints_cap (int, optional): Optionally specify a hitpoints cap to accurately simulate
            overkill hitsplats. Excess damage is aggregated in the largest allowed damage value.
            Defaults to None.

        Returns:
            Hitsplat: A Hitsplat object
        """
        damage = np.arange(0, int(max_hit) + 1)
        probability = np.asarray([accuracy * (1 / (int(max_hit) + 1)) for _ in damage])
        probability[0] += 1 - accuracy

        # TODO: < Comparison probably works ??
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

        Returns:
            Hitsplat: Thrall Hitsplat object.
        """
        dmg = np.arange(0, 4 + 1)
        prb = (1 / dmg.size) * np.ones(shape=dmg.shape)
        return cls(dmg, prb)


@define
class Damage:
    attack_speed: int
    hitsplats: tuple[Hitsplat] = field(repr=False)
    min_hit: int = field(init=False)
    max_hit: int = field(init=False)
    mean_hit: float = field(init=False)
    probability_nonzero_damage: float = field(init=False, repr=False)
    per_tick: float = field(init=False)
    per_second: float = field(init=False, repr=False)
    per_minute: float = field(init=False, repr=False)
    per_hour: float = field(init=False, repr=False)

    def __attrs_post_init__(self):
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

    def random_hit(self, k: int = 1) -> int | np.ndarray:
        """Return an integer or 1D array representing a random hit from the Damage object.

        Args:
            k (int, optional): Attack attempts. Defaults to 1.

        Returns:
            int | np.ndarray: int if k = 1, else np.ndarray of shape (k*n, ) where n is the
            number of hitsplats a Damage object contains.
        """
        n = len(self.hitsplats)
        hits = np.empty(shape=(k, n), dtype=int)
        for idx, hs in enumerate(self.hitsplats):
            hits[:, idx] = hs.random_hit(k)

        if n == 1 and k == 1:
            hits: int = int(hits[0, 0])
        else:
            hits: np.ndarray = hits.reshape((k * n,))

        return hits

    @classmethod
    def basic_constructor(
        cls,
        attack_speed: int,
        max_hit: DamageValue | int,
        accuracy: float,
        hitpoints_cap: int = None,
    ):
        """Basic constructor for a hit distribution with a uniform damage value from 0 to max_hit.

        Args:
            attack_speed (int): The attack speed in ticks.
            max_hit (MaxHit | int): An integer-like object that denotes the maximum damage value.
            accuracy (float): The probability an attack will succeed, not to be confused with the
            probability to deal positive damage.
            hitpoints_cap (int, optional): Optionally specify a hitpoints cap to accurately simulate
            overkill hitsplats. Excess damage is aggregated in the largest allowed damage value.
            Defaults to None.

        Returns:
            Damage: A Damage object
        """
        hs = Hitsplat.basic_constructor(max_hit, accuracy, hitpoints_cap)
        return cls(attack_speed, (hs,))

    @classmethod
    def thrall(cls):
        """Constructs a thrall Damage object.

        Returns:
            Damage: Thrall Damage object.
        """
        attack_speed = 4
        hs = Hitsplat.thrall()
        return cls(attack_speed, (hs,))


class DamageError(OsrsException):
    pass
