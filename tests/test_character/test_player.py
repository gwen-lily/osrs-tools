"""Test the player class

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""

from osrs_tools.boost import BastionPotion, ImbuedHeart, Overload, SuperCombatPotion
from osrs_tools.boost.boosts import SmellingSalts
from osrs_tools.character.player import Player
from osrs_tools.data import Effect, Slayer
from osrs_tools.stats import PlayerLevels
from osrs_tools.style import UnarmedStyles

###############################################################################
# misc                                                                        #
###############################################################################


def test_player_init():
    lad = Player()

    for skill, level in lad.lvl:
        print(skill, level)

    assert lad.lvl == PlayerLevels.maxed_player()
    assert lad._attack_delay == 0
    assert lad.style == UnarmedStyles.default
    assert lad._autocast is None
    assert lad.levels == lad._levels
    assert len(lad._prayers) == 0
    assert lad.slayer_task is Slayer.NONE
    assert len(lad.timers) == 0
    assert lad.last_attacked is None
    assert lad.last_attacked_by is None
    assert not lad.name


def test_player_stats():
    lad = Player()

    lad.boost(SuperCombatPotion)
    # assert Effect.UPDATE_STATS in lad.timers
    assert lad.lvl.strength.value == 118
    assert lad.lvl.attack.value == 118
    assert lad.lvl.defence.value == 118

    lad.reset_stats()
    lad.boost(BastionPotion)
    assert lad.lvl.ranged.value == 112
    assert lad.lvl.defence.value == 118

    lad.boost(ImbuedHeart)
    assert lad.lvl.magic.value == 109

    lad.reset_stats()
    assert Effect.UPDATE_STATS not in lad.timers
    assert lad.lvl == PlayerLevels.maxed_player()

    lad.boost(Overload)
    assert all(
        [
            lad.lvl.attack.value == 120,
            lad.lvl.strength.value == 120,
            lad.lvl.defence.value == 120,
            lad.lvl.ranged.value == 120,
            lad.lvl.magic.value == 120,
            lad.lvl.hitpoints.value == 49,
        ]
    )

    lad.boost(SmellingSalts)
    assert all(
        [
            lad.lvl.attack.value == 125,
            lad.lvl.strength.value == 125,
            lad.lvl.defence.value == 125,
            lad.lvl.ranged.value == 125,
            lad.lvl.magic.value == 125,
        ]
    )
