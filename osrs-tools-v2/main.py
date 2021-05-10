# osrs-tools-v2\main.py
from typing import Tuple, Union, List
import math
import pandas as pd
import numpy as np
import random
from bedevere import markov

import resource_reader
import spells

# # Stats


class Stats:

    class Combat:

        def __init__(self, hitpoints: int, attack: int, strength: int, defence: int, magic: int, ranged: int):
            self.hitpoints = hitpoints
            self.attack = attack
            self.strength = strength
            self.defence = defence
            self.magic = magic
            self.ranged = ranged

        @classmethod
        def from_dict(cls, d: dict):
            return cls(
                hitpoints=d['hitpoints'],
                attack=d['attack'],
                strength=d['strength'],
                defence=d['defence'],
                magic=d['magic'],
                ranged=d['ranged']
            )

        @classmethod
        def npc_style_bonus(cls):
            return cls(0, 1, 1, 1, 1, 1)

        def __add__(self, other):
            attributes = [
                'hitpoints',
                'attack',
                'strength',
                'defence',
                'magic',
                'ranged'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) + other.__getattribute__(a)

            return self.from_dict(new_values)

        def __sub__(self, other):
            attributes = [
                'hitpoints',
                'attack',
                'strength',
                'defence',
                'magic',
                'ranged'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) - other.__getattribute__(a)

            return self.from_dict(new_values)

        def __radd__(self, other):
            if other == 0:
                return self
            else:
                return self.__add__(other)

        def __rsub__(self, other):
            if other == 0:
                return self
            else:
                return self.__sub__(other)

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                attributes = [
                    'hitpoints',
                    'attack',
                    'strength',
                    'defence',
                    'magic',
                    'ranged'
                ]

                for a in attributes:
                    if not self.__getattribute__(a) == other.__getattribute__(a):
                        return False

                return True

            else:
                return False

        def __str__(self):
            attributes = [
                'hitpoints',
                'attack',
                'strength',
                'defence',
                'magic',
                'ranged'
            ]

            s = '\ncombat:\n\t' + '\n\t'.join(["{:10}: {:>3}".format(a, self.__getattribute__(a)) for a in attributes])
            return s

    class Aggressive:

        def __init__(self, stab: int, slash: int, crush: int, magic: int, ranged: int, melee_strength: int,
                     ranged_strength: int, magic_strength: Union[float, int]):
            self.stab = stab
            self.slash = slash
            self.crush = crush
            self.magic = magic
            self.ranged = ranged
            self.melee_strength = melee_strength
            self.ranged_strength = ranged_strength
            self.magic_strength = magic_strength

        @classmethod
        def from_dict(cls, d: dict):
            return cls(
                stab=d['stab'],
                slash=d['slash'],
                crush=d['crush'],
                magic=d['magic'],
                ranged=d['ranged'],
                melee_strength=d['melee_strength'],
                ranged_strength=d['ranged_strength'],
                magic_strength=d['magic_strength']
            )

        @classmethod
        def no_bonus(cls):
            zeros = (0,) * 8
            return cls(*zeros)

        def __add__(self, other):
            attributes = [
                'stab',
                'slash',
                'crush',
                'magic',
                'ranged',
                'melee_strength',
                'ranged_strength',
                'magic_strength'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) + other.__getattribute__(a)

            return self.from_dict(new_values)

        def __sub__(self, other):
            attributes = [
                'stab',
                'slash',
                'crush',
                'magic',
                'ranged',
                'melee_strength',
                'ranged_strength',
                'magic_strength'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) - other.__getattribute__(a)

            return self.from_dict(new_values)

        def __radd__(self, other):
            if other == 0:
                return self
            else:
                return self.__add__(other)

        def __rsub__(self, other):
            if other == 0:
                return self
            else:
                return self.__sub__(other)

        def __str__(self):
            attributes = [
                'stab',
                'slash',
                'crush',
                'magic',
                'ranged',
                'melee_strength',
                'ranged_strength',
                'magic_strength'
            ]

            s = '\naggressive:\n\t' + '\n\t'.join(["{:20}: {:>3}".format(a, self.__getattribute__(a)) for a in
                                                   attributes])
            return s

    class Defensive:

        def __init__(self, stab: int, slash: int, crush: int, magic: int, ranged: int):
            self.stab = stab
            self.slash = slash
            self.crush = crush
            self.magic = magic
            self.ranged = ranged

        @classmethod
        def from_dict(cls, d: dict):
            return cls(
                stab=d['stab'],
                slash=d['slash'],
                crush=d['crush'],
                magic=d['magic'],
                ranged=d['ranged']
            )

        @classmethod
        def no_bonus(cls):
            zeros = (0,) * 5
            return cls(*zeros)

        def __add__(self, other):
            attributes = [
                'stab',
                'slash',
                'crush',
                'magic',
                'ranged'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) + other.__getattribute__(a)

            return self.from_dict(new_values)

        def __sub__(self, other):
            attributes = [
                'stab',
                'slash',
                'crush',
                'magic',
                'ranged'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) - other.__getattribute__(a)

            return self.from_dict(new_values)

        def __radd__(self, other):
            if other == 0:
                return self
            else:
                return self.__add__(other)

        def __rsub__(self, other):
            if other == 0:
                return self
            else:
                return self.__sub__(other)

        def __str__(self):
            attributes = [
                'stab',
                'slash',
                'crush',
                'magic',
                'ranged'
            ]

            s = '\ndefensive:\n\t' + '\n\t'.join(["{:20}: {:>3}".format(a, self.__getattribute__(a)) for a in
                                                   attributes])
            return s

    class CurrentCombatBase:

        def __init__(self, hitpoints: int, attack: int, strength: int, magic: int, ranged: int):
            self.hitpoints = hitpoints
            self.attack = attack
            self.strength = strength
            # no defence, implement different per subclass
            self.magic = magic
            self.ranged = ranged

    def __init__(self, combat: Combat, aggressive: Aggressive, defensive: Defensive):
        self.combat = combat
        self.aggressive = aggressive
        self.defensive = defensive

    def unpack(self) -> (Combat, Aggressive, Defensive):
        return self.combat, self.aggressive, self.defensive


class PlayerStats(Stats):

    class Combat(Stats.Combat):
        min_level = 0
        max_level = 99
        max_combat_level = 126

        def __init__(self, hitpoints: int, attack: int, strength: int, defence: int, magic: int, ranged: int,
                     prayer: int, mining: int, slayer: int, agility: int):
            super().__init__(hitpoints, attack, strength, defence, magic, ranged)
            self.prayer = prayer
            self.mining = mining
            self.slayer = slayer
            self.agility = agility

        @classmethod
        def maxed_combat(cls):
            return cls(
                hitpoints=99,
                attack=99,
                strength=99,
                defence=99,
                magic=99,
                ranged=99,
                prayer=99,
                mining=99,
                slayer=99,
                agility=99
            )

        @classmethod
        def no_requirements(cls):
            ones = (1,) * 10
            return cls(*ones)

        @classmethod
        def no_boost(cls):
            zeros = (0,) * 10
            return cls(*zeros)

        @classmethod
        def from_dict(cls, d: dict):
            return cls(
                hitpoints=d['hitpoints'],
                attack=d['attack'],
                strength=d['strength'],
                defence=d['defence'],
                magic=d['magic'],
                ranged=d['ranged'],
                prayer=d['prayer'],
                mining=d['mining'],
                slayer=d['slayer'],
                agility=d['agility']
            )

        @classmethod
        def from_highscores(cls, rsn: str):
            user_hs = resource_reader.lookup_player_highscores(rsn)
            return cls(
                hitpoints=int(user_hs.hitpoints.level),
                attack=int(user_hs.attack.level),
                strength=int(user_hs.strength.level),
                defence=int(user_hs.defence.level),
                magic=int(user_hs.magic.level),
                ranged=int(user_hs.ranged.level),
                prayer=int(user_hs.prayer.level),
                mining=int(user_hs.mining.level),
                slayer=int(user_hs.slayer.level),
                agility=int(user_hs.agility.level)
            )

        def __add__(self, other):
            attributes = [
                'hitpoints',
                'attack',
                'strength',
                'defence',
                'magic',
                'ranged',
                'prayer',
                'mining',
                'slayer',
                'agility'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) + other.__getattribute__(a)

            return self.from_dict(new_values)

        def __sub__(self, other):
            attributes = [
                'hitpoints',
                'attack',
                'strength',
                'defence',
                'magic',
                'ranged',
                'prayer',
                'mining',
                'slayer',
                'agility'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) - other.__getattribute__(a)

            return self.from_dict(new_values)

        def __radd__(self, other):
            if other == 0:
                return self
            else:
                return self.__add__(other)

        def __rsub__(self, other):
            if other == 0:
                return self
            else:
                return self.__sub__(other)

        def __eq__(self, other):

            if isinstance(other, self.__class__):
                attributes = [
                'hitpoints',
                'attack',
                'strength',
                'defence',
                'magic',
                'ranged',
                'prayer',
                'mining',
                'slayer',
                'agility'
            ]

                for a in attributes:
                    if not self.__getattribute__(a) == other.__getattribute__(a):
                        return False

                return True

            else:
                return False

        def __str__(self):
            lvl = '{:2.0f}'
            s = f"hp:  {lvl} atk: {lvl} str: {lvl} def: {lvl} mag: {lvl} rng: {lvl} pry: {lvl} min: {lvl} " \
                f"sly: {lvl} agi: {lvl}"
            return s.format(
                self.hitpoints,
                self.attack,
                self.strength,
                self.defence,
                self.magic,
                self.ranged,
                self.prayer,
                self.mining,
                self.slayer,
                self.agility
            )

    # ill-advised definition, functionally equivalent to Combat unless I implement floats
    class CurrentCombat(Stats.CurrentCombatBase):

        def __init__(self, hitpoints: int, attack: int, strength: int, defence: int, magic: int, ranged: int,
                     prayer: int, mining: int, slayer: int, agility: int):
            super().__init__(hitpoints, attack, strength, magic, ranged)
            self.defence = defence
            self.prayer = prayer
            self.mining = mining
            self.slayer = slayer
            self.agility = agility

        @classmethod
        def from_combat(cls, cb):
            assert isinstance(cb, PlayerStats.Combat)
            return cls(
                hitpoints=cb.hitpoints,
                attack=cb.attack,
                strength=cb.strength,
                defence=cb.defence,
                magic=cb.magic,
                ranged=cb.ranged,
                prayer=cb.prayer,
                mining=cb.mining,
                slayer=cb.slayer,
                agility=cb.agility
            )

        @classmethod
        def from_dict(cls, d: dict):
            return cls(
                hitpoints=d['hitpoints'],
                attack=d['attack'],
                strength=d['strength'],
                defence=d['defence'],
                magic=d['magic'],
                ranged=d['ranged'],
                prayer=d['prayer'],
                mining=d['mining'],
                slayer=d['slayer'],
                agility=d['agility']
            )

        def __add__(self, other):
            attributes = [
                'hitpoints',
                'attack',
                'strength',
                'defence',
                'magic',
                'ranged',
                'prayer',
                'mining',
                'slayer',
                'agility'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) + other.__getattribute__(a)

            return self.from_dict(new_values)

        def __sub__(self, other):
            attributes = [
                'hitpoints',
                'attack',
                'strength',
                'defence',
                'magic',
                'ranged',
                'prayer',
                'mining',
                'slayer',
                'agility'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) - other.__getattribute__(a)

            return self.from_dict(new_values)

        def __radd__(self, other):
            if other == 0:
                return self
            else:
                return self.__add__(other)

        def __rsub__(self, other):
            if other == 0:
                return self
            else:
                return self.__sub__(other)

        def __str__(self):
            lvl = '{:2.0f}'
            s = f"hp:  {lvl} atk: {lvl} str: {lvl} def: {lvl} mag: {lvl} rng: {lvl} pry: {lvl} min: {lvl} " \
                f"sly: {lvl} agi: {lvl}"
            return s.format(
                self.hitpoints,
                self.attack,
                self.strength,
                self.defence,
                self.magic,
                self.ranged,
                self.prayer,
                self.mining,
                self.slayer,
                self.agility
            )

    class StatPrayer:
        _no_prayer = 'no prayer'
        _piety = 'piety'
        _rigour = 'rigour'
        _augury = 'augury'
        _eagle_eye = 'eagle eye'
        _preserve = 'preserve'
        _rapid_restore = 'rapid restore'
        _rapid_heal = 'rapid heal'

        def __init__(self,
                     name: str,
                     drain_rate: float = 0,   # value is 1 point per N seconds as reported on wiki
                     drain_effect: int = 0,
                     attack: float = 1,
                     strength: float = 1,
                     defence: float = 1,
                     ranged_attack: float = 1,
                     ranged_strength: float = 1,
                     magic_attack: float = 1,
                     magic_strength: float = 1,
                     magic_defence: float = 1
                     ):
            self.name = name

            self.drain_rate = drain_rate
            self.drain_effect = drain_effect

            self.attack = attack
            self.strength = strength
            self.defence = defence
            self.ranged_attack = ranged_attack
            self.ranged_strength = ranged_strength
            self.magic_attack = magic_attack
            self.magic_strength = magic_strength
            self.magic_defence = magic_defence

        @classmethod
        def no_boost(cls):
            return cls(name=cls._no_prayer)

        @classmethod
        def piety(cls):
            return cls(
                name=cls._piety,
                drain_rate=1.5,
                drain_effect=24,
                attack=1.2,
                strength=1.23,
                defence=1.25
            )

        @classmethod
        def rigour(cls):
            return cls(
                name=cls._rigour,
                drain_rate=1.5,
                drain_effect=24,
                ranged_attack=1.2,
                ranged_strength=1.23,
                defence=1.25
            )

        @classmethod
        def augury(cls):
            return cls(
                name=cls._augury,
                drain_rate=1.5,
                drain_effect=24,
                magic_attack=1.25,
                magic_defence=1.25,
                defence=1.25
            )

        @classmethod
        def eagle_eye(cls):
            return cls(
                name=cls._eagle_eye,
                drain_rate=3,
                drain_effect=12,
                ranged_attack=1.15
            )

        @classmethod
        def preserve(cls):
            return cls(name=cls._preserve, drain_rate=18, drain_effect=2)

        @classmethod
        def rapid_restore(cls):
            return cls(name=cls._rapid_restore, drain_rate=36, drain_effect=1)

        @classmethod
        def rapid_heal(cls):
            return cls(name=cls._rapid_heal, drain_rate=18, drain_effect=2)

    def __init__(self,
                 combat: Combat,
                 aggressive: Stats.Aggressive,
                 defensive: Stats.Defensive,
                 potion_modifiers: Combat = None,
                 prayer_modifiers: StatPrayer = None):
        super().__init__(combat, aggressive, defensive)
        self.combat = combat
        self.current_combat = PlayerStats.CurrentCombat.from_combat(combat)
        self.potion_modifiers = potion_modifiers if potion_modifiers else PlayerStats.Combat.no_boost()
        self.prayer_modifiers = prayer_modifiers if prayer_modifiers else PlayerStats.StatPrayer.no_boost()

    def unpack(self) -> (Combat, Stats.Aggressive, Stats.Defensive):
        return self.combat, self.aggressive, self.defensive

    @classmethod
    def max_player_stats(cls):
        return cls(
            combat=PlayerStats.Combat.maxed_combat(),
            aggressive=PlayerStats.Aggressive.no_bonus(),
            defensive=PlayerStats.Defensive.no_bonus()
        )


