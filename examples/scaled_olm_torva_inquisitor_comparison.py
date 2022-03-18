import numpy as np
from copy import copy

from osrs_tools.character import Player, Olm, OlmHead, OlmMageHand, OlmMeleeHand
from osrs_tools.equipment import Equipment, Gear
from osrs_tools.prayer import Piety
from osrs_tools.stats import Overload
from osrs_tools.analysis_tools import DataMode, robin_the_brave, table_2d, bedevere_the_wise


bedevere_2d = table_2d(bedevere_the_wise)

def dwh_comparison(lads: tuple[Player], olms: tuple[OlmMeleeHand], **kwargs):
    options = {}
    options.update(kwargs)

    for lad in lads:
        lad.active_style = lad.equipment.equip_dwh(avernic=True, brimstone=True)

    equipments = (torva_set, inquis_set, bandos_set) = tuple(Equipment() for _ in range(3))
    torva_set.equip_torva_set()
    inquis_set.equip_inquisitor_set()
    bandos_set.equip_bandos_set()

    _, table = bedevere_2d(
        lads,
        olms,
        prayers=Piety,
        boosts=Overload,
        equipment=equipments,
        data_mode=DataMode.DWH_SUCCESS,
        **kwargs
    )
    
    print(table)


def main():
    lads = tuple(Player(name) for name in ('lad', ))
    hammers_range = range(4)

    for lad in lads:
        lad.equipment.equip_basic_melee_gear(brimstone=True)

    olms = tuple(OlmMeleeHand.from_de0(ps) for ps in range(15, 52, 8))
    col_labels_basis = [f'olm ({olm.party_size})' for olm in olms]
    row_labels = ['torva', 'inquis', 'bandos']

    for hammers_landed in hammers_range:
        for olm in olms:
            olm.reset_stats()
        
            for _ in range(hammers_landed):
                olm.apply_dwh()
                

        meta_header = f'DWH Attempt #{hammers_landed}'
        dwh_comparison(lads, olms, transpose=True, col_labels=col_labels_basis, row_labels=row_labels, floatfmt='.2f', meta_header=meta_header)


def limited_switches_dwh_comparison(n: int = 5):
    eqp = Equipment()
    eqp.equip_basic_melee_gear(berserker=False)
    eqp.equip(Gear.from_bb('avernic defender'))
    eqp.equip_inquisitor_set()

    # start with a lad basis of a scaled olm runner (max mage)
    # only guarantee the dwh, everything else is optional
    lad = Player()
    lad.equipment.equip_basic_magic_gear()
    lad.active_style = lad.equipment.equip_dwh(avernic=False, brimstone=True)
    eqp_copy = copy(lad.equipment)

    robin_2d = table_2d(robin_the_brave)

    olms = [OlmMeleeHand.from_de0(ps) for ps in range(15, 60, 8)]
    
    for olm in olms:
        meta_header = f'{olm} w/ base gear: {eqp_copy}'
        _, table = robin_2d(lad, olm, eqp, n, data_mode=DataMode.DWH_SUCCESS, special_attack=True, floatfmt='.3f', meta_header=meta_header, sort_cols=True, ascending=False)
        print(table)


def limited_switches_guardian_comparison(n: int = 5):
    eqp = Equipment()
    eqp.equip_basic_melee_gear(berserker=False)
    eqp.equip(Gear.from_bb('avernic defender'))
    eqp.equip_inquisitor_set()


if __name__ == '__main__':
    # main()
    limited_switches_dwh_comparison()
