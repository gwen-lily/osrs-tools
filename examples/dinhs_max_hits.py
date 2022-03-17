from osrs_tools.character import *
from osrs_tools.analysis_tools import DataMode, bedevere_the_wise, table_2d
from itertools import product

@table_2d
def dinhs_max(lads: tuple[Player], gear_swap_tuples: tuple[tuple], **kwargs):

    equipment_axis = list([Equipment(**{g.slot.name: g for g in gear_tuple}) for gear_tuple in product(*gear_swap_tuples)])

    return bedevere_the_wise(
        lads,
        dummy,
        prayers=Piety,
        boosts=Overload,
        equipment=equipment_axis,
        **kwargs
    )


if __name__ == '__main__':
    # gear of interest
    fury = Gear.from_bb('amulet of fury')
    torture = Gear.from_bb('amulet of torture')

    prims = Gear.from_bb('primordial boots')
    guardian_boots = Gear.from_bb('guardian boots')

    bgloves = Gear.from_bb('barrows gloves')
    fgloves = Gear.from_bb('ferocious gloves')

    suffering = Gear.from_bb('ring of suffering (i)')
    berserker = Gear.from_bb('berserker (i)')

    salve = Gear.from_bb('salve amulet (ei)')

    # equipment swap cartesian product construction
    # gear_swap_tuples = [
    #     (salve, ),
    #     (prims, guardian_boots),
    #     (bgloves, fgloves),
    #     (suffering, berserker),
    # ]

    gear_swap_tuples = [
        (fury, torture),
        (prims, guardian_boots),
        (bgloves, fgloves),
        (suffering, berserker),
    ]

    lad_names = (
        'torva (slayer helm)', 
        'torva', 
        'justi'
        )
    lads = torva_slayer, torva, justi = [Player(name=name) for name in lad_names]
    
    justi.equipment.equip_justi_set()
    torva.equipment.equip_torva_set()
    torva_slayer.equipment.equip_torva_set()
    torva_slayer.equipment.equip_slayer_helm()
    dummy = Dummy()

    for lad in lads:
        lad.active_style = lad.equipment.equip_dinhs(style=BulwarkStyles.get_by_style(Styles.pummel))
        lad.equipment.equip_basic_melee_gear(
            torture=False,
            primordial=False,
            infernal=True,
            ferocious=False,
            berserker=False,
        )

        # boosts
        lad.pray(Piety)
        lad.boost(Overload)
 

    _, table = dinhs_max(lads, gear_swap_tuples, transpose=True, special_attack=True, data_mode=DataMode.MAX_HIT)
    print(table)
