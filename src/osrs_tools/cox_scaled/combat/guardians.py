"""An estimate for the guardians room. A good lad that you can boof quick.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools.character import Guardian
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.cox_scaled.strategy import CombatStrategy, MeleeStrategy
from osrs_tools.data import Level
from osrs_tools.equipment import Gear, SpecialWeapon

###############################################################################
# default factory lists & extra info                                          #
###############################################################################

MAIN_RSN = "SirBedevere"
HYBRID_RSN = "decihybrid"

# additional gear handled
_MAIN_GEAR = [
    Gear.from_bb("amulet of blood fury"),
    SpecialWeapon.from_bb("dragon pickaxe"),
    Gear.from_bb("bandos chestplate"),
    Gear.from_bb("avernic defender"),
    Gear.from_bb("bandos tassets"),
    Gear.from_bb("brimstone ring"),
]

_HYBRID_GEAR = [
    Gear.from_bb("neitiznot helm"),
    Gear.from_bb("fire cape"),
    SpecialWeapon.from_bb("dragon pickaxe"),
    Gear.from_bb("god d'hide body"),
    Gear.from_bb("dragon defender"),
    Gear.from_bb("god d'hide legs"),
    Gear.from_bb("regen bracelet"),
    Gear.from_bb("dragon boots"),
]

###############################################################################
# protocols
###############################################################################


@dataclass
class MainFit(MeleeStrategy):
    """Main dps account, full melee bis."""

    gear = field(default_factory=lambda: _MAIN_GEAR)


@dataclass
class HybridFit(MeleeStrategy):
    gear = field(default_factory=lambda: _HYBRID_GEAR)


@dataclass
class GuardiansEstimate(RoomEstimate):
    strategy: CombatStrategy
    alt_strategy: CombatStrategy
    defence_estimate = Level(15, "an honest estimate")
    damage_alts: int = 0
    setup_ticks = 300

    def room_estimates(self) -> tuple[int, int]:
        target = Guardian.from_de0(self.scale)
        target.defence = self.defence_estimate

        main_dam = self.strategy.activate().damage_distribution(target)
        alt_dam = self.alt_strategy.activate().damage_distribution(target)

        main_dpt = main_dam.per_tick
        alt_dpt = self.damage_alts * alt_dam.per_tick

        total_dpt = main_dpt + alt_dpt
        total_hp = target.base_hp * target.count_per_room()

        damage_ticks = total_hp // total_dpt
        total_ticks = damage_ticks + self.setup_ticks

        points = target.points_per_room()
        return total_ticks, points
