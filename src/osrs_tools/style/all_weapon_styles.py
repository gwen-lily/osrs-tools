"""All the ones that matter at least

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from osrs_tools.data import DT, Stances, Styles

from .style import PlayerStyle
from .styles_collection import WeaponStyles

TwoHandedStyles = WeaponStyles(
    "two-handed swords",
    [
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SMASH, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
)

AxesStyles = WeaponStyles(
    "axes",
    [
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.HACK, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SMASH, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.HACK, DT.SLASH, Stances.AGGRESSIVE),
)

BluntStyles = WeaponStyles(
    "blunt weapons",
    [
        PlayerStyle(Styles.POUND, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.AGGRESSIVE),
    ],
    PlayerStyle(Styles.POUND, DT.CRUSH, Stances.ACCURATE),
)

BludgeonStyles = WeaponStyles(
    "bludgeons",
    [PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE)],
    PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),
)

BulwarkStyles = WeaponStyles(
    "bulwarks",
    [
        PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.DEFENSIVE),
)

ClawStyles = WeaponStyles(
    "claws",
    [
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.LUNGE, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
)

PickaxeStyles = WeaponStyles(
    "pickaxes",
    [
        PlayerStyle(Styles.SPIKE, DT.STAB, Stances.ACCURATE),
        PlayerStyle(Styles.IMPALE, DT.STAB, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SMASH, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.STAB, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.SMASH, DT.CRUSH, Stances.AGGRESSIVE),
)

PolearmStyles = WeaponStyles(
    "polearms",
    [
        PlayerStyle(Styles.JAB, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.FEND, DT.STAB, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.AGGRESSIVE),
)

ScytheStyles = WeaponStyles(
    "scythes",
    [
        PlayerStyle(Styles.REAP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.JAB, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.CHOP, DT.SLASH, Stances.AGGRESSIVE),
)

SlashSwordStyles = WeaponStyles(
    "slash swords",
    [
        PlayerStyle(Styles.CHOP, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.LUNGE, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.BLOCK, DT.SLASH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
)

SpearStyles = WeaponStyles(
    "spears",
    [
        PlayerStyle(Styles.LUNGE, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.CONTROLLED),
        PlayerStyle(Styles.POUND, DT.CRUSH, Stances.CONTROLLED),
        PlayerStyle(Styles.BLOCK, DT.STAB, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.LUNGE, DT.STAB, Stances.CONTROLLED),
)

SpikedWeaponsStyles = WeaponStyles(
    "spiked weapons",
    [
        PlayerStyle(Styles.POUND, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SPIKE, DT.STAB, Stances.CONTROLLED),
        PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.PUMMEL, DT.CRUSH, Stances.AGGRESSIVE),
)

StabSwordStyles = WeaponStyles(
    "stab swords",
    [
        PlayerStyle(Styles.STAB, DT.STAB, Stances.ACCURATE),
        PlayerStyle(Styles.LUNGE, DT.STAB, Stances.AGGRESSIVE),
        PlayerStyle(Styles.SLASH, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.STAB, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.LUNGE, DT.STAB, Stances.AGGRESSIVE),
)

UnarmedStyles = WeaponStyles(
    "unarmed weapons",
    [
        PlayerStyle(Styles.PUNCH, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.KICK, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.BLOCK, DT.CRUSH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.KICK, DT.CRUSH, Stances.AGGRESSIVE),
)

WhipStyles = WeaponStyles(
    "whips",
    [
        PlayerStyle(Styles.FLICK, DT.SLASH, Stances.ACCURATE),
        PlayerStyle(Styles.LASH, DT.SLASH, Stances.CONTROLLED),
        PlayerStyle(Styles.DEFLECT, DT.SLASH, Stances.DEFENSIVE),
    ],
    PlayerStyle(Styles.LASH, DT.SLASH, Stances.CONTROLLED),
)

BowStyles = WeaponStyles(
    "bow",
    [
        PlayerStyle(Styles.ACCURATE, DT.RANGED, Stances.ACCURATE),
        PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
        PlayerStyle(Styles.LONGRANGE, DT.RANGED, Stances.LONGRANGE),
    ],
    PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
)

ChinchompaStyles = WeaponStyles(
    "chinchompas",
    [
        PlayerStyle(Styles.SHORT_FUSE, DT.RANGED, Stances.ACCURATE),
        PlayerStyle(Styles.MEDIUM_FUSE, DT.RANGED, Stances.RAPID),
        PlayerStyle(Styles.LONG_FUSE, DT.RANGED, Stances.LONGRANGE),
    ],
    PlayerStyle(Styles.MEDIUM_FUSE, DT.RANGED, Stances.RAPID),
)

CrossbowStyles = WeaponStyles(
    "crossbow",
    [
        PlayerStyle(Styles.ACCURATE, DT.RANGED, Stances.ACCURATE),
        PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
        PlayerStyle(Styles.LONGRANGE, DT.RANGED, Stances.LONGRANGE),
    ],
    PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
)

ThrownStyles = WeaponStyles(
    "thrown",
    [
        PlayerStyle(Styles.ACCURATE, DT.RANGED, Stances.ACCURATE),
        PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
        PlayerStyle(Styles.LONGRANGE, DT.RANGED, Stances.LONGRANGE),
    ],
    PlayerStyle(Styles.RAPID, DT.RANGED, Stances.RAPID),
)

BladedStaffStyles = WeaponStyles(
    "bladed staves",
    [
        PlayerStyle(Styles.JAB, DT.STAB, Stances.ACCURATE),
        PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.FEND, DT.CRUSH, Stances.DEFENSIVE),
        PlayerStyle(Styles.STANDARD_SPELL, DT.MAGIC, Stances.NO_STYLE),
        PlayerStyle(Styles.DEFENSIVE_SPELL, DT.MAGIC, Stances.NO_STYLE),
    ],
    PlayerStyle(Styles.SWIPE, DT.SLASH, Stances.AGGRESSIVE),
)

PoweredStaffStyles = WeaponStyles(
    "powered staves",
    [
        PlayerStyle(Styles.ACCURATE, DT.MAGIC, Stances.ACCURATE),
        PlayerStyle(Styles.LONGRANGE, DT.MAGIC, Stances.LONGRANGE),
    ],
    PlayerStyle(Styles.ACCURATE, DT.MAGIC, Stances.ACCURATE),
)

StaffStyles = WeaponStyles(
    "staves",
    [
        PlayerStyle(Styles.BASH, DT.CRUSH, Stances.ACCURATE),
        PlayerStyle(Styles.POUND, DT.CRUSH, Stances.AGGRESSIVE),
        PlayerStyle(Styles.FOCUS, DT.CRUSH, Stances.DEFENSIVE),
        PlayerStyle(Styles.STANDARD_SPELL, DT.MAGIC, Stances.NO_STYLE),
        PlayerStyle(Styles.DEFENSIVE_SPELL, DT.MAGIC, Stances.NO_STYLE),
    ],
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
