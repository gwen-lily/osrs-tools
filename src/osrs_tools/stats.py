from attrs import define, asdict, astuple, field, validators
from typing import Callable
import math
from copy import copy, deepcopy

from .exceptions import *
import osrs_tools.resource_reader as rr

player_skill_field = field(converter=lambda s: min([max([1, int(s)]), 99]), default=1)
player_skill_unbounded_field = field(converter=int, default=0)
monster_skill_field = field(converter=lambda s: max([0, math.ceil(s)]))     # fractional reductions round up
BoostType = Callable[[int], int]


def boost_effect_factory():
    return lambda x: x


boost_effect_field = field(factory=boost_effect_factory, validator=validators.is_callable())
ordered_immutable_attrs_settings = {'order': True, 'frozen': True}


@define(frozen=True, order=True)
class _Skills:
    """
    Simple reference point for all skills to avoid spelling/abbreviation mistakes.
    """
    attack = field(default="attack", init=False)
    strength = field(default="strength", init=False)
    defence = field(default="defence", init=False)
    ranged = field(default="ranged", init=False)
    prayer = field(default="prayer", init=False)
    magic = field(default="magic", init=False)
    runecraft = field(default="runecraft", init=False)
    hitpoints = field(default="hitpoints", init=False)
    crafting = field(default="crafting", init=False)
    mining = field(default="mining", init=False)
    smithing = field(default="smithing", init=False)
    fishing = field(default="fishing", init=False)
    cooking = field(default="cooking", init=False)
    firemaking = field(default="firemaking", init=False)
    woodcutting = field(default="woodcutting", init=False)
    agility = field(default="agility", init=False)
    herblore = field(default="herblore", init=False)
    thieving = field(default="thieving", init=False)
    fletching = field(default="fletching", init=False)
    slayer = field(default="slayer", init=False)
    farming = field(default="farming", init=False)
    construction = field(default="construction", init=False)
    hunter = field(default="hunter", init=False)


Skills = _Skills()


# noinspection PyArgumentList
@define(order=True)
class Stats:

    def __add__(self, other):
        # TODO: Validate the behavior of __add__
        if isinstance(other, self.__class__):
            try:
                for s in asdict(self).keys():
                    self.__setattr__(s, self.__getattribute__(s) + other.__getattribute__(s))
                return self
            except AttributeError:
                keys = list(asdict(self).keys())
                keys.extend(asdict(other).keys())
                combined_keys = set(keys)
                kwargs = {}
                for s in combined_keys:
                    try:
                        self_val = self.__getattribute__(s)
                    except AttributeError:
                        self_val = 0

                    try:
                        other_val = other.__getattribute__(s)
                    except AttributeError:
                        other_val = 0

                    kwargs[s] = self_val + other_val

                return self.__class__(**kwargs)
        else:
            return NotImplemented

    def __sub__(self, other):
        # TODO: Validate the behavior of __sub__
        if isinstance(other, self.__class__):
            try:
                for s in asdict(self).keys():
                    self.__setattr__(s, self.__getattribute__(s) - other.__getattribute__(s))
                return self
            except AttributeError:
                keys = list(asdict(self).keys())
                keys.extend(asdict(other).keys())
                combined_keys = set(keys)
                kwargs = {}
                for s in combined_keys:
                    try:
                        self_val = self.__getattribute__(s)
                    except AttributeError:
                        self_val = 0

                    try:
                        other_val = other.__getattribute__(s)
                    except AttributeError:
                        other_val = 0

                    kwargs[s] = self_val - other_val

                return self.__class__(**kwargs)
        else:
            return NotImplemented

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __rsub__(self, other):
        return NotImplemented

    # TODO: Find out if these be auto-generated for element-wise comparison with attrs.
    def __lt__(self, other):
        return NotImplemented
        # if isinstance(other, self.__class__):
        #     return any(self.__getattribute__(s) < other.__getattribute__(s) for s in asdict(self).keys())
        # else:
        #     return NotImplemented

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return all(self.__getattribute__(s) <= other.__getattribute__(s) for s in asdict(self).keys())
        else:
            return NotImplemented

    def __gt__(self, other):
        return NotImplemented
        # if isinstance(other, self.__class__):
        #     return all(self.__getattribute__(s) > other.__getattribute__(s) for s in asdict(self).keys())
        # else:
        #     return NotImplemented

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return all(self.__getattribute__(s) >= other.__getattribute__(s) for s in asdict(self).keys())
        else:
            return NotImplemented

    def __copy__(self):
        return self.__class__(**{copy(k): deepcopy(v) for k, v in asdict(self).items()})


