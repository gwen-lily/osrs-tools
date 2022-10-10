"""Combat strategies derived from the basic strategies.

These strategies implement weapons & styles basically.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-03-27                                                        #
###############################################################################
"""

from dataclasses import dataclass

from osrs_tools import gear
from osrs_tools.data import Stances, Styles
from osrs_tools.gear import AvernicDefender, BrimstoneRing, DragonWarhammer
from osrs_tools.gear.common_gear import (
    BandosGodsword,
    BerserkerRingI,
    DragonArrows,
    RedChinchompa,
    SanguinestiStaff,
    SlayerHelmetI,
    TwistedBow,
    TwistedBuckler,
)
from osrs_tools.spell import PoweredSpells, Spell
from osrs_tools.style import BluntStyles, PlayerStyle, PoweredStaffStyles, TwoHandedStyles
from typing_extensions import Self

from .basic_combat_strategies import EliteVoidStrategy, MagicStrategy, MeleeStrategy, RangedStrategy

###############################################################################
# melee strategies                                                            #
###############################################################################


@dataclass
class DwhStrategy(MeleeStrategy):
    """A basically bis (brimstone) dwh strategy with max melee."""

    style: PlayerStyle = BluntStyles[Stances.ACCURATE]

    def equip_player(self) -> Self:
        # equip dwh, avernic, and brimstone
        self.player.eqp += [DragonWarhammer, AvernicDefender, BrimstoneRing]

        # correct gear, handle style.
        return super().equip_player()


class BgsStrategy(MeleeStrategy):
    """A bis bgs strategy with max melee."""

    def equip_player(self) -> Self:
        """Equip bgs and choose appropriate style if none is provided.

        Returns
        -------
        Self
        """
        # equip bgs and berserker
        self.player.eqp += [BandosGodsword, BerserkerRingI]

        # equip gear and handle style
        super().equip_player()

        # if no style is specified, choose based on equipment bonus
        if self.style is None:
            ab = self.player.aggressive_bonus

            if ab.slash >= ab.crush:
                style = TwoHandedStyles[Styles.SLASH]
            else:
                style = TwoHandedStyles[Styles.SMASH]

            self.player.style = style

        return self


###############################################################################
# ranged strategies                                                           #
###############################################################################


class TbowStrategy(RangedStrategy):
    """A bis tbow strategy with arma."""

    def equip_player(self) -> Self:
        # equip bow
        self.player.eqp += [TwistedBow, DragonArrows]

        # equip basic bis 'n such, as well as default to rapid style
        return super().equip_player()


class TbowVoidStrategy(EliteVoidStrategy):
    """A bis tbow strategy with void."""

    def equip_player(self) -> Self:
        # equip bow and such
        self.player.eqp += [TwistedBow, DragonArrows]

        # equip basic bis 'n such, as well as default to rapid style
        return super().equip_player()


class RedChinsVoidStrategy(EliteVoidStrategy):
    """A basically bis (red chins) chin strategy with void."""

    def equip_player(self) -> Self:
        # equip chins
        self.player.eqp += [RedChinchompa, TwistedBuckler]
        # equip basic bits 'n such, as well as default to medium fuse / rapid.
        return super().equip_player()


class RedChinsSlayerStrategy(RangedStrategy):
    """A basically bis (red chins) chin strategy with arma + slayer helm."""

    def equip_player(self) -> Self:
        # equip basic bits 'n such, as well as default to medium fuse / rapid.
        super().equip_player()

        # specific equipment
        self.player.eqp += [RedChinchompa, TwistedBuckler, SlayerHelmetI]

        return self


###############################################################################
# magic strategies                                                            #
###############################################################################


class SangStrategy(MagicStrategy):
    """A strategy for bis (with brimstone) sanguinesti staff.

    Attributes
    ----------

    _style : PlayerStyle
        The attack style. Defaults to accurate.

    autocast : Spell
        The sanguinesti spell. Defaults to the appropriate value.
    """

    style: PlayerStyle | None = PoweredStaffStyles[Stances.ACCURATE]
    autocast: Spell | None = PoweredSpells.SANGUINESTI_STAFF.value

    def equip_player(self) -> Self:
        # equip the sang
        self.player.eqp += SanguinestiStaff

        # handle the rest
        return super().equip_player()
