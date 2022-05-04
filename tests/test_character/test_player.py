"""Test the player class

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""

from osrs_tools.boost import BastionPotion, ImbuedHeart, Overload, SuperCombatPotion
from osrs_tools.boost.boosts import RangingPotion
from osrs_tools.character.player import Player
from osrs_tools.data import Effect, Level, Slayer
from osrs_tools.gear import common_gear as cg
from osrs_tools.gear.equipment import Equipment
from osrs_tools.stats.stats import PlayerLevels
from osrs_tools.style.style import UnarmedStyles

###############################################################################
# misc                                                                        #
###############################################################################

# important levels

_112 = Level(112)
_118 = Level(118)
_120 = Level(120)


def test_player_init():
    lad = Player()

    assert lad.lvl == PlayerLevels.maxed_player
    assert lad._attack_delay == 0
    assert lad.style == UnarmedStyles.default
    assert lad._autocast is None
    assert lad.equipment == Equipment()
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
    assert Effect.UPDATE_STATS in lad.timers
    assert lad.lvl.strength == _118
    assert lad.lvl.attack == _118
    assert lad.lvl.defence == _118

    lad.reset_stats()
    lad.boost(BastionPotion)
    assert lad.lvl.ranged == Level(112)
    assert lad.lvl.defence == _118

    lad.boost(ImbuedHeart)
    assert lad.lvl.magic == Level(110)

    lad.reset_stats()
    assert Effect.UPDATE_STATS not in lad.timers
    assert lad.lvl == PlayerLevels.maxed_player()

    lad.boost(Overload)
    assert all(
        [
            lad.lvl.attack == _120,
            lad.lvl.strength == _120,
            lad.lvl.defence == _120,
            lad.lvl.ranged == _120,
            lad.lvl.magic == _120,
            lad.lvl.hitpoints == Level(49),
        ]
    )
