"""An estimate for the shamans room. The best combat room in scaled cox.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools import gear
from osrs_tools.character.monster.cox import LizardmanShaman
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.data import Slayer
from osrs_tools.gear import Equipment
from osrs_tools.strategy import CombatStrategy, RedChinsSlayerStrategy
from typing_extensions import Self

###############################################################################
# default factory lists                                                       #
###############################################################################

_SLAYER_HELM = [gear.SlayerHelmetI]

###############################################################################
# strategy & estimate                                                         #
###############################################################################


@dataclass
class TaskShamans(RedChinsSlayerStrategy):
    equipment = field(default_factory=lambda: Equipment().equip(*_SLAYER_HELM))

    def misc_player(self) -> Self:
        self.player.slayer_task = Slayer.LIZARDMEN
        return super().misc_player()


@dataclass
class ShamansEstimate(RoomEstimate):
    strategy: CombatStrategy
    vulnerability: bool = True
    setup_ticks: int = 250

    def room_estimates(self) -> tuple[int, int]:
        target = LizardmanShaman.simple(self.scale)

        if self.vulnerability:
            target.apply_vulnerability()

        self.strategy.activate()
        dam = self.strategy.damage_distribution(target)

        player_dpt = dam.per_tick
        thrall_dpt = 0  # PID based attacks? inconsistent.
        dpt = player_dpt + thrall_dpt

        damage_ticks = target.base_hp // dpt
        total_ticks = sum([damage_ticks, self.setup_ticks])

        points = target.points_per_room()
        return total_ticks, points
