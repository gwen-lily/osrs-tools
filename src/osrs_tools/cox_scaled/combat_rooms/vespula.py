"""An estimate for the vespula room. Surprisingly pog for scaled solos! :3

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-16                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools import gear
from osrs_tools.character.monster.cox import AbyssalPortal
from osrs_tools.cox_scaled.estimate import CombatStrategy, RoomEstimate
from osrs_tools.gear import Equipment
from osrs_tools.strategy import TbowStrategy

###############################################################################
# default factory lists                                                       #
###############################################################################

_RING_OF_ENDURANCE = [gear.RingOfEndurance]

###############################################################################
# strategy & estimate                                                         #
###############################################################################


@dataclass
class TbowPortal(TbowStrategy):
    equipment = field(default_factory=lambda: Equipment().equip(*_RING_OF_ENDURANCE))


@dataclass
class VespulaEstimate(RoomEstimate):
    strategy: CombatStrategy
    vulnerability: bool = True

    def room_estimates(self) -> tuple[int, int]:
        target = AbyssalPortal.simple(self.scale)

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
