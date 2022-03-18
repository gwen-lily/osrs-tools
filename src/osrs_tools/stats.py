from __future__ import annotations
from dataclasses import dataclass, field, fields, astuple
from functools import total_ordering
from typing import NamedTuple
from copy import copy

from osrs_tools.modifier import CallableLevelsModifierType, Level, CallableLevelsModifier, LevelModifier, MonsterCombatSkills, Skills, StyleBonus
from osrs_tools.exceptions import OsrsException
import osrs_tools.resource_reader as rr


@dataclass
class Stats:
    """Base stats class.
    """
    def __copy__(self):
        unpacked = tuple(getattr(self, field.name) for field in fields(self))
        return self.__class__(*(copy(x) for x in unpacked))

# TODO: Validate @dataclass / @total_ordering decorater order importance


@dataclass
@total_ordering
class PlayerLevels(Stats):
    attack: Level | None = None
    strength: Level | None = None
    defence: Level | None = None
    ranged: Level | None = None
    prayer: Level | None = None
    magic: Level | None = None
    runecraft: Level | None = None
    hitpoints: Level | None = None
    crafting: Level | None = None
    mining: Level | None = None
    smithing: Level | None = None
    fishing: Level | None = None
    cooking: Level | None = None
    firemaking: Level | None = None
    woodcutting: Level | None = None
    agility: Level | None = None
    herblore: Level | None = None
    thieving: Level | None = None
    fletching: Level | None = None
    slayer: Level | None = None
    farming: Level | None = None
    construction: Level | None = None
    hunter: Level | None = None


    def __add__(self, other: PlayerLevels | CallableLevelsModifier) -> PlayerLevels:
        if isinstance(other, PlayerLevels):
            new_vals = []
            for skill in Skills:
                self_val = self.__getattribute__(skill.name)
                other_val = self.__getattribute__(skill.name)

                if self_val is not None and other_val is None:
                    new_vals.append(self_val)
                elif self_val is None and other_val is not None:
                    new_vals.append(other_val)
                else:
                    new_vals.append(self_val + other_val)
            
            return PlayerLevels(*new_vals)
            
        elif isinstance(other, CallableLevelsModifier):
            modified = copy(self)
            for skill in other.skills:
                if (self_val := modified.__getattribute__(skill.name)) is None:
                    continue
                elif isinstance(self_val, Level):
                    new_val = other.func(self_val)
                    modified.__setattr__(skill.name, new_val)

            return modified
            
        else:
            raise NotImplementedError

    def __sub__(self, other: PlayerLevels) -> PlayerLevels:
        if isinstance(other, PlayerLevels):
            new_vals = []
            for skill in Skills:
                self_val = self.__getattribute__(skill.name)
                other_val = self.__getattribute__(skill.name)

                if self_val is not None and other_val is None:
                    new_vals.append(self_val)
                elif self_val is None and other_val is not None:
                    raise StatsError(f'Subtraction between None and {other_val}')
                else:
                    new_vals.append(self_val - other_val)
            
            return PlayerLevels(*new_vals)
        else:
            raise NotImplementedError

    def __lt__(self, other: PlayerLevels) -> bool:
        if isinstance(other, PlayerLevels):
            for skill in Skills:
                self_val = self.__getattribute__(skill.name)
                other_val = self.__getattribute__(skill.name)

                if self_val is not None and other_val is not None:
                    if not self_val < other_val:                
                        return False
            
            return True
        else:
            raise NotImplementedError

    def __eq__(self, other: PlayerLevels) -> bool:
        if isinstance(other, PlayerLevels):
            for skill in Skills:
                self_val = self.__getattribute__(skill.name)
                other_val = other.__getattribute__(skill.name)

                if self_val is not None and other_val is not None:
                    if self_val != other_val:
                        return False
                elif self_val is None and other_val is None:
                    continue
                elif self_val is not None and other_val is None:
                    return False
                elif self_val is None and other_val is not None:
                    return False

            return True
        else:
            raise NotImplementedError

    def max_levels_per_skill(self, other: PlayerLevels) -> PlayerLevels:
        skill_vals_dict = {}
        for skill in Skills:
            self_val = self.__getattribute__(skill.name)
            other_val = other.__getattribute__(skill.name)

            if self_val is not None and other_val is None:
                value = self_val
            elif self_val is None and other_val is not None:
                value = other_val
            elif self_val is None and other_val is None:
                value = None
            else:
                value = max([self_val, other_val])

            skill_vals_dict[skill.name] = value

        return PlayerLevels(**skill_vals_dict)

    @staticmethod
    def max_skill_level() -> Level:
        return Level(99, 'max skill level')

    def min_skill_level(self, skill: Skills) -> Level:
        comment = 'min skill level'
        if skill is Skills.hitpoints:
            value = 10
        else:
            value = 1

        return Level(value, comment)

    @classmethod
    def maxed_player(cls):
        maxed_levels = (Level(99, 'max skill level') for _ in range(23))
        return cls(*maxed_levels)

    @classmethod
    def no_requirements(cls):
        # min_level_values = [*(1, )*7, 10, *(1, )*15]    # 10 for Skills.hitpoints
        # min_levels = (Level(lvl, 'min skill level') for lvl in min_level_values)
        # return cls(*min_levels)
        return cls()

    @classmethod
    def zeros(cls):
        return cls(*(Level(0) for _ in Skills))

    @classmethod
    def from_rsn(cls, rsn: str):
        hs = rr.lookup_player_highscores(rsn)
        levels = [Level(hs.__getattribute__(skill.name).level, f'{rsn}: {skill.name}') for skill in Skills]
        return cls(*levels)


