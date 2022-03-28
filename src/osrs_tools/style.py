import itertools
from dataclasses import dataclass

from osrs_tools.data import (
    DT,
    MagicDamageTypes,
    MeleeDamageTypes,
    RangedDamageTypes,
    SpellStylesNames,
    Stances,
    Styles,
)
from osrs_tools.exceptions import OsrsException
from osrs_tools.stats import StyleStats


@dataclass(eq=True)
class Style:
    """A Style object with information about combat bonuses and modifiers."""

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
            if self.stance is Stances.ACCURATE:
                self.combat_bonus = StyleStats.melee_accurate_bonuses()
            elif self.stance is Stances.AGGRESSIVE:
                self.combat_bonus = StyleStats.melee_strength_bonuses()
            elif self.stance is Stances.DEFENSIVE:
                self.combat_bonus = StyleStats.defensive_bonuses()
            elif self.stance is Stances.CONTROLLED:
                self.combat_bonus = StyleStats.melee_shared_bonus()
            else:
                raise NotImplementedError

        elif self.damage_type in RangedDamageTypes:
            if self.stance is Stances.ACCURATE:
                self.combat_bonus = StyleStats.ranged_bonus()
            elif self.stance is Stances.RAPID:
                self.combat_bonus = StyleStats.no_style_bonus()
                attack_speed_modifier -= 1
            elif self.stance is Stances.LONGRANGE:
                self.combat_bonus = StyleStats.defensive_bonuses()
                attack_range_modifier += 2
            else:
                raise NotImplementedError

        elif self.damage_type in MagicDamageTypes:
            if self.stance is Stances.ACCURATE:
                self.combat_bonus = StyleStats.magic_bonus()
            elif self.stance is Stances.LONGRANGE:
                self.combat_bonus = StyleStats(defence=1)
                attack_range_modifier += 2
            elif self.stance is Stances.NO_STYLE:
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
        return cls(Styles.PUNCH, DT.CRUSH, Stances.ACCURATE)


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
            raise StyleError(f"No styles with {dt}")
        else:
            raise StyleError(f"More than one style with {dt}")

    def get_by_stance(self, stance: Stances) -> Style:
        matches = [s for s in self.styles if s.stance is stance]

        if (n := len(matches)) == 1:
            return matches[0]
        elif n == 0:
            raise StyleError(f"No style with {stance}")
        else:
            raise StyleError(f"More than one style with {stance}")

    @classmethod
    def from_weapon_type(cls, weapon_type: str):
        for weapon_style_coll in AllWeaponStylesCollections:
            if weapon_type.strip().lower() == weapon_style_coll.name:
                return weapon_style_coll

        raise StyleError(weapon_type)


TwoHandedStyles = StylesCollection(
    "two-handed swords",
    (
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SMASH, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
)

AxesStyles = StylesCollection(
    "axes",
    (
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.HACK, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SMASH, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.HACK, DT.SLASH, Stances.AGGRESSIVE),
)

BluntStyles = StylesCollection(
    "blunt weapons",
    (
        PlayerStyle(Styles.POUND, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.AGGRESSIVE),
    ),
    PlayerStyle(Styles.POUND, DT.CRUSH, Stances.ACCURATE),
)

BludgeonStyles = StylesCollection(
    "bludgeons",
    (PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),),
    PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),
)

BulwarkStyles = StylesCollection(
    "bulwarks",
    (
        PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.DEFENSIVE),
)

