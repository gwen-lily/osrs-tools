from osrs_tools import gear
from osrs_tools.gear import Equipment


def test_equip():
    eqp = Equipment()
    assert len(eqp) == 0

    eqp.equip(gear.AbyssalBludgeon)
    assert len(eqp) == 1

    eqp.equip(gear.ArcaneSpiritShield)
    assert len(eqp) == 1

    eqp.equip(gear.SanguinestiStaff)
    assert len(eqp) == 2
