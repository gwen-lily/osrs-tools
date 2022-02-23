import itertools
from typing import NamedTuple

from .stats import *
from src.osrs_tools.exceptions import *


# noinspection GrazieInspection
class Style:
    from src.osrs_tools import stats

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

    all_damage_types = tuple(itertools.chain.from_iterable((
        melee_damage_types,
        ranged_damage_types,
        magic_damage_types,
        typeless_damage_types
    )))

    def __init__(self,
                 name: str,
                 damage_type: str,
                 stance: str,
                 combat_bonus: StyleStats,
                 attack_speed_modifier: int = None,
                 attack_range_modifier: int = None
                 ):
        """

        :param name: The name of the style as it is displayed in game.
        :param damage_type: The category of damage the Character attempts to deal.
        :param stance: The category of style as it relates to stat boosts.
        :param combat_bonus: A StyleStats object representing the style bonuses of the style.
        :param attack_speed_modifier: An unsigned integer which is summed with the base attack speed.
        :param attack_range_modifier: An unsigned integer which is summed with the base attack range.
        """
        self.name = name
        self.damage_type = damage_type
        self.stance = stance
        self.combat_bonus = combat_bonus
        self.attack_speed_modifier = attack_speed_modifier if attack_speed_modifier else 0
        self.attack_range_modifier = attack_range_modifier if attack_range_modifier else 0

    def __repr__(self):
        string = f'{self.__class__.__name__}({self.name=}, {self.damage_type=}, {self.stance=}, {self.combat_bonus=},' \
            f' {self.attack_speed_modifier}, {self.attack_range_modifier})'
        return string

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            equivalent_attributes = (
                'name',
                'damage_type',
                'stance',
                'combat_bonus',
            )
            return any(not self.__getattribute__(a) == other.__getattribute__(a) for a in equivalent_attributes)
        else:
            return NotImplemented


class PlayerStyle(Style):
    # type ambiguous class vars
    accurate = 'accurate'
    longrange = 'longrange'
    defensive = 'defensive'
    no_style = 'no style'

    # melee style class vars
    aggressive = 'aggressive'
    controlled = 'controlled'
    melee_stances = (accurate, aggressive, defensive, controlled)

    # ranged style class vars
    rapid = 'rapid'
    ranged_stances = (accurate, rapid, longrange)

    # magic style class vars
    standard = 'standard'   # also, longrange, shared with ranged
    magic_stances = (accurate, longrange, no_style, no_style)

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
    standard_spell = 'standard spell'
    defensive_spell = 'defensive spell'

    chinchompa_style_names = (short_fuse, medium_fuse, long_fuse)
    spell_styles = (standard_spell, defensive_spell)

    def __init__(self, name: str, damage_type: str, stance: str):
        attack_speed_modifier = 0
        attack_range_modifier = 0

        if damage_type in Style.melee_damage_types:
            if stance == PlayerStyle.accurate:
                cb = StyleStats.attack_bonus()
            elif stance == PlayerStyle.aggressive:
                cb = StyleStats.strength_bonus()
            elif stance == PlayerStyle.defensive:
                cb = StyleStats.defence_bonus()
            elif stance == PlayerStyle.controlled:
                cb = StyleStats.shared_bonus()
            else:
                raise StyleError(f'{name=}{damage_type=}{stance=}')

        elif damage_type in Style.ranged_damage_types:
            if stance == PlayerStyle.accurate:
                cb = StyleStats.ranged_bonus()
            elif stance == PlayerStyle.rapid:
                cb = StyleStats.no_style_bonus()
                attack_speed_modifier -= 1
            elif stance == PlayerStyle.longrange:
                cb = StyleStats.defence_bonus()
                attack_range_modifier += 2
            else:
                raise StyleError(f'{name=}{damage_type=}{stance=}')

        elif damage_type in Style.magic_damage_types:
            if stance == PlayerStyle.accurate:
                cb = StyleStats.magic_bonus()
            elif stance == PlayerStyle.longrange:
                cb = StyleStats(defence=1)
                attack_range_modifier += 2
            elif stance == PlayerStyle.no_style:
                cb = StyleStats.no_style_bonus()
            else:
                raise StyleError(f'{name=}{damage_type=}{stance=}')

        else:
            raise StyleError(f'{name=}{damage_type=}')

        super(PlayerStyle, self).__init__(
            name=name,
            damage_type=damage_type,
            stance=stance,
            combat_bonus=cb,
            attack_speed_modifier=attack_speed_modifier,
            attack_range_modifier=attack_range_modifier
        )

    def __str__(self):
        message = f'{self.__class__.__name__}({self.name})'
        return message

    def __repr__(self):
        return self.__str__()

    def is_spell_style(self):
        return self.name in self.spell_styles and self.damage_type in self.magic_damage_types

    @classmethod
    def default_style(cls):
        return cls(cls.punch, cls.crush, cls.accurate)


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
            combat_bonus=StyleStats.npc_style_bonus(),
            attack_speed_modifier=attack_speed_modifier if attack_speed_modifier else 0,
            attack_range_modifier=attack_range_modifier if attack_range_modifier else 0
        )
        self.attack_speed = attack_speed if attack_speed else 0
        self.ignores_defence = ignores_defence if ignores_defence else False
        self.ignores_prayer = ignores_prayer if ignores_prayer else False

    def __repr__(self):
        string = f'{self.__class__.__name__}({self.name=}, {self.damage_type=}, {self.stance=}, {self.combat_bonus=},' \
            f' {self.attack_speed_modifier}, {self.attack_range_modifier}, {self.attack_speed=},' \
            f' {self.ignores_defence=}, {self.ignores_prayer=})'
        return string

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            equivalent_attributes = (
                'name',
                'damage_type',
                'stance',
                'combat_bonus',
                'attack_speed',
                'ignores_defence',
                'ignores_prayer'
            )
            return any(not self.__getattribute__(a) == other.__getattribute__(a) for a in equivalent_attributes)
        else:
            return NotImplemented

    @classmethod
    def default_style(cls):
        return cls(
            damage_type=Style.typeless,
            name='npc default',
        )


