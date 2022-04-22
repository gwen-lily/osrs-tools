"""Styles & their containers, as well as definitions of all weapon styles.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from dataclasses import dataclass, field
from typing import Any

from osrs_tools.data import (
    DT,
    MagicDamageTypes,
    MeleeDamageTypes,
    RangedDamageTypes,
    SpellStylesNames,
    Stances,
    StyleBonus,
    Styles,
)
from osrs_tools.exceptions import OsrsException
from osrs_tools.stats import StyleStats

###############################################################################
# errors 'n such                                                              #
###############################################################################


class StyleError(OsrsException):
    pass


###############################################################################
# style                                                                       #
###############################################################################


@dataclass
class Style:
    """A Style object with information about combat bonuses and modifiers.

    Attributes
    ----------

    name : Styles
        The name of the style.

    damage_type : DT
        The damage type.

    stance : Stances
        The stance.

    attack_speed_modifier : int, optional
        The modifier to attack speed in ticks.

    attack_range_modifier : int, optional
        The modifier to attack range in tiles.
    """

    name: Styles
    damage_type: DT
    stance: Stances
    _combat_bonus: StyleStats | None = field(init=False, default=None)
    attack_speed_modifier: int = 0
    attack_range_modifier: int = 0

    @property
    def combat_bonus(self) -> StyleStats:
        """Type validation for _combat_bonus"""
        assert isinstance(self._combat_bonus, StyleStats)
        return self._combat_bonus

    @combat_bonus.setter
    def combat_bonus(self, __value: StyleStats, /):
        self._combat_bonus = __value


@dataclass
class PlayerStyle(Style):
    """A PlayerStyle object with information about combat bonuses and modifiers.

    Attributes
    ----------

    name : Styles
        The name of the style.

    damage_type : DT
        The damage type.

    stance : Stances
        The stance.

    attack_speed_modifier : int, optional
        The modifier to attack speed in ticks.

    attack_range_modifier : int, optional
        The modifier to attack range in tiles.
    """

    def __post_init__(self):

        if (dt := self.damage_type) in MeleeDamageTypes:
            if (st := self.stance) is Stances.ACCURATE:
                cb = StyleStats.melee_accurate_bonuses()
            elif st is Stances.AGGRESSIVE:
                cb = StyleStats.melee_strength_bonuses()
            elif st is Stances.DEFENSIVE:
                cb = StyleStats.defensive_bonuses()
            elif st is Stances.CONTROLLED:
                cb = StyleStats.melee_shared_bonus()
            else:
                raise NotImplementedError

        elif dt in RangedDamageTypes:
            if (st := self.stance) is Stances.ACCURATE:
                cb = StyleStats.ranged_bonus()
            elif st is Stances.RAPID:
                cb = StyleStats.no_style_bonus()
                self.attack_speed_modifier -= 1
            elif st is Stances.LONGRANGE:
                cb = StyleStats.defensive_bonuses()
                self.attack_range_modifier += 2
            else:
                raise NotImplementedError

        elif dt in MagicDamageTypes:
            if (st := self.stance) is Stances.ACCURATE:
                cb = StyleStats.magic_bonus()
            elif st is Stances.LONGRANGE:
                cb = StyleStats(defence=StyleBonus(1, "long range"))
                self.attack_range_modifier += 2
            elif st is Stances.NO_STYLE:
                cb = StyleStats.no_style_bonus()
            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

        self.combat_bonus = cb

    @property
    def is_spell_style(self) -> bool:
        return self.name in SpellStylesNames and self.damage_type in MagicDamageTypes


@dataclass
class MonsterStyle(Style):
    """A MonsterStyle object with information about combat bonuses and modifiers.

    Attributes
    ----------

    name : Styles
        The name of the style.

    damage_type : DT
        The damage type.

    stance : Stances
        The stance.

    attack_speed_modifier : int, optional
        The modifier to attack speed in ticks.

    attack_range_modifier : int, optional
        The modifier to attack range in tiles.

    ignores_defence : bool, optional
        Set to True to ignore defence. Defaults to False.

    ignores_prayer : bool, optional
        Set to True to ignore prayer. Defaults to False.
    """

    _attack_speed: int | None = None
    ignores_defence: bool = False
    ignores_prayer: bool = False

    @property
    def attack_speed(self) -> int:
        assert isinstance(self._attack_speed, int)
        return self._attack_speed

    @attack_speed.setter
    def attack_speed(self, __value: int):
        self._attack_speed = __value


###############################################################################
# styles collection                                                           #
###############################################################################


@dataclass
class StylesCollection:
    name: str
    styles: list[Style]
    default: Style

    def __iter__(self):
        yield from self.styles

    def __getattribute__(self, __name: str | Styles | DT | Stances) -> Any:
        """Direct lookup for Style, DT, & Stances.

        Parameters
        ----------
        __name : str | Styles | DT | Stances
            The attribute name.

        Returns
        -------
        Any
        """

        if isinstance(__name, str):
            return super().__getattribute__(__name)

        elif isinstance(__name, Styles):
            for _style in self.styles:
                if __name is _style.name:
                    return _style

            raise AttributeError(__name)

        elif isinstance(__name, DT):
            matches = [_s for _s in self.styles if _s.damage_type is __name]

            if (n := len(matches)) == 1:
                return matches[0]
            elif n == 0:
                raise ValueError(__name)
            else:
                raise ValueError(__name, matches)

        elif isinstance(__name, Stances):
            matches = [_s for _s in self.styles if _s.stance is __name]

            if (n := len(matches)) == 1:
                return matches[0]
            elif n == 0:
                raise ValueError(__name)
            else:
                raise ValueError(__name, matches)

        else:
            raise TypeError(__name)

    def get_by_style(self, style: Styles) -> Style:

        # for instance_style in self.styles:
        #     if instance_style.name is style:
        #         return instance_style
        #
        # raise ValueError(style)
        raise DeprecationWarning

    def get_by_dt(self, damage_type: DT) -> Style:

        # matches = [s for s in self.styles if s.damage_type is damage_type]
        #
        # if (n := len(matches)) == 1:
        #     return matches[0]
        # elif n == 0:
        #     raise ValueError(f"No styles with {damage_type}")
        # else:
        #     raise ValueError(f"More than one style with {damage_type}")
        raise DeprecationWarning

    def get_by_stance(self, stance: Stances) -> Style:

        # matches = [s for s in self.styles if s.stance is stance]
        #
        # if (n := len(matches)) == 1:
        #     return matches[0]
        # elif n == 0:
        #     raise ValueError(f"No style with {stance}")
        # else:
        #     raise ValueError(f"More than one style with {stance}")
        raise DeprecationWarning

    @classmethod
    def from_weapon_type(cls, weapon_type: str):
        for weapon_style_coll in AllWeaponStylesCollections:
            if weapon_type.strip().lower() == weapon_style_coll.name:
                return weapon_style_coll

        raise StyleError(weapon_type)


@dataclass(eq=True)
class WeaponStyles(StylesCollection):
    default: PlayerStyle

    def get_by_style(self, style: Styles) -> PlayerStyle:
        _style = self.__getattribute__(style)
        assert isinstance(_style, PlayerStyle)

        return _style

    def get_by_dt(self, damage_type: DT) -> PlayerStyle:
        _style = self.__getattribute__(damage_type)
        assert isinstance(_style, PlayerStyle)

        return _style

    def get_by_stance(self, stance: Stances) -> PlayerStyle:
        _style = self.__getattribute__(stance)
        assert isinstance(_style, PlayerStyle)

        return _style


@dataclass(eq=True)
class NpcStyles(StylesCollection):
    default: MonsterStyle

    def get_by_style(self, style: Styles) -> MonsterStyle:
        _style = self.__getattribute__(style)
        assert isinstance(_style, MonsterStyle)

        return _style

    def get_by_dt(self, damage_type: DT) -> MonsterStyle:
        _style = self.__getattribute__(damage_type)
        assert isinstance(_style, MonsterStyle)

        return _style

    def get_by_stance(self, stance: Stances) -> MonsterStyle:
        _style = self.__getattribute__(stance)
        assert isinstance(_style, MonsterStyle)

        return _style


# complete weapon styles definition ###########################################

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
