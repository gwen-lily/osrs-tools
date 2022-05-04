"""An estimate for the muttadile room. A decent room with a semi-safespot.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools.character import BigMuttadile, SmallMuttadile
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.cox_scaled.strategy import (
    CombatStrategy,
    EliteVoidStrategy,
    RangedStrategy,
    SangStrategy,
)
from osrs_tools.damage import Damage
from osrs_tools.data import Styles
from osrs_tools.equipment import Equipment, Gear, SpecialWeapon
from osrs_tools.style.style import BowStyles, CrossbowStyles, PoweredStaffStyles

###############################################################################
# default factory lists                                                       #
###############################################################################

_ZCB_GEAR = (
    Equipment()
    .equip_crossbow(SpecialWeapon.from_bb("zaryte crossbow"), buckler=True, rubies=True)
    .equipped_gear
)
_CROSSBOW_LONGRANGE = CrossbowStyles.get_by_style(Styles.LONGRANGE)

_FBOW_GEAR = Equipment().equip_crystal_bowfa(crystal_set=True).equipped_gear
_FBOW_RAPID = BowStyles.get_by_style(Styles.LONGRANGE)

_SANG_GEAR = [Gear.from_bb("elysian spirit shield")]
_SANG_LONGRANGE = PoweredStaffStyles.get_by_style(Styles.LONGRANGE)

###############################################################################
# strategy & estimate                                                         #
###############################################################################


@dataclass
class SangSmallMutta(SangStrategy):
    """Sang small mutta with an elysian offhand."""

    gear = field(default_factory=lambda: _SANG_GEAR)
    _style = _SANG_LONGRANGE


@dataclass
class ZcbSmallMutta(EliteVoidStrategy):
    """Zcb small muttadile from safespot."""

    gear = field(default_factory=lambda: _ZCB_GEAR)
    _style = _CROSSBOW_LONGRANGE


@dataclass
class FbowSmallMutta(RangedStrategy):
    """Fbow small muttadile from safespot."""

    gear = field(default_factory=lambda: _FBOW_GEAR)
    _style = _FBOW_RAPID


###############################################################################
# room estimates
###############################################################################


@dataclass
class SmallMuttadileEstimate(RoomEstimate):
    strategy: CombatStrategy
    freeze: bool = True

    def room_estimates(self) -> tuple[int, int]:
        target = SmallMuttadile.from_de0(self.scale)

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
        target = BigMuttadile.from_de0(self.scale)

        dam = self.strategy.activate().damage_distribution(target)

        player_dpt = dam.per_tick
        thrall_dpt = Damage.thrall().per_tick
        dpt = player_dpt + thrall_dpt

        ticks = target.base_hp // dpt
        points = target.points_per_room(freeze=self.freeze)
        return ticks, points