class MonsterStats(Stats):

    class Aggressive(Stats.Aggressive):

        def __init__(self,
                     magic: int,
                     ranged: int,
                     melee_strength: int,
                     ranged_strength: int,
                     magic_strength: int,
                     stab: int = None,
                     slash: int = None,
                     crush: int = None,
                     attack: int = None
                     ):
            super().__init__(
                stab=stab if stab else 0,
                slash=slash if slash else 0,
                crush=crush if crush else 0,
                magic=magic,
                ranged=ranged,
                melee_strength=melee_strength,
                ranged_strength=ranged_strength,
                magic_strength=magic_strength,
            )
            self._attack = attack if attack else 0

        def attack(self, damage_type: str = None) -> int:
            # I think this one liner behaves how it should, error if no _attack and no type provided
            return self._attack if self._attack > 0 else self.__getattribute__(damage_type.lower())

        @classmethod
        def from_dict(cls, d: dict):
            return cls(
                magic=d['magic'],
                ranged=d['ranged'],
                melee_strength=d['melee_strength'],
                ranged_strength=d['ranged_strength'],
                magic_strength=d['magic_strength'],
                stab=d['stab'],
                slash=d['slash'],
                crush=d['crush'],
                attack=d['_attack']
            )

        def __add__(self, other):
            attributes = [
                'magic',
                'ranged',
                'melee_strength',
                'ranged_strength',
                'magic_strength',
                'stab',
                'slash',
                'crush',
                '_attack'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) + other.__getattribute__(a)

            return self.from_dict(new_values)

        def __sub__(self, other):
            attributes = [
                'magic',
                'ranged',
                'melee_strength',
                'ranged_strength',
                'magic_strength',
                'stab',
                'slash',
                'crush',
                '_attack'
            ]
            new_values = {}

            for a in attributes:
                new_values[a] = self.__getattribute__(a) - other.__getattribute__(a)

            return self.from_dict(new_values)

        def __radd__(self, other):
            if other == 0:
                return self
            else:
                return self.__add__(other)

        def __rsub__(self, other):
            if other == 0:
                return self
            else:
                return self.__sub__(other)

    class CurrentCombat:

        def __init__(self, hitpoints: int, attack: int, strength: int, defence: Union[int, float], magic: int,
                     ranged: int):
            self.hitpoints = hitpoints
            self.attack = attack
            self.strength = strength
            self._defence = float(defence)
            self.magic = magic
            self.ranged = ranged

        def reduce_stat_flat(self, stat: str, amount: int):
            current_val = self.__getattribute__(stat)
            self.__setattr__(stat, current_val - amount)

        def reduce_defence_flat(self, amount: int):
            self._defence -= amount

        def reduce_defence_ratio(self, multiplier: float):
            assert 0 < multiplier <= 1
            self._defence *= multiplier

        @classmethod
        def from_combat(cls, cb):
            assert isinstance(cb, MonsterStats.Combat)
            return cls(
                hitpoints=cb.hitpoints,
                attack=cb.attack,
                strength=cb.strength,
                defence=cb.defence,
                magic=cb.magic,
                ranged=cb.ranged
            )

        @property
        def defence(self) -> int:
            return math.ceil(self._defence)

        @defence.setter
        def defence(self, val: Union[float, int]):
            self._defence = float(val)

    def __init__(self, combat: Stats.Combat, aggressive: Aggressive, defensive: Stats.Defensive):
        super(MonsterStats, self).__init__(combat, aggressive, defensive)
        self.aggressive = aggressive
        self.current_combat = MonsterStats.CurrentCombat.from_combat(combat)

    def unpack(self) -> (Stats.Combat, Aggressive, Stats.Defensive):
        return self.combat, self.aggressive, self.defensive

    @classmethod
    def from_bitterkoekje(cls, name: str):
        boss_df = resource_reader.lookup_monster(name)

        combat = MonsterStats.Combat(
            hitpoints=boss_df['hitpoints'].values[0],
            attack=boss_df['attack level'].values[0],
            strength=boss_df['strength level'].values[0],
            defence=boss_df['defence level'].values[0],
            magic=boss_df['magic level'].values[0],
            ranged=boss_df['ranged level'].values[0]
        )
        aggressive = MonsterStats.Aggressive(
            magic=boss_df['magic attack'].values[0],
            ranged=boss_df['ranged attack'].values[0],
            melee_strength=boss_df['melee strength'].values[0],
            ranged_strength=boss_df['ranged strength'].values[0],
            magic_strength=boss_df['magic strength'].values[0],
            stab=boss_df['stab attack'].values[0],
            slash=boss_df['slash attack'].values[0],
            crush=boss_df['crush attack'].values[0],
            attack=boss_df['attack bonus'].values[0]
        )
        defensive = MonsterStats.Defensive(
            stab=boss_df['stab defence'].values[0],
            slash=boss_df['slash defence'].values[0],
            crush=boss_df['crush defence'].values[0],
            magic=boss_df['magic defence'].values[0],
            ranged=boss_df['ranged defence'].values[0]
        )
        return cls(combat, aggressive, defensive)

    @classmethod
    def from_de0(cls, name: str):
        boss_df = resource_reader.lookup_cox_monster_base_stats(name)

        combat = MonsterStats.Combat(
            hitpoints=boss_df['hp'].values[0],
            attack=boss_df['melee'].values[0],
            strength=boss_df['melee'].values[0],
            defence=boss_df['defence'].values[0],
            magic=boss_df['magic'].values[0],
            ranged=boss_df['ranged'].values[0]
        )
        aggressive = MonsterStats.Aggressive(
            magic=boss_df['magic att+'].values[0],
            ranged=boss_df['ranged att+'].values[0],
            melee_strength=boss_df['melee str+'].values[0],
            ranged_strength=boss_df['ranged str+'].values[0],
            magic_strength=boss_df['magic str+'].values[0],
            attack=boss_df['melee att+'].values[0]
        )
        defensive = MonsterStats.Defensive(
            stab=boss_df['stab def+'].values[0],
            slash=boss_df['slash def+'].values[0],
            crush=boss_df['crush def+'].values[0],
            magic=boss_df['magic def+'].values[0],
            ranged=boss_df['ranged def+'].values[0]
        )

        return cls(combat, aggressive, defensive)

    def __str__(self):
        s = ''.join([str(o) for o in self.unpack()])
        return s

# # Styles


class Style:
    # melee style class vars
    stab = 'stab'
    slash = 'slash'
    crush = 'crush'
    melee_damage_types = (stab, slash, crush)

    # ranged style class vars
    ranged = 'ranged'
    ranged_damage_types = (ranged,)

    # magic style class vars
    magic = 'magic'
    magic_damage_types = (magic,)

    # typeless class vars
    typeless = 'typeless'
    typeless_damage_types = (typeless,)

    class StyleError(Exception):

        def __init__(self, *args):
            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            if self.message:
                return 'The following aspect of a Style caused an error: {:}'.format(self.message)
            else:
                return 'A StyleError was raised'

    def __init__(self,
                 name: str,
                 damage_type: str,
                 stance: str,
                 combat_bonus: Stats.Combat,
                 attack_speed_modifier: int = None,
                 attack_range_modifier: int = None
                 ):
        self.name = name
        self.damage_type = damage_type
        self.stance = stance
        self.combat_bonus = combat_bonus
        self.attack_speed_modifier = attack_speed_modifier if attack_speed_modifier else 0
        self.attack_range_modifier = attack_range_modifier if attack_range_modifier else 0


class PlayerStyle(Style):
    # type ambiguous class vars
    accurate = 'accurate'
    longrange = 'longrange'
    defensive = 'defensive'

    # melee style class vars
    aggressive = 'aggressive'
    controlled = 'controlled'
    melee_stances = (accurate, aggressive, defensive, controlled)

    # ranged style class vars
    rapid = 'rapid'
    ranged_stances = (accurate, rapid, longrange)

    # magic style class vars
    standard = 'standard'   # also longrange, shared with ranged
    magic_stances = (accurate, longrange, standard, defensive)

    # style names, flavor text as far as I can tell
    chop = 'chop'
    smash = 'smash'
    block = 'block'
    hack = 'hack'
    lunge = 'lunge'
    swipe = 'swipe'
    pound = 'pound'
    pummel = 'pummel'
    spike = 'spike'
    impale = 'impale'
    jab = 'jab'
    fend = 'fend'
    bash = 'bash'
    reap = 'reap'
    punch = 'punch'
    kick = 'kick'
    flick = 'flick'
    lash = 'lash'
    deflect = 'deflect'
    short_fuse = 'short fuse'
    medium_fuse = 'medium fuse'
    long_fuse = 'long fuse'
    spell = 'spell'
    focus = 'focus'

    chinchompa_style_names = (short_fuse, medium_fuse, long_fuse)

    def __init__(self, name: str, damage_type: str, stance: str):
        attack_speed_modifier = 0
        attack_range_modifier = 0

        if damage_type in Style.melee_damage_types:
            if stance in PlayerStyle.melee_stances:
                if stance == PlayerStyle.accurate:
                    cb = Stats.Combat(0, 3, 0, 0, 0, 0)
                elif stance == PlayerStyle.aggressive:
                    cb = Stats.Combat(0, 0, 3, 0, 0, 0)
                elif stance == PlayerStyle.defensive:
                    cb = Stats.Combat(0, 0, 0, 3, 0, 0)
                elif stance == PlayerStyle.controlled:
                    cb = Stats.Combat(0, 1, 1, 1, 0, 0)
                else:
                    raise Style.StyleError(stance, 'not defined')
            else:
                raise Style.StyleError(stance, 'not in', PlayerStyle.melee_stances)

        elif damage_type in Style.ranged_damage_types:
            if stance in PlayerStyle.ranged_stances:
                if stance == PlayerStyle.accurate:
                    cb = Stats.Combat(0, 0, 0, 0, 0, 3)
                elif stance == PlayerStyle.rapid:
                    cb = Stats.Combat(0, 0, 0, 0, 0, 0)
                    attack_speed_modifier -= 1
                elif stance == PlayerStyle.longrange:
                    cb = Stats.Combat(0, 0, 0, 3, 0, 0)
                    attack_range_modifier += 2
                else:
                    raise Style.StyleError(stance, 'not defined')
            else:
                raise Style.StyleError(stance, 'not in', PlayerStyle.ranged_stances)

        elif damage_type in Style.magic_damage_types:
            if stance in PlayerStyle.magic_stances:
                if stance == PlayerStyle.accurate:
                    cb = Stats.Combat(0, 0, 0, 0, 3, 0)
                elif stance == PlayerStyle.longrange:
                    cb = Stats.Combat(0, 0, 0, 1, 0, 0)
                    attack_range_modifier += 2
                else:
                    raise Style.StyleError(stance, 'not defined')
            else:
                raise Style.StyleError(stance, 'not in', PlayerStyle.magic_stances)

        else:
            raise Style.StyleError(damage_type, 'not defined')

        super(PlayerStyle, self).__init__(
            name=name,
            damage_type=damage_type,
            stance=stance,
            combat_bonus=cb,
            attack_speed_modifier=attack_speed_modifier,
            attack_range_modifier=attack_range_modifier
        )

    def __str__(self):
        s = f"name: {self.name} -- damage_type: {self.damage_type} -- stance: {self.stance}"
        return s


class NpcStyle(Style):
    npc_stance = 'npc'

    def __init__(self,
                 damage_type: str,
                 name: str = None,
                 attack_speed: int = None,
                 ignores_defence: bool = None,
                 ignores_prayer: bool = None,
                 attack_speed_modifier: int = None,
                 attack_range_modifier: int = None):
        super(NpcStyle, self).__init__(
            name=name if name else damage_type,
            damage_type=damage_type,
            stance=self.npc_stance,
            combat_bonus=Stats.Combat.npc_style_bonus(),
            attack_speed_modifier=attack_speed_modifier if attack_speed_modifier else 0,
            attack_range_modifier=attack_range_modifier if attack_range_modifier else 0
        )
        self.attack_speed = attack_speed if attack_speed else 0
        self.ignores_defence = ignores_defence if ignores_defence else False
        self.ignores_prayer = ignores_prayer if ignores_prayer else False

# # Collections of styles


class StyleCollection:

    def __init__(self, name: str, *styles: Style):
        self.name = name
        self.styles = styles


