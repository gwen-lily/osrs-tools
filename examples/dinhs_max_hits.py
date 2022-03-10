from osrs_tools.character import *
from osrs_tools.analysis_tools import ComparisonMode, DataMode, generic_comparison_better, tabulate_wrapper

def main(**kwargs):
    tank = Player(name='tank')
    dummy = LizardmanShaman.from_de0(15)

    # equipment
    additional_gear = [Gear.from_bb(s) for s in ('infernal cape', 'barrows gloves', 'guardian boots', 'ring of suffering (i)')]
    tank.equipment.equip_dinhs(style=BulwarkStyles.get_style(PlayerStyle.pummel))
    tank.equipment.equip_fury()
    tank.equipment.equip(*additional_gear)

    additional_equipment = (justi_set, torva_set, strength_set) = [Equipment() for _ in range(3)]
    justi_set.equip_justi_set()
    torva_set.equip_torva_set()
    strength_set.equip_basic_melee_gear(torture=True, primordial=True, ferocious=True, berserker=True)
    strength_set.equip_torva_set()
    
    # boosts
    tank.pray(Prayer.piety())
    tank.boost(Overload.overload())

    # comparison
    indices, axes, data_ary = generic_comparison_better(
        tank,
        equipment=additional_equipment,
        target=dummy,
        comparison_mode=ComparisonMode.CARTESIAN,
        data_mode=DataMode.MAX_HIT
    )
    data = data_ary[0, 0, 0, 0, :, 0, 0]
    col_labels = ['equipment', 'max hit']
    row_labels = [str(eqp) for eqp in additional_equipment]

    print(tabulate_wrapper(data, col_labels, row_labels))


def strength_bonus_derivative():
    


if __name__ == '__main__':
    main()