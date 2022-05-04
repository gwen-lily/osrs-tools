"""Test the Equipment class

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""

from osrs_tools.data import EquipmentStat
from osrs_tools.gear import common_gear as cg
from osrs_tools.gear.equipment import Equipment
from osrs_tools.stats.stats import AggressiveStats, DefensiveStats


def test_bis_mage():
    eqp = Equipment().equip_bis_mage().equip(cg.SanguinestiStaff, cg.BrimstoneRing)

    assert eqp.full_set
    assert eqp.aggressive_bonus == AggressiveStats(
        stab=EquipmentStat(),
        slash=EquipmentStat(),
        crush=EquipmentStat(),
        magic_attack=EquipmentStat(),
        ranged_attack=EquipmentStat(),
        melee_strength=EquipmentStat(),
        ranged_strength=EquipmentStat(),
        magic_strength=TrackedFloat(),
    )

    assert eqp.defensive_bonus == DefensiveStats(
        stab=EquipmentStat(),
        slash=EquipmentStat(),
        crush=EquipmentStat(),
        magic=EquipmentStat(),
        ranged=EquipmentStat(),
    )
    assert eqp.prayer_bonus == 420
