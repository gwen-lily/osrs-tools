"""An estimate for the vespula room. Surprisingly pog for scaled solos! :3

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-16                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools.character import AbyssalPortal
from osrs_tools.cox_scaled.estimate import CombatStrategy, RoomEstimate
from osrs_tools.cox_scaled.strategy import TbowStrategy
from osrs_tools.equipment import Gear

###############################################################################
# default factory lists                                                       #
###############################################################################

_RING_OF_ENDURANCE = [Gear.from_bb("ring of endurance")]

###############################################################################
# strategy & estimate                                                         #
###############################################################################


@dataclass
class TbowPortal(TbowStrategy):
    gear = field(default_factory=lambda: _RING_OF_ENDURANCE)


@dataclass
class VespulaEstimate(RoomEstimate):
    strategy: CombatStrategy
    vulnerability: bool = True

    def room_estimates(self) -> tuple[int, int]:
        target = AbyssalPortal.from_de0(self.scale)

        if self.vulnerability:
            target.apply_vulnerability()

        self.strategy.activate()
        dam = self.strategy.damage_distribution(target)

        player_dpt = dam.per_tick
        thrall_dpt = 0  # TODO: Can thralls attack the portal?
        dpt = player_dpt + thrall_dpt

        ticks = target.base_hp // dpt
        points = target.points_per_room()
        return ticks, points