class StylesTuple(NamedTuple):
    name: str
    styles: tuple[Style, ...]


# noinspection PyArgumentList,PyTypeChecker
class WeaponStyles(NamedTuple):
    name: str
    styles: tuple[PlayerStyle, ...]
    default: PlayerStyle

    def get_style(self, name: str) -> PlayerStyle:
        for weapon_style in self.styles:
            if weapon_style.name == name.lower():
                return weapon_style

        raise StyleError(f'{name=} not found in {self.styles=}')

    def __iter__(self):
        return iter(self.styles)

    def __str__(self):
        message = f'WeaponStyles({self.name}, {self.styles}, {self.default=})'
        return message

    @classmethod
    def from_weapon_type(cls, weapon_type: str):
        for weapon_style in AllWeaponStyles:
            if weapon_type.strip().lower() == weapon_style.name:
                return weapon_style

        raise StyleError(f'{weapon_type=} was not found in {AllWeaponStyles=}')


TwoHandedStyles = WeaponStyles(
    'two-handed swords',
    (
        PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.smash, PlayerStyle.crush, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
)

AxesStyles = WeaponStyles(
    'axes',
    (
        PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.hack, PlayerStyle.slash, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.smash, PlayerStyle.crush, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.hack, PlayerStyle.slash, PlayerStyle.aggressive),
)

BluntStyles = WeaponStyles(
    'blunt weapons',
    (
        PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.aggressive),
    ),
    PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.accurate),
)

BludgeonStyles = WeaponStyles(
    'bludgeons',
    (
        PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.aggressive),
    ),
    PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.aggressive),
)

BulwarkStyles = WeaponStyles(
    'bulwarks',
    (
        PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.defensive),
)

ClawStyles = WeaponStyles(
    'claws',
    (
        PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.controlled),
        PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
)

