"""An estimate for the tightrope room. The best puzzle room in scaled cox.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass

from osrs_tools.character import DeathlyMage, DeathlyRanger
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.cox_scaled.strategy import CombatStrategy, RedChinsStrategy
from osrs_tools.modifier import Styles
from osrs_tools.style import ChinchompaStyles, PlayerStyle

###############################################################################
# roppa gangnam style                                                        #
###############################################################################

_LONG_FUSE = ChinchompaStyles.get_by_style(Styles.LONG_FUSE)

###############################################################################
# strategy & estimate                                                         #
###############################################################################


@dataclass
class ChinRope(RedChinsStrategy):
    """Elite void red chin strategy with long range."""

    style: PlayerStyle = _LONG_FUSE


@dataclass
class RopeEstimate(RoomEstimate):
    strategy: CombatStrategy
    vulnerability: bool = True
    setup_ticks: int = 200

    def room_estimates(self) -> tuple[int, int]:
        mage = DeathlyMage.from_de0(self.scale)
        ranger = DeathlyRanger.from_de0(self.scale)

        if self.vulnerability:
            mage.apply_vulnerability()
            ranger.apply_vulnerability()

        self.strategy.activate()
        dam_mage = self.strategy.damage_distribution(mage)
        dam_ranger = self.strategy.damage_distribution(ranger)

        player_dpt_mage = dam_mage.per_tick
        player_dpt_ranger = dam_ranger.per_tick
        thrall_dpt = 0  # PID based attacks? inconsistent.
        dpt_mage = player_dpt_mage + thrall_dpt
        dpt_ranger = player_dpt_ranger + thrall_dpt

        damage_ticks_mage = mage.base_hp // dpt_mage
        damage_ticks_ranger = ranger.base_hp // dpt_ranger
        ticks = [damage_ticks_mage, damage_ticks_ranger, self.setup_ticks]
        total_ticks = sum(ticks)

        points = mage.points_per_room() + ranger.points_per_room()
        return total_ticks, points
