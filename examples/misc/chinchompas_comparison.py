from copy import copy

from osrs_tools.analysis_tools import DataAxes, DataMode, bedevere_2d
from osrs_tools.character import (
    DeathlyMage,
    DeathlyRanger,
    LizardmanShaman,
    Player,
    SkeletalMystic,
)
from osrs_tools.data import Level, Styles
from osrs_tools.equipment import Equipment, Gear, Slots
from osrs_tools.prayer import Rigour
from osrs_tools.stats import BastionPotion, Overload
from osrs_tools.style import ChinchompaStyles

bgloves = Gear.from_bb("barrows gloves")
zvambs = Gear.from_bb("zaryte vambraces")
fgloves = Gear.from_bb("ferocious gloves")
arma_helm = Gear.from_bb("armadyl helmet")


def arma_slayer_void_comparison():
    party_size = 26
    lad = Player(name="lad")
    lad.equipment.equip_basic_ranged_gear()
    lad.active_style = lad.equipment.equip_black_chins()
    zaryte = False

    set_names = ("arma", "void", "slayer", "salve (ei)")
    eqps = (arma, void, slayer, salve) = [Equipment(set_name=sn) for sn in set_names]
    eqps = (arma, void, slayer, salve) = [Equipment(set_name=sn) for sn in set_names]
    arma.equip_arma_set(zaryte=zaryte)
    void.equip_void_set(elite=True)
    slayer.equip_arma_set(zaryte=zaryte)
    slayer.equip_slayer_helm(imbued=True)
    salve.equip_arma_set(zaryte=zaryte)
    salve.equip_salve()

    if not zaryte:
        for eqp in (arma, slayer, salve):
            eqp.equip(bgloves)

    monsters = (LizardmanShaman, DeathlyMage, DeathlyRanger, SkeletalMystic)
    targets = (_, _, _, mystic) = [mon.from_de0(party_size) for mon in monsters]
    mystic.levels.defence = Level(0, "manual")

    _, table = bedevere_2d(
        lad,
        targets,
        equipment=eqps,
        boosts=Overload,
        prayers=Rigour,
        transpose=True,
        data_mode=DataMode.MAX_HIT,
        floatfmt=".0f",
    )
    print(table)


def bgloves_zvambs_chin_comparison(scale: int, **kwargs):
    lad = Player(task=True)
    lad.equipment.equip_basic_ranged_gear()
    lad.equipment.equip_arma_set()
    lad.equipment.unequip(Slots.head)
    lad.active_style = lad.equipment.equip_chins(
        red=True, style=ChinchompaStyles.get_by_style(Styles.LONG_FUSE)
    )

    eqps = arma, slay = [Equipment() for _ in range(2)]
    arma.equip(arma_helm)
    slay.equip_slayer_helm()
    gloves_tup = (bgloves, zvambs)
    eqps.extend([copy(e) for e in eqps])

    targets = [mon.from_de0(scale) for mon in (LizardmanShaman, DeathlyMage)]
    for t in targets:
        t.apply_vulnerability()

    for eqp_idx, eqp in enumerate(eqps):
        if eqp_idx // 2 == 0:
            eqp.equip(bgloves)
        else:
            eqp.equip(zvambs)

    for boost in (BastionPotion, Overload):
        _, table = bedevere_2d(
            lad,
            targets,
            equipment=eqps,
            prayers=Rigour,
            boosts=boost,
            meta_header=str(boost),
            **kwargs
        )
        print(table)


def mystics_max_hit_comparisons(scale: int, **kwargs):
    lad = Player()
    lad.equipment.equip_basic_ranged_gear()
    lad.equipment.equip_arma_set()
    lad.active_style = lad.equipment.equip_twisted_bow()

    target = SkeletalMystic.from_de0(scale)

    eqps = b_eqp, z_eqp = [Equipment() for _ in range(2)]
    b_eqp.equip(bgloves)
    z_eqp.equip(zvambs)

    _, table = bedevere_2d(
        lad, target, equipment=eqps, prayers=Rigour, boosts=Overload, **kwargs
    )
    print(table)


def main(**kwargs):
    my_scale = range(26, 27)

    for ms in my_scale:
        # arma_slayer_void_comparison()
        bgloves_zvambs_chin_comparison(
            scale=ms, **kwargs, transpose=True, sort_cols=True
        )
        # mystics_max_hit_comparisons(scale=ms, **kwargs)


if __name__ == "__main__":
    options = {
        "data_mode": DataMode.MAX_HIT,
        "floatfmt": ".0f",
    }
    main(**options)