PickaxeStyles = WeaponStyles(
    'pickaxes',
    (
        PlayerStyle(PlayerStyle.spike, PlayerStyle.stab, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.impale, PlayerStyle.stab, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.smash, PlayerStyle.crush, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.block, PlayerStyle.stab, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.smash, PlayerStyle.crush, PlayerStyle.aggressive),
)

PolearmStyles = WeaponStyles(
    'polearms',
    (
        PlayerStyle(PlayerStyle.jab, PlayerStyle.stab, PlayerStyle.controlled),
        PlayerStyle(PlayerStyle.swipe, PlayerStyle.slash, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.fend, PlayerStyle.stab, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.swipe, PlayerStyle.slash, PlayerStyle.aggressive),
)

ScytheStyles = WeaponStyles(
    'scythes',
    (
        PlayerStyle(PlayerStyle.reap, PlayerStyle.slash, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.jab, PlayerStyle.crush, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.aggressive),
)

SlashSwordStyles = WeaponStyles(
    'slash swords',
    (
        PlayerStyle(PlayerStyle.chop, PlayerStyle.slash, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.controlled),
        PlayerStyle(PlayerStyle.block, PlayerStyle.slash, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
)

SpearStyles = WeaponStyles(
    'spears',
    (
        PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.controlled),
        PlayerStyle(PlayerStyle.swipe, PlayerStyle.slash, PlayerStyle.controlled),
        PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.controlled),
        PlayerStyle(PlayerStyle.block, PlayerStyle.stab, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.controlled),
)

SpikedWeapons = WeaponStyles(
    'spiked weapons',
    (
        PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.spike, PlayerStyle.stab, PlayerStyle.controlled),
        PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.pummel, PlayerStyle.crush, PlayerStyle.aggressive),
)

StabSwordStyles = WeaponStyles(
    'stab swords',
    (
        PlayerStyle(PlayerStyle.stab, PlayerStyle.stab, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.slash, PlayerStyle.slash, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.block, PlayerStyle.stab, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.lunge, PlayerStyle.stab, PlayerStyle.aggressive),
)

UnarmedStyles = WeaponStyles(
    'unarmed weapons',
    (
        PlayerStyle(PlayerStyle.punch, PlayerStyle.crush, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.kick, PlayerStyle.crush, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.block, PlayerStyle.crush, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.kick, PlayerStyle.crush, PlayerStyle.aggressive),
)

WhipStyles = WeaponStyles(
    'whips',
    (
        PlayerStyle(PlayerStyle.flick, PlayerStyle.slash, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.lash, PlayerStyle.slash, PlayerStyle.controlled),
        PlayerStyle(PlayerStyle.deflect, PlayerStyle.slash, PlayerStyle.defensive),
    ),
    PlayerStyle(PlayerStyle.lash, PlayerStyle.slash, PlayerStyle.controlled),
)

BowStyles = WeaponStyles(
    'bow',
    (
        PlayerStyle(PlayerStyle.accurate, PlayerStyle.ranged, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
        PlayerStyle(PlayerStyle.longrange, PlayerStyle.ranged, PlayerStyle.longrange),
    ),
    PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
)

ChinchompaStyles = WeaponStyles(
    'chinchompas',
    (
        PlayerStyle(PlayerStyle.short_fuse, PlayerStyle.ranged, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.medium_fuse, PlayerStyle.ranged, PlayerStyle.rapid),
        PlayerStyle(PlayerStyle.long_fuse, PlayerStyle.ranged, PlayerStyle.longrange),
    ),
    PlayerStyle(PlayerStyle.medium_fuse, PlayerStyle.ranged, PlayerStyle.rapid),
)

CrossbowStyles = WeaponStyles(
    'crossbow',
    (
        PlayerStyle(PlayerStyle.accurate, PlayerStyle.ranged, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
        PlayerStyle(PlayerStyle.longrange, PlayerStyle.ranged, PlayerStyle.longrange),
    ),
    PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
)

ThrownStyles = WeaponStyles(
    'thrown',
    (
        PlayerStyle(PlayerStyle.accurate, PlayerStyle.ranged, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
        PlayerStyle(PlayerStyle.longrange, PlayerStyle.ranged, PlayerStyle.longrange),
    ),
    PlayerStyle(PlayerStyle.rapid, PlayerStyle.ranged, PlayerStyle.rapid),
)

BladedStaffStyles = WeaponStyles(
    'bladed staves',
    (
        PlayerStyle(PlayerStyle.jab, PlayerStyle.stab, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.swipe, PlayerStyle.slash, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.fend, PlayerStyle.crush, PlayerStyle.defensive),
        PlayerStyle(PlayerStyle.standard_spell, PlayerStyle.magic, PlayerStyle.no_style),
        PlayerStyle(PlayerStyle.defensive_spell, PlayerStyle.magic, PlayerStyle.no_style),
    ),
    PlayerStyle(PlayerStyle.swipe, PlayerStyle.slash, PlayerStyle.aggressive),
)

PoweredStaffStyles = WeaponStyles(
    'powered staves',
    (
        PlayerStyle(PlayerStyle.accurate, PlayerStyle.magic, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.longrange, PlayerStyle.magic, PlayerStyle.longrange),
    ),
    PlayerStyle(PlayerStyle.accurate, PlayerStyle.magic, PlayerStyle.accurate),
)

StaffStyles = WeaponStyles(
    'staves',
    (
        PlayerStyle(PlayerStyle.bash, PlayerStyle.crush, PlayerStyle.accurate),
        PlayerStyle(PlayerStyle.pound, PlayerStyle.crush, PlayerStyle.aggressive),
        PlayerStyle(PlayerStyle.focus, PlayerStyle.crush, PlayerStyle.defensive),
        PlayerStyle(PlayerStyle.standard_spell, PlayerStyle.magic, PlayerStyle.no_style),
        PlayerStyle(PlayerStyle.defensive_spell, PlayerStyle.magic, PlayerStyle.no_style),
    ),
    PlayerStyle(PlayerStyle.standard_spell, PlayerStyle.magic, PlayerStyle.no_style),
)

AllWeaponStyles = (
    TwoHandedStyles,
    AxesStyles,
    BluntStyles,
    BludgeonStyles,
    BulwarkStyles,
    ClawStyles,
    PickaxeStyles,
    PolearmStyles,
    ScytheStyles,
    SlashSwordStyles,
    SpearStyles,
    SpikedWeapons,
    StabSwordStyles,
    UnarmedStyles,
    WhipStyles,
    BowStyles,
    ChinchompaStyles,
    CrossbowStyles,
    ThrownStyles,
    BladedStaffStyles,
    PoweredStaffStyles,
    StaffStyles,
)


class NpcAttacks(NamedTuple):
    name: str
    styles: tuple[NpcStyle, ...]

    def get_style(self, style_name: str) -> NpcStyle:
        for sty in self.styles:
            if sty.name == style_name:
                return sty
        raise StyleError


class StyleError(OsrsException):
    pass
