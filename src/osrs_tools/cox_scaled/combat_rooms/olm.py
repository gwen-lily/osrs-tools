"""An estimate for olm, the final boss. It assumes basic competency.

TL;DR ring of endurance + thralls & blood fury, minimal range switch to allow
for 10 stams. Assume proper brewing practice and you probably wanna pray mage
at all times on melee. (#TODO: Test that claim)

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-17                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from osrs_tools import gear
from osrs_tools.character.monster.cox import OlmHead, OlmMageHand, OlmMeleeHand
from osrs_tools.character.monster.cox.olm import OlmABC
from osrs_tools.cox_scaled.data import MeleeAttackPattern, RangedAttackPattern
from osrs_tools.cox_scaled.estimate import MonsterEstimate, RoomEstimate
from osrs_tools.strategy import (
    BgsStrategy,
    CombatStrategy,
    DwhStrategy,
    MeleeStrategy,
    SangStrategy,
    TbowStrategy,
)

###############################################################################
# default factory lists                                                       #
###############################################################################

_MAGE_GEAR = [
    gear.BookOfTheDead,
    gear.RingOfEndurance,
]

_RANGED_GEAR = [
    gear.TorvaFullHelm,
    gear.PrimordialBoots,
    gear.RingOfEndurance,
]

_MELEE_GEAR = [
    gear.AmuletofBloodFury,
    gear.BandosChestplate,
    gear.BandosTassets,
    gear.RingOfEndurance,
]


_DHLANCE_GEAR = _MELEE_GEAR[:] + [gear.DragonHunterLance, gear.AvernicDefender]

_DWH_GEAR = _MELEE_GEAR[:] + [
    gear.DragonWarhammer,
    gear.AvernicDefender,
]

_BGS_GEAR = _MELEE_GEAR[:] + [gear.BandosGodsword]

###############################################################################
# strategies                                                                  #
###############################################################################


@dataclass
class SangOlm(SangStrategy):
    gear = field(default_factory=lambda: _MAGE_GEAR)


@dataclass
class TbowOlm(TbowStrategy):
    gear = field(default_factory=lambda: _RANGED_GEAR)


@dataclass
class DwhOlm(DwhStrategy):
    gear = field(default_factory=lambda: _DWH_GEAR)


@dataclass
class BgsOlm(BgsStrategy):
    gear = field(default_factory=lambda: _BGS_GEAR)


@dataclass
class DHLanceOlm(MeleeStrategy):
    gear = field(default_factory=lambda: _DHLANCE_GEAR)


###############################################################################
# estimates                                                                   #
###############################################################################


@dataclass
class OlmEstimate(MonsterEstimate):
    """Functionally an ABC."""

    monster: OlmABC
    thralls = True


@dataclass
class OlmHeadEstimate(OlmEstimate):
    monster: OlmHead
    vulnerability: bool = False
    head_strategy: RangedAttackPattern = RangedAttackPattern.FOUR_TO_ONE

    def ticks_per_unit(self, **kwargs) -> int:
        """Find the ticks to kill olm head."""

        dam = self._get_dam(**kwargs)

        if (_hs := self.head_strategy) is RangedAttackPattern.FOUR_TO_ONE:
            dpt_fraction = 15 / 16
        elif _hs is RangedAttackPattern.TWO_TO_ZERO:
            dpt_fraction = (2 * dam.attack_speed) / 16
        else:
            raise NotImplementedError

        return self._get_ticks(dam, dpt_fraction)


@dataclass
class OlmMageHandEstimate(OlmEstimate):
    monster: OlmMageHand


@dataclass
class OlmMeleeHandEstimate(MonsterEstimate):
    """An estimate for the olm melee hand.

    Set zero_defence to True if your olm is sufficiently big (>23) or so. If
    not, specify a dwh_strategy and bgs_strategy to get a good estimate.

    Attributes
    ----------
    monster: OlmMeleeHand
        The type of the monster

    main_strategy : CombatStrategy
        The strategy for dealing damage.

    thralls: bool
        Set to True if using thralls. Defaults to True

    zero_defence: bool
        Set to True if you can safely assume that the hand will be zero
        defence. Defaults to True.

    damage_strategy: CombatStrategy
        The damage strategy to use. Defaults to DHLanceOlm

    dwh_strategy: DwhStrategy
        The dwh strategy to use. Defaults to DwhOlm.

    bgs_strategy: BgsStrategy
        The bgs strategy to use. Defaults to BgsOlm.
    """

    monster: OlmMeleeHand
    main_strategy: CombatStrategy
    thralls: bool = True
    zero_defence: bool = True
    dwh_strategy: DwhStrategy | None = None
    bgs_strategy: BgsStrategy | None = None
    attack_pattern: MeleeAttackPattern = MeleeAttackPattern.FOUR_TO_ONE

    def ticks_per_unit(self, **kwargs) -> int:
        """Get the ticks to kill an olm melee hand.

        For now, only works with zero defence estimation.
        """
        # TODO: Add non-zero defence methods with markov chains

        if not self.zero_defence:
            raise NotImplementedError

        dam = self._get_dam(**kwargs)

        if (_ap := self.attack_pattern) is MeleeAttackPattern.FOUR_TO_ONE:
            dpt_fraction = 1.0
        elif _ap is MeleeAttackPattern.ONE_TO_ZERO:
            dpt_fraction = dam.attack_speed / 8
        elif _ap is MeleeAttackPattern.CHAD_FACETANK:
            dpt_fraction = 1.0  # fix later, less than 1.0
        else:
            raise NotImplementedError

        return self._get_ticks(dam, dpt_fraction)


@dataclass
class OlmRoomEstimate(RoomEstimate):
    head_estimate: OlmHeadEstimate
    mage_estimate: OlmMageHandEstimate
    melee_estimate: OlmMeleeHandEstimate

    def room_estimates(self) -> tuple[int, int]:
        melee_hand = self.melee_estimate.monster
        mage_hand = self.mage_estimate.monster
        head = self.head_estimate.monster

        phases = melee_hand.phases

        melee_ticks = phases * self.melee_estimate.ticks_per_unit()
        mage_ticks = phases * self.mage_estimate.ticks_per_unit()
        head_ticks = self.head_estimate.ticks_per_unit()
        ticks = sum([melee_ticks, mage_ticks, head_ticks])

        points = 0

        for _olm in (melee_hand, mage_hand, head):
            points += _olm.points_per_room()

        return ticks, points
