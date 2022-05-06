"""Estimate classes which allow for re-usable room efficiency analysis.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-03-27                                                        #
###############################################################################
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

from osrs_tools.character.monster import CoxMonster
from osrs_tools.combat import Damage
from osrs_tools.data import COX_POINTS_PER_HITPOINT
from osrs_tools.strategy import CombatStrategy, Strategy
from osrs_tools.tracked_value import Level


@dataclass
class CoxEstimate:
    """Base class for estimates.

    Attributes
    ----------
    scale : int
        The scale of the raid.
    """

    scale: int


@dataclass
class RoomEstimate(CoxEstimate, ABC):
    """Abstract base class for room estimates.

    Attributes
    ----------

    strategy : Strategy
        The main room strategy.

    setup_ticks : int
        Any extra ticks that should be counted in efficiency calculations such
        as tanking, trading, setup, etc.

    """

    strategy: Strategy
    setup_ticks: int

    @abstractmethod
    def room_estimates(self) -> tuple[int, int]:  # type: ignore
        """Generic room_estimates method which returns ticks & points.

        Returns:
            tuple[int, int]: (ticks, points)
        """


@dataclass
class MonsterEstimate(CoxEstimate):
    """A monster estimate.

    Attributes
    ----------

    monster : CoxMonster
        The cox monster.

    main_strategy : CombatStrategy
        The primary strategy used to damage the boss.

    thralls : bool
        Set to True if using thralls. Defaults to False.

    zero_defence : bool
        Set to True if completely reducing a monster's defence. Defaults to
        False.

    vulnerability : bool
        Set to True if casting vulnerability on a monster. Assumes tome of
        water. Defaults to False.
    """

    monster: CoxMonster
    main_strategy: CombatStrategy
    thralls: bool = False
    zero_defence: bool = False
    vulnerability: bool = False

    def _get_dam(self, **kwargs) -> Damage:
        """Get the damage distribution from a normal strategy."""
        strat = self.main_strategy

        if self.zero_defence:
            self.monster.lvl.defence = Level(0, "zero defence")
        elif self.vulnerability:
            self.monster.apply_vulnerability()

        dam = strat.activate().damage_distribution(self.monster, **kwargs)
        return dam

    def _get_ticks(self, damage: Damage, damage_modifier: float) -> int:
        player_dpt = damage.per_tick * damage_modifier
        thrall_dpt = self.thralls * Damage.thrall().per_tick
        dpt = player_dpt + thrall_dpt

        return self.monster.base_hp // dpt

    def ticks_per_unit(self, damage_modifier: float = 1.00, **kwargs) -> int:
        """Find the ticks to kill a unit.

        Parameters
        ----------
        damage_modifier : float, optional
            A modifier to apply to the player damage, by default 1.00.

        Returns
        -------
        int
        """
        dam = self._get_dam(**kwargs)

        return self._get_ticks(dam, damage_modifier)

    def points_per_unit(self, **kwargs) -> int:
        """Find the points yielded by killing a unit."""
        base_hp = self.monster.base_hp

        _points_per_unit = math.floor(int(base_hp) * COX_POINTS_PER_HITPOINT)
        return _points_per_unit