@total_ordering
@dataclass
class MonsterLevels(Stats):
    attack: Level | None = None
    strength: Level | None = None
    defence: Level | None = None
    ranged: Level | None = None
    magic: Level | None = None
    hitpoints: Level | None = None


    def __add__(self, other: MonsterLevels) -> MonsterLevels:
        if isinstance(other, MonsterLevels):
            new_vals = []
            for skill in MonsterCombatSkills:
                self_val = self.__getattribute__(skill.name)
                other_val = self.__getattribute__(skill.name)

                if self_val is not None and other_val is None:
                    new_vals.append(self_val)
                elif self_val is None and other_val is not None:
                    new_vals.append(other_val)
                else:
                    new_vals.append(self_val + other_val)
            
            return MonsterLevels(*new_vals)
                        
        else:
            raise NotImplementedError

    def __sub__(self, other: MonsterLevels) -> MonsterLevels:
        if isinstance(other, MonsterLevels):
            new_vals = []
            for skill in MonsterCombatSkills:
                self_val = self.__getattribute__(skill.name)
                other_val = self.__getattribute__(skill.name)

                if self_val is not None and other_val is None:
                    new_vals.append(self_val)
                elif self_val is None and other_val is not None:
                    raise StatsError(f'Subtraction between None and {other_val}')
                else:
                    new_vals.append(self_val - other_val)
            
            return MonsterLevels(*new_vals)
                        
        else:
            raise NotImplementedError

    def __lt__(self, other: MonsterLevels) -> bool:
        if isinstance(other, MonsterLevels):
            for skill in MonsterCombatSkills:
                self_val = self.__getattribute__(skill.name)
                other_val = self.__getattribute__(skill.name)

                if self_val is not None and other_val is not None:
                    if not self_val < other_val:                
                        return False
            
            return True
        else:
            raise NotImplementedError

    def __eq__(self, other: MonsterLevels) -> bool:
        if isinstance(other, MonsterLevels):
            for skill in MonsterCombatSkills:
                self_val = self.__getattribute__(skill.name)
                other_val = other.__getattribute__(skill.name)

                if self_val is not None and other_val is not None:
                    if self_val != other_val:
                        return False
                elif self_val is None and other_val is None:
                    continue
                elif self_val is not None and other_val is None:
                    return False
                elif self_val is None and other_val is not None:
                    return False

            return True
        else:
            raise NotImplementedError

    @classmethod
    def from_bb(cls, name: str):
        mon_df = rr.lookup_normal_monster_by_name(name)
        return cls(
            mon_df[Skills.attack.name].values[0],
            mon_df[Skills.strength.name].values[0],
            mon_df[Skills.defence.name].values[0],
            mon_df[Skills.ranged.name].values[0],
            mon_df[Skills.magic.name].values[0],
            mon_df[Skills.hitpoints.name].values[0],
        )

    @classmethod
    def dummy_levels(cls, hitpoints: Level | int = None):
        hp = hitpoints if hitpoints is not None else 1000

        return cls(
            Level(1),
            Level(1),
            Level(0),
            Level(1),
            Level(1),
            Level(int(hp))
        )

    @classmethod
    def zeros(cls):
        return cls(*(Level(0) for _ in MonsterCombatSkills))