class WeaponStyles(StyleCollection):

    def __init__(self, name: str, *styles: PlayerStyle):
        super(WeaponStyles, self).__init__(name, *styles)
        self.styles = styles

    @classmethod
    def from_weapon_type(cls, weapon_type: str):
        wt = weapon_type.strip().lower()    # clean
        WT = WeaponStyles                     # brevity
        if wt == 'two-handed swords':
            return WT.two_handed_swords()
        elif wt == 'axes':
            return WT.axes()
        elif wt == 'blunt weapons':
            return WT.blunt_weapons()
        elif wt == 'bludgeons':
            return WT.bludgeons()
        elif wt == 'bulwarks':
            return WT.bulwarks()
        elif wt == 'claws':
            return WT.claws()
        elif wt == 'pickaxes':
            return WT.pickaxes()
        elif wt == 'polearms':
            return WT.polearms()
        elif wt == 'scythes':
            return WT.scythes()
        elif wt == 'slash swords':
            return WT.slash_swords()
        elif wt == 'spears':
            return WT.spears()
        elif wt == 'spiked weapons':
            return WT.spiked_weapons()
        elif wt == 'stab swords':
            return WT.stab_swords()
        elif wt == 'unarmed weapons':
            return WT.unarmed_weapons()
        elif wt == 'whips':
            return WT.whips()
        elif wt == 'bow':
            return WT.bow()
        elif wt == 'chinchompas':
            return WT.chinchompas()
        elif wt == 'crossbow':
            return WT.crossbow()
        elif wt == 'thrown':
            return WT.thrown()
        elif wt == 'bladed staves':
            return WT.bladed_staves()
        elif wt == 'powered staves':
            return WT.powered_staves()
        elif wt == 'staves':
            return WT.staves()
        else:
            raise PlayerStyle.StyleError(f'{weapon_type} does not exist or is not defined')

    @classmethod
    def two_handed_swords(cls):
        return cls(
            'two-handed swords',
            PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.smash, PlayerStyle.crush, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive)
        )

    @classmethod
    def axes(cls):
        return cls(
            'axes',
            PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.hack, PlayerStyle.slash, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.smash, PlayerStyle.crush, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive)
        )

    @classmethod
    def blunt_weapons(cls):
        return cls(
            'blunt weapons',
            PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.aggressive)
        )

    @classmethod
    def bludgeons(cls):
        return cls(
            'bludgeons',
            PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.aggressive)
        )

    @classmethod
    def bulwarks(cls):      # TODO: Bulwark stance
        return cls(
            'bulwarks',
            PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.defensive)
        )

    @classmethod
    def claws(cls):
        return cls(
            'claws',
            PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.controlled),
            PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive)
        )

    @classmethod
    def pickaxes(cls):
        return cls(
            'pickaxes',
            PlayerStyle(PlayerStyle.spike, PlayerStyle.stab, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.impale, PlayerStyle.stab, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.smash, PlayerStyle.crush, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.block, PlayerStyle.stab, PlayerStyle.defensive)
        )

    @classmethod
    def polearms(cls):
        return cls(
            'polearms',
            PlayerStyle(PlayerStyle.jab, PlayerStyle.stab, PlayerStyle.controlled),
            PlayerStyle(PlayerStyle.swipe, PlayerStyle.slash, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.fend, PlayerStyle.stab, PlayerStyle.defensive)
        )

    @classmethod
    def scythes(cls):
        return cls(
            'scythes',
            PlayerStyle(PlayerStyle.reap, PlayerStyle.slash, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.jab, PlayerStyle.crush, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive)
        )

    @classmethod
    def slash_swords(cls):
        return cls(
            'slash_swords',
            PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.controlled),
            PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive)
        )

    @classmethod
    def spears(cls):
        return cls(
            'spears',
            PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.controlled),
            PlayerStyle(PlayerStyle.swipe, PlayerStyle.slash, PlayerStyle.controlled),
            PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.controlled),
            PlayerStyle(PlayerStyle.block, PlayerStyle.stab, PlayerStyle.defensive)
        )

    @classmethod
    def spiked_weapons(cls):
        return cls(
            'spiked weapons',
            PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.spike, PlayerStyle.stab, PlayerStyle.controlled),
            PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.defensive)
        )

    @classmethod
    def stab_swords(cls):
        return cls(
            'stab swords',
            PlayerStyle(PlayerStyle.stab, PlayerStyle.stab, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.block, PlayerStyle.stab, PlayerStyle.defensive)
        )

    @classmethod
    def unarmed_weapons(cls):
        return cls(
            'unarmed weapons',
            PlayerStyle(PlayerStyle.punch, PlayerStyle.crush, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.kick, PlayerStyle.crush, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.defensive)
        )

    @classmethod
    def whips(cls):
        return cls(
            'whips',
            PlayerStyle(PlayerStyle.flick, PlayerStyle.slash, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.lash, PlayerStyle.slash, PlayerStyle.controlled),
            PlayerStyle(PlayerStyle.deflect, PlayerStyle.slash, PlayerStyle.defensive)
        )

    @classmethod
    def bow(cls):
        return cls(
            'bow',
            PlayerStyle(PlayerStyle.accurate, PlayerStyle.ranged, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
            PlayerStyle(PlayerStyle.longrange, PlayerStyle.ranged, PlayerStyle.longrange)
        )

    @classmethod
    def chinchompas(cls):
        return cls(
            'chinchompas',
            PlayerStyle(PlayerStyle.short_fuse, PlayerStyle.ranged, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.medium_fuse, PlayerStyle.ranged, PlayerStyle.rapid),
            PlayerStyle(PlayerStyle.long_fuse, PlayerStyle.ranged, PlayerStyle.longrange)
        )

    @classmethod
    def crossbow(cls):
        return cls(
            'crossbow',
            PlayerStyle(PlayerStyle.accurate, PlayerStyle.ranged, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
            PlayerStyle(PlayerStyle.longrange, PlayerStyle.ranged, PlayerStyle.longrange)
        )

    @classmethod
    def thrown(cls):
        return cls(
            'thrown',
            PlayerStyle(PlayerStyle.accurate, PlayerStyle.ranged, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
            PlayerStyle(PlayerStyle.longrange, PlayerStyle.ranged, PlayerStyle.longrange)
        )

    @classmethod
    def bladed_staves(cls):
        return cls(
            'bladed staves',
            PlayerStyle(PlayerStyle.jab, PlayerStyle.stab, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.swipe, PlayerStyle.slash, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.fend, PlayerStyle.crush, PlayerStyle.defensive),
            PlayerStyle(PlayerStyle.spell, PlayerStyle.magic, PlayerStyle.defensive),
            PlayerStyle(PlayerStyle.spell, PlayerStyle.magic, PlayerStyle.standard)
        )

    @classmethod
    def powered_staves(cls):
        return cls(
            'powered staves',
            PlayerStyle(PlayerStyle.accurate, PlayerStyle.magic, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.longrange, PlayerStyle.magic, PlayerStyle.longrange)
        )

    @classmethod
    def staves(cls):
        return cls(
            'staves',
            PlayerStyle(PlayerStyle.bash, PlayerStyle.crush, PlayerStyle.accurate),
            PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.aggressive),
            PlayerStyle(PlayerStyle.focus, PlayerStyle.crush, PlayerStyle.defensive),
            PlayerStyle(PlayerStyle.spell, PlayerStyle.magic, PlayerStyle.defensive),
            PlayerStyle(PlayerStyle.spell, PlayerStyle.magic, PlayerStyle.standard)
        )

    def __str__(self):
        s = f"name: {self.name}\n\t" + '\n\t'.join([str(st) for st in self.styles])
        return s


class NpcAttacks(StyleCollection):

    def __init__(self, name: str, *styles: NpcStyle):
        super(NpcAttacks, self).__init__(name, *styles)

# # Player gear / equipment / stats


class Gear:
    head = 'head'
    cape = 'cape'
    neck = 'neck'
    ammunition = 'ammunition'
    weapon = 'weapon'
    shield = 'shield'
    body = 'body'
    legs = 'legs'
    hands = 'hands'
    feet = 'feet'
    ring = 'ring'

    class GearError(Exception):

        def __init__(self, *args):
            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            if self.message:
                return 'The following aspect of a Gear caused an error: {:}'.format(self.message)
            else:
                return 'A GearError was raised'

    class EquipableError(GearError):

        def __init__(self, gear, stats, *args):
            self.gear = gear
            self.stats = stats

            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            s = 'You cannot equip {:} with the following stats: {:}\t{:}'
            return s.format(self.gear, self.stats, self.message)

    class DuplicateGearError(GearError):

        def __init__(self, search_term, df, *args):
            self.search_term = search_term
            self.df = df
            assert isinstance(df, pd.DataFrame)

            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            s = 'The search term {:} produced the following results:'.format(self.search_term)

            for row in self.df.iterrows():
                s += f'\n\t{row.name.values[0]}'

            return s

    def __init__(
            self,
            name: str,
            aggressive_bonus: Stats.Aggressive,
            defensive_bonus: Stats.Defensive,
            prayer_bonus: int,
            slot: str,
            combat_requirements: PlayerStats.Combat = None,
            degradable: bool = None,
            quest_req: bool = None
    ):
        self.name = name
        self.aggressive_bonus = aggressive_bonus
        self.defensive_bonus = defensive_bonus
        self.prayer_bonus = prayer_bonus
        self.slot = slot
        self.combat_requirements = combat_requirements if combat_requirements else PlayerStats.Combat.no_requirements()
        self.degradable = degradable if degradable else False
        self.quest_req = quest_req if quest_req else False

    @classmethod
    def from_bitterkoekje_bedevere(cls, name: str):
        item_df = resource_reader.lookup_gear(name)

        if len(item_df) == 1:
            return cls(
                name=item_df['name'].values[0],
                aggressive_bonus=Stats.Aggressive(
                    stab=item_df['stab attack'].values[0],
                    slash=item_df['slash attack'].values[0],
                    crush=item_df['crush attack'].values[0],
                    magic=item_df['magic attack'].values[0],
                    ranged=item_df['ranged attack'].values[0],
                    melee_strength=item_df['melee strength'].values[0],
                    ranged_strength=item_df['ranged strength'].values[0],
                    magic_strength=item_df['magic damage'].values[0]
                ),
                defensive_bonus=Stats.Defensive(
                    stab=item_df['stab defence'].values[0],
                    slash=item_df['slash defence'].values[0],
                    crush=item_df['crush defence'].values[0],
                    magic=item_df['magic defence'].values[0],
                    ranged=item_df['ranged defence'].values[0]
                ),
                prayer_bonus=item_df['prayer'].values[0],
                slot=item_df['slot'].values[0],
                combat_requirements=PlayerStats.Combat(
                    hitpoints=item_df['hitpoints level req'].values[0],
                    attack=item_df['attack level req'].values[0],
                    strength=item_df['strength level req'].values[0],
                    defence=item_df['defence level req'].values[0],
                    magic=item_df['magic level req'].values[0],
                    ranged=item_df['ranged level req'].values[0],
                    prayer=1,   # TODO: Prayer req item_df['prayer level req'].values[0],
                    mining=item_df['mining level req'].values[0],
                    slayer=item_df['slayer level req'].values[0],
                    agility=item_df['agility level req'].values[0]
                ),
                degradable=item_df['degradable'].values[0],
                quest_req=item_df['quest req'].values[0]
            )

        else:
            raise Gear.DuplicateGearError(name, item_df)

    @classmethod
    def empty_slot(cls, slot: str):
        return cls(
            name='empty ' + slot,
            aggressive_bonus=PlayerStats.Aggressive.no_bonus(),
            defensive_bonus=PlayerStats.Defensive.no_bonus(),
            prayer_bonus=0,
            slot=slot
        )

    def __str__(self):
        return "{:} ({:} slot)".format(self.name, self.slot)


class Weapon(Gear):

    class WeaponError(Exception):

        def __init__(self, obj, *args):
            self.obj = obj

            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            if self.message:
                return 'The following aspect of a {:} caused an error: {:}'.format(type(self.obj), self.message)
            else:
                return 'A WeaponError was raised from a {:}'.format(type(self.obj))

    def __init__(
            self,
            name: str,
            aggressive_bonus: Stats.Aggressive,
            defensive_bonus: Stats.Defensive,
            prayer_bonus: int,
            attack_speed: int,
            attack_range: int,
            two_handed: bool,
            weapon_styles: WeaponStyles,
            combat_requirements: PlayerStats.Combat = None,
            degradable: bool = None,
            quest_req: bool = None
    ):
        super().__init__(name, aggressive_bonus, defensive_bonus, prayer_bonus, Gear.weapon, combat_requirements,
                         degradable, quest_req)
        self._attack_speed = attack_speed
        self._attack_range = attack_range
        self.two_handed = two_handed
        self.weapon_styles = weapon_styles
        self._active_style = self.weapon_styles.styles[0]
        self._autocast = None

    def choose_style_by_name(self, name: str):

        for s in self.weapon_styles.styles:
            if s.name == name:
                # if self.weapon_styles.name == 'staves' and name in (PlayerStyle.standard, PlayerStyle.defensive):
                #     raise PlayerStyle.StyleError('To choose an autocast style use Weapon.choose_autocast method')

                self.active_style = s
                return

        text = f'{name} is not a style for {self.name} with available styles:'
        raise Style.StyleError(text, *self.weapon_styles.styles)

    def choose_autocast(self, style_name: str, spell: spells.Spell):
        self.choose_style_by_name(style_name)
        self._autocast = spell


    @property
    def autocast(self) -> Union[None, spells.Spell]:
        return self._autocast

    @property
    def active_style(self) -> PlayerStyle:
        return self._active_style

    @active_style.setter
    def active_style(self, style: PlayerStyle):
        if style in self.weapon_styles.styles:
            self._active_style = style
        else:
            text = f"{style.name} is not a style for {self.name} with available styles: "
            raise Style.StyleError(text, *self.weapon_styles.styles)

    @property
    def attack_speed(self) -> int:
        return self._attack_speed + self.active_style.attack_speed_modifier

    @property
    def attack_range(self) -> int:
        return self._attack_range + self.active_style.attack_range_modifier

    @classmethod
    def unarmed(cls):
        return cls(
            'unarmed',
            Stats.Aggressive.no_bonus,
            Stats.Defensive.no_bonus,
            0,
            4,
            1,
            False,
            WeaponStyles.unarmed_weapons
        )

    @classmethod
    def from_bitterkoekje_bedevere(cls, name: str):
        default_attack_range = 0
        item_df = resource_reader.lookup_gear(name)

        assert item_df['slot'].values[0] == 'weapon'
        assert item_df['weapon type'].values[0]

        if len(item_df) == 1:
            return cls(
                name=item_df['name'].values[0],
                aggressive_bonus=Stats.Aggressive(
                    stab=item_df['stab attack'].values[0],
                    slash=item_df['slash attack'].values[0],
                    crush=item_df['crush attack'].values[0],
                    magic=item_df['magic attack'].values[0],
                    ranged=item_df['ranged attack'].values[0],
                    melee_strength=item_df['melee strength'].values[0],
                    ranged_strength=item_df['ranged strength'].values[0],
                    magic_strength=item_df['magic damage'].values[0]
                ),
                defensive_bonus=Stats.Defensive(
                    stab=item_df['stab defence'].values[0],
                    slash=item_df['slash defence'].values[0],
                    crush=item_df['crush defence'].values[0],
                    magic=item_df['magic defence'].values[0],
                    ranged=item_df['ranged defence'].values[0]
                ),
                prayer_bonus=item_df['prayer'].values[0],
                attack_speed=item_df['attack speed'].values[0],
                attack_range=default_attack_range,
                two_handed=item_df['two handed'].values[0],
                weapon_styles=WeaponStyles.from_weapon_type(item_df['weapon type'].values[0]),
                combat_requirements=PlayerStats.Combat(
                    hitpoints=item_df['hitpoints level req'].values[0],
                    attack=item_df['attack level req'].values[0],
                    strength=item_df['strength level req'].values[0],
                    defence=item_df['defence level req'].values[0],
                    magic=item_df['magic level req'].values[0],
                    ranged=item_df['ranged level req'].values[0],
                    prayer=1,   # TODO: Fix sheet to have prayer reqs - item_df['prayer level req'].values[0],
                    mining=item_df['mining level req'].values[0],
                    slayer=item_df['slayer level req'].values[0],
                    agility=item_df['agility level req'].values[0]
                ),
                degradable=item_df['degradable'].values[0],
                quest_req=item_df['quest req'].values[0]
            )

        else:
            raise Gear.DuplicateGearError(name, item_df)


class SpecialWeapon(Weapon):

    def __init__(
            self,
            name: str,
            aggressive_bonus: Stats.Aggressive,
            defensive_bonus: Stats.Defensive,
            prayer_bonus: int,
            attack_speed: int,
            attack_range: int,
            two_handed: bool,
            weapon_styles: WeaponStyles,
            special_accuracy_modifier: float,
            special_damage_modifier_1: float,
            special_damage_modifier_2: float,
            special_defence_roll: str = None,
            combat_requirements: PlayerStats.Combat = None,
            degradable: bool = None,
            quest_req: bool = None
    ):
        super().__init__(name, aggressive_bonus, defensive_bonus, prayer_bonus, attack_speed, attack_range, two_handed,
                         weapon_styles, combat_requirements, degradable, quest_req)
        self.special_accuracy_modifier = special_accuracy_modifier
        self.special_damage_modifier_1 = special_damage_modifier_1
        self.special_damage_modifier_2 = special_damage_modifier_2
        self.special_defence_roll = special_defence_roll

    @classmethod
    def from_bitterkoekje_bedevere(cls, name: str):
        default_attack_range = 0
        item_df = resource_reader.lookup_gear(name)

        assert item_df['slot'].values[0] == 'weapon'
        assert item_df['weapon type'].values[0]

        if len(item_df) == 1:
            return cls(
                name=item_df['name'].values[0],
                aggressive_bonus=Stats.Aggressive(
                    stab=item_df['stab attack'].values[0],
                    slash=item_df['slash attack'].values[0],
                    crush=item_df['crush attack'].values[0],
                    magic=item_df['magic attack'].values[0],
                    ranged=item_df['ranged attack'].values[0],
                    melee_strength=item_df['melee strength'].values[0],
                    ranged_strength=item_df['ranged strength'].values[0],
                    magic_strength=item_df['magic damage'].values[0]
                ),
                defensive_bonus=Stats.Defensive(
                    stab=item_df['stab defence'].values[0],
                    slash=item_df['slash defence'].values[0],
                    crush=item_df['crush defence'].values[0],
                    magic=item_df['magic defence'].values[0],
                    ranged=item_df['ranged defence'].values[0]
                ),
                prayer_bonus=item_df['prayer'].values[0],
                attack_speed=item_df['attack speed'].values[0],
                attack_range=default_attack_range,
                two_handed=item_df['two handed'].values[0],
                weapon_styles=WeaponStyles.from_weapon_type(item_df['weapon type'].values[0]),
                special_accuracy_modifier=1 + item_df['special accuracy'].values[0],
                special_damage_modifier_1=1 + item_df['special damage 1'].values[0],
                special_damage_modifier_2=1 + item_df['special damage 2'].values[0],
                special_defence_roll=item_df['special defence roll'].values[0],
                combat_requirements=PlayerStats.Combat(
                    hitpoints=item_df['hitpoints level req'].values[0],
                    attack=item_df['attack level req'].values[0],
                    strength=item_df['strength level req'].values[0],
                    defence=item_df['defence level req'].values[0],
                    magic=item_df['magic level req'].values[0],
                    ranged=item_df['ranged level req'].values[0],
                    prayer=1,   # TODO: Fix sheet to have prayer reqs - item_df['prayer level req'].values[0],
                    mining=item_df['mining level req'].values[0],
                    slayer=item_df['slayer level req'].values[0],
                    agility=item_df['agility level req'].values[0]
                ),
                degradable=item_df['degradable'].values[0],
                quest_req=item_df['quest req'].values[0]
            )

        else:
            raise Gear.DuplicateGearError(name, item_df)


class Equipment:

    class EquipmentError(Exception):

        def __init__(self, *args):
            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            if self.message:
                return 'The following gear caused an error: {:}'.format(self.message)
            else:
                return 'An EquipmentError was raised'

    class DuplicateEquipmentError(EquipmentError):

        def __init__(self, slot: str, *args):
            self.slot = slot
            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            if self.message:
                return 'The following items were registered to the {:} slot: {:}'.format(self.slot, self.message)
            else:
                return 'A DuplicateEquipmentError was raised'

    class TwoHandedError(EquipmentError):

        def __init__(self, obj, *args):
            self.obj = obj

            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            if self.message:
                return 'The weapon: {:} caused an error: {:}'.format(type(self.obj), self.message)
            else:
                return 'A TwoHandedError was raised from a {:}'.format(type(self.obj))

    def __init__(self, *gear: Union[Gear, Weapon, SpecialWeapon]):
        self.head = Gear.empty_slot(Gear.head)
        self.cape = Gear.empty_slot(Gear.cape)
        self.neck = Gear.empty_slot(Gear.neck)
        self.ammunition = Gear.empty_slot(Gear.ammunition)
        self.weapon: Weapon = Weapon.unarmed
        self.shield = Gear.empty_slot(Gear.shield)
        self.body = Gear.empty_slot(Gear.body)
        self.legs = Gear.empty_slot(Gear.legs)
        self.hands = Gear.empty_slot(Gear.hands)
        self.feet = Gear.empty_slot(Gear.feet)
        self.ring = Gear.empty_slot(Gear.ring)

        for g in gear:

            if isinstance(g, Weapon):
                self.weapon = g
            elif isinstance(g, Gear):
                try:
                    found_gear = self.__getattribute__(g.slot)

                    if "empty" in found_gear.name:
                        self.__setattr__(g.slot, g)
                    else:
                        # a found attribute means duplicate gear, not allowed for initial construction
                        raise Equipment.DuplicateEquipmentError(g.slot, g, found_gear)

                except AttributeError:
                    raise Equipment.EquipmentError(g, g.slot)

        self.compatibility_check()

    def compatibility_check(self):
        # two handed check
        if self.weapon.two_handed and "empty" not in self.shield.name:
            raise Equipment.TwoHandedError(self.weapon, self.weapon, 'and', self.shield)

        gear = self.get_gear()

        if not len(set([g.slot for g in gear if isinstance(g, Gear)])) == len(gear):
            pass    # TODO: Fix this to allow for nonetypes raise Equipment.DuplicateEquipmentError('unknown', str(self))

        if not self.weapon:
            self.weapon = Weapon.unarmed

    def equip(self, *gear: Gear):

        for g in gear:
            if isinstance(g, Weapon):   # redundant in including this except for IDE type familiarity / convenience
                self.weapon = g
            else:
                self.__setattr__(g.slot, g)

        self.compatibility_check()

    def unequip(self, *gear: Union[Gear, str]):

        for g in gear:
            try:
                if isinstance(g, Gear):
                    self.__setattr__(g.slot, Gear.empty_slot(g.slot))
                elif isinstance(g, str):
                    self.__setattr__(g, Gear.empty_slot(g))
                else:
                    raise Equipment.EquipmentError(g)

            except AttributeError:
                raise Equipment.EquipmentError(g)

        self.compatibility_check()

    def get_gear(self) -> List[Union[Gear, Weapon, SpecialWeapon]]:
        gear = [
            self.head,
            self.cape,
            self.neck,
            self.ammunition,
            self.weapon,
            self.shield,
            self.body,
            self.legs,
            self.hands,
            self.feet,
            self.ring
        ]
        return gear

    def aggressive_bonus(self) -> Stats.Aggressive:
        return sum([g.aggressive_bonus for g in self.get_gear() if isinstance(g, Gear)])

    def defensive_bonus(self) -> Stats.Defensive:
        return sum([g.defensive_bonus for g in self.get_gear() if isinstance(g, Gear)])

    def prayer_bonus(self) -> int:
        return sum([g.prayer_bonus for g in self.get_gear() if isinstance(g, Gear)])

    def wearing(self, **kwargs):
        bools = []

        for kw in kwargs:
            g = self.__getattribute__(kw)
            if isinstance(g, Gear):
                bools.append(g.name == kwargs[kw])
            else:
                bools.append(False)

        return all(bools)

    def void_set(self) -> bool:
        return self.normal_void_set() or self.elite_void_set()

    def normal_void_set(self) -> bool:
        return self.wearing(
            head='void knight helm',
            body='void knight top',
            legs='void knight robe',
            hands='void knight gloves'
        )

    def elite_void_set(self) -> bool:
        return self.wearing(
            head='void knight helm',
            body='elite void top',
            legs='elite void robe',
            hands='void knight gloves'
        )

    def dharok_set(self) -> bool:
        return self.wearing(
            head="dharok's greataxe",
            body="dharok's platebody",
            legs="dharok's platelegs",
            weapon="dharok's greataxe"
        )

    def inquisitor_set(self) -> bool:
        return self.wearing(
            head="inquisitor's great helm",
            body="inquisitor's hauberk",
            legs="inquisitor's plateskirt"
        )

    def justiciar_set(self) -> bool:
        return self.wearing(
            head="justiciar faceguard",
            body="justiciar chestguard",
            legs="justiciar legguard"
        )

    def obsidian_armor_set(self) -> bool:
        # weapon_bool = self.weapon.name in ["obsidian dagger", "obsidian mace", "obsidian maul", "obsidian sword"]
        return self.wearing(
            head="obsidian helm",
            body="obsidian platebody",
            legs="obsidian platelegs"
        )

    def obsidian_weapon(self) -> bool:
        qualifying_weapons = [
            "obsidian dagger",
            "obsidian mace",
            "obsidian maul",
            "obsidian sword"
        ]
        return self.weapon.name in qualifying_weapons

    def crystal_armor_set(self) -> bool:
        return self.wearing(
            head="crystal helm",
            body="crystal body",
            legs="crystal legs"
        )

    def graceful_set(self) -> bool:
        return self.wearing(
            head="graceful hood",
            body="graceful top",
            legs="graceful legs",
            hands="graceful gloves",
            feet="graceful boots",
            cape="graceful cape"
        )

    def __str__(self):
        gear = self.get_gear()
        s = ''.join(["Equipment:", "\n\t{:}"*len(gear)])
        return s.format(*gear)


# Characters / Players / Monsters / Cox Monsters

class Character:

    def __init__(
            self,
            name: str,
            stats: Stats,
    ):
        self.name = name
        self.stats = stats

    def damage(self, amount: int):
        pass

    def heal(self, amount: int, overheal: bool = False):
        # accidentally updated signature this might be messed up whoops!
        pass

    def reset_current_stats(self):
        pass

    @staticmethod
    def effective_accuracy_level(invisible_level: int, style_bonus: int, void_modifier: float = 1):
        stance_level = invisible_level + style_bonus + 8
        void_level = math.floor(void_modifier * stance_level)
        effective_level = void_level

        return effective_level

    @staticmethod
    def effective_strength_level(invisible_level: int, style_bonus: int, void_modifier: float = 1):
        stance_level = invisible_level + style_bonus
        void_level = math.floor(void_modifier * stance_level)
        effective_level = void_level

        return effective_level

    @staticmethod
    def maximum_roll(effective_level: int, aggressive_or_defensive_bonus: int,
                     roll_modifier: Union[float, List[float]] = None) -> int:
        """

        :param effective_level: A function of stat, (potion), prayers, other modifiers, and stance
        :param aggressive_or_defensive_bonus: The bonus a player gets from gear or monsters have innately
        :param roll_modifier: A direct multiplier on the roll, such as a BGS special attack.
        :return:
        """

        if isinstance(roll_modifier, list):
            modifier_steps = roll_modifier
        elif isinstance(roll_modifier, float):
            modifier_steps = [roll_modifier]
        else:
            modifier_steps = []

        roll = effective_level * (aggressive_or_defensive_bonus + 64)

        for step in modifier_steps:
            roll = math.floor(roll * step)

        return roll

    @staticmethod
    def accuracy(offensive_roll: int, defensive_roll: int) -> float:
        """

        :param offensive_roll: The maximum offensive roll of the attacker.
        :param defensive_roll: The maximum defensive roll of the defender.
        :return: Accuracy, or the chance that an attack is successful. This is NOT the chance to deal 0 damage.
        """
        if offensive_roll > defensive_roll:
            return 1 - (defensive_roll + 2) / (2 * (offensive_roll + 1))
        else:
            return offensive_roll / (2 * (defensive_roll + 1))

    @staticmethod
    def base_damage(effective_strength_level: int, strength_bonus: int) -> float:
        """

        :param effective_strength_level: A function of strength, (potions), prayer, and stance.
        :param strength_bonus: damage-type-dependent bonus value, monsters have innately and players get from gear.
        :return: A float that represents basically the max hit except for special attacks.
        """
        term_1 = 1.3 + effective_strength_level / 10 + strength_bonus / 80
        term_2 = effective_strength_level * strength_bonus / 640
        base_damage = term_1 + term_2

        return base_damage

    @staticmethod
    def _max_hit(base_damage: float, damage_modifier: Union[float, List[float]] = None) -> int:

        if isinstance(damage_modifier, list):
            modifier_steps = damage_modifier
        elif isinstance(damage_modifier, float):
            modifier_steps = [damage_modifier]
        else:
            modifier_steps = []

        max_hit = math.floor(base_damage)

        for step in modifier_steps:
            max_hit = math.floor(max_hit * step)

        return max_hit


class Player(Character):

    def __init__(self, name: str, stats: PlayerStats, equipment: Equipment, on_task: bool = True):
        super().__init__(name, stats)
        self.equipment = equipment
        self.weapon = self.equipment.weapon
        assert isinstance(self.weapon, Weapon)
        self.stats = stats
        self.on_task = on_task

        self.compatibility_check()
        self._charge_spell = False
        self._weight = 0
        self._run_energy = 10000    # this is 100% run energy
        self._stamina_potion_active = False

    def compatibility_check(self):
        self.equipment.compatibility_check()
        gear = self.equipment.get_gear()
        attributes = [
            'agility',
            'mining',
            'prayer',
            'slayer',
            'attack',
            'defence',
            'hitpoints',
            'magic',
            'ranged',
            'strength'
        ]

        for g in gear:
            if not isinstance(g, Gear):
                continue

            reqs = g.combat_requirements
            vals = self.stats.combat

            for a in attributes:
                v = vals.__getattribute__(a)
                r = reqs.__getattribute__(a)

                if v < r:
                    raise Gear.EquipableError(g, vals, 'offending comparison (val / req)', v, r)

    def damage(self, amount: int):
        current_hp = self.stats.current_combat.hitpoints
        minimum_hp = 0
        new_hp = max([minimum_hp, current_hp - amount])
        self.stats.current_combat.hitpoints = new_hp

    def heal(self, amount, overheal=False):
        current_hp = self.stats.current_combat.hitpoints

        if overheal:
            new_hp = max([current_hp, self.stats.combat.hitpoints + amount])
        else:
            maximum_hp = self.stats.combat.hitpoints
            new_hp = min([maximum_hp, current_hp + amount])

        self.stats.current_combat.hitpoints = new_hp

    def reset_current_stats(self):
        self.stats.current_combat = PlayerStats.CurrentCombat.from_combat(self.stats.combat)

    def reset_potion_modifiers(self):
        self.stats.potion_modifiers = PlayerStats.Combat.no_boost()

    def reset_prayers(self):
        self.stats.prayer_modifiers = self.stats.StatPrayer.no_boost()

    def pray(self, prayer: Union[PlayerStats.StatPrayer, str]):
        self.reset_prayers()

        if isinstance(prayer, PlayerStats.StatPrayer):
            self.stats.prayer_modifiers = prayer
        else:
            if prayer == 'piety':
                self.stats.prayer_modifiers = PlayerStats.StatPrayer.piety()
            elif prayer == 'rigour':
                self.stats.prayer_modifiers = PlayerStats.StatPrayer.rigour()
            elif prayer == 'augury':
                self.stats.prayer_modifiers = PlayerStats.StatPrayer.augury()
            else:
                raise Exception('unrecognized prayer string', prayer)

    def tick_down_potion_modifiers(self, n: int = 1):

        def tick_pot(pot_bonus: int) -> int:
            return max([pot_bonus - n, 0])

        pm = self.stats.potion_modifiers
        pm.attack = tick_pot(pm.attack)
        pm.strength = tick_pot(pm.strength)
        pm.defence = tick_pot(pm.defence)
        pm.magic = tick_pot(pm.magic)
        pm.ranged = tick_pot(pm.ranged)
        pm.mining = tick_pot(pm.mining)
        pm.slayer = tick_pot(pm.slayer)
        pm.agility = tick_pot(pm.agility)

    def regen_stats(self):
        # def tick_stat(current_stat: int, max_stat: int) -> int:
        #     return min([current_stat + 1, max_stat])
        #
        # cb = self.stats.combat
        # ccb = self.stats.current_combat
        # ccb.attack = tick_stat(ccb.attack, cb.attack)
        # ccb.strength = tick_stat(ccb.strength, cb.strength)
        # ccb.defence = tick_stat(ccb.defence, cb.defence)
        # ccb.magic = tick_stat(ccb.magic, cb.magic)
        # ccb.ranged = tick_stat(ccb.ranged, cb.ranged)
        # ccb.mining = ccb
        pass

    def super_combat_potion(self):
        cb = self.stats.combat
        pm = self.stats.potion_modifiers

        def scb_stat(x: int):
            return 5 + math.floor(x * 0.15)

        pm.attack = scb_stat(cb.attack)
        pm.strength = scb_stat(cb.strength)
        pm.defence = scb_stat(cb.defence)

    def zamorak_brew(self):
        # TODO: Test
        cb = self.stats.combat
        ccb = self.stats.current_combat
        pm = self.stats.potion_modifiers

        pm.attack = 2 + math.floor(0.2 * ccb.attack)
        pm.strength = 2 + math.floor(0.12 * ccb.strength)
        pm.defence = -1 * (2 + math.floor(0.10 * ccb.defence))
        self.damage(math.floor(0.12 * ccb.hitpoints))

    def ranging_potion(self):
        cb = self.stats.combat
        pm = self.stats.potion_modifiers

        pm.ranged = 4 + math.floor(cb.ranged * 0.10)

    def bastion_potion(self):
        cb = self.stats.combat
        pm = self.stats.potion_modifiers

        pm.ranged = 4 + math.floor(cb.ranged * 0.10)
        pm.defence = 5 + math.floor(cb.defence * 0.15)

    def imbued_heart(self):
        cb = self.stats.combat
        pm = self.stats.potion_modifiers

        pm.magic = 1 + math.floor(cb.magic * 0.10)

    def overload(self):
        cb = self.stats.combat
        pm = self.stats.potion_modifiers

        def ovl_stat(x: int):
            return 6 + math.floor(x * 0.16)

        pm.attack = ovl_stat(cb.attack)
        pm.strength = ovl_stat(cb.strength)
        pm.defence = ovl_stat(cb.defence)
        pm.ranged = ovl_stat(cb.ranged)
        pm.magic = ovl_stat(cb.magic)

    def xerics_aid(self):
        cb = self.stats.combat
        pm = self.stats.potion_modifiers

        def cb_boost(x: int):
            return 4 + math.floor(x * 0.10)

        def_boost = 5 + math.floor(cb.defence * 0.20)
        atk_boost = cb_boost(cb.attack)
        str_boost = cb_boost(cb.strength)
        rng_boost = cb_boost(cb.ranged)
        mag_boost = cb_boost(cb.magic)

        self.heal(5 + math.floor(cb.hitpoints * 0.15), overheal=True)
        pm.defence = min([pm.defence - def_boost, 1])
        pm.attack = min([pm.attack - atk_boost, 1])
        pm.strength = min([pm.strength - str_boost, 1])
        pm.ranged = min([pm.ranged - rng_boost, 1])
        pm.magic = min([pm.magic - mag_boost, 1])

    def cast_charge(self):
        self._charge_spell = True

    @property
    def charged(self):
        return self._charge_spell

    @charged.setter
    def charged(self, state: bool):
        self._charge_spell = state

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value: int):
        self._weight = value

    @property
    def run_energy(self):
        return self._run_energy

    @run_energy.setter
    def run_energy(self, value: int):
        self._run_energy = min([max([0, value]), 10000])    # clamp(0, 10 000)

    def energy_lost(self, ticks: int = 1):
        clamped_weight = min([max([0, self.weight]), 64])
        loss_base = 67 + math.floor((67*clamped_weight)/64)

        if self.stamina:
            loss_per_tick = math.floor(0.3 * loss_base)
        elif self.equipment.wearing(ring='ring of endurance'):
            loss_per_tick = math.floor(0.85 * loss_base)
        else:
            loss_per_tick = loss_base

        loss = loss_per_tick * ticks
        return loss

    def energy_recovered(self, ticks: int = 1):
        gain_base = math.floor(self.stats.combat.agility / 6) + 8

        if self.equipment.graceful_set():
            gain_per_tick = math.floor(1.3 * gain_base)
        else:
            gain_per_tick = gain_base

        gain = gain_per_tick * ticks
        return gain

    def run(self, ticks: int):
        loss = self.energy_lost(ticks=ticks)
        self.run_energy = self.run_energy - loss

    def rest(self, ticks: int):
        gain = self.energy_recovered(ticks=ticks)
        self.run_energy = self.run_energy + gain

    @property
    def stamina(self):
        return self._stamina_potion_active

    @stamina.setter
    def stamina(self, value: bool):
        self._stamina_potion_active = value

    def drink_stamina_potion(self):
        self.stamina = True
        self.run_energy = self.run_energy + 2000    # stamina restores 20%

    @property
    def combat_level(self):
        cb = self.stats.combat
        base_level = (1/4) * (cb.defence + cb.hitpoints + math.floor(cb.prayer / 2))
        melee_level = (13/40) * (cb.attack + cb.strength)
        magic_level = (13/40) * (math.floor(cb.magic / 2) + cb.magic)
        ranged_level = (13/40) * (math.floor(cb.ranged / 2) + cb.ranged)
        type_level = max([melee_level, magic_level, ranged_level])
        combat_level = math.floor(base_level + type_level)
        return combat_level

    @property
    def visible_attack(self):
        return self.stats.current_combat.attack + self.stats.potion_modifiers.attack

    @property
    def visible_strength(self):
        return self.stats.current_combat.strength + self.stats.potion_modifiers.strength

    @property
    def visible_defence(self):
        return self.stats.current_combat.defence + self.stats.potion_modifiers.defence

    @property
    def visible_magic(self):
        return self.stats.current_combat.magic + self.stats.potion_modifiers.magic

    @property
    def visible_ranged(self):
        return self.stats.current_combat.ranged + self.stats.potion_modifiers.ranged

    @property
    def visible_mining(self):
        return self.stats.current_combat.mining + self.stats.potion_modifiers.mining

    @property
    def invisible_attack(self):
        return math.floor(self.visible_attack * self.stats.prayer_modifiers.attack)

    @property
    def invisible_strength(self):
        return math.floor(self.visible_strength * self.stats.prayer_modifiers.strength)

    @property
    def invisible_defence(self):
        return math.floor(self.visible_defence * self.stats.prayer_modifiers.defence)

    @property
    def invisible_magic(self):
        return math.floor(self.visible_magic * self.stats.prayer_modifiers.magic_attack)

    @property
    def invisible_ranged_attack(self):
        return math.floor(self.visible_ranged * self.stats.prayer_modifiers.ranged_attack)

    @property
    def invisible_ranged_strength(self):
        return math.floor(self.visible_ranged * self.stats.prayer_modifiers.ranged_strength)

    @property
    def effective_attack_level(self) -> int:
        assert isinstance(self.weapon, Weapon)
        style_bonus = self.weapon.active_style.combat_bonus.attack
        void_atk_lvl_mod, _ = self._void_modifiers()

        return Character.effective_accuracy_level(self.invisible_attack, style_bonus, void_atk_lvl_mod)

    @property
    def effective_melee_strength_level(self) -> int:
        assert isinstance(self.weapon, Weapon)
        style_bonus = self.weapon.active_style.combat_bonus.strength
        _, void_str_lvl_mod = self._void_modifiers()

        return Character.effective_strength_level(self.invisible_strength, style_bonus, void_str_lvl_mod)

    @property
    def effective_defence_level(self) -> int:
        assert isinstance(self.weapon, Weapon)
        style_bonus = self.weapon.active_style.combat_bonus.defence
        return Character.effective_accuracy_level(self.invisible_defence, style_bonus)

    @property
    def effective_ranged_attack_level(self) -> int:
        assert isinstance(self.weapon, Weapon)
        style_bonus = self.weapon.active_style.combat_bonus.ranged
        void_rng_atk_lvl_mod, _ = self._void_modifiers()

        return Character.effective_accuracy_level(self.invisible_ranged_attack, style_bonus, void_rng_atk_lvl_mod)

    @property
    def effective_ranged_strength_level(self) -> int:
        assert isinstance(self.weapon, Weapon)
        style_bonus = self.weapon.active_style.combat_bonus.ranged
        _, void_rng_str_lvl_mod = self._void_modifiers()

        return Character.effective_strength_level(self.invisible_ranged_strength, style_bonus, void_rng_str_lvl_mod)

    @property
    def effective_magic_level(self) -> int:
        assert isinstance(self.weapon, Weapon)
        style_bonus = self.weapon.active_style.combat_bonus.magic
        void_mag_atk_lvl_mod, _ = self._void_modifiers()

        return Character.effective_accuracy_level(self.invisible_magic, style_bonus, void_mag_atk_lvl_mod)

    def _void_modifiers(self) -> (float, float):
        weapon = self.equipment.weapon
        assert isinstance(weapon, Weapon)

        if self.equipment.normal_void_set():
            if weapon.active_style.damage_type in Style.melee_damage_types:
                void_attack_level_modifier = 1.1
                void_strength_level_modifier = 1.1
            elif weapon.active_style.damage_type in Style.ranged_damage_types:
                void_attack_level_modifier = 1.1
                void_strength_level_modifier = 1.1
            elif weapon.active_style.damage_type in Style.magic_damage_types:
                void_attack_level_modifier = 1.45
                void_strength_level_modifier = 1
            else:
                raise Style.StyleError(f"{weapon.active_style.damage_type} is not a recognized damage type")

        elif self.equipment.elite_void_set():
            if weapon.active_style.damage_type in Style.melee_damage_types:
                void_attack_level_modifier = 1.1
                void_strength_level_modifier = 1.1
            elif weapon.active_style.damage_type in Style.ranged_damage_types:
                void_attack_level_modifier = 1.1
                void_strength_level_modifier = 1.125
            elif weapon.active_style.damage_type in Style.magic_damage_types:
                void_attack_level_modifier = 1.45
                void_strength_level_modifier = 1.025
            else:
                raise Style.StyleError(f"{weapon.active_style.damage_type} is not a recognized damage type")
        else:
            void_attack_level_modifier = 1
            void_strength_level_modifier = 1

        return void_attack_level_modifier, void_strength_level_modifier

    def _salve_modifier(self, other) -> (float, float):
        assert isinstance(other, Monster)

        if Monster.undead in other.attributes:
            if self.equipment.wearing(neck='salve (i)'):
                modifier = 7/6
            elif self.equipment.wearing(neck='salve (ei)'):
                modifier = 1.2
            else:
                modifier = 1
        else:
            modifier = 1

        salve_arm = modifier
        salve_dm = modifier
        return salve_arm, salve_dm

    def _slayer_modifier(self) -> (float, float):
        weapon = self.equipment.weapon
        assert isinstance(weapon, Weapon)
        if self.on_task:
            if self.equipment.wearing(head='slayer helmet (i)'):
                if weapon.active_style.damage_type in Style.melee_damage_types:
                    modifier = 7/6
                elif weapon.active_style.damage_type in Style.ranged_damage_types:
                    modifier = 1.15
                elif weapon.active_style.damage_type in Style.magic_damage_types:
                    modifier = 1.15
                else:
                    raise Style.StyleError(f"{weapon.active_style.damage_type} is not a recognized damage type")
            elif self.equipment.wearing(head='slayer helmet'):
                raise NotImplementedError('slayer helmet / black mask / black mask (i) / ...')
            else:
                modifier = 1

        else:
            modifier = 1

        slayer_arm = modifier
        slayer_dm = modifier
        return slayer_arm, slayer_dm

    def _arclight_modifier(self, other) -> (float, float):
        assert isinstance(other, Monster)

        modifier = 1.7 if Monster.demon in other.attributes and self.equipment.weapon.name == 'arclight' else 1

        arclight_arm = modifier
        arclight_dm = modifier
        return arclight_arm, arclight_dm

    def _draconic_modifier(self, other) -> (float, float):
        weapon = self.equipment.weapon
        assert isinstance(weapon, Weapon)
        assert isinstance(other, Monster)

        if Monster.draconic in other.attributes:
            if weapon.name == 'dragon hunter lance':
                modifier = 1.2
            elif weapon.name == 'dragon hunter crossbow':
                modifier = 1.3
            else:
                modifier = 1
        else:
            modifier = 1

        draconic_arm = modifier
        draconic_dm = modifier
        return draconic_arm, draconic_dm

    def _wilderness_modifier(self, other) -> (float, float):
        weapon = self.equipment.weapon
        assert isinstance(weapon, Weapon)
        assert isinstance(other, Monster)

        if other.location == Monster.wilderness:
            if weapon.name == "craw's bow":
                wilderness_arm = 1.5
                wilderness_sm = 1.5
            elif weapon.name == "viggora's chainmace":
                wilderness_arm = 1.5
                wilderness_sm = 1.5
            elif weapon.name == "thammaron's sceptre":
                wilderness_arm = 2
                wilderness_sm = 1.25
            else:
                wilderness_arm = 1
                wilderness_sm = 1
        else:
            wilderness_arm = 1
            wilderness_sm = 1

        return wilderness_arm, wilderness_sm

    def _twisted_bow_modifier(self, other) -> (float, float):

        if self.equipment.wearing(weapon='twisted bow'):
            accuracy_modifier_ceiling = 1.40
            damage_modifier_ceiling = 2.50

            if isinstance(other, Monster) and Monster.xerician not in other.attributes:
                magic_ceiling = 250
                magic = max([other.stats.current_combat.magic, other.stats.aggressive.magic])
                magic = min([magic, magic_ceiling])

            elif isinstance(other, CoxMonster) or (isinstance(other, Monster) and Monster.xerician in other.attributes):
                magic_ceiling = 350
                magic = max([other.stats.current_combat.magic, other.stats.aggressive.magic])
                magic = min([magic, magic_ceiling])
            else:
                raise Monster.MonsterError(f"Unrecognized monster type {type(other)}")

            accuracy_modifier_percent = 140 + math.floor((3 * magic - 10) / 100) - math.floor(
                ((3 * magic) / 10 - 100) ** 2 / 100)

            damage_modifier_percent = 250 + math.floor((3 * magic - 14) / 100) - math.floor(
                ((3 * magic) / 10 - 140) ** 2 / 100)

            twisted_bow_arm = min([accuracy_modifier_ceiling, accuracy_modifier_percent / 100])
            twisted_bow_dm = min([damage_modifier_ceiling, damage_modifier_percent / 100])

        else:
            twisted_bow_arm = 1
            twisted_bow_dm = 1

        return twisted_bow_arm, twisted_bow_dm

    def _obsidian_armor_modifier(self) -> (float, float):
        if self.equipment.obsidian_armor_set() and self.equipment.obsidian_weapon():
            obsidian_arm = 1.1
            obsidian_dm = 1.1
        else:
            obsidian_arm = 1
            obsidian_dm = 1

        return obsidian_arm, obsidian_dm

    def _crystal_armor_modifier(self) -> (float, float):
        crystal_arm = 1
        crystal_dm = 1

        if self.weapon.name == 'crystal bow':
            piece_arm_bonus = 0.06
            piece_dm_bonus = 0.03
            set_arm_bonus = 0.12
            set_dm_bonus = 0.06

            if self.equipment.wearing(head="crystal helm"):
                crystal_arm += piece_arm_bonus
                crystal_dm += piece_dm_bonus
            if self.equipment.wearing(body="crystal body"):
                crystal_arm += piece_arm_bonus
                crystal_dm += piece_dm_bonus
            if self.equipment.wearing(legs="crystal legs"):
                crystal_arm += piece_arm_bonus
                crystal_dm += piece_dm_bonus

            if self.equipment.crystal_armor_set():
                crystal_arm += set_arm_bonus
                crystal_dm += set_dm_bonus

        return crystal_arm, crystal_dm

    def _inquisitor_modifier(self) -> (float, float):
        weapon = self.equipment.weapon
        assert isinstance(weapon, Weapon)

        modifier = 1

        if weapon.active_style.damage_type == Style.crush:
            piece_bonus = 0.005
            set_bonus = 0.01

            if self.equipment.wearing(head="inquisitor's great helm"):
                modifier += piece_bonus
            if self.equipment.wearing(body="inquisitor's hauberk"):
                modifier += piece_bonus
            if self.equipment.wearing(legs="inquisitor's plateskirt"):
                modifier += piece_bonus

            if self.equipment.inquisitor_set():
                modifier += set_bonus

        inquisitor_arm = modifier
        inquisitor_dm = modifier
        return inquisitor_arm, inquisitor_dm

    def _chinchompa_modifier(self, distance: int = None) -> float:
        weapon = self.equipment.weapon
        assert isinstance(weapon, Weapon)

        if not distance:
            chin_arm = 1.00
        else:
            if weapon.active_style.name == PlayerStyle.short_fuse:
                if 0 <= distance <= 3:
                    chin_arm = 1.00
                elif 4 <= distance <= 6:
                    chin_arm = 0.75
                else:
                    chin_arm = 0.50
            elif weapon.active_style.name == PlayerStyle.medium_fuse:
                if 4 <= distance <= 6:
                    chin_arm = 1.00
                else:
                    chin_arm = 0.75
            elif weapon.active_style.name == PlayerStyle.long_fuse:
                if 0 <= distance <= 3:
                    chin_arm = 0.50
                elif 4 <= distance <= 6:
                    chin_arm = 0.75
                else:
                    chin_arm = 1.00
            else:
                chin_arm = 1.00

        return chin_arm

    def _vampyric_modifier(self, other) -> (float, float):
        raise NotImplementedError()

    def _tome_of_fire_damage_modifier(self, spell: spells.Spell = None):
        tome_dm = 1.5 if spell in spells.fire_spells and self.equipment.wearing(shield='tome of fire') else 1
        return tome_dm

    def _chaos_gauntlets_bonus(self, spell: spells.Spell = None):
        cg_damage_boost = 3 if spell in spells.bolt_spells and self.equipment.wearing(hands='chaos gauntlets') else 0
        return cg_damage_boost

    def attack_roll(self, other, special_attack: bool = False, distance: int = None) -> int:
        aggressive_combat_bonus = self.equipment.aggressive_bonus()
        assert isinstance(self.weapon, Weapon)
        dt = self.weapon.active_style.damage_type

        if dt in Style.melee_damage_types:
            effective_level = self.effective_attack_level
            bonus = aggressive_combat_bonus.__getattribute__(dt)
        elif dt in Style.ranged_damage_types:
            effective_level = self.effective_ranged_attack_level
            bonus = aggressive_combat_bonus.ranged
        elif dt in Style.magic_damage_types:
            effective_level = self.effective_magic_level
            bonus = aggressive_combat_bonus.magic
        else:
            raise Style.StyleError(self.weapon, self.weapon.active_style, dt)

        assert isinstance(other, Monster)
        # X_arm: X attack roll modifier
        # X_dm: X damage modifier

        salve_arm, _ = self._salve_modifier(other)
        slayer_arm, _ = self._slayer_modifier()

        # salve and slayer helm cannot stack, only use salve effect
        if salve_arm > 1 and slayer_arm > 1:
            slayer_arm = 1

        arclight_arm, _ = self._arclight_modifier(other)
        draconic_arm, _ = self._draconic_modifier(other)
        wilderness_arm, _ = self._wilderness_modifier(other)
        twisted_bow_arm, _ = self._twisted_bow_modifier(other)
        obsidian_arm, _ = self._obsidian_armor_modifier()
        crystal_arm, _ = self._crystal_armor_modifier()
        chin_arm = self._chinchompa_modifier(distance)
        inquisitor_arm, _ = self._inquisitor_modifier()

        all_roll_modifiers = [
            salve_arm,
            slayer_arm,
            arclight_arm,
            draconic_arm,
            wilderness_arm,
            twisted_bow_arm,
            obsidian_arm,
            crystal_arm,
            chin_arm,
            inquisitor_arm
        ]

        if special_attack:
            assert isinstance(self.weapon, SpecialWeapon)
            all_roll_modifiers.append(self.weapon.special_accuracy_modifier)

        active_roll_modifiers = [x for x in all_roll_modifiers if not x == 1]

        return Character.maximum_roll(effective_level, bonus, active_roll_modifiers)

    def max_hit(self, other, special_attack: bool = False) -> int:
        assert isinstance(self.weapon, Weapon)
        assert isinstance(other, Monster)
        aggressive_gear_bonus: PlayerStats.Aggressive = self.equipment.aggressive_bonus()

        dt = self.weapon.active_style.damage_type

        if dt in Style.melee_damage_types or dt in Style.ranged_damage_types:
            if dt in Style.melee_damage_types:
                effective_level = self.effective_melee_strength_level
                bonus = aggressive_gear_bonus.melee_strength
            else:
                effective_level = self.effective_ranged_strength_level
                bonus = aggressive_gear_bonus.ranged_strength

            base_damage = Character.base_damage(effective_level, bonus)

            _, salve_dm = self._salve_modifier(other)
            _, slayer_dm = self._slayer_modifier()

            # salve and slayer helm cannot stack, only use salve effect
            if salve_dm > 1 and slayer_dm > 1:
                slayer_dm = 1

            _, arclight_dm = self._arclight_modifier(other)
            _, draconic_dm = self._draconic_modifier(other)
            _, wilderness_dm = self._wilderness_modifier(other)
            _, twisted_bow_dm = self._twisted_bow_modifier(other)
            _, obsidian_dm = self._obsidian_armor_modifier()
            _, crystal_dm = self._crystal_armor_modifier()
            _, inquisitor_dm = self._inquisitor_modifier()
            # TODO: vampyric weapons and a few others

            all_roll_modifiers = [
                salve_dm,
                slayer_dm,
                arclight_dm,
                draconic_dm,
                wilderness_dm,
                twisted_bow_dm,
                obsidian_dm,
                crystal_dm,
                inquisitor_dm
            ]

            if special_attack:
                assert isinstance(self.weapon, SpecialWeapon)
                all_roll_modifiers.append(self.weapon.special_damage_modifier_1)
                all_roll_modifiers.append(self.weapon.special_damage_modifier_2)

            active_roll_modifiers = [x for x in all_roll_modifiers if not x == 1]

            max_hit = Character._max_hit(base_damage, active_roll_modifiers)

        elif dt in Style.magic_damage_types:
            spell = self.weapon.autocast
            assert isinstance(spell, spells.Spell)

            if isinstance(spell, spells.StandardSpell) or isinstance(spell, spells.AncientSpell):
                base_damage = spell.base_max_hit()
            elif isinstance(spell, spells.GodSpell):
                base_damage = spell.base_max_hit(self.charged)
            elif isinstance(spell, spells.PoweredSpell):
                base_damage = spell.base_max_hit(self.visible_magic)
            else:
                raise Style.StyleError('autocast spell is not a recognized type')

            cg_bonus = self._chaos_gauntlets_bonus(spell)
            gear_bonus_modifier = 1 + self.equipment.aggressive_bonus().magic_strength
            _, salve_dm = self._salve_modifier(other)
            _, slayer_dm = self._slayer_modifier()
            tome_dm = self._tome_of_fire_damage_modifier(spell)

            base_damage += cg_bonus
            base_damage = math.floor(base_damage * gear_bonus_modifier)

            if salve_dm > 1:
                base_damage = math.floor(base_damage * salve_dm)
            elif slayer_dm > 1:
                base_damage = math.floor(base_damage * slayer_dm)

            max_hit = math.floor(base_damage * tome_dm)
            # TODO: Castle wars bracelet

        else:
            raise Style.StyleError(self.weapon, self.weapon.active_style, dt)

        return max_hit

    def damage_against_monster(self, other, special_attack: bool = False, distance: int = None):    # -> Damage:
        assert isinstance(other, Monster)
        assert isinstance(self.weapon, Weapon)
        dt = self.weapon.active_style.damage_type

        if special_attack:
            assert isinstance(self.weapon, SpecialWeapon)

        att_roll = self.attack_roll(other, special_attack, distance)
        def_roll = other.defence_roll(self, special_attack)
        accuracy = self.accuracy(att_roll, def_roll)

        max_hit = self.max_hit(other, special_attack)
        hitpoints_cap = other.stats.current_combat.hitpoints

        # specific weapon types handled here

        if 'scythe of vitur' in self.weapon.name:
            damage = Damage(
                self.weapon.attack_speed,
                Hitsplat.from_max_hit_acc(max_hit, accuracy, hitpoints_cap),
                Hitsplat.from_max_hit_acc(math.floor(0.50 * max_hit), accuracy, hitpoints_cap),
                Hitsplat.from_max_hit_acc(math.floor(0.25 * max_hit), accuracy, hitpoints_cap)
            )
        else:
            damage = Damage.from_max_hit_acc(max_hit, accuracy, self.weapon.attack_speed, hitpoints_cap)

        return damage

    def attack_monster(self, other, special_attack: bool = False, distance: int = None, attempts: int = 1) -> int:
        assert isinstance(other, Monster)
        damage = self.damage_against_monster(other, special_attack, distance)
        damage_dealt = 0
        max_damage_dealt = other.stats.current_combat.hitpoints

        for rd in damage.random(attempts):
            damage_dealt += rd
            other.damage(rd)

        return min([damage_dealt, max_damage_dealt])

    def kill_monster(self, other, distance: int = None) -> (int, int):
        assert isinstance(other, Monster)
        assert isinstance(self.weapon, Weapon)
        damage = self.damage_against_monster(other, special_attack=False, distance=distance)
        max_damage_dealt = other.stats.current_combat.hitpoints
        ticks = 0

        while other.alive:
            ticks += self.weapon.attack_speed
            for rd in damage.random():
                other.damage(rd)

        return ticks, max_damage_dealt

    @property
    def alive(self) -> bool:
        return self.stats.current_combat.hitpoints > 0

    @classmethod
    def from_highscores(cls, rsn: str, equipment: Equipment):
        return cls(
            name=rsn,
            stats=PlayerStats(
                combat=PlayerStats.Combat.from_highscores(rsn),
                aggressive=PlayerStats.Aggressive.no_bonus(),
                defensive=PlayerStats.Defensive.no_bonus()
            ),
            equipment=equipment
        )

    @classmethod
    def max_scythe_bandos(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('scythe of vitur')
        weapon.choose_style_by_name(PlayerStyle.chop)

        return cls(
            name='[max] scythe bandos',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere('neitiznot faceguard'),
                Gear.from_bitterkoekje_bedevere('infernal cape'),
                Gear.from_bitterkoekje_bedevere('amulet of torture'),
                Gear.from_bitterkoekje_bedevere('bandos chestplate'),
                Gear.from_bitterkoekje_bedevere('bandos tassets'),
                Gear.from_bitterkoekje_bedevere('ferocious gloves'),
                Gear.from_bitterkoekje_bedevere('primordial boots'),
                Gear.from_bitterkoekje_bedevere('berserker (i)')
            )
        )

    @classmethod
    def max_blood_fury_scythe_bandos(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('scythe of vitur')
        weapon.choose_style_by_name(PlayerStyle.chop)

        return cls(
            name='blood fury scythe bandos',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere('neitiznot faceguard'),
                Gear.from_bitterkoekje_bedevere('infernal cape'),
                Gear.from_bitterkoekje_bedevere('amulet of fury'),
                Gear.from_bitterkoekje_bedevere('bandos chestplate'),
                Gear.from_bitterkoekje_bedevere('bandos tassets'),
                Gear.from_bitterkoekje_bedevere('ferocious gloves'),
                Gear.from_bitterkoekje_bedevere('primordial boots'),
                Gear.from_bitterkoekje_bedevere('berserker (i)')
            )
        )

    @classmethod
    def max_scythe_inquisitor(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('scythe of vitur')
        weapon.choose_style_by_name(PlayerStyle.jab)

        return cls(
            name='[max] scythe inquisitor',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("inquisitor's great helm"),
                Gear.from_bitterkoekje_bedevere("infernal cape"),
                Gear.from_bitterkoekje_bedevere("amulet of torture"),
                Gear.from_bitterkoekje_bedevere("inquisitor's hauberk"),
                Gear.from_bitterkoekje_bedevere("inquisitor's plateskirt"),
                Gear.from_bitterkoekje_bedevere("ferocious gloves"),
                Gear.from_bitterkoekje_bedevere("primordial boots"),
                Gear.from_bitterkoekje_bedevere("berserker (i)")
            )
        )

    @classmethod
    def max_lance_inquisitor(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('dragon hunter lance')
        weapon.choose_style_by_name(PlayerStyle.pound)

        return cls(
            name='[max] lance inquisitor',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("inquisitor's great helm"),
                Gear.from_bitterkoekje_bedevere("infernal cape"),
                Gear.from_bitterkoekje_bedevere("amulet of torture"),
                Gear.from_bitterkoekje_bedevere("inquisitor's hauberk"),
                Gear.from_bitterkoekje_bedevere("inquisitor's plateskirt"),
                Gear.from_bitterkoekje_bedevere("avernic defender"),
                Gear.from_bitterkoekje_bedevere("ferocious gloves"),
                Gear.from_bitterkoekje_bedevere("primordial boots"),
                Gear.from_bitterkoekje_bedevere("berserker (i)")
            )
        )

    @classmethod
    def dwh_inquisitor_brimstone(cls):
        weapon = Weapon.from_bitterkoekje_bedevere("dragon warhammer")
        weapon.choose_style_by_name(PlayerStyle.pound)

        return cls(
            name='dwh inquisitor (brimstone)',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("inquisitor's great helm"),
                Gear.from_bitterkoekje_bedevere("infernal cape"),
                Gear.from_bitterkoekje_bedevere("amulet of torture"),
                Gear.from_bitterkoekje_bedevere("inquisitor's hauberk"),
                Gear.from_bitterkoekje_bedevere("inquisitor's plateskirt"),
                Gear.from_bitterkoekje_bedevere("avernic defender"),
                Gear.from_bitterkoekje_bedevere("ferocious gloves"),
                Gear.from_bitterkoekje_bedevere("primordial boots"),
                Gear.from_bitterkoekje_bedevere("brimstone ring")
            )
        )

    @classmethod
    def void_bp(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('toxic blowpipe')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[void] bp',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon dart"),
                Gear.from_bitterkoekje_bedevere("void knight helm"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("elite void top"),
                Gear.from_bitterkoekje_bedevere("elite void robe"),
                Gear.from_bitterkoekje_bedevere("void knight gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def void_tbow(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('twisted bow')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[void] tbow',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon arrow"),
                Gear.from_bitterkoekje_bedevere("void knight helm"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("elite void top"),
                Gear.from_bitterkoekje_bedevere("elite void robe"),
                Gear.from_bitterkoekje_bedevere("void knight gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def void_chinchompa(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('black chinchompa')
        weapon.choose_style_by_name(PlayerStyle.medium_fuse)

        return cls(
            name='[void] chinchompa',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("void knight helm"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("elite void top"),
                Gear.from_bitterkoekje_bedevere("elite void robe"),
                Gear.from_bitterkoekje_bedevere("twisted buckler"),
                Gear.from_bitterkoekje_bedevere("void knight gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def arma_tbow(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('twisted bow')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[arma] tbow',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon arrow"),
                Gear.from_bitterkoekje_bedevere("armadyl helmet"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("armadyl chestplate"),
                Gear.from_bitterkoekje_bedevere("armadyl chainskirt"),
                Gear.from_bitterkoekje_bedevere("barrows gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def arma_bp(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('toxic blowpipe')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[arma] bp',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon dart"),
                Gear.from_bitterkoekje_bedevere("armadyl helmet"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("armadyl chestplate"),
                Gear.from_bitterkoekje_bedevere("armadyl chainskirt"),
                Gear.from_bitterkoekje_bedevere("barrows gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def arma_chinchompa(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('black chinchompa')
        weapon.choose_style_by_name(PlayerStyle.medium_fuse)

        return cls(
            name='[arma] chinchompa',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("armadyl helmet"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("armadyl chestplate"),
                Gear.from_bitterkoekje_bedevere("armadyl chainskirt"),
                Gear.from_bitterkoekje_bedevere("twisted buckler"),
                Gear.from_bitterkoekje_bedevere("barrows gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def on_task_tbow(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('twisted bow')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[on task] tbow',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon arrow"),
                Gear.from_bitterkoekje_bedevere("slayer helmet (i)"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("armadyl chestplate"),
                Gear.from_bitterkoekje_bedevere("armadyl chainskirt"),
                Gear.from_bitterkoekje_bedevere("barrows gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def on_task_bp(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('toxic blowpipe')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[on task] tbow',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon arrow"),
                Gear.from_bitterkoekje_bedevere("slayer helmet (i)"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("armadyl chestplate"),
                Gear.from_bitterkoekje_bedevere("armadyl chainskirt"),
                Gear.from_bitterkoekje_bedevere("barrows gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def on_task_chinchompa(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('black chinchompa')
        weapon.choose_style_by_name(PlayerStyle.medium_fuse)

        return cls(
            name='[on task] chinchompa',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("slayer helmet (i)"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("armadyl chestplate"),
                Gear.from_bitterkoekje_bedevere("armadyl chainskirt"),
                Gear.from_bitterkoekje_bedevere("twisted buckler"),
                Gear.from_bitterkoekje_bedevere("barrows gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def salve_void_bp(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('toxic blowpipe')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[void] [salve] bp',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon dart"),
                Gear.from_bitterkoekje_bedevere("void knight helm"),
                Gear.from_bitterkoekje_bedevere("salve amulet (ei)"),
                Gear.from_bitterkoekje_bedevere("necklace of anguish"),
                Gear.from_bitterkoekje_bedevere("elite void top"),
                Gear.from_bitterkoekje_bedevere("elite void robe"),
                Gear.from_bitterkoekje_bedevere("void knight gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def salve_arma_bp(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('toxic blowpipe')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[arma] [salve] bp',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon dart"),
                Gear.from_bitterkoekje_bedevere("armadyl helmet"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("salve amulet (ei)"),
                Gear.from_bitterkoekje_bedevere("armadyl chestplate"),
                Gear.from_bitterkoekje_bedevere("armadyl chainskirt"),
                Gear.from_bitterkoekje_bedevere("barrows gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def salve_arma_tbow(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('twisted bow')
        weapon.choose_style_by_name(PlayerStyle.rapid)

        return cls(
            name='[arma] [salve] tbow',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("dragon arrow"),
                Gear.from_bitterkoekje_bedevere("armadyl helmet"),
                Gear.from_bitterkoekje_bedevere("ava's assembler"),
                Gear.from_bitterkoekje_bedevere("salve amulet (ei)"),
                Gear.from_bitterkoekje_bedevere("armadyl chestplate"),
                Gear.from_bitterkoekje_bedevere("armadyl chainskirt"),
                Gear.from_bitterkoekje_bedevere("barrows gloves"),
                Gear.from_bitterkoekje_bedevere("pegasian boots"),
                Gear.from_bitterkoekje_bedevere("archer (i)")
            )
        )

    @classmethod
    def max_sang_brimstone(cls):
        weapon = Weapon.from_bitterkoekje_bedevere('sanguinesti staff')
        weapon.choose_autocast(PlayerStyle.accurate, spells.sanguinesti_staff)

        return cls(
            name='[max] sang (brimstone)',
            stats=PlayerStats.max_player_stats(),
            equipment=Equipment(
                weapon,
                Gear.from_bitterkoekje_bedevere("ancestral hat"),
                Gear.from_bitterkoekje_bedevere("god cape (i)"),
                Gear.from_bitterkoekje_bedevere("occult necklace"),
                Gear.from_bitterkoekje_bedevere("ancestral robe top"),
                Gear.from_bitterkoekje_bedevere("ancestral robe bottoms"),
                Gear.from_bitterkoekje_bedevere("arcane spirit shield"),
                Gear.from_bitterkoekje_bedevere("tormented bracelet"),
                Gear.from_bitterkoekje_bedevere("eternal boots"),
                Gear.from_bitterkoekje_bedevere("brimstone ring")
            )
        )

    def __str__(self):
        return "name: {:}\n{:}".format(self.name, self.equipment)


class Monster(Character):
    demon = 'demon'
    draconic = 'draconic'
    fiery = 'fiery'
    golem = 'golem'
    kalphite = 'kalphite'
    leafy = 'leafy'
    penance = 'penance'
    shade = 'shade'
    spectral = 'spectral'
    undead = 'undead'
    vampyre = 'vampyre'
    vampyre_tier_1 = 'vampyre - tier 1'
    vampyre_tier_2 = 'vampyre - tier 2'
    vampyre_tier_3 = 'vampyre - tier 3'
    xerician = 'xerician'

    wilderness = 'wilderness'

    _dwh_defence_multiplier = 0.70
    _dwh_defence_multiplier_on_miss = 1

    _bgs_defence_reduction_on_miss = 0

    class MonsterError(Exception):

        def __init__(self, *args):
            if args:
                self.message = ' '.join([str(a) for a in args])
            else:
                self.message = ''

        def __str__(self):
            if self.message:
                return 'The following aspect of a Monster (or subclass) caused an error: {:}'.format(self.message)
            else:
                return 'A MonsterError was raised'

    def __init__(self,
                 name: str,
                 stats: MonsterStats,
                 location: str = None,
                 exp_bonus: float = None,
                 combat_level: int = None,
                 attack_styles: NpcAttacks = None,
                 defence_floor: int = None,
                 attribute: Union[List[str], str] = None
                 ):
        super().__init__(name, stats)
        self.stats = stats

        self.location = location
        self.exp_modifier = 1 + exp_bonus if exp_bonus else 1
        self.combat_level = combat_level if combat_level else 0
        self.attack_styles = attack_styles
        self.defence_floor = defence_floor if defence_floor else 0

        if isinstance(attribute, str):
            self.attributes = [attribute]
        elif isinstance(attribute, list):
            self.attributes = attribute
        else:
            self.attributes = []

    def damage(self, amount: int):
        current_hp = self.stats.current_combat.hitpoints
        minimum_hp = 0
        new_hp = max([minimum_hp, current_hp - amount])
        self.stats.current_combat.hitpoints = new_hp

    def heal(self, amount: int, overheal: bool = False):
        current_hp = self.stats.current_combat.hitpoints

        if overheal:
            new_hp = current_hp + amount
        else:
            maximum_hp = self.stats.combat.hitpoints
            new_hp = min([maximum_hp, current_hp + amount])

        self.stats.current_combat.hitpoints = new_hp

    def reset_current_stats(self):
        self.stats.current_combat = MonsterStats.CurrentCombat.from_combat(self.stats.combat)

    def dwh_reduce(self, damage_dealt: bool = True):
        multiplier = self._dwh_defence_multiplier if damage_dealt else self._dwh_defence_multiplier_on_miss
        self.stats.current_combat.reduce_defence_ratio(multiplier)

    def arclight_reduce(self):
        reduction_modifier = 0.10 if self.demon in self.attributes else 0.05
        atk_reduction = reduction_modifier * self.stats.combat.attack
        str_reduction = reduction_modifier * self.stats.combat.strength
        def_reduction = reduction_modifier * self.stats.combat.defence

        possible_attack_reduction = self.stats.current_combat.attack
        possible_strength_reduction = self.stats.current_combat.strength
        possible_defence_reduction = self.stats.current_combat.defence - self.defence_floor

        self.stats.current_combat.reduce_defence_flat(min([def_reduction, possible_defence_reduction]))
        self.stats.current_combat.reduce_stat_flat('attack', min([atk_reduction, possible_attack_reduction]))
        self.stats.current_combat.reduce_stat_flat('strength', min([str_reduction, possible_strength_reduction]))

    def bgs_reduce(self, damage_dealt: int) -> int:
        possible_defence_reduction = self.stats.current_combat.defence - self.defence_floor

        if damage_dealt > possible_defence_reduction:
            self.stats.current_combat.defence = self.defence_floor
            reduction_remaining = damage_dealt - possible_defence_reduction
        else:
            self.stats.current_combat.reduce_defence_flat(damage_dealt)
            return 0

        possible_strength_reduction = self.stats.current_combat.strength

        if reduction_remaining > possible_strength_reduction:
            self.stats.current_combat.strength = 0
            reduction_remaining -= possible_strength_reduction
        else:
            self.stats.current_combat.strength -= reduction_remaining
            return 0

        possible_attack_reduction = self.stats.current_combat.attack

        if reduction_remaining > possible_attack_reduction:
            self.stats.current_combat.attack = 0
            reduction_remaining -= possible_attack_reduction
        else:
            self.stats.current_combat.attack -= reduction_remaining
            return 0

        possible_magic_reduction = self.stats.current_combat.magic

        if reduction_remaining > possible_magic_reduction:
            self.stats.current_combat.magic = 0
            reduction_remaining -= possible_magic_reduction
        else:
            self.stats.current_combat.magic -= reduction_remaining
            return 0

        possible_ranged_reduction = self.stats.current_combat.ranged

        if reduction_remaining > possible_ranged_reduction:
            self.stats.current_combat.ranged = 0
        else:
            self.stats.current_combat.ranged -= reduction_remaining

        return 0

    @property
    def effective_defence_level(self) -> int:
        style_bonus = MonsterStats.Combat.npc_style_bonus().defence
        return Character.effective_accuracy_level(self.stats.current_combat.defence, style_bonus)

    @property
    def effective_magic_defence_level(self) -> int:
        style_bonus = MonsterStats.Combat.npc_style_bonus().magic
        return Character.effective_accuracy_level(self.stats.current_combat.magic, style_bonus)

    def defence_roll(self, other, special_attack: bool = False) -> int:
        assert isinstance(other, Player)
        assert isinstance(other.weapon, Weapon)

        dt = other.weapon.active_style.damage_type

        if dt in Style.melee_damage_types or dt in Style.ranged_damage_types:
            stat = self.effective_defence_level
        elif dt in Style.magic_damage_types:
            stat = self.effective_magic_defence_level
        else:
            raise Style.StyleError('unrecognized damage type: {:}'.format(dt))

        if special_attack:
            assert isinstance(other.weapon, SpecialWeapon)
            dt_def_roll = other.weapon.special_defence_roll if other.weapon.special_defence_roll else dt
        else:
            dt_def_roll = dt

        bonus = self.stats.defensive.__getattribute__(dt_def_roll)
        roll = Character.maximum_roll(stat, bonus)

        if other.equipment.wearing(ring='brimstone ring') and dt in Style.magic_damage_types:
            reduction = math.floor(roll / 10) / 4
            roll = math.floor(roll - reduction)

        return roll

    @property
    def alive(self) -> bool:
        return self.stats.current_combat.hitpoints > 0

    @classmethod
    def from_bitterkoekje(cls, name: str):
        boss_df = resource_reader.lookup_monster(name)

        if boss_df['location'].values[0] == 'raids':
            raise Monster.MonsterError(name, 'should be instantiated via the from_de0 method of CoxMonster(Monster)')

        # attack style parsing
        damage_types: str = boss_df['main attack style'].values[0]
        styles_tup = damage_types.split(' and ')

        styles = []

        for s in styles_tup:
            if s == '':
                continue

            style = NpcStyle(
                damage_type=s,
                attack_speed=boss_df['attack speed'].values[0]
            )
            styles.append(style)

        attack_styles = NpcAttacks(name=name, *styles)

        # type parsing
        raw_type_value = boss_df['type'].values[0]
        attributes = []

        if raw_type_value == 'demon':
            attributes.append(Monster.demon)
        elif raw_type_value == 'dragon':
            attributes.append(Monster.draconic)
        elif raw_type_value == 'fire':
            attributes.append(Monster.fiery)
        elif raw_type_value == 'kalphite':
            attributes.append(Monster.kalphite)
        elif raw_type_value == 'kurask':
            attributes.append(Monster.leafy)
        elif raw_type_value == 'vorkath':
            attributes.append(Monster.draconic)
            attributes.append(Monster.undead)
        elif raw_type_value == 'undead':
            attributes.append(Monster.undead)
        elif raw_type_value == 'vampyre - tier 1':
            attributes.append(Monster.vampyre)
            attributes.append(Monster.vampyre_tier_1)
        elif raw_type_value == 'vampyre - tier 2':
            attributes.append(Monster.vampyre)
            attributes.append(Monster.vampyre_tier_2)
        elif raw_type_value == 'vampyre - tier 3':
            attributes.append(Monster.vampyre)
            attributes.append(Monster.vampyre_tier_3)
        elif raw_type_value == 'guardian':
            raise Monster.MonsterError(name, raw_type_value, 'should not be instantiated from Monster, '
                                                             'use Guardian(CoxMonster)')
        elif raw_type_value == '':
            pass
        else:
            raise Monster.MonsterError(name, raw_type_value, 'is an unsupported or undefined type')

        # would do a location check here for xerician but we raise all those errors for now

        return cls(
            name=name,
            stats=MonsterStats.from_bitterkoekje(name),
            location=boss_df['location'].values[0],
            exp_bonus=boss_df['exp bonus'].values[0],
            combat_level=boss_df['combat level'].values[0],
            attack_styles=attack_styles,
            attribute=attributes
        )


class CoxMonster(Monster):
    _location = 'chambers of xeric'
    _name: str

    def __init__(self, name: str, base_stats: MonsterStats, party_size: int, challenge_mode: bool,
                 max_combat_level: int = None,
                 max_hitpoints_level: int = None,
                 exp_bonus: float = None,
                 combat_level: int = None,
                 attack_styles: NpcAttacks = None,
                 attribute: Union[List[str], str] = None
                 ):

        # catch improper definitions
        if name == Guardian.get_name() and not isinstance(self, Guardian):
            raise CoxMonster.MonsterError(self, f'wrong {name} class definition, use Guardian(CoxMonster)')
        elif name == Tekton.get_name() and not isinstance(self, Tekton):
            raise CoxMonster.MonsterError(self, f'wrong {name} class definition, use Tekton(CoxMonster)')
        elif 'olm' in name and not isinstance(self, Olm):
            raise CoxMonster.MonsterError(self, f'wrong {name} class definition, use Olm, OlmMeleeHand, OlmMageHand')

        self.party_size = party_size
        self.challenge_mode = challenge_mode
        self.max_combat_level = max_combat_level if max_combat_level else PlayerStats.Combat.max_combat_level
        self.max_hitpoints_level = max_hitpoints_level if max_hitpoints_level else PlayerStats.Combat.max_level

        if isinstance(attribute, str):
            attributes = [attribute]
        elif isinstance(attribute, list):
            attributes = attribute
        else:
            attributes = []

        if Monster.xerician not in attributes:
            attributes.append(Monster.xerician)

        combat, aggressive, defensive = base_stats.unpack()
        assert isinstance(aggressive, MonsterStats.Aggressive)

        # order matters, floor each intermediate value
        hitpoints_scaled = math.floor(
            self.challenge_mode_hp_scaling_factor() * math.floor(
                self.party_hp_scaling_factor() * math.floor(
                    self.player_hp_scaling_factor() * combat.hitpoints
                )
            )
        )

        # attack and strength
        melee_scaled = math.floor(
            self.challenge_mode_offensive_scaling_factor() * math.floor(
                self.party_offensive_scaling_factor() * math.floor(
                    self.player_offensive_defensive_scaling_factor() * combat.attack
                )
            )
        )

        magic_scaled = math.floor(
            self.challenge_mode_offensive_scaling_factor() * math.floor(
                self.party_offensive_scaling_factor() * math.floor(
                    self.player_offensive_defensive_scaling_factor() * combat.magic
                )
            )
        )

        ranged_scaled = math.floor(
            self.challenge_mode_offensive_scaling_factor() * math.floor(
                self.party_offensive_scaling_factor() * math.floor(
                    self.player_offensive_defensive_scaling_factor() * combat.ranged
                )
            )
        )

        defence_scaled = math.floor(
            self.challenge_mode_defensive_scaling_factor() * math.floor(
                self.party_defensive_scaling_factor() * math.floor(
                    self.player_offensive_defensive_scaling_factor() * combat.defence
                )
            )
        )

        scaled_stats = MonsterStats(
            combat=Stats.Combat(
                hitpoints=hitpoints_scaled,
                attack=melee_scaled,
                strength=melee_scaled,
                defence=defence_scaled,
                magic=magic_scaled,
                ranged=ranged_scaled
            ),
            aggressive=aggressive,
            defensive=defensive
        )

        super(CoxMonster, self).__init__(
            name=name,
            stats=scaled_stats,
            location=CoxMonster._location,
            exp_bonus=exp_bonus,
            combat_level=combat_level,
            attack_styles=attack_styles,
            attribute=attributes
        )

    @classmethod
    def from_de0(cls, name: str, party_size: int, challenge_mode: bool, max_combat_level: int = None,
                 max_hitpoints_level: int = None, attribute: Union[List[str], str] = None):

        return cls(
            name=name,
            base_stats=MonsterStats.from_de0(name),
            party_size=party_size,
            challenge_mode=challenge_mode,
            max_combat_level=max_combat_level,
            max_hitpoints_level=max_hitpoints_level,
            attribute=attribute
        )

    def player_hp_scaling_factor(self):
        return self.max_combat_level / PlayerStats.Combat.max_combat_level

    def player_offensive_defensive_scaling_factor(self):
        hp = self.max_hitpoints_level
        return (math.floor(hp * 4 / 9) + 55) / 99

    def party_hp_scaling_factor(self):
        n = self.party_size
        return 1 + math.floor(n / 2)

    def party_offensive_scaling_factor(self):
        n = self.party_size
        return (7 * math.floor(math.sqrt(n - 1)) + (n - 1) + 100) / 100

    def party_defensive_scaling_factor(self):
        n = self.party_size
        return (math.floor(math.sqrt(n - 1)) + math.floor((7/10) * (n - 1)) + 100) / 100

    def challenge_mode_hp_scaling_factor(self):
        factor = 3/2 if self.challenge_mode else 1
        return factor

    def challenge_mode_offensive_scaling_factor(self):
        factor = 3/2 if self.challenge_mode else 1
        return factor

    def challenge_mode_defensive_scaling_factor(self):
        factor = 3/2 if self.challenge_mode else 1
        return factor

    @classmethod
    def get_name(cls) -> str:
        return cls._name


class Guardian(CoxMonster):
    _name = 'guardian'

    def __init__(self, party_size: int, challenge_mode: bool,
                 max_combat_level: int = None,
                 max_hitpoints_level: int = None,
                 average_mining_level: Union[int, List[int]] = None
                 ):
        if not average_mining_level:
            reduction = PlayerStats.Combat.max_level
        else:
            if isinstance(average_mining_level, int):
                reduction = average_mining_level
            else:
                reduction = math.floor(np.mean(average_mining_level))

        # only calculation that applies to guardians only, rest of the scaling handled normally
        combat, aggressive, defensive = MonsterStats.from_de0(Guardian._name).unpack()
        combat.hitpoints -= PlayerStats.Combat.max_level - reduction

        reduced_guardian_stats = MonsterStats(
            combat=combat,
            aggressive=aggressive,
            defensive=defensive
        )

        super().__init__(
            name=Guardian._name,
            base_stats=reduced_guardian_stats,
            party_size=party_size,
            challenge_mode=challenge_mode,
            max_combat_level=max_combat_level,
            max_hitpoints_level=max_hitpoints_level
        )


class Tekton(CoxMonster):
    _name = 'tekton'
    _dwh_defence_multiplier_on_miss = 0.95
    _bgs_defence_reduction_on_miss = 10

    def __init__(self, party_size: int, challenge_mode: bool, max_combat_level: int = None,
                 max_hitpoints_level: int = None):
        base_stats = MonsterStats.from_de0(Tekton._name)
        super().__init__(
            name=Tekton._name,
            base_stats=base_stats,
            party_size=party_size,
            challenge_mode=challenge_mode,
            max_combat_level=max_combat_level,
            max_hitpoints_level=max_hitpoints_level
        )

    def challenge_mode_defensive_scaling_factor(self):
        return 12 / 10


class Olm(CoxMonster):
    _name: str
    _combat_level: int

    def __init__(self, party_size: int, challenge_mode: bool, max_combat_level: int = None,
                 max_hitpoints_level: int = None):
        attributes = [Monster.xerician, Monster.draconic]
        base_stats = MonsterStats.from_de0(self._name)

        super().__init__(
            name=self._name,
            base_stats=base_stats,
            party_size=party_size,
            challenge_mode=challenge_mode,
            max_combat_level=max_combat_level,
            max_hitpoints_level=max_hitpoints_level,
            combat_level=self._combat_level,
            attribute=attributes
        )

    def player_hp_scaling_factor(self):
        return 1

    def player_offensive_defensive_scaling_factor(self):
        return 1

    def party_hp_scaling_factor(self):
        n = self.party_size
        return ((n + 1) - 3*math.floor(n/8)) / 2

    def challenge_mode_hp_scaling_factor(self):
        return 1

    def phases(self):
        return min([9, 3 + math.floor(self.party_size / 8)])


class OlmHead(Olm):
    _name = 'great olm'
    _combat_level = 1043

    def __init__(self, party_size: int, challenge_mode: bool, max_combat_level: int = None,
                 max_hitpoints_level: int = None):
        super().__init__(party_size, challenge_mode, max_combat_level, max_hitpoints_level)


class OlmMeleeHand(Olm):
    _name = 'great olm (left/melee claw)'
    _combat_level = 750

    def __init__(self, party_size: int, challenge_mode: bool,
                 max_combat_level: int = None,
                 max_hitpoints_level: int = None):
        super().__init__(party_size, challenge_mode, max_combat_level, max_hitpoints_level)

    def cripple_threshold(self):
        pass


class OlmMageHand(Olm):
    _name = 'great olm (right/mage claw)'
    _combat_level = 549

    def __init__(self, party_size: int, challenge_mode: bool,
                 max_combat_level: int = None,
                 max_hitpoints_level: int = None):
        super().__init__(party_size, challenge_mode, max_combat_level, max_hitpoints_level)

# Damage Data


class Hitsplat:

    def __init__(self, damage: Union[List[int], np.array], probability: Union[List[float], np.array],
                 hitpoints_cap: int = None):
        """
        Construct a Hitsplat object from exact damage and probability information.

        :param damage:  Array-like of possible damage values.
        :param probability: Exact probabilities of corresponding damage values occurring.
        :param hitpoints_cap: If the Monster's current HP is less than the max hit, smoosh all such values into cap HP.
        """
        tolerance = 1e-6
        assert len(damage) == len(probability)
        assert tolerance > math.fabs(sum(probability) - 1)

        if not hitpoints_cap or max(damage) <= hitpoints_cap:
            self.damage = np.asarray(damage)
            self.probability = np.asarray(probability)

        else:
            self.damage = np.asarray(damage[:hitpoints_cap+1])
            self.probability = np.zeros(self.damage.shape)
            self.probability[:hitpoints_cap] = probability[:hitpoints_cap]
            self.probability[hitpoints_cap] = sum(probability[hitpoints_cap:])

        self.max_hit = self.damage.max()
        self.mean = np.dot(self.damage, self.probability)
        self.damage_dict = {}

        for d, p in zip(self.damage, self.probability):
            self.damage_dict[d] = p

    def random(self, attempts: int = 1) -> List[int]:
        return random.choices(self.damage, self.probability, k=attempts)

    @classmethod
    def from_max_hit_acc(cls, max_hit: int, accuracy: float, hitpoints_cap: int = None):
        damage = np.arange(0, max_hit+1)
        probability = [accuracy * (1 / (max_hit+1)) for d in damage]
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


class Damage:
    _seconds_per_tick = 0.6
    _ticks_per_second = 1 / _seconds_per_tick

    def __init__(self, attack_speed: int, *hitsplats: Hitsplat):
        # TODO: Make the default __iter__ behavior of this class yield hitsplats
        self.attack_speed = attack_speed
        assert len(hitsplats) > 0
        self.hitsplats = hitsplats
        self.mean = sum(hs.mean for hs in self.hitsplats)
        self.per_tick = self.mean / attack_speed
        self.per_second = self.per_tick * Damage._ticks_per_second

    def random(self, attempts: int = 1) -> List[int]:
        hits = []

        for hs in self.hitsplats:
            for rd in hs.random(attempts):
                hits.append(rd)

        return hits

    @classmethod
    def from_max_hit_acc(cls, max_hit: int, accuracy: float, attack_speed: int, hitpoints_cap: int = None):
        hs = Hitsplat.from_max_hit_acc(max_hit=max_hit, accuracy=accuracy, hitpoints_cap=hitpoints_cap)
        return cls(attack_speed, hs)


def attack_absorbing_markov_chain(player: Player, monster: Monster, special_attack: bool = False, distance: int = None):
    max_health = monster.stats.current_combat.hitpoints
    health_states = np.arange(max_health, -1, -1)  # HP, HP - 1, HP - 2, ... 2, 1, 0
    damage = player.damage_against_monster(monster, special_attack, distance)

    t = max_health  # number of transient states
    r = 1  # number of absorbing states (death)
    P_list = []  # The transition matrix is handled as a multiplication of each hitsplat matrix

    for hs in damage.hitsplats:
        Q0 = np.zeros(shape=(t, t))
        R0 = np.zeros(shape=(t, r))
        P0 = np.zeros(shape=(t + r, t + r))

        for i in range(t):
            for j in range(i, t):
                damage_dealt = j - i

                try:
                    Q0[i, j] = hs.damage_dict[damage_dealt]
                except (IndexError, KeyError):
                    pass

            if hs.max_hit >= t - i:
                R0[i, 0] = 1 - sum(Q0[i, :])

        P0[:t, :t] = Q0
        P0[:t, t:] = R0
        P0[t:, :t] = np.zeros((r, t))
        P0[t:, t:] = np.eye(r)
        P_list.append(P0)

    P = P_list[0]

    for Pi in P_list[1:]:
        P = np.dot(P, Pi)

    Q = P[:t, :t]
    R = P[:t, t:]

    absorbing_markov_chain = markov.AbsorbingMarkovChain(Q, R, health_states)
    return absorbing_markov_chain


if __name__ == '__main__':
    pass
