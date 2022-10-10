from osrs_tools.boost import ImbuedHeart, Overload, RangingPotion, SuperCombatPotion
from osrs_tools.character import Monster, Player
from osrs_tools.data import Styles
from osrs_tools.gear import BandosGodsword, DragonArrows, DragonWarhammer, TwistedBow
from osrs_tools.gear.common_gear import DharoksSet, TorvaFullHelm
from osrs_tools.gear.equipment import Equipment
from osrs_tools.prayer import Augury, Piety, Rigour
from osrs_tools.prayer.prayers import Prayers
from osrs_tools.stats import PlayerLevels
from osrs_tools.strategy import CombatStrategy
from osrs_tools.strategy.derivative_combat_strategies import DwhStrategy
from osrs_tools.style import AxesStyles, BluntStyles, UnarmedStyles


def test_strategy():
    player = Player()
    target = Monster.dummy()

    strat = CombatStrategy(player, boosts=None)
    strat = strat.activate()

    dam = strat.damage_distribution(target)
    assert dam.max_hit == 11

    strat = CombatStrategy(player, boosts=Overload)
    strat = strat.activate()

    dam = strat.damage_distribution(target)
    assert dam.max_hit == 13

    player = Player()

    strat = CombatStrategy(player, boosts=None, prayers=Prayers(prayers=[Piety]))
    strat = strat.activate()

    dam = strat.damage_distribution(target)
    assert dam.max_hit == 13

    strat = CombatStrategy(player, boosts=Overload, prayers=Prayers(prayers=[Piety]))
    strat = strat.activate()

    dam = strat.damage_distribution(target)
    assert dam.max_hit == 16


def test_equip_player():
    player = Player()

    set_1 = Equipment()
    set_1 += DharoksSet

    strat = CombatStrategy(player, equipment=set_1, style=AxesStyles[Styles.HACK])
    assert len(player.eqp) == 1
    strat.activate()
    assert len(player.eqp) == 4


def test_dwh_strategy():
    player = Player()
    strat = DwhStrategy(player)

    strat = strat.activate()
    assert DragonWarhammer in player.eqp.equipped_gear

    player = Player()
    strat = DwhStrategy(player, equipment=Equipment().equip(TorvaFullHelm))

    strat = strat.activate()
    assert TorvaFullHelm in player.eqp.equipped_gear