@dataclass
class StyleStats(Stats):
    """Integer container class for validation, security, and logging.
    """
    melee_attack: StyleBonus | None = field(default=None)
    melee_strength: StyleBonus | None = field(default=None)
    defence: StyleBonus | None = field(default=None)
    ranged_attack: StyleBonus | None = field(default=None)
    ranged_strength: StyleBonus | None = field(default=None)
    magic_attack: StyleBonus | None = field(default=None)

    @classmethod
    def melee_shared_bonus(cls):
        value = 1
        comment = 'shared style'
        return cls(
            melee_attack=StyleBonus(value, comment),
            melee_strength=StyleBonus(value, comment),
            defence=StyleBonus(value, comment)
        )

    @classmethod
    def melee_accurate_bonuses(cls):
        value = 3
        comment = 'accurate style'
        return cls(melee_attack=StyleBonus(value, comment))

    @classmethod
    def melee_strength_bonuses(cls):
        value = 3
        comment = 'aggressive style'
        return cls(melee_strength=StyleBonus(value, comment))

    @classmethod
    def defensive_bonuses(cls):
        value = 3
        comment = 'defensive style'
        return cls(defence=StyleBonus(value, comment))

    @classmethod
    def ranged_bonus(cls):
        value = 3
        comment = 'ranged (accurate) style'
        return cls(
            ranged_attack=StyleBonus(value, comment),
            ranged_strength=StyleBonus(value, comment)
        )

    @classmethod
    def magic_bonus(cls):
        value = 3
        comment = 'magic (accurate) style'
        return cls(magic_attack=StyleBonus(value, comment))

    @classmethod
    def npc_bonus(cls):
        value = 1
        comment = 'npc style'
        return cls(
            melee_attack=StyleBonus(value, comment),
            melee_strength=StyleBonus(value, comment),
            defence=StyleBonus(value, comment),
            ranged_attack=StyleBonus(value, comment),
            magic_attack=StyleBonus(value, comment)
        )

    @classmethod
    def no_style_bonus(cls):
        return cls()


@dataclass
class AggressiveStats(Stats):
    """Class with information relevant to offensive damage calculation.

    Included attributes are attack bonus values: stab, slash, crush, magic attack, ranged attack,
    melee strength, ranged strength, and magic strength (not to be confused with magic damage).
    This class stores magic strength (float modifier) as opposed to percentile magic damage (percentage)
    """
    stab: int = 0
    slash: int = 0
    crush: int = 0
    magic_attack: int = 0
    ranged_attack: int = 0
    melee_strength: int = 0
    ranged_strength: int = 0
    magic_strength: float = 0

    def __add__(self, other: int | AggressiveStats) -> AggressiveStats:
        if isinstance(other, int):
            if other == 0:
                return copy(self)
            else:
                raise NotImplementedError
        elif isinstance(other, AggressiveStats):
            new_vals = {}
            
            for f in fields(self):
                self_val = getattr(self, f.name)
                other_val = getattr(other, f.name)
                new_vals[f.name] = self_val + other_val
        else:
            raise NotImplementedError
        
        return AggressiveStats(**new_vals)

    def __radd__(self, other: int) -> AggressiveStats:
        if isinstance(other, int):
            if other == 0:
                return copy(self)
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

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

    @classmethod
    def from_osrsbox(cls, name: str):
        raise NotImplementedError