# noinspection PyArgumentList
@define(order=True, frozen=False)
class PlayerLevels(Stats):
    attack: int = player_skill_field
    strength: int = player_skill_field
    defence: int = player_skill_field
    ranged: int = player_skill_field
    prayer: int = player_skill_field
    magic: int = player_skill_field
    runecraft: int = player_skill_field
    hitpoints: int = player_skill_field
    crafting: int = player_skill_field
    mining: int = player_skill_field
    smithing: int = player_skill_field
    fishing: int = player_skill_field
    cooking: int = player_skill_field
    firemaking: int = player_skill_field
    woodcutting: int = player_skill_field
    agility: int = player_skill_field
    herblore: int = player_skill_field
    thieving: int = player_skill_field
    fletching: int = player_skill_field
    slayer: int = player_skill_field
    farming: int = player_skill_field
    construction: int = player_skill_field
    hunter: int = player_skill_field

    def to_unbounded(self):
        return PlayerLevelsUnbounded(**asdict(self))

    @property
    def max_skill_level(self) -> int:
        return 99

    @property
    def min_skill_level(self) -> int:
        return 1

    @classmethod
    def maxed_player(cls):
        nn = (99,)*23
        return cls(*nn)

    @classmethod
    def from_rsn(cls, rsn: str):
        hs = rr.lookup_player_highscores(rsn)
        return cls(
            hs.attack.level,
            hs.strength.level,
            hs.defence.level,
            hs.ranged.level,
            hs.prayer.level,
            hs.magic.level,
            hs.runecraft.level,
            hs.hitpoints.level,
            hs.crafting.level,
            hs.mining.level,
            hs.smithing.level,
            hs.fishing.level,
            hs.cooking.level,
            hs.firemaking.level,
            hs.woodcutting.level,
            hs.agility.level,
            hs.herblore.level,
            hs.thieving.level,
            hs.fletching.level,
            hs.slayer.level,
            hs.farming.level,
            hs.construction.level,
            hs.hunter.level,
        )

    @classmethod
    def no_requirements(cls):
        ones = (1,)*23
        return cls(*ones)

    def __str__(self):
        header = f'{self.__class__.__name__}('
        content = ''

        for k, v in asdict(self, recurse=False).items():
            if not v == self.max_skill_level:
                content += f'{k}={v}, '

        if content:
            content = content.strip(', ') + ')'
        else:
            content = f'all={self.max_skill_level})'

        message = header + content
        return message

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if isinstance(other, self.__class__) or isinstance(other, PlayerLevelsUnbounded):
            args = (u + v for u, v in zip(astuple(self), astuple(other)))
            return self.__class__(*args)
        elif isinstance(other, Boost):
            args = [modifier_func(value) for value, modifier_func in zip(astuple(self), astuple(other))]
            return PlayerLevelsUnbounded(*args)
        else:
            return NotImplemented

    def __mul__(self, other):
        """
        Multiplication between PlayerLevels objects yields a combination of PlayerLevels objects by retaining the max
        values for all stats. This is useful for comparing Player-Equipment compatibility on an Equipment level rather
        than just Gear.
        :param other:
        :return:
        """
        if isinstance(other, self.__class__):
            args = (max([u, v]) for u, v in zip(astuple(self), astuple(other)))
            return self.__class__(*args)
        else:
            return NotImplemented

    def __copy__(self):
        return self.__class__(**asdict(self))


