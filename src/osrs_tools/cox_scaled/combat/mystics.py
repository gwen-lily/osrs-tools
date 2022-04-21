"""An estimate for the mystics room. Kinda mid but it's alright.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools.character import SkeletalMystic
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.cox_scaled.strategy import (
    CombatStrategy,
    DwhStrategy,
    RangedStrategy,
    TbowStrategy,
)
from osrs_tools.damage import Damage
from osrs_tools.equipment import Equipment, Gear, Weapon
from osrs_tools.modifier import Level
from osrs_tools.prayer import (
    IncredibleReflexes,
    PrayerCollection,
    ProtectFromMagic,
    Rigour,
)
from osrs_tools.stats import SuperAttackPotion
from typing_extensions import Self

###############################################################################
# default factory lists & prayers                                             #
###############################################################################

# prayers

_RIGOUR_PRAYMAGE = PrayerCollection(
    name="rigour & pray mage", prayers=[Rigour, ProtectFromMagic]
)

# gear

_DRGIMP_EXTRA_GEAR = [
    Gear.from_bb("dwarven helmet"),
    Gear.from_bb("mythical cape"),
    Gear.from_bb("bandos chestplate"),
    Gear.from_bb("bandos tassets"),
    Gear.from_bb("tyrannical (i)"),
]

_SIRNARGETH_EXTRA_GEAR = [
    Gear.from_bb("god d'hide coif"),
    Gear.from_bb("book of law"),
    Gear.from_bb("god d'hide boots"),
    Gear.from_bb("ring of suffering (i)"),
]

_SALVE_GEAR = Equipment().equip_salve().equipped_gear
_DRGIMP_GEAR = (
    Equipment().equip_salve(e=True, i=True).equip(*_DRGIMP_EXTRA_GEAR).equipped_gear
)
_SIRNARGETH_GEAR = (
    Equipment()
    .equip_basic_ranged_gear(pegasian=False, brimstone=False)
    .equip_crystal_set(barrows=True)
    .equip_salve(e=True, i=True)
    .equip_crossbow(Weapon.from_bb("rune crossbow"), rubies=True)
    .equip(*_SIRNARGETH_EXTRA_GEAR)
    .equipped_gear
)

###############################################################################
# strategy                                                                    #
###############################################################################


@dataclass
class TbowMystic(TbowStrategy):
    """Standard tbow mystics strategy."""

    prayers = _RIGOUR_PRAYMAGE
    gear = field(default_factory=lambda: _SALVE_GEAR)


@dataclass
class RuneCbowMystic(RangedStrategy):
    """For the iron."""

    gear = field(default_factory=lambda: _SIRNARGETH_GEAR)


@dataclass
class DrGimp(DwhStrategy):
    """Strategy for hammer boppin' mystics while taking minimal points."""

    boost = SuperAttackPotion
    prayers = IncredibleReflexes
    gear = field(default_factory=lambda: _DRGIMP_GEAR)

    def boost_player(self) -> Self:
        """Gimp the doctor with 20 strength."""
        super().boost_player()
        self.player.levels.strength = Level(20, "the gimp's greatest trick")

        return self


###############################################################################
# estimate                                                                    #
###############################################################################


@dataclass
class MysticsEstimate(RoomEstimate):
    strategy: CombatStrategy
    specialist_strategy: DwhStrategy
    _scale_at_load_time: int | None = None
    spec_transfer_alts: int = 6
    dwh_target_per_mystic: int = 3
    setup_ticks: int = 200

    def __post_init__(self) -> None:
        if self._scale_at_load_time is None:
            self._scale_at_load_time = self.scale

    @property
    def scale_at_load_time(self) -> int:
        assert isinstance(self._scale_at_load_time, int)
        return self._scale_at_load_time

    def room_estimates(self) -> tuple[int, int]:
        target = SkeletalMystic.from_de0(self.scale)

        dam = self.strategy.activate().damage_distribution(target)

        player_dpt = dam.per_tick
        thrall_dpt = Damage.thrall().per_tick
        total_dpt = sum([player_dpt, thrall_dpt])
        assert total_dpt != 0
        total_hp = target.base_hp * target.count_per_room(self.scale_at_load_time)

        damage_ticks = total_hp // total_dpt
        total_ticks = sum([damage_ticks, self.setup_ticks])

        points = target.points_per_room(scale_at_load_time=self._scale_at_load_time)

        return total_ticks, points
