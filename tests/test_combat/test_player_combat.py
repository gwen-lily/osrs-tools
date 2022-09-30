from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.combat.player import PvMCalc
from osrs_tools.data import Styles
from osrs_tools.gear import AbyssalTentacle
from osrs_tools.style.all_weapon_styles import WhipStyles


def test_pvm_calc():
    player = Player()
    player.eqp += AbyssalTentacle
    player.style = WhipStyles[Styles.LASH]

    monster = Monster.dummy()

    calc = PvMCalc(player, monster)
    dam = calc.get_damage()

    assert dam.max_hit == 25
