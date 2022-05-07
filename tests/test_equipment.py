"""Test the Equipment class

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""

from osrs_tools.gear import Equipment
from osrs_tools.gear import common_gear as cg
from osrs_tools.stats import AggressiveStats
from osrs_tools.tracked_value import EquipmentStat, TrackedFloat


def test_bis_mage():
    eqp = Equipment().equip_bis_mage().equip(cg.SanguinestiStaff, cg.BrimstoneRing)

    assert eqp.full_set
    assert eqp.aggressive_bonus == AggressiveStats(
        stab=EquipmentStat(4),
        slash=EquipmentStat(4),
        crush=EquipmentStat(4),
        magic_attack=EquipmentStat(165),
        ranged_attack=EquipmentStat(-17),
        melee_strength=EquipmentStat(4),
        ranged_strength=EquipmentStat(0),
        magic_strength=TrackedFloat(0.23),
    )

    #     assert eqp.defensive_bonus == DefensiveStats(
    #         stab=EquipmentStat(),
    #         slash=EquipmentStat(),
    #         crush=EquipmentStat(),
    #         magic=EquipmentStat(),
    #         ranged=EquipmentStat(),
    #     )
    assert eqp.prayer_bonus == 7