@dataclass
class DefensiveStats(Stats):
    """Class with information relevant to defensive damage calculation.

    Included attributes are defence bonus values: stab, slash, crush, magic, & ranged.
    """
    stab: int = 0
    slash: int = 0
    crush: int = 0
    magic: int = 0
    ranged: int = 0

    def __add__(self, other: int | DefensiveStats) -> DefensiveStats:
        if isinstance(other, int):
            if other == 0:
                return copy(self)
            else:
                raise NotImplementedError
        elif isinstance(other, DefensiveStats):
            new_vals = {}
            
            for f in fields(self):
                self_val = getattr(self, f.name)
                other_val = getattr(other, f.name)
                new_vals[f.name] = self_val + other_val
        else:
            raise NotImplementedError
        
        return DefensiveStats(**new_vals)

    def __radd__(self, other: int) -> DefensiveStats:
        if isinstance(other, int):
            if other == 0:
                return copy(self)
            else:
                raise NotImplementedError
        else:
            raise NotImplementedError

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

    @classmethod
    def from_osrsbox(cls, name: str):
        raise NotImplementedError


class Boost(NamedTuple):
    name: str
    modifiers: CallableLevelsModifier | tuple[CallableLevelsModifier]


class CallableLevelsModifierBuilder:

    @staticmethod
    def create_simple_callable(base: int, ratio: float, negative: bool = None, comment: str = None) -> CallableLevelsModifierType:
        f"""
        Generator function for easily writing Boost class methods.

        OSRS boosts tend to have the form: boost(level) = base_boost + math.floor(ratio_boost*level).
        This method simplifies definition to one line of the form: [f': (int, float, bool | None)] -> [f: (int,) -> int].
        
        :param base: Note that's "base boost", not to be confused with the "bass boost" you might find on your speaker. 
        :param ratio: Get ratio'd nerd.
        :param negative: No positive vibes allowed. Listen to gy!be.
        :return: f: (int,) -> int
        """

        def inner_builder(lvl: Level) -> Level:
            ratio_mod = LevelModifier(float(ratio), comment)
            if negative is not None and negative is True:
                new_lvl = lvl - (base + (lvl * ratio_mod))
            else:
                new_lvl = lvl + (base + (lvl * ratio_mod))

            return new_lvl

        return inner_builder

    def create_simple_callable_modifiers(
        self,
        skills: Skills | tuple[Skills],
        base: int,
        ratio: float,
        negative: bool = False,
        comment: str | None = None
    ) -> list[CallableLevelsModifier]:
        """Construct callable modifiers that only depend on the skill being modified.

        A perfect use case for this constructor would be the Super Combat Potion, which
        boosts three skills (Attack, Strength, Defence) by the same modifier.

        Args:
            skills (Skills | tuple[Skills]): A Skills enum or list of Skills enums.
            base (int): _description_
            ratio (float): _description_
            negative (bool, optional): _description_. Defaults to False.
            comment (str | None, optional): _description_. Defaults to None.

        Returns:
            list[CallableLevelsModifier]: _description_
        """
        if isinstance(skills, Skills):
            skills_tup = tuple(skills)
        elif isinstance(skills, tuple):
            skills_tup = skills
        else:
            raise TypeError(skills)

        modifiers: list[CallableLevelsModifier] = []

        for skill in skills_tup:
            callable = self.create_simple_callable(base, ratio, negative, comment)
            modifiers.append(CallableLevelsModifier((skill, ), callable, comment))

        return modifiers


clmb = CallableLevelsModifierBuilder()
super_combat_callable = clmb.create_simple_callable(5, 0.15, comment='super combat potion')
ranged_callable = clmb.create_simple_callable(4, 0.10, comment='ranging potion')
magic_callable = clmb.create_simple_callable(4, 0, comment='magic potion')
combat_potion_callable = clmb.create_simple_callable(3, 0.10, comment='combat potion')

prayer_callable_no_wrench = clmb.create_simple_callable(7, 0.25, comment='prayer potion')
prayer_callable_wrench = clmb.create_simple_callable(7, 0.27, comment='prayer potion (wrench)')

