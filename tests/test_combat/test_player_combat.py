from osrs_tools.boost import SmellingSalts
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.combat.player import PvMCalc
from osrs_tools.data import Styles
from osrs_tools.gear import AbyssalTentacle
from osrs_tools.gear.common_gear import BrimstoneRing, TumekensShadow
from osrs_tools.gear.equipment import Equipment
from osrs_tools.spell.spells import PoweredSpells
from osrs_tools.style.all_weapon_styles import PoweredStaffStyles, WhipStyles


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