# noinspection PyArgumentList
@define(order=True, frozen=False)
class PlayerLevelsUnbounded(Stats):
    attack: int = player_skill_unbounded_field
    strength: int = player_skill_unbounded_field
    defence: int = player_skill_unbounded_field
    ranged: int = player_skill_unbounded_field
    prayer: int = player_skill_unbounded_field
    magic: int = player_skill_unbounded_field
    runecraft: int = player_skill_unbounded_field
    hitpoints: int = player_skill_unbounded_field
    crafting: int = player_skill_unbounded_field
    mining: int = player_skill_unbounded_field
    smithing: int = player_skill_unbounded_field
    fishing: int = player_skill_unbounded_field
    cooking: int = player_skill_unbounded_field
    firemaking: int = player_skill_unbounded_field
    woodcutting: int = player_skill_unbounded_field
    agility: int = player_skill_unbounded_field
    herblore: int = player_skill_unbounded_field
    thieving: int = player_skill_unbounded_field
    fletching: int = player_skill_unbounded_field
    slayer: int = player_skill_unbounded_field
    farming: int = player_skill_unbounded_field
    construction: int = player_skill_unbounded_field
    hunter: int = player_skill_unbounded_field

    def to_bounded(self) -> PlayerLevels:
        return PlayerLevels(**asdict(self))

    def __add__(self, other):
        if isinstance(other, self.__class__) or isinstance(other, PlayerLevels):
            args = (u + v for u, v in zip(astuple(self), astuple(other)))
            return self.__class__(*args)
        elif isinstance(other, Boost):
            args = [modifier_func(value) for value, modifier_func in zip(astuple(self), astuple(other))]
            return PlayerLevelsUnbounded(*args)
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, self.__class__) or isinstance(other, PlayerLevels):
            args = (u - v for u, v in zip(astuple(self), astuple(other)))
            return self.__class__(*args)
        else:
            return NotImplemented


