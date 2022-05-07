"""Basic combat strategies with bis gear and no weapons

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-03-27                                                        #
###############################################################################
"""

from dataclasses import dataclass

from osrs_tools import gear
from osrs_tools.gear import Equipment
from osrs_tools.prayer import Augury, Piety, Prayers, Rigour
from osrs_tools.spell import Spell
from typing_extensions import Self

from .strategy import CombatStrategy


@dataclass
class MeleeStrategy(CombatStrategy):
    prayers = Prayers(prayers=[Piety])

    def equip_player(self) -> Self:
        # basic bis 'n such
        eqp = Equipment().equip_bis_melee()

        # equip it
        self.player.eqp.equip(*eqp.equipped_gear)

        # Specific gear and style
        return super().equip_player()


@dataclass
class RangedStrategy(CombatStrategy):
    prayers = Prayers(prayers=[Rigour])

    def equip_player(self) -> Self:
        # basic bis 'n such.
        eqp = Equipment().equip_bis_ranged().equip(gear.ArchersRingI)

        # equip it
        self.player.eqp.equip(*eqp.equipped_gear)

        # Specific gear and style.
        return super().equip_player()


class EliteVoidStrategy(RangedStrategy):
    """Big boy strategies for trade chads only.

    Basically, if you're not bringing elite void into these raids I question
    your bloodline and everything they've claimed to stand for.
    """

    def equip_player(self) -> Self:
        # equip melvin gear
        super().equip_player()

        # overwrite it with trade chad gear
        self.player.eqp.equip(*gear.EliteVoidSet)

        return self


@dataclass
class MagicStrategy(CombatStrategy):
    """The basic magic strategy pattern.

    See CombatStrategy for a complete list of Attributes.

    Attributes
    ----------
    _autocast : Spell | None
        The spell to autocast. If ommitted, will produce variable results. For
        example, powered staves will likely handle this but not something like
        a kodai wand. Tread carefully. Defaults to None.
    """

    prayers = Prayers(prayers=[Augury])
    _autocast: Spell | None = None

    @property
    def autocast(self) -> Spell:
        """Type validation for autocast."""
        assert isinstance(self._autocast, Spell)
        return self._autocast

    def equip_player(self) -> Self:
        # equip gear and set the autocast
        self.player.eqp.equip_bis_mage().equip(gear.BrimstoneRing)

        if self._autocast is not None:
            self.player.autocast = self.autocast

        # special gear and style
        return super().equip_player()
