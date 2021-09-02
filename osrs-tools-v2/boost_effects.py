from experience import SKILLS
import math


class BoostEffect:

    def __init__(self, divine: bool = True, **kwargs):
        """
        Create a BoostEffect object that can calculate and apply boosts flexibly

        :param kwargs: key, val pair with stat name and corresponding boost function
        """
        self.divine = divine

        options = {s: lambda x: x for s in SKILLS}      # default function is f(x) = x
        options.update(kwargs)
        self.affected_skills = list(kwargs.keys())

        for key, val in options.items():
            self.__setattr__(key, val)

    def update_effect(self, **kwargs):
        """
        Add or update existing skill effects for a BoostEffect object, similar to __init__

        :param kwargs:
        :return:
        """

        for key, val in kwargs.items():
            assert key in SKILLS
            assert callable(val)
            self.__setattr__(key, val)


def super_combat_potion(divine: bool = True):
    def scb_stat(x: int):
        return 5 + math.floor(x * 0.15)

    return BoostEffect(divine=divine, attack=scb_stat, strength=scb_stat, defence=scb_stat)


def ranging_potion(divine: bool = True):
    def rng_stat(x: int):
        return 4 + math.floor(x * 0.10)

    return BoostEffect(divine=divine, ranged=rng_stat)


def bastion_potion(divine: bool = True):
    def rng_stat(x: int):
        return 4 + math.floor(x * 0.10)

    def def_stat(y: int):
        return 5 + math.floor(y * 0.15)

    return BoostEffect(divine=divine, ranged=rng_stat, defence=def_stat)


def imbued_heart():
    def mag_boost(x: int):
        return 1 + math.floor(x * 0.10)

    return BoostEffect(divine=False, magic=mag_boost)


def overload():
    def ovl_stat(x: int):
        return 6 + math.floor(x * 0.16)

    return BoostEffect(divine=False, attack=ovl_stat, strength=ovl_stat, defence=ovl_stat, ranged=ovl_stat,
                       magic=ovl_stat)

