import itertools
from dataclasses import dataclass

from osrs_tools.modifier import DT, Stances, Styles, MagicDamageTypes, MeleeDamageTypes, RangedDamageTypes, SpellStylesNames
from osrs_tools.stats import StyleStats
from osrs_tools.exceptions import OsrsException


@dataclass(eq=True)
class Style:
    """A Style object with information about combat bonuses and modifiers.
    """
    name: Styles
    damage_type: DT
    stance: Stances
    combat_bonus: StyleStats | None = None
    attack_speed_modifier: int | None = None
    attack_range_modifier: int | None = None


@dataclass(eq=True)
class PlayerStyle(Style):

    def __post_init__(self):
        attack_speed_modifier = 0
        attack_range_modifier = 0

        if self.damage_type in MeleeDamageTypes:
            if self.stance is Stances.accurate:
                self.combat_bonus = StyleStats.melee_accurate_bonuses()
            elif self.stance is Stances.aggressive:
                self.combat_bonus = StyleStats.melee_strength_bonuses()
            elif self.stance is Stances.defensive:
                self.combat_bonus = StyleStats.defensive_bonuses()
            elif self.stance is Stances.controlled:
                self.combat_bonus = StyleStats.melee_shared_bonus()
            else:
                raise NotImplementedError

        elif self.damage_type in RangedDamageTypes:
            if self.stance is Stances.accurate:
                self.combat_bonus = StyleStats.ranged_bonus()
            elif self.stance is Stances.rapid:
                self.combat_bonus = StyleStats.no_style_bonus()
                attack_speed_modifier -= 1
            elif self.stance is Stances.longrange:
                self.combat_bonus = StyleStats.defensive_bonuses()
                attack_range_modifier += 2
            else:
                raise NotImplementedError

        elif self.damage_type in MagicDamageTypes:
            if self.stance is Stances.accurate:
                self.combat_bonus = StyleStats.magic_bonus()
            elif self.stance is Stances.longrange:
                self.combat_bonus = StyleStats(defence=1)
                attack_range_modifier += 2
            elif self.stance is Stances.no_style:
                self.combat_bonus = StyleStats.no_style_bonus()
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

    @property
    def is_spell_style(self) -> bool:
        return self.stance in SpellStylesNames and self.damage_type in MagicDamageTypes

    @classmethod
    def default_style(cls):
        return cls(Styles.punch, DT.crush, Stances.accurate)


@dataclass(eq=True)
class NpcStyle(Style):
    attack_speed: int | None = None
    ignores_defence: bool = False
    ignores_prayer: bool = False


@dataclass(eq=True)
class StylesCollection:
    name: str
    styles: tuple[Style, ...]
    default: Style

    def __iter__(self):
        return iter(self.styles)

    def get_by_style(self, style: Styles) -> Style:
        for instance_style in self.styles:
            if instance_style.name is style:
                return instance_style

        raise StyleError(style)

    def get_by_dt(self, dt: DT) -> Style:
        matches = [s for s in self.styles if s.damage_type is dt]

        if (n := len(matches)) == 1:
            return matches[0]
        elif n == 0:
            raise StyleError(f'No styles with {dt}')
        else:
            raise StyleError(f'More than one style with {dt}')

    def get_by_stance(self, stance: Stances) -> Style:
        matches = [s for s in self.styles if s.stance is stance]

        if (n := len(matches)) == 1:
            return matches[0]
        elif n == 0:
            raise StyleError(f'No style with {stance}')
        else:
            raise StyleError(f'More than one style with {stance}')

    @classmethod
    def from_weapon_type(cls, weapon_type: str):
        for weapon_style_coll in AllWeaponStylesCollections:
            if weapon_type.strip().lower() == weapon_style_coll.name:
                return weapon_style_coll

        raise StyleError(weapon_type)

TwoHandedStyles = StylesCollection(
    'two-handed swords',
    (
        PlayerStyle(Styles.chop, DT.slash, Stances.accurate),
        PlayerStyle(Styles.slash, DT.slash, Stances.aggressive),
        PlayerStyle(Styles.smash, DT.crush, Stances.aggressive),
        PlayerStyle(Styles.block, DT.slash, Stances.defensive),
    ),
    PlayerStyle(Styles.slash, DT.slash, Stances.aggressive),
)

AxesStyles = StylesCollection(
    'axes',
    (
        PlayerStyle(Styles.chop, DT.slash, Stances.accurate),
        PlayerStyle(Styles.hack, DT.slash, Stances.aggressive),
        PlayerStyle(Styles.smash, DT.crush, Stances.aggressive),
        PlayerStyle(Styles.block, DT.slash, Stances.defensive),
    ),
    PlayerStyle(Styles.hack, DT.slash, Stances.aggressive),
)