# noinspection PyArgumentList
@define(order=True)
class Boost:
    attack: BoostType = boost_effect_field
    strength: BoostType = boost_effect_field
    defence: BoostType = boost_effect_field
    ranged: BoostType = boost_effect_field
    prayer: BoostType = boost_effect_field
    magic: BoostType = boost_effect_field
    runecraft: BoostType = boost_effect_field
    hitpoints: BoostType = boost_effect_field
    crafting: BoostType = boost_effect_field
    mining: BoostType = boost_effect_field
    smithing: BoostType = boost_effect_field
    fishing: BoostType = boost_effect_field
    cooking: BoostType = boost_effect_field
    firemaking: BoostType = boost_effect_field
    woodcutting: BoostType = boost_effect_field
    agility: BoostType = boost_effect_field
    herblore: BoostType = boost_effect_field
    thieving: BoostType = boost_effect_field
    fletching: BoostType = boost_effect_field
    slayer: BoostType = boost_effect_field
    farming: BoostType = boost_effect_field
    construction: BoostType = boost_effect_field
    hunter: BoostType = boost_effect_field

    @staticmethod
    def idiom(base: int, ratio: float, negative: bool = False) -> BoostType:
        f"""
        Generator function for easily writing Boost class methods.

        OSRS boosts tend to have the form: boost(level) = base_boost + math.floor(ratio_boost*level).
        This method simplifies definition to one line of the form: [f': (int,float,bool | None)] -> [f: (int,) -> int].
        
        :param base: Note that's "base boost", not to be confused with the "bass boost" you might find on your speaker. 
        :param ratio: Get ratio'd nerd.
        :param negative: No positive vibes allowed. Listen to gy!be.
        :return: f: (int,) -> int
        """
        return lambda x: x + (-1 if negative else 1) * (base + math.floor(ratio * x))

    def __add__(self, other):
        """
        Addition of functions is defined by chaining: f(x) + g(x) = f(g(x)) = g(f(x)).
        They don't call me the f o g enabler for nothing after all! And it's not just for my Dungeons & Dragons hijinks.
        :param other:
        :return: Boost
        """
        if isinstance(other, self.__class__):
            return NotImplemented
            # args = (lambda x: f(g(x)) for g, f in zip(astuple(self), astuple(other)))
            # return self.__class__(*args)
        elif isinstance(other, PlayerLevels) or isinstance(other, PlayerLevelsUnbounded):
            return other.__add__(self)
        else:
            return NotImplemented

    @classmethod
    def super_combat_potion(cls):
        scb_func = cls.idiom(5, 0.15)
        return cls(*(scb_func,)*3)

    @classmethod
    def bastion_potion(cls):
        return cls(defence=cls.idiom(5, 0.15), ranged=cls.idiom(4, 0.10))

    @classmethod
    def battlemage_potion(cls):
        return cls(defence=cls.idiom(5, 0.15), magic=cls.idiom(4, 0))

    @classmethod
    def imbued_heart(cls):
        return cls(magic=cls.idiom(1, 0.10))

    @classmethod
    def prayer_potion(cls, holy_wrench: bool = False):
        return cls(prayer=cls.idiom(7, 0.27 if holy_wrench else 0.25))

    @classmethod
    def super_restore(cls, holy_wrench: bool = False):
        kwargs = {skill: cls.idiom(8, 0.25) for skill in astuple(Skills)}
        if holy_wrench:
            kwargs[Skills.prayer] = cls.idiom(8, 0.27)
        return cls(**kwargs)

    @classmethod
    def sanfew_serum(cls, holy_wrench: bool = False):
        kwargs = {skill: cls.idiom(4, 0.30) for skill in astuple(Skills)}
        if holy_wrench:
            kwargs[Skills.prayer] = cls.idiom(4, 0.32)
        return cls(**kwargs)

    @classmethod
    def saradomin_brew(cls):
        debuff = cls.idiom(2, 0.10, True)
        kwargs = {skill: debuff for skill in (Skills.attack, Skills.strength, Skills.ranged, Skills.magic)}
        return cls(defence=cls.idiom(2, 0.20), hitpoints=cls.idiom(2, 0.15), **kwargs)

    @classmethod
    def zamorak_brew(cls):
        # TODO: Implement actual usage with levels and active_levels
        return cls(
            attack=cls.idiom(2, 0.20),
            strength=cls.idiom(2, 0.12),
            defence=cls.idiom(2, 0.10, True),
            hitpoints=cls.idiom(0, 0.12, True),
            prayer=cls.idiom(0, 0.10)
        )

    @classmethod
    def ancient_brew(cls):
        debuff = cls.idiom(2, 0.10, True)
        return cls(*(debuff,)*3, prayer=cls.idiom(2, 0.10), magic=cls.idiom(2, 0.05))

    @classmethod
    def super_attack_potion(cls):
        return cls(attack=cls.idiom(5, 0.15))

    @classmethod
    def super_strength_potion(cls):
        return cls(strength=cls.idiom(5, 0.15))

    @classmethod
    def super_defence_potion(cls):
        return cls(defence=cls.idiom(5, 0.15))

    @classmethod
    def ranging_potion(cls):
        return cls(ranged=cls.idiom(4, 0.10))

    @classmethod
    def magic_potion(cls):
        return cls(magic=cls.idiom(4, 0))

    @classmethod
    def combat_potion(cls):
        cb_func = cls.idiom(3, 0.10)
        return cls(attack=cb_func, strength=cb_func)

    @classmethod
    def attack_potion(cls):
        return cls(attack=cls.idiom(3, 0.10))

    @classmethod
    def strength_potion(cls):
        return cls(strength=cls.idiom(3, 0.10))

    @classmethod
    def defence_potion(cls):
        return cls(defence=cls.idiom(3, 0.10))


# noinspection PyArgumentList
class Divine(Boost):
    pass


# noinspection PyArgumentList
@define(order=True)
class Overload(Boost):
    hitpoints: BoostType = field(default=Boost.idiom(50, 0, True), validator=validators.is_callable(),
                                            init=False)

    @classmethod
    def _overload_generic(cls, base: int, ratio: float):
        ovl_func = cls.idiom(base, ratio)
        return cls(*(ovl_func,)*4, magic=ovl_func)

    @classmethod
    def overload(cls):
        """
        A normal, upstanding overload that rewards 600 points when drunk. Unless you've drunk alone, then it's 400.
        :return:
        """
        return cls._overload_generic(6, 0.16)

    @classmethod
    def _overload_mugwump_centrist(cls):
        """
        The Saint Hatred Special. This overload will leave you somewhat satisfied. Just do your farm contracts bro.
        :return:
        """
        return cls._overload_generic(5, 0.13)

    @classmethod
    def _overload_bottom_text(cls):
        """
        The worst overload. If this function ever gets used I will be upset. Email me at noahgill409@gmail.com.
        :return:
        """
        return cls._overload_generic(4, 0.10)