ClawStyles = StylesCollection(
    "claws",
    (
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.LUNGE, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
)

PickaxeStyles = StylesCollection(
    "pickaxes",
    (
        PlayerStyle(Styles.SPIKE, DT.STAB, Stances.ACCURATE),
        PlayerStyle(Styles.IMPALE, DT.STAB, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SMASH, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.STAB, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.SMASH, DT.CRUSH, Stances.AGGRESSIVE),
)

PolearmStyles = StylesCollection(
    "polearms",
    (
        PlayerStyle(Styles.JAB, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.FEND, DT.STAB, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.AGGRESSIVE),
)

ScytheStyles = StylesCollection(
    "scythes",
    (
        PlayerStyle(Styles.REAP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.JAB, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.CHOP, DT.SLASH, Stances.AGGRESSIVE),
)

SlashSwordStyles = StylesCollection(
    "slash swords",
    (
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.LUNGE, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
)

SpearStyles = StylesCollection(
    "spears",
    (
        PlayerStyle(Styles.LUNGE, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.CONTROLLED),
        PlayerStyle(Styles.POUND, DT.CRUSH, Stances.CONTROLLED),
        PlayerStyle(Styles.BLOCK, DT.STAB, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.LUNGE, DT.STAB, Stances.CONTROLLED),
)

SpikedWeaponsStyles = StylesCollection(
    "spiked weapons",
    (
        PlayerStyle(Styles.POUND, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SPIKE, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),
)

StabSwordStyles = StylesCollection(
    "stab swords",
    (
        PlayerStyle(Styles.STAB, DT.STAB, Stances.ACCURATE),
        PlayerStyle(Styles.LUNGE, DT.STAB, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.STAB, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.LUNGE, DT.STAB, Stances.AGGRESSIVE),
)

UnarmedStyles = StylesCollection(
    "unarmed weapons",
    (
        PlayerStyle(Styles.PUNCH, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.KICK, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.KICK, DT.CRUSH, Stances.AGGRESSIVE),
)

WhipStyles = StylesCollection(
    "whips",
    (
        PlayerStyle(Styles.FLICK, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.LASH, DT.SLASH, Stances.CONTROLLED),
        PlayerStyle(Styles.DEFLECT, DT.SLASH, Stances.DEFENSIVE),
    ),
    PlayerStyle(Styles.LASH, DT.SLASH, Stances.CONTROLLED),
)

BowStyles = StylesCollection(
    "bow",
    (
        PlayerStyle(Styles.ACCURATE, DT.RANGED, Stances.ACCURATE),
        PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
        PlayerStyle(Styles.LONGRANGE, DT.RANGED, Stances.LONGRANGE),
    ),
    PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
)

ChinchompaStyles = StylesCollection(
    "chinchompas",
    (
        PlayerStyle(Styles.SHORT_FUSE, DT.RANGED, Stances.ACCURATE),
        PlayerStyle(Styles.MEDIUM_FUSE, DT.RANGED, Stances.RAPID),
        PlayerStyle(Styles.LONG_FUSE, DT.RANGED, Stances.LONGRANGE),
    ),
    PlayerStyle(Styles.MEDIUM_FUSE, DT.RANGED, Stances.RAPID),
)

CrossbowStyles = StylesCollection(
    "crossbow",
    (
        PlayerStyle(Styles.ACCURATE, DT.RANGED, Stances.ACCURATE),
        PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
        PlayerStyle(Styles.LONGRANGE, DT.RANGED, Stances.LONGRANGE),
    ),
    PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
)

ThrownStyles = StylesCollection(
    "thrown",
    (
        PlayerStyle(Styles.ACCURATE, DT.RANGED, Stances.ACCURATE),
        PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
        PlayerStyle(Styles.LONGRANGE, DT.RANGED, Stances.LONGRANGE),
    ),
    PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
)

BladedStaffStyles = StylesCollection(
    "bladed staves",
    (
        PlayerStyle(Styles.JAB, DT.STAB, Stances.ACCURATE),
        PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.FEND, DT.CRUSH, Stances.DEFENSIVE),
        PlayerStyle(Styles.STANDARD_SPELL, DT.MAGIC, Stances.NO_STYLE),
        PlayerStyle(Styles.DEFENSIVE_SPELL, DT.MAGIC, Stances.NO_STYLE),
    ),
    PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.AGGRESSIVE),
)

PoweredStaffStyles = StylesCollection(
    "powered staves",
    (
        PlayerStyle(Styles.ACCURATE, DT.MAGIC, Stances.ACCURATE),
        PlayerStyle(Styles.LONGRANGE, DT.MAGIC, Stances.LONGRANGE),
    ),
    PlayerStyle(Styles.ACCURATE, DT.MAGIC, Stances.ACCURATE),
)

StaffStyles = StylesCollection(
    "staves",
    (
        PlayerStyle(Styles.BASH, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.POUND, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.FOCUS, DT.CRUSH, Stances.DEFENSIVE),
        PlayerStyle(Styles.STANDARD_SPELL, DT.MAGIC, Stances.NO_STYLE),
        PlayerStyle(Styles.DEFENSIVE_SPELL, DT.MAGIC, Stances.NO_STYLE),
    ),
    PlayerStyle(Styles.STANDARD_SPELL, DT.MAGIC, Stances.NO_STYLE),
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
