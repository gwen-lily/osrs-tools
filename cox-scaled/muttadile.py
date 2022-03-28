from dataclasses import dataclass, field

from osrs_tools.character import BigMuttadile, Player, SmallMuttadile
from osrs_tools.damage import Damage
from osrs_tools.equipment import Equipment
from osrs_tools.modifier import Level, Styles
from osrs_tools.prayer import Augury, Rigour
from osrs_tools.spells import PoweredSpells
from osrs_tools.stats import Boost, Overload
from osrs_tools.style import PlayerStyle, PoweredStaffStyles

from estimate import RoomEstimate, ScaledCoxStrategy, TbowStrategy

###############################################################################
# email:    noahgill409@gmail.com
# created:  2022-03-27
###############################################################################


###############################################################################
# protocols
###############################################################################


class SangSmallMutta:
    def equip_player(self, player: Player):
        player.equipment = Equipment.no_equipment()
        player.equipment.equip_basic_magic_gear(arcane=False)

        style = PoweredStaffStyles.get_by_style(Styles.LONGRANGE)
        assert isinstance(style, PlayerStyle)
        player.active_style = player.equipment.equip_sang(arcane=False, style=style)
        player.autocast = PoweredSpells.sanguinesti_staff.value

        assert player.equipment.full_set

    def boost_player(self, player: Player, boost: Boost):
        player.boost(boost)

    def pray_player(self, player: Player):
        player.reset_prayers()
        player.pray(Augury)

    def damage_target(self, player: Player, target: SmallMuttadile, **kwargs) -> Damage:
        options = {}
        options.update(kwargs)
        dam = player.damage_distribution(target, **options)
        return dam


class ZcbSmallMutta:
    def equip_player(self, player: Player):
        player.equipment = Equipment.no_equipment()
        player.equipment.equip_basic_ranged_gear()
        player.equipment.equip_arma_set(zaryte=True)
        # TODO: Confirm that you can attack with rapid
        player.active_style = player.equipment.equip_zaryte_crossbow(
            buckler=True, rubies=True
        )

        assert player.equipment.full_set

    def boost_player(self, player: Player, boost: Boost):
        player.boost(boost)

    def pray_player(self, player: Player):
        player.reset_prayers()
        player.pray(Rigour)

    def damage_target(self, player: Player, target: SmallMuttadile, **kwargs) -> Damage:
        options = {}
        options.update(kwargs)
        dam = player.damage_distribution(target, **options)
        return dam


class FbowSmallMutta:
    def equip_player(self, player: Player):
        player.equipment = Equipment.no_equipment()
        player.equipment.equip_basic_ranged_gear()
        player.equipment.equip_arma_set(zaryte=True)
        player.active_style = player.equipment.equip_crystal_bowfa()

        assert player.equipment.full_set

    def boost_player(self, player: Player, boost: Boost):
        player.boost(boost)

    def pray_player(self, player: Player):
        player.reset_prayers()
        player.pray(Rigour)

    def damage_target(self, player: Player, target: SmallMuttadile, **kwargs) -> Damage:
        options = {}
        options.update(kwargs)
        dam = player.damage_distribution(target, **options)
        return dam


###############################################################################
# room estimates
###############################################################################


@dataclass
class SmallMuttadileEstimate(RoomEstimate):
    strategy: ScaledCoxStrategy = field()
    boost: Boost = field()
    freeze: bool = True
    vulnerability: bool = True

    def room_estimates(self) -> tuple[int, int]:
        # prep the monster
        target = SmallMuttadile.from_de0(self.scale)
        points = target.points_per_room(freeze=self.freeze)

        if self.vulnerability is True:
            target.apply_vulnerability()

        player = Player()

        # use protocols
        self.strategy.equip_player(player)
        self.strategy.boost_player(player, self.boost)
        self.strategy.pray_player(player)

        player_dpt = self.strategy.damage_target(player, target).per_tick
        thrall_dpt = Damage.thrall().per_tick
        dpt = player_dpt + thrall_dpt

        assert isinstance(target.levels.hitpoints, Level)
        ticks = target.levels.hitpoints // dpt

        return ticks, points


@dataclass
class BigMuttadileEstimate(RoomEstimate):
    strategy: ScaledCoxStrategy = field(default=TbowStrategy)
    freeze: bool = True
    vulnerability: bool = True

    def room_estimates(self) -> tuple[int, int]:
        # prep the monster
        target = BigMuttadile.from_de0(self.scale)
        points = target.points_per_room(freeze=self.freeze)

        if self.vulnerability is True:
            target.apply_vulnerability()

        player = Player()

        # use protocols
        self.strategy.equip_player(player)
        self.strategy.boost_player(player, Overload)
        self.strategy.pray_player(player)

        player_dpt = self.strategy.damage_target(player, target).per_tick
        thrall_dpt = Damage.thrall().per_tick
        dpt = player_dpt + thrall_dpt

        assert isinstance(target.levels.hitpoints, Level)
        ticks = target.levels.hitpoints // dpt

        return ticks, points
