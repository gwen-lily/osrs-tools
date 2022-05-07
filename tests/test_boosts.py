"""Test the Boost class

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""

from osrs_tools.boost import Overload
from osrs_tools.stats import PlayerLevels
from osrs_tools.tracked_value import Level

from .data import _120


def test_overload():
    max_lvls = PlayerLevels.maxed_player()

    boosted_lvls = max_lvls + Overload

    assert boosted_lvls.attack == _120
    assert boosted_lvls.strength == _120
    assert boosted_lvls.defence == _120
    assert boosted_lvls.magic == _120
    assert boosted_lvls.ranged == _120
    assert boosted_lvls.hitpoints == Level(49)
