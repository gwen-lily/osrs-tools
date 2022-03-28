from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

from osrs_tools.character import CoxMonster, Player
from osrs_tools.damage import Damage
from osrs_tools.equipment import Equipment
from osrs_tools.prayer import Rigour
from osrs_tools.stats import Boost
from osrs_tools.style import PlayerStyle

###############################################################################
# email:    noahgill409@gmail.com
# created:  2022-03-27
###############################################################################

###############################################################################
# protocols
###############################################################################


class ScaledCoxStrategy(Protocol):
    def equip_player(self, player: Player, **kwargs):
        ...

    def boost_player(self, player: Player, boost: Boost, **kwargs):
        ...

    def pray_player(self, player: Player, **kwargs):
        ...

    def damage_target(self, player: Player, target: CoxMonster, **kwargs) -> Damage:
        ...


class TbowStrategy:
    def equip_player(self, player: Player):
        player.equipment = Equipment.no_equipment()
        player.equipment.equip_basic_ranged_gear()
        player.equipment.equip_arma_set(zaryte=True)
        player.active_style = player.equipment.equip_twisted_bow()

        assert player.equipment.full_set

    def boost_player(self, player: Player, boost: Boost):
        player.boost(boost)

    def pray_player(self, player: Player):
        player.reset_prayers()
        player.pray(Rigour)

    def damage_target(self, player: Player, target: CoxMonster, **kwargs) -> Damage:
        options = {}
        options.update(kwargs)
        dam = player.damage_distribution(target, **options)
        return dam


class ZcbStrategy:
    def equip_player(self, player: Player, style: PlayerStyle):
        player.equipment = Equipment.no_equipment()
        player.equipment.equip_basic_ranged_gear()
        player.equipment.equip_arma_set(zaryte=True)
        player.active_style = player.equipment.equip_zaryte_crossbow(
            buckler=True, rubies=True, style=style
        )

        assert player.equipment.full_set

    def boost_player(self, player: Player, boost: Boost):
        player.boost(boost)

    def pray_player(self, player: Player):
        player.reset_prayers()
        player.pray(Rigour)

    def damage_target(self, player: Player, target: CoxMonster, **kwargs) -> Damage:
        options = {}
        options.update(kwargs)
        dam = player.damage_distribution(target, **options)
        return dam


###############################################################################
# main
###############################################################################


@dataclass
class RoomEstimate(ABC):
    scale: int

    @abstractmethod
    def room_estimates(self) -> tuple[int, int]:  # type: ignore
        """Generic room_estimates method which returns ticks & points.

        Returns:
            tuple[int, int]: (ticks, points)
        """
