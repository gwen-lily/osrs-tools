from osrs_tools.analysis.pvm_axes import PvmAxes
from osrs_tools.analysis.utils import bedevere_the_wise
from osrs_tools.boost import SmellingSalts
from osrs_tools.boost.boosts import Overload
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.combat.player import PvMCalc
from osrs_tools.data import DataMode, Styles
from osrs_tools.gear import AbyssalTentacle
from osrs_tools.gear.common_gear import AvernicDefender, BrimstoneRing, OsmumtensFang, TumekensShadow
from osrs_tools.gear.equipment import Equipment
from osrs_tools.prayer.all_prayers import Piety
from osrs_tools.spell.spells import PoweredSpells
from osrs_tools.style.all_weapon_styles import PoweredStaffStyles, StabSwordStyles, WhipStyles


def test_pvm_calc():
    player = Player()
    player.eqp += AbyssalTentacle
    player.style = WhipStyles[Styles.LASH]

    monster = Monster.dummy()

    calc = PvMCalc(player, monster)
    dam = calc.get_damage()

    assert dam.max_hit == 25


def test_tumekens_shadow_max():
    player = Player()
    player.eqp = Equipment().equip_bis_mage().equip(BrimstoneRing, TumekensShadow)
    player.style = PoweredStaffStyles[Styles.ACCURATE]
    player.autocast = PoweredSpells.TUMEKENS_SHADOW.value

    # unboosted

    monster = Monster.dummy()

    calc = PvMCalc(player, monster)
    dam = calc.get_damage()

    assert dam.max_hit == 65

    # boosted
    player.boost(SmellingSalts)
    dam = calc.get_damage()

    assert dam.max_hit == 80


def test_osmumtens_fang():

    player = Player()
    target = Monster.dummy()

    player.eqp += Equipment().equip_bis_melee().equip(OsmumtensFang, AvernicDefender)
    player.style = StabSwordStyles[Styles.LUNGE]

    prayer = Piety
    boost = Overload
    special_attack = False

    ax = PvmAxes.create(player, target, prayers=prayer, boosts=boost, special_attack=special_attack)

    dam_ary = bedevere_the_wise(ax, DataMode.MAX_HIT)

    with open("out.txt", mode="w", encoding="UTF-8") as f:
        f.write(str(dam_ary))
