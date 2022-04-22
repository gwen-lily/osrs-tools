"""Strategy classes which allow for re-usable combat simulation.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-03-27                                                        #
###############################################################################
"""

from dataclasses import dataclass, field

from bedevere.markov import MarkovChain
from osrs_tools.character import CoxMonster, Player
from osrs_tools.damage import Damage
from osrs_tools.equipment import Equipment, Gear
from osrs_tools.modifier import Styles
from osrs_tools.prayer import Augury, Piety, Prayer, PrayerCollection, Rigour
from osrs_tools.spells import PoweredSpells, Spell
from osrs_tools.stats import Boost, Overload
from osrs_tools.style import (
    BluntStyles,
    PlayerStyle,
    PoweredStaffStyles,
    TwoHandedStyles,
)
from typing_extensions import Self

###############################################################################
# styles                                                                      #
###############################################################################

_ACCURATE_SANG_STYLE = PoweredStaffStyles.get_by_style(Styles.ACCURATE)
_ACCURATE_DWH_STYLE = BluntStyles.get_by_style(Styles.ACCURATE)

###############################################################################
# main classes                                                                #
###############################################################################


class Strategy:
    """Abstract base class for strategies."""


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

    boost : Boost
        The Boost the player will use.

    prayers : Prayer | PrayerCollection
        The prayers the player will use.

    gear : list[Gear]
        Any gear overrides can be applied here. These will be equipped
        last and override any defaults. Defaults to empty list.

    style : PlayerStyle | None
        The style to use. If ommitted, will default based on weapon type.
        Defaults to None.

    """

    player: Player
    prayers: Prayer | PrayerCollection
    boost: Boost = Overload
    gear: list[Gear] = field(default_factory=list)
    _style: PlayerStyle | None = None

    @property
    def style(self) -> PlayerStyle:
        """Type validation for style."""
        assert isinstance(self._style, PlayerStyle)
        return self._style

    def equip_player(self, **kwargs) -> Self:
        """Modify equipment."""
        eqp = self.player.equipment

        if self.gear:
            eqp.equip(*self.gear)

        if self._style is not None:
            weapon_style = self._style
        else:
            weapon_style = eqp.weapon.styles.default

        self.player.active_style = weapon_style

        assert self.player.equipment.full_set
        return self

    def boost_player(self) -> Self:
        self.player.reset_stats()
        self.player.boost(self.boost)
        return self

    def pray_player(self) -> Self:
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
        return (
            self.equip_player(**kwargs)
            .boost_player()
            .pray_player()
            .misc_player(**kwargs)
        )

    def damage_distribution(self, target: CoxMonster, **kwargs) -> Damage:
        """Simple wrapper for Player.damage_distribution"""
        return self.player.damage_distribution(target, **kwargs)

    def get_markov(self, target: CoxMonster, **kwargs) -> MarkovChain:
        raise NotImplementedError


@dataclass
class MeleeStrategy(CombatStrategy):
    prayers: Prayer | PrayerCollection = Piety

    def equip_player(self) -> Self:
        # basic bis 'n such
        eqp = Equipment.no_equipment()
        eqp.equip_basic_melee_gear(berserker=True)
        eqp.equip_torva_set()

        # equip it
        self.player.equipment.equip(*eqp.equipped_gear)

        # Specific gear and style
        return super().equip_player()


@dataclass
class RangedStrategy(CombatStrategy):
    prayers: Prayer | PrayerCollection = Rigour

    def equip_player(self) -> Self:
        # basic bis 'n such.
        eqp = Equipment.no_equipment()
        eqp.equip_basic_ranged_gear(archers=True)
        eqp.equip_arma_set(zaryte=True)

        # equip it
        self.player.equipment.equip(*eqp.equipped_gear)

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

        eqp = Equipment.no_equipment()
        eqp.equip_void_set(elite=True)

        # overwrite it with trade chad gear
        self.player.equipment.equip(*eqp.equipped_gear)

        return self


@dataclass
class MagicStrategy(CombatStrategy):
    """The basic magic strategy pattern.

    See CombatStrategy for a complete list of Attributes.

    Attributes
    ----------
    autocast : Spell | None
        The spell to autocast. If ommitted, will produce variable results. For
        example, powered staves will likely handle this but not something like
        a kodai wand. Tread carefully. Defaults to None.
    """

    prayers: Prayer | PrayerCollection = Augury
    _autocast: Spell | None = None

    @property
    def autocast(self) -> Spell:
        """Type validation for autocast."""
        assert isinstance(self._autocast, Spell)
        return self._autocast

    def equip_player(self) -> Self:
        # equip basic bis gear 'n such.
        eqp = Equipment.no_equipment()
        eqp.equip_basic_magic_gear(brimstone=False)
        eqp.equip(Gear.from_bb("berserker (i)"))  # brimstone irrelevant.

        # equip it and set the autocast
        self.player.equipment.equip(*eqp.equipped_gear)
        self.player.autocast = self.autocast

        # special gear and style
        return super().equip_player()


# melee strategies ############################################################


class DwhStrategy(MeleeStrategy):
    """A basically bis (berserker) dwh strategy with max melee."""

    _style = _ACCURATE_DWH_STYLE

    def equip_player(self) -> Self:
        # equip dwh, avernic, and brimstone
        self.player.equipment.equip_dwh(avernic=True, brimstone=False)

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
        # equip bgs
        self.player.equipment.equip_bgs()

        # equip gear and handle style
        super().equip_player()

        # if no style is specified, choose based on equipment bonus
        if self._style is None:
            ab = self.player.aggressive_bonus

            if ab.slash >= ab.crush:
                style = TwoHandedStyles.get_by_style(Styles.SLASH)
            else:
                style = TwoHandedStyles.get_by_style(Styles.SMASH)

            self.player.active_style = style

        return self


# ranged strategies ###########################################################


class TbowStrategy(RangedStrategy):
    """A bis tbow strategy with arma."""

    def equip_player(self) -> Self:
        # equip bow
        self.player.equipment.equip_twisted_bow(dragon_arrows=True)

        # equip basic bis 'n such, as well as default to rapid style
        return super().equip_player()


class TbowVoidStrategy(EliteVoidStrategy):
    """A bis tbow strategy with void."""

    def equip_player(self) -> Self:
        # equip bow
        self.player.equipment.equip_twisted_bow(dragon_arrows=True)

        # equip basic bis 'n such, as well as default to rapid style
        return super().equip_player()


class RedChinsStrategy(EliteVoidStrategy):
    """A basically bis (red chins) chin strategy with void."""

    def equip_player(self) -> Self:
        # equip chins
        self.player.equipment.equip_chins(buckler=True, red=True)

        # equip basic bits 'n such, as well as default to medium fuse / rapid.
        return super().equip_player()


class RedChinsSlayerStrategy(RangedStrategy):
    """A basically bis (red chins) chin strategy with arma + slayer helm."""

    def equip_player(self) -> Self:
        # equip basic bits 'n such, as well as default to medium fuse / rapid.
        super().equip_player()

        # specific equipment
        self.player.equipment.equip_chins(buckler=True, red=True)
        self.player.equipment.equip_slayer_helm(imbued=True)

        return self


# magic strategies ############################################################


class SangStrategy(MagicStrategy):
    """A strategy for bis (with brimstone) sanguinesti staff.

    Attributes
    ----------

    _style : PlayerStyle
        The attack style. Defaults to accurate.

    autocast : Spell
        The sanguinesti spell. Defaults to the appropriate value.
    """

    _style: PlayerStyle = _ACCURATE_SANG_STYLE
    autocast: Spell = PoweredSpells.sanguinesti_staff.value

    def equip_player(self) -> Self:
        # equip the sang
        self.player.equipment.equip_sang(arcane=False)

        # handle the rest
        return super().equip_player()
