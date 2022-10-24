"""Strategy classes which allow for re-usable combat simulation.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-03-27                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from bedevere.markov import MarkovChain
from osrs_tools.boost import Boost, Overload
from osrs_tools.character.monster import Monster
from osrs_tools.character.monster.cox import CoxMonster
from osrs_tools.character.player import Player
from osrs_tools.combat import Damage, PvMCalc
from osrs_tools.gear.equipment import Equipment
from osrs_tools.prayer import Prayers
from osrs_tools.stats import PlayerLevels
from osrs_tools.style import PlayerStyle
from typing_extensions import Self

###############################################################################
# abstract class                                                              #
###############################################################################


class Strategy:
    """Abstract base class for strategies."""


###############################################################################
# main classes                                                                #
###############################################################################


@dataclass
class SkillingStrategy(Strategy):
    """Abstract skilling strategy."""


@dataclass
class CombatStrategy(Strategy):
    """The basic format for defining a re-usable combat strategy.

    All methods must return either self or an object. This is because I just
    learned about method chaining and I thought here would be a neat place to
    enforce it. A combat strategy basically runs a few buffs and then does
    something like attack a monster, or get a markov chain.

    Attributes
    ----------

    player : Player
        The player.

    boost : Boost | list[Boost]
        The Boost the player will use.

    prayers : Prayers | None
        The prayers the player will use.

    gear : list[Gear]
        Any gear overrides can be applied here. These will be equipped
        last and override any defaults. Defaults to empty list.

    style : PlayerStyle | None
        The style to use. If ommitted, will default based on weapon type.
        Defaults to None.

    _levels: PlayerLevels | None
        The levels to set the player to before boosts are applied. If omitted,
        the player's default levels will be left alone, defaults to None

    """

    player: Player
    equipment: Equipment = field(default_factory=Equipment)
    style: PlayerStyle | None = None
    prayers: Prayers | None = None
    boosts: Boost | list[Boost] | None = Overload
    levels: PlayerLevels | None = None

    # methods

    def equip_player(self, **kwargs) -> Self:
        """Modify equipment."""
        eqp = self.player.eqp

        if self.equipment:
            eqp += self.equipment

        if self.style is not None:
            self.player.style = self._style

        if self.player.style not in self.player.wpn.styles:
            _exc_str = f"{self.player.style} not in {self.player.wpn.styles}"
            raise ValueError(_exc_str)

        # assert self.player.eqp.full_set
        return self

    def boost_player(self) -> Self:
        if self.boosts is None:
            return self

        if self.levels is not None:
            self.player._levels = self._levels

        self.player.reset_stats()

        if isinstance(self.boosts, list):
            self.player.boost(*self.boosts)
        else:
            self.player.boost(self.boosts)

        return self

    def pray_player(self) -> Self:
        if self.prayers is not None:
            self.player.reset_prayers()
            self.player.pray(self.prayers)

        return self

    def misc_player(self, **kwargs) -> Self:
        """Allows subclasses to perform miscellaneous tasks.

        Returns
        -------
        Self
        """
        return self

    def activate(self, **kwargs) -> Self:
        """Run all the initialization methods with one method.

        Returns
        -------
        Self
        """
        return self.equip_player(**kwargs).boost_player().pray_player().misc_player(**kwargs)

    def damage_distribution(self, target: Monster, **kwargs) -> Damage:
        """Simple wrapper for Player.damage_distribution"""
        calc = PvMCalc(self.player, target)
        return calc.get_damage(**kwargs)

    # properties

    @property
    def _style(self) -> PlayerStyle:
        """Type validation for style."""
        assert isinstance(self.style, PlayerStyle)
        return self.style

    @property
    def _prayers(self) -> Prayers:
        """Type validation for prayers."""
        assert isinstance(self.prayers, Prayers)
        return self.prayers

    @property
    def _levels(self) -> PlayerLevels:
        """Type validation for levels."""
        assert isinstance(self.levels, PlayerLevels)
        return self.levels
