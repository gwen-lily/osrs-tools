"""Test the Gear class

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""

from osrs_tools import gear
from osrs_tools.data import Slots
from osrs_tools.stats import AggressiveStats, DefensiveStats
from osrs_tools.tracked_value import EquipmentStat, Level, TrackedFloat


def test_zaryte_vambraces():
    zvambs = gear.ZaryteVambraces

    assert zvambs.slot is Slots.HANDS
    assert zvambs.aggressive_bonus == AggressiveStats(
        stab=EquipmentStat(-8),
        slash=EquipmentStat(-8),
        crush=EquipmentStat(-8),
        magic_attack=EquipmentStat(0),
        ranged_attack=EquipmentStat(18),
        melee_strength=EquipmentStat(0),
        ranged_strength=EquipmentStat(2),
        magic_strength=TrackedFloat(0.0),
    )
    assert zvambs.defensive_bonus == DefensiveStats(
        stab=EquipmentStat(8),
        slash=EquipmentStat(8),
        crush=EquipmentStat(8),
        magic=EquipmentStat(5),
        ranged=EquipmentStat(8),
    )
    assert zvambs.prayer_bonus == 1

    assert zvambs.level_requirements.ranged == Level(80)
    assert zvambs.level_requirements.defence == Level(45)
