"""An estimate for the mystics room. Kinda mid but it's alright.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools import gear
from osrs_tools.boost import SuperAttackPotion
from osrs_tools.character.monster.cox import SkeletalMystic
from osrs_tools.combat.damage import Damage
from osrs_tools.cox_scaled.estimate import RoomEstimate
from osrs_tools.gear import Equipment
from osrs_tools.prayer import IncredibleReflexes, Prayers, ProtectFromMagic, Rigour
from osrs_tools.strategy import CombatStrategy, DwhStrategy, RangedStrategy, TbowStrategy
from osrs_tools.tracked_value import Level
from typing_extensions import Self

###############################################################################
# default factory lists & prayers                                             #
###############################################################################

# prayers

_RIGOUR_PRAYMAGE = Prayers(name="rigour & pray mage", prayers=[Rigour, ProtectFromMagic])

# gear
_DRGIMP_GEAR = gear.InquisitorsArmourSet + [
    gear.SalveAmuletEI,
    gear.MythicalCape,
    gear.TyrannicalRingI,
]

_SIRNARGETH__GEAR = gear.CrystalArmorSet + [
    gear.SalveAmuletEI,
    gear.BookOfLaw,
    gear.BlessedBoots,
    gear.RingOfSufferingI,
    gear.RuneCrossbow,
    gear.RubyBoltsE,
]

###############################################################################
# strategy                                                                    #
###############################################################################


@dataclass
class TbowMystic(TbowStrategy):
    """Standard tbow mystics strategy."""

    prayers = _RIGOUR_PRAYMAGE
    equipment = field(default_factory=lambda: Equipment().equip(gear.SalveAmuletEI))


@dataclass
class RuneCbowMystic(RangedStrategy):
    """For the iron."""

    equipment = field(default_factory=lambda: Equipment().equip(*_SIRNARGETH__GEAR))


@dataclass
class DrGimp(DwhStrategy):
    """Strategy for hammer boppin' mystics while taking minimal points."""

    boost = SuperAttackPotion
    prayers = IncredibleReflexes
    equipment = field(default_factory=lambda: Equipment().equip(*_DRGIMP_GEAR))

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
        target = SkeletalMystic.simple(self.scale)

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
