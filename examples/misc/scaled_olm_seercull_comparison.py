import math
from copy import copy

import numpy as np
from osrs_tools.analysis_tools import (
    DataMode,
    bedevere_the_wise,
    robin_the_brave,
    table_2d,
)
from osrs_tools.character import (
    Dummy,
    Guardian,
    Olm,
    OlmHead,
    OlmMageHand,
    OlmMeleeHand,
    Player,
)
from osrs_tools.data import Stances
from osrs_tools.equipment import Equipment, Gear
from osrs_tools.prayer import Augury, Piety
from osrs_tools.stats import Overload
from osrs_tools.style import BulwarkStyles

bedevere_2d = table_2d(bedevere_the_wise)


def seercull_comparison(olms: OlmMageHand | tuple[OlmMageHand], **kwargs):
    options = {"data_mode": DataMode.DPT}
    options.update(kwargs)

    # seercull data
    ranger = Player(name="seercull specialist")
    ranger.equipment.equip_basic_ranged_gear()
    ranger.equipment.equip_arma_set(zaryte=True)
    ranger.active_style = ranger.equipment.equip_seercull()
    ranger.equipment.equip(Gear.from_bb("amethyst arrow"))  # NOTE: AMETHYST ARROWS
    assert ranger.equipment.full_set

    mean_hit = math.floor(
        ranger.damage_distribution(Dummy(), special_attack=True).mean_hit
    )

    normal_olms: list[OlmMageHand] = [copy(olm) for olm in olms]
    culled_olms: list[OlmMageHand] = [copy(olm) for olm in olms]

    for olm in culled_olms:
        olm.apply_seercull(mean_hit)
        olm.name += " [seercull]"

    combined_olms = []
    for o1, o2 in zip(normal_olms, culled_olms, strict=True):
        combined_olms.append(o1)
        combined_olms.append(o2)

    lad = Player()
    lad.equipment.equip_basic_magic_gear()
    lad.active_style = lad.equipment.equip_sang()

    (axes_dict, indices, data), table = bedevere_2d(
        lad, combined_olms, prayers=Augury, boosts=Overload, **kwargs
    )

    # print(data)
    print(table)


def main():
    olms = tuple(OlmMageHand.from_de0(ps) for ps in range(15, 52, 8))
    # meta_header = f'DWH Attempt #{hammers_landed}'
    seercull_comparison(
        olms, floatfmt=".2f", data_mode=DataMode.DPT
    )  # , transpose=True, col_labels=col_labels_basis, row_labels=row_labels, floatfmt='.2f', meta_header=meta_header)


# def sim_lmao():
#     guardian = Guardian.from_de0(1, party_average_mining_level=40)
#     sim = Player(name='sim')
#     sim.active_style = sim.equipment.equip_dinhs(style=BulwarkStyles.get_by_stance(Stances.accurate))

#     dam = sim.damage_distribution(guardian, special_attack=True)
#     print(dam.probability_nonzero_damage, dam.mean_hit)

#     sim.equipment.equip_torva_set()
#     sim.equipment.equip_basic_melee_gear()
#     assert sim.equipment.full_set

#     dam = sim.damage_distribution(guardian, special_attack=True)
#     print(dam.probability_nonzero_damage, dam.mean_hit)


if __name__ == "__main__":
    main()
    # sim_lmao()
