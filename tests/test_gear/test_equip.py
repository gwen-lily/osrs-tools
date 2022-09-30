import math

from osrs_tools import gear
from osrs_tools.data import DT, Slots
from osrs_tools.gear import (
    ArchersRingI,
    BrimstoneRing,
    DragonArrows,
    Equipment,
    JusticiarSet,
    SanguinestiStaff,
    ScytheOfVitur,
    TwistedBow,
    ZamorakianHasta,
)
from osrs_tools.gear.common_gear import AvernicDefender, GuardianBoots


def test_equip():
    eqp = Equipment()
    assert len(eqp) == 0

    eqp = eqp.equip(gear.AbyssalBludgeon)
    assert gear.AbyssalBludgeon in eqp.equipped_gear
    assert len(eqp) == 1

    eqp += gear.ArcaneSpiritShield
    assert len(eqp) == 1

    eqp.equip(gear.SanguinestiStaff)
    assert len(eqp) == 2


def test_aggressive_bonus():
    eqp = Equipment()

    # melee
    eqp = eqp.equip_bis_melee().equip(ScytheOfVitur)
    ab = eqp.aggressive_bonus

    assert ab.stab.value == 107
    assert ab.slash.value == 147
    assert ab.crush.value == 67
    assert ab.magic_attack.value == -72
    assert ab.ranged_attack.value == -46

    mel_atk, mel_str = ab[DT.SLASH]
    assert mel_atk == ab.slash
    assert mel_str == 138

    # ranged
    eqp = eqp.equip_bis_ranged().equip(DragonArrows, TwistedBow, ArchersRingI)
    ab = eqp.aggressive_bonus

    assert ab.stab.value == -26
    assert ab.slash.value == -26
    assert ab.crush.value == -26
    assert ab.magic_attack.value == -42

    # DT key lookup
    rng_atk, rng_str = ab[DT.RANGED]
    assert rng_atk.value == 194
    assert rng_str.value == 89

    eqp.unequip(Slots.AMMUNITION)

    # magic
    eqp = eqp.equip_bis_mage().equip(SanguinestiStaff, BrimstoneRing).unequip(Slots.SHIELD)
    ab = eqp.aggressive_bonus

    assert ab.stab.value == 4
    assert ab.slash.value == 4
    assert ab.crush.value == 4
    assert ab.ranged_attack == -17

    mag_atk, mag_str = ab[DT.MAGIC]

    assert mag_atk.value == 145
    assert math.fabs(mag_str.value - 0.23) < 1e-6


def test_defensive_bonus():
    eqp = Equipment()

    # melee
    eqp = eqp.equip_bis_melee().equip(ZamorakianHasta, AvernicDefender)
    db = eqp.defensive_bonus

    assert db.stab.value == 340
    assert db.slash.value == 325
    assert db.crush.value == 340
    assert db.magic.value == -15
    assert db.ranged.value == 322

    eqp = Equipment()
    eqp += JusticiarSet
    eqp += GuardianBoots
    db = eqp.defensive_bonus

    assert db.stab.value == 319
    assert db.slash.value == 317
    assert db.crush.value == 301
    assert db.magic.value == -39
    assert db.ranged.value == 335