BluntStyles = StylesCollection(
    'blunt weapons',
    (
        PlayerStyle(Styles.pound, DT.crush, Stances.accurate),
        PlayerStyle(Styles.pummel, DT.crush, Stances.aggressive),
        PlayerStyle(Styles.block, DT.crush, Stances.aggressive),
    ),
    PlayerStyle(Styles.pound, DT.crush, Stances.accurate),
)

BludgeonStyles = StylesCollection(
    'bludgeons',
    (
        PlayerStyle(Styles.pummel, DT.crush, Stances.aggressive),
    ),
    PlayerStyle(Styles.pummel, DT.crush, Stances.aggressive),
)

BulwarkStyles = StylesCollection(
    'bulwarks',
    (
        PlayerStyle(Styles.pummel, DT.crush, Stances.accurate),
        PlayerStyle(Styles.block, DT.crush, Stances.defensive),
    ),
    PlayerStyle(Styles.block, DT.crush, Stances.defensive),
)

ClawStyles = StylesCollection(
    'claws',
    (
        PlayerStyle(Styles.chop, DT.slash, Stances.accurate),
        PlayerStyle(Styles.slash, DT.slash, Stances.aggressive),
        PlayerStyle(Styles.lunge, DT.stab, Stances.controlled),
        PlayerStyle(Styles.block, DT.slash, Stances.defensive),
    ),
    PlayerStyle(Styles.slash, DT.slash, Stances.aggressive),
)

PickaxeStyles = StylesCollection(
    'pickaxes',
    (
        PlayerStyle(Styles.spike, DT.stab, Stances.accurate),
        PlayerStyle(Styles.impale, DT.stab, Stances.aggressive),
        PlayerStyle(Styles.smash, DT.crush, Stances.aggressive),
        PlayerStyle(Styles.block, DT.stab, Stances.defensive),
    ),
    PlayerStyle(Styles.smash, DT.crush, Stances.aggressive),
)

PolearmStyles = StylesCollection(
    'polearms',
    (
        PlayerStyle(Styles.jab, DT.stab, Stances.controlled),
        PlayerStyle(Styles.swipe, DT.slash, Stances.aggressive),
        PlayerStyle(Styles.fend, DT.stab, Stances.defensive),
    ),
    PlayerStyle(Styles.swipe, DT.slash, Stances.aggressive),
)

ScytheStyles = StylesCollection(
    'scythes',
    (
        PlayerStyle(Styles.reap, DT.slash, Stances.accurate),
        PlayerStyle(Styles.chop, DT.slash, Stances.aggressive),
        PlayerStyle(Styles.jab, DT.crush, Stances.aggressive),
        PlayerStyle(Styles.block, DT.slash, Stances.defensive),
    ),
    PlayerStyle(Styles.chop, DT.slash, Stances.aggressive),
)

SlashSwordStyles = StylesCollection(
    'slash swords',
    (
        PlayerStyle(Styles.chop, DT.slash, Stances.accurate),
        PlayerStyle(Styles.slash, DT.slash, Stances.aggressive),
        PlayerStyle(Styles.lunge, DT.stab, Stances.controlled),
        PlayerStyle(Styles.block, DT.slash, Stances.defensive),
    ),
    PlayerStyle(Styles.slash, DT.slash, Stances.aggressive),
)

SpearStyles = StylesCollection(
    'spears',
    (
        PlayerStyle(Styles.lunge, DT.stab, Stances.controlled),
        PlayerStyle(Styles.swipe, DT.slash, Stances.controlled),
        PlayerStyle(Styles.pound, DT.crush, Stances.controlled),
        PlayerStyle(Styles.block, DT.stab, Stances.defensive),
    ),
    PlayerStyle(Styles.lunge, DT.stab, Stances.controlled),
)

SpikedWeaponsStyles = StylesCollection(
    'spiked weapons',
    (
        PlayerStyle(Styles.pound, DT.crush, Stances.accurate),
        PlayerStyle(Styles.pummel, DT.crush, Stances.aggressive),
        PlayerStyle(Styles.spike, DT.stab, Stances.controlled),
        PlayerStyle(Styles.block, DT.crush, Stances.defensive),
    ),
    PlayerStyle(Styles.pummel, DT.crush, Stances.aggressive),
)

