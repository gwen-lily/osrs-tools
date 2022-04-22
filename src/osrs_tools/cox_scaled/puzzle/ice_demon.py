"""An estimate for the ice, ice, demon room. Decent room if you've got alts.

Pre-chop kindling & surge it down on one or two accounts. Arclight reduce if
you are able.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools.character import IceDemon
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.cox_scaled.strategy import CombatStrategy, MagicStrategy
from osrs_tools.data import Stances
from osrs_tools.equipment import Equipment, Gear, Weapon
from osrs_tools.spells import Spell, StandardSpells
from osrs_tools.style import PlayerStyle, StaffStyles

###############################################################################
# default factory lists & data                                                #
###############################################################################

# data

KINDLING_POINT_CAP = int(15e3)

# default factory lists

_SURGER_EXTRA_GEAR = [
    Gear.from_bb("amulet of fury"),
    Weapon.from_bb("kodai wand"),
    Gear.from_bb("tome of fire"),
    Gear.from_bb("ring of suffering (i)"),
]

_SURGER_RSN = "SirNargeth"
_SURGER_GEAR = (
    Equipment()
    .equip_basic_magic_gear(
        ancestral_set=True,
        god_cape=True,
        occult=False,
        arcane=False,
        tormented=True,
        eternal=True,
        brimstone=False,
        seers=False,
    )
    .equip(*_SURGER_EXTRA_GEAR)
    .equipped_gear
)

_DEFENSIVE_CAST = StaffStyles.get_by_stance(Stances.DEFENSIVE)

###############################################################################
# protocols
###############################################################################


class KodaiSurgeIceDemon(MagicStrategy):
    gear = field(default_factory=lambda: _SURGER_GEAR)
    style: PlayerStyle = _DEFENSIVE_CAST
    autocast: Spell = StandardSpells.FIRE_SURGE.value


@dataclass
class IceDemonEstimate(RoomEstimate):
    strategy: CombatStrategy
    zero_defence: bool = False
    extra_dpt: int | float = 0
    setup_ticks = 500

    def room_estimates(self) -> tuple[int, int]:
        target = IceDemon.from_de0(self.scale)

        if self.zero_defence:
            target.defence = 0

        dam = self.strategy.activate().damage_distribution(target)

        player_dpt = dam.per_tick
        dpt = player_dpt + self.extra_dpt

        ticks = target.base_hp // dpt
        points = target.points_per_room()
        return ticks, points
