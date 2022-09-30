"""An estimate for the ice, ice, demon room. Decent room if you've got alts.

Pre-chop kindling & surge it down on one or two accounts. Arclight reduce if
you are able.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools import gear
from osrs_tools.character.monster.cox import IceDemon
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.data import Stances
from osrs_tools.gear import Equipment
from osrs_tools.spell import Spell, StandardSpells
from osrs_tools.strategy import CombatStrategy, MagicStrategy
from osrs_tools.style import PlayerStyle, StaffStyles
from osrs_tools.tracked_value.tracked_values import Level

###############################################################################
# default factory lists & data                                                #
###############################################################################

# data

KINDLING_POINT_CAP = int(15e3)

# default factory lists

_SURGER_GEAR = gear.AncestralSet + [
    gear.GodCapeI,
    gear.AmuletofFury,
    gear.KodaiWand,
    gear.TomeOfFire,
    gear.TormentedBracelet,
    gear.EternalBoots,
    gear.RingOfSufferingI,
]

_SURGER_RSN = "SirNargeth"

###############################################################################
# protocols
###############################################################################


class KodaiSurgeIceDemon(MagicStrategy):
    equipment = field(default_factory=lambda: Equipment().equip(*_SURGER_GEAR))
    style: PlayerStyle = StaffStyles[Stances.DEFENSIVE]
    _autocast: Spell = StandardSpells.FIRE_SURGE.value


@dataclass
class IceDemonEstimate(RoomEstimate):
    strategy: CombatStrategy
    zero_defence: bool = False
    extra_dpt: int | float = 0
    setup_ticks = 500

    def room_estimates(self) -> tuple[int, int]:
        target = IceDemon.simple(self.scale)

        if self.zero_defence:
            target.lvl.defence = Level.zero()

        dam = self.strategy.activate().damage_distribution(target)

        player_dpt = dam.per_tick
        dpt = player_dpt + self.extra_dpt

        ticks = target.base_hp // dpt
        points = target.points_per_room()
        return ticks, points
