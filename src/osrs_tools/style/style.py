"""Styles & their containers, as well as definitions of all weapon styles.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools.data import (
    DT,
    MagicDamageTypes,
    MeleeDamageTypes,
    RangedDamageTypes,
    SpellStylesNames,
    Stances,
    Styles,
)
from osrs_tools.stats import StyleStats
from osrs_tools.tracked_value import StyleBonus

###############################################################################
# abstract class                                                              #
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


###############################################################################
# main classes                                                                #
###############################################################################


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
                cb = StyleStats()
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
                cb = StyleStats()
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