StabSwordStyles = StylesCollection(
    'stab swords',
    (
        PlayerStyle(Styles.stab, DT.stab, Stances.accurate),
        PlayerStyle(Styles.lunge, DT.stab, Stances.aggressive),
        PlayerStyle(Styles.slash, DT.slash, Stances.aggressive),
        PlayerStyle(Styles.block, DT.stab, Stances.defensive),
    ),
    PlayerStyle(Styles.lunge, DT.stab, Stances.aggressive),
)

UnarmedStyles = StylesCollection(
    'unarmed weapons',
    (
        PlayerStyle(Styles.punch, DT.crush, Stances.accurate),
        PlayerStyle(Styles.kick, DT.crush, Stances.aggressive),
        PlayerStyle(Styles.block, DT.crush, Stances.defensive),
    ),
    PlayerStyle(Styles.kick, DT.crush, Stances.aggressive),
)

WhipStyles = StylesCollection(
    'whips',
    (
        PlayerStyle(Styles.flick, DT.slash, Stances.accurate),
        PlayerStyle(Styles.lash, DT.slash, Stances.controlled),
        PlayerStyle(Styles.deflect, DT.slash, Stances.defensive),
    ),
    PlayerStyle(Styles.lash, DT.slash, Stances.controlled),
)

BowStyles = StylesCollection(
    'bow',
    (
        PlayerStyle(Styles.accurate, DT.ranged, Stances.accurate),
        PlayerStyle(Styles.rapid, DT.ranged, Stances.rapid),
        PlayerStyle(Styles.longrange, DT.ranged, Stances.longrange),
    ),
    PlayerStyle(Styles.rapid, DT.ranged, Stances.rapid),
)

ChinchompaStyles = StylesCollection(
    'chinchompas',
    (
        PlayerStyle(Styles.short_fuse, DT.ranged, Stances.accurate),
        PlayerStyle(Styles.medium_fuse, DT.ranged, Stances.rapid),
        PlayerStyle(Styles.long_fuse, DT.ranged, Stances.longrange),
    ),
    PlayerStyle(Styles.medium_fuse, DT.ranged, Stances.rapid),
)

CrossbowStyles = StylesCollection(
    'crossbow',
    (
        PlayerStyle(Styles.accurate, DT.ranged, Stances.accurate),
        PlayerStyle(Styles.rapid, DT.ranged, Stances.rapid),
        PlayerStyle(Styles.longrange, DT.ranged, Stances.longrange),
    ),
    PlayerStyle(Styles.rapid, DT.ranged, Stances.rapid),
)

ThrownStyles = StylesCollection(
    'thrown',
    (
        PlayerStyle(Styles.accurate, DT.ranged, Stances.accurate),
        PlayerStyle(Styles.rapid, DT.ranged, Stances.rapid),
        PlayerStyle(Styles.longrange, DT.ranged, Stances.longrange),
    ),
    PlayerStyle(Styles.rapid, DT.ranged, Stances.rapid),
)

BladedStaffStyles = StylesCollection(
    'bladed staves',
    (
        PlayerStyle(Styles.jab, DT.stab, Stances.accurate),
        PlayerStyle(Styles.swipe, DT.slash, Stances.aggressive),
        PlayerStyle(Styles.fend, DT.crush, Stances.defensive),
        PlayerStyle(Styles.standard_spell, DT.magic, Stances.no_style),
        PlayerStyle(Styles.defensive_spell, DT.magic, Stances.no_style),
    ),
    PlayerStyle(Styles.swipe, DT.slash, Stances.aggressive),
)

PoweredStaffStyles = StylesCollection(
    'powered staves',
    (
        PlayerStyle(Styles.accurate, DT.magic, Stances.accurate),
        PlayerStyle(Styles.longrange, DT.magic, Stances.longrange),
    ),
    PlayerStyle(Styles.accurate, DT.magic, Stances.accurate),
)

StaffStyles = StylesCollection(
    'staves',
    (
        PlayerStyle(Styles.bash, DT.crush, Stances.accurate),
        PlayerStyle(Styles.pound, DT.crush, Stances.aggressive),
        PlayerStyle(Styles.focus, DT.crush, Stances.defensive),
        PlayerStyle(Styles.standard_spell, DT.magic, Stances.no_style),
        PlayerStyle(Styles.defensive_spell, DT.magic, Stances.no_style),
    ),
    PlayerStyle(Styles.standard_spell, DT.magic, Stances.no_style),
)

AllWeaponStylesCollections = (
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
    SpikedWeaponsStyles,
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


class StyleError(OsrsException):
    pass
