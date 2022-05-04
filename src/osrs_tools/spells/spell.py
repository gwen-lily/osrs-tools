"""Spells and definition of all OSRS spells.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from osrs_tools.data import DamageValue, Level, MaximumVisibleLevel

###############################################################################
# abstract class                                                              #
###############################################################################


@dataclass(frozen=True, kw_only=True)
class Spell(ABC):
    """An abstract Spell from which concrete spells inherit.

    Attributes
    ----------

    name : str
        The name of the spell.

    base_max_hit : int
        A parameter, check the wiki.

    attack_speed : int
        The time between casts (in ticks).

    max_targets_hit : int
        The maximum number of targets hit by a spell.

    """

    name: str
    base_max_hit: DamageValue
    attack_speed: int = field(default=5, init=False)
    max_targets_hit: int = field(default=1, init=False)

    @abstractmethod
    def max_hit(self, **kwargs) -> DamageValue:
        """Define the max hit of a concrete spell class"""


###############################################################################
# main classes                                                                #
###############################################################################


class StandardSpell(Spell):
    """A spell on the standard spellbook"""

    def max_hit(self) -> DamageValue:
        return self.base_max_hit


@dataclass(frozen=True)
class GodSpell(StandardSpell):
    """A god spell unlocked in the mage arena"""

    base_max_hit: DamageValue = field(
        default_factory=lambda: DamageValue(20), init=False
    )
    charge_bonus: DamageValue = field(
        default_factory=lambda: DamageValue(10), init=False
    )

    def max_hit(self, __charged: bool, /) -> DamageValue:
        return self.base_max_hit + (__charged * self.charge_bonus)


@dataclass(frozen=True)
class AncientSpell(Spell):
    """A spell on the ancient spellbook"""

    max_targets_hit: int = field(default=1)

    def max_hit(self, /) -> DamageValue:
        return self.base_max_hit


@dataclass(frozen=True)
class PoweredSpell(Spell):
    """A spell cast from a powered staff"""

    attack_speed: int = field(default=4, init=False)

    def max_hit(self, __vis_mag_lvl: Level, /) -> DamageValue:
        """The max hit of a powered spell.

        Parameters
        ----------
        __vis_mag_lvl : Level
            The caster's visible magic level.

        Returns
        -------
        DamageValue
        """
        min_vis_lvl = Level(75, "minimum PoweredSpell visible level")

        vis_lvl_clamped = min(max(min_vis_lvl, __vis_mag_lvl), MaximumVisibleLevel)
        max_hit = self.base_max_hit + (vis_lvl_clamped - min_vis_lvl) // 3

        return max_hit
