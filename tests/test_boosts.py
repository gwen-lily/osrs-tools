"""Test the Boost class

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""

from osrs_tools.boost import Overload, SuperCombatPotion
from osrs_tools.character.player import Player
from osrs_tools.data import Skills
from osrs_tools.stats import PlayerLevels


def test_overload():
    max_lvls = PlayerLevels.maxed_player()

    boosted_lvls = max_lvls + Overload

    assert boosted_lvls.attack.value == 120
    assert boosted_lvls.strength.value == 120
    assert boosted_lvls.defence.value == 120
    assert boosted_lvls.magic.value == 120
    assert boosted_lvls.ranged.value == 120
    assert boosted_lvls.hitpoints.value == 49


def test_super_combat_potion():
    max_lvls = PlayerLevels.maxed_player()
    boosted_lvls = max_lvls + SuperCombatPotion

    assert boosted_lvls[Skills.ATTACK].value == 118
    assert boosted_lvls[Skills.STRENGTH].value == 118
    assert boosted_lvls[Skills.DEFENCE].value == 118


def test_on_player():
    player = Player()

    levels = player.lvl

    assert levels[Skills.ATTACK].value == 99
    assert levels[Skills.STRENGTH].value == 99
    assert levels[Skills.DEFENCE].value == 99

    player.lvl += SuperCombatPotion

    levels = player.lvl

    assert levels[Skills.ATTACK].value == 118
    assert levels[Skills.STRENGTH].value == 118
    assert levels[Skills.DEFENCE].value == 118