super_restore_callable_no_wrench = clmb.create_simple_callable(8, 0.25, comment='super restore')
super_restore_callable_wrench = clmb.create_simple_callable(8, 0.27, comment='super restore (wrench)')
sanfew_serum_callable_no_wrench = clmb.create_simple_callable(4, 0.30, comment='sanfew serum')
sanfew_serum_callable_wrench = clmb.create_simple_callable(4, 0.32, comment='sanfew serum (wrench)')

saradomin_brew_debuff_skills = (Skills.attack, Skills.strength, Skills.ranged, Skills.magic)
saradomin_brew_debuff_callable = clmb.create_simple_callable(2, 0.10, True, comment='sara brew (debuff)')
saradomin_brew_defence_callable = clmb.create_simple_callable(2, 0.20, comment='sara brew')
saradomin_brew_hitpoints_callable = clmb.create_simple_callable(2, 0.15, comment='sara brew')

ancient_brew_debuff_skills = (Skills.attack, Skills.strength, Skills.defence)
ancient_brew_debuffs = clmb.create_simple_callable_modifiers(ancient_brew_debuff_skills, 2, 0.10, True, 'ancient brew (debuff)')

overload_buffs_skills = (Skills.attack, Skills.strength, Skills.defence, Skills.ranged, Skills.magic)
overload_buffs = clmb.create_simple_callable_modifiers(overload_buffs_skills, 6, 0.16, comment='overload (+)')
overload_hitpoints_callable = clmb.create_simple_callable(50, 0, True, 'overload damage')

SuperAttackPotion = Boost(
    'super attack potion',
    CallableLevelsModifier(
        (Skills.attack, ),
        super_combat_callable,
        'super attack'
    )
)

SuperStrengthPotion = Boost(
    'super strength potion',
    CallableLevelsModifier(
        (Skills.strength, ),
        super_combat_callable,
        'super strength'
    )
)

SuperDefencePotion = Boost(
    'super defence potion',
    CallableLevelsModifier(
        (Skills.defence, ),
        super_combat_callable,
        'super defence'
    )
)

SuperCombatPotion = Boost(
    'super combat potion',
    (SuperAttackPotion, SuperStrengthPotion, SuperDefencePotion)
)

RangingPotion = Boost(
    'ranging potion',
    CallableLevelsModifier(
        (Skills.ranged, ),
        ranged_callable,
        'ranging'
    )
)

BastionPotion = Boost(
    'bastion potion',
    (RangingPotion, SuperDefencePotion)
)

MagicPotion = Boost(
    'magic potion',
    CallableLevelsModifier(
        (Skills.magic, ),
        magic_callable,
        'magic'
    )
)

BattlemagePotion = Boost(
    'battlemage potion',
    (SuperDefencePotion, MagicPotion)
)

ImbuedHeart = Boost(
    'imbued heart',
    CallableLevelsModifier(
        (Skills.magic, ),
        clmb.create_simple_callable(1, 0.10),
        "imbued heart"
    )
)

AttackPotion = Boost(
    'attack potion',
    CallableLevelsModifier(
        (Skills.attack, ),
        combat_potion_callable,
        'attack'
    )
)

StrengthPotion = Boost(
    'strength potion',
    CallableLevelsModifier(
        (Skills.strength, ),
        combat_potion_callable,
        'strength'
    )
)

DefencePotion = Boost(
    'defence potion',
    CallableLevelsModifier(
        (Skills.defence, ),
        combat_potion_callable,
        'defence'
    )
)

CombatPotion = Boost(
    'combat potion',
    (AttackPotion, StrengthPotion)
)

PrayerPotion = Boost(
    'prayer potion',
    CallableLevelsModifier(
        (Skills.prayer, ),
        prayer_callable_no_wrench,
        'prayer (no wrench)'
    )
)

PrayerPotionWrench = Boost(
    'prayer potion (holy wrench)',
    CallableLevelsModifier(
        (Skills.prayer, ),
        prayer_callable_wrench,
        'prayer (wrench)'
    )
)

super_restore_clms = []
super_restore_clms_wrench = []
sanfew_clms = []
sanfew_clms_wrench = []

