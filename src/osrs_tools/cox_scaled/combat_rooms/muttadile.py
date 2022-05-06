"""An estimate for the muttadile room. A decent room with a semi-safespot.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools import gear
from osrs_tools.character.monster import BigMuttadile, SmallMuttadile
from osrs_tools.combat.damage import Damage
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.data import Styles
from osrs_tools.strategy import (
    CombatStrategy,
    EliteVoidStrategy,
    RangedStrategy,
    SangStrategy,
)
from osrs_tools.style import BowStyles, CrossbowStyles, PoweredStaffStyles

###############################################################################
# default factory lists                                                       #
###############################################################################

_ZCB_GEAR = [gear.ZaryteCrossbow, gear.TwistedBuckler, gear.RubyDragonBoltsE]
_FBOW_GEAR = gear.CrystalArmorSet + [gear.BowOfFaerdhinen]
_SANG_GEAR = [gear.ElysianSpiritShield]

###############################################################################
# strategy & estimate                                                         #
###############################################################################


@dataclass
class SangSmallMutta(SangStrategy):
    """Sang small mutta with an elysian offhand."""

    gear = field(default_factory=lambda: _SANG_GEAR)
    _style = PoweredStaffStyles[Styles.LONGRANGE]


@dataclass
class ZcbSmallMutta(EliteVoidStrategy):
    """Zcb small muttadile from safespot."""

    gear = field(default_factory=lambda: _ZCB_GEAR)
    _style = CrossbowStyles[Styles.LONGRANGE]


@dataclass
class FbowSmallMutta(RangedStrategy):
    """Fbow small muttadile from safespot."""

    gear = field(default_factory=lambda: _FBOW_GEAR)
    _style = BowStyles[Styles.LONGRANGE]


###############################################################################
# room estimates
###############################################################################


@dataclass
class SmallMuttadileEstimate(RoomEstimate):
    strategy: CombatStrategy
    freeze: bool = True

    def room_estimates(self) -> tuple[int, int]:
        target = SmallMuttadile.simple(self.scale)

        dam = self.strategy.activate().damage_distribution(target)

        player_dpt = dam.per_tick
        thrall_dpt = Damage.thrall().per_tick
        dpt = player_dpt + thrall_dpt

        ticks = target.hp // dpt
        points = target.points_per_room(freeze=self.freeze)
        return ticks, points


@dataclass
class BigMuttadileEstimate(RoomEstimate):
    strategy: CombatStrategy
    freeze: bool = True

    def room_estimates(self) -> tuple[int, int]:
        target = BigMuttadile.simple(self.scale)

        dam = self.strategy.activate().damage_distribution(target)

        player_dpt = dam.per_tick
        thrall_dpt = Damage.thrall().per_tick
        dpt = player_dpt + thrall_dpt

        ticks = target.base_hp // dpt
        points = target.points_per_room(freeze=self.freeze)
        return ticks, points