@define
class BoostCollection:
    name: str = field(factory=str, converter=str)
    boosts: tuple[Boost, ...] = field(factory=tuple)

    def __str__(self):
        message = f'{self.__class__.__name__}({self.name}, {self.boosts})'
        return message


@define(order=True)
class CombatLevels(Stats):
    attack: int
    strength: int
    defence: int
    ranged: int
    magic: int
    hitpoints: int


# noinspection PyArgumentList
@define(order=True)
class MonsterCombatLevels(CombatLevels):
    attack: int = monster_skill_field
    strength: int = monster_skill_field
    defence: int = monster_skill_field
    ranged: int = monster_skill_field
    magic: int = monster_skill_field
    hitpoints: int = monster_skill_field

    def __copy__(self):
        return self.__class__(**asdict(self))

    @classmethod
    def from_bb(cls, name: str):
        mon_df = rr.lookup_normal_monster_by_name(name)
        return cls(
            mon_df[Skills.attack].vaules[0],
            mon_df[Skills.strength].values[0],
            mon_df[Skills.defence].values[0],
            mon_df[Skills.ranged].values[0],
            mon_df[Skills.magic].values[0],
            mon_df[Skills.hitpoints].values[0],
        )


# noinspection PyArgumentList
@define(order=True)
class StyleStats(Stats):
    attack: int = 0
    strength: int = 0
    defence: int = 0
    ranged: int = 0
    magic: int = 0

    @classmethod
    def attack_bonus(cls):
        return cls(attack=3)

    @classmethod
    def strength_bonus(cls):
        return cls(strength=3)

    @classmethod
    def defence_bonus(cls):
        return cls(defence=3)

    @classmethod
    def ranged_bonus(cls):
        return cls(ranged=3)

    @classmethod
    def magic_bonus(cls):
        return cls(magic=3)

    @classmethod
    def shared_bonus(cls):
        return cls(attack=1, strength=1, defence=1)

    @classmethod
    def no_style_bonus(cls):
        return cls()

    @classmethod
    def npc_style_bonus(cls):
        ones = (1,)*5
        return cls(*ones)


# noinspection PyArgumentList
@define(**ordered_immutable_attrs_settings)
class AggressiveStats(Stats):
    stab: int = 0
    slash: int = 0
    crush: int = 0
    magic: int = 0
    ranged: int = 0
    melee_strength: int = 0
    ranged_strength: int = 0
    magic_strength: float | int = 0

    @classmethod
    def no_bonus(cls):
        return cls()

    @classmethod    # TODO: Look into bitterkoekje's general attack stat and see where it matters
    def from_bb(cls, name: str):
        mon_df = rr.lookup_normal_monster_by_name(name)

        if (general_attack_bonus := mon_df['attack bonus'].values[0]) > 0:
            stab_attack, slash_attack, crush_attack = 3*(general_attack_bonus,)
        else:
            stab_attack = mon_df['stab attack'].values[0]
            slash_attack = mon_df['slash attack'].values[0]
            crush_attack = mon_df['crush attack'].values[0]

        return cls(
            stab_attack,
            slash_attack,
            crush_attack,
            mon_df['magic attack'].values[0],
            mon_df['ranged attack'].values[0],
            mon_df['melee strength'].values[0],
            mon_df['ranged strength'].values[0],
            mon_df['magic strength'].values[0],
        )


# noinspection PyArgumentList
@define(**ordered_immutable_attrs_settings)
class DefensiveStats(Stats):
    stab: int = 0
    slash: int = 0
    crush: int = 0
    magic: int = 0
    ranged: int = 0

    @classmethod
    def no_bonus(cls):
        return cls()

    @classmethod
    def from_bb(cls, name: str):
        mon_df = rr.lookup_normal_monster_by_name(name)

        return cls(
            mon_df['stab defence'].values[0],
            mon_df['slash defence'].values[0],
            mon_df['crush defence'].values[0],
            mon_df['magic defence'].values[0],
            mon_df['ranged defence'].values[0],
        )


class StatsError(OsrsException):
    pass