for skill in Skills:
    if skill is Skills.prayer:
        super_restore_clms.append(
            CallableLevelsModifier(
                (skill, ),
                super_restore_callable_no_wrench,
                'super restore (no wrench)'
            )
        )
        super_restore_clms_wrench.append(
            CallableLevelsModifier(
                (skill, ),
                super_restore_callable_wrench,
                'super restore (wrench)'
            )
        )
        sanfew_clms.append(
            CallableLevelsModifier(
                (skill, ),
                sanfew_serum_callable_no_wrench,
                'sanfew serum (no wrench)'
            )
        )
        sanfew_clms_wrench.append(
            CallableLevelsModifier(
                (skill, ),
                sanfew_serum_callable_wrench,
                'sanfew serum (wrench)'
            )
        )
    else:
        sr_callable = super_restore_callable_no_wrench
        ss_callable = sanfew_serum_callable_no_wrench

        sr_lm = CallableLevelsModifier(
            (skill, ),
            sr_callable,
            'super restore'
        )
        ss_lm = CallableLevelsModifier(
            (skill, ),
            ss_callable,
            'sanfew serum'
        )

        super_restore_clms.append(sr_lm)
        super_restore_clms_wrench.append(sr_lm)
        sanfew_clms.append(ss_lm)
        sanfew_clms_wrench.append(ss_lm)

SuperRestore = Boost('super restore', tuple(super_restore_clms))
SuperRestoreWrench = Boost('super restore (holy wrench)', tuple(super_restore_clms_wrench))
SanfewSerum = Boost('sanfew serum', sanfew_clms)
SanfewSerumWrench = Boost('sanfew serum (holy wrench)', sanfew_clms_wrench)

saradomin_brew_clms = []

for skill in saradomin_brew_debuff_skills:
    saradomin_brew_debuff_levels_modifier = CallableLevelsModifier(
        (skill, ),
        saradomin_brew_debuff_callable,
        'saradomin brew (debuff)'
    )
    saradomin_brew_clms.append(saradomin_brew_debuff_levels_modifier)

saradomin_brew_clms.append(CallableLevelsModifier(
    (Skills.defence, ),
    saradomin_brew_debuff_callable,
    'saradomin brew (buff)'
))

saradomin_brew_clms.append(CallableLevelsModifier(
    (Skills.hitpoints, ),
    saradomin_brew_hitpoints_callable,
    'saradomin brew (buff)'
))

SaradominBrew = Boost('saradomin brew', tuple(saradomin_brew_clms))

zamorak_brew_clms = [
    CallableLevelsModifier(
        (Skills.attack, ),
        clmb.create_simple_callable(2, 0.20),
        'zamorak brew (buff)'
    ),
    CallableLevelsModifier(
        (Skills.strength, ),
        clmb.create_simple_callable(2, 0.12),
        'zamorak brew (buff)'
    ),
    CallableLevelsModifier(
        (Skills.defence, ),
        clmb.create_simple_callable(2, 0.10, True),
        'zamorak brew (debuff)'
    ),
    CallableLevelsModifier(
        (Skills.hitpoints, ),
        clmb.create_simple_callable(0, 0.12, True),
        'zamorak brew (debuff)'
    ),
    CallableLevelsModifier(
        (Skills.prayer, ),
        clmb.create_simple_callable(0, 0.10),
        'zamorak brew (buff)'
    )
]

ZamorakBrew = Boost('zamorak brew', tuple(zamorak_brew_clms))

ancient_brew_clms = [*ancient_brew_debuffs,
                     CallableLevelsModifier(
                         (Skills.prayer, ),
                         clmb.create_simple_callable(2, 0.10),
                         'ancient brew (buff)'
                     ),
                     CallableLevelsModifier(
                         (Skills.magic, ),
                         clmb.create_simple_callable(2, 0.05),
                         'ancient brew (buff)'
                     )
                     ]

AncientBrew = Boost('ancient brew', tuple(ancient_brew_clms))

overload_clms = [*overload_buffs,
                 CallableLevelsModifier(
                     (Skills.hitpoints, ),
                     overload_hitpoints_callable,
                     'overload (hp)')
                 ]

Overload = Boost('overload (+)', tuple(overload_clms))


class StatsError(OsrsException):
    pass
