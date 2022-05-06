from copy import copy
from itertools import product

from osrs_tools.analysis.utils import DataMode, bedevere_2d
from osrs_tools.character import Dummy, Player
from osrs_tools.data import Styles
from osrs_tools.equipment import Equipment, Gear, Slots
from osrs_tools.prayer import Piety
from osrs_tools.stats.stats import Overload
from osrs_tools.style.style import BulwarkStyles, PlayerStyle


def generate_equipment_axis(*gear: Gear | Equipment) -> list[Equipment]:
    """Return a list of all possible Equipment setups.

    Raises:
        TypeError: Raised from arguments of gear.

    Returns:
        list[Equipment]: A list of all possible Equipment setups.
    """

    # gather gear from all sources
    gear_list: list[Gear] = []
    eqp_list: list[Equipment] = []
    slots_dict: dict[Slots, list[Gear]] = {k: [] for k in Slots}

    for item in gear:
        if isinstance(item, Gear):
            gear_list.append(item)
        elif isinstance(item, Equipment):
            gear_list.extend(item.equipped_gear)
        else:
            raise TypeError(item)

    # organize all gear into lists of gear per slot
    for g in gear_list:
        slots_dict[g.slot].append(g)

    filtered_slots_dict = copy(slots_dict)

    for k, v in slots_dict.items():
        if len(v) == 0:
            filtered_slots_dict.pop(k)

    # generate all possible Equipment combinations
    for loadout in product(*filtered_slots_dict.values()):
        eqp_list.append(Equipment.from_gear(*loadout))

    return eqp_list


def dinhs_max(**kwargs):

    eligible_gear = [
        fury,
        torture,
        prims,
        guardian_boots,
        bgloves,
        fgloves,
        suffering,
        berserker,
    ]

    options = {
        "prayers": Piety,
        "boosts": Overload,
        "data_mode": DataMode.MAX_HIT,
        "floatfmt": ".0f",
        "special_attack": True,
    }
    options.update(kwargs)

    normal_equipment_axis = generate_equipment_axis(*eligible_gear)
    salve_equipment_axis = generate_equipment_axis(
        *[g for g in eligible_gear if g.slot is not Slots.NECK]
    )
    lad_names = ("torva (salve ei)", "torva (slayer helm)", "torva", "justi")
    lads = [Player(name=name) for name in lad_names]
    torva_lads = torva_salve, torva_slayer, _ = lads[:3]
    normal_lads = lads[1:]

    justi = lads[3]

    justi.equipment.equip_justi_set()

    for tl in torva_lads:
        tl.equipment.equip_torva_set()

    torva_slayer.equipment.equip_slayer_helm()
    torva_salve.equipment.equip_salve()
    dummy = Dummy()

    attack_style = BulwarkStyles.get_by_style(Styles.PUMMEL)
    assert isinstance(attack_style, PlayerStyle)

    for lad in lads:
        lad.active_style = lad.equipment.equip_dinhs(style=attack_style)
        lad.equipment.equip(infernal_cape)

    # justi, torva, torva (slayer)
    mh = "Non-salve (Overload, Piety)"
    _, normal_table = bedevere_2d(
        normal_lads,
        dummy,
        equipment=normal_equipment_axis,
        meta_header=mh,
        transpose=True,
        **options
    )
    print(normal_table)

    # torva (salve ei)
    mh = "Salve (Torva, Overload, Piety)"

    _, salve_table = bedevere_2d(
        torva_salve, dummy, equipment=salve_equipment_axis, meta_header=mh, **options
    )
    print(salve_table)

    return normal_table, salve_table


if __name__ == "__main__":
    # gear of interest
    fury = Gear.from_bb("amulet of fury")
    torture = Gear.from_bb("amulet of torture")

    prims = Gear.from_bb("primordial boots")
    guardian_boots = Gear.from_bb("guardian boots")

    bgloves = Gear.from_bb("barrows gloves")
    fgloves = Gear.from_bb("ferocious gloves")

    suffering = Gear.from_bb("ring of suffering (i)")
    berserker = Gear.from_bb("berserker (i)")

    salve = Gear.from_bb("salve amulet (ei)")

    infernal_cape = Gear.from_bb("infernal cape")

    tables = dinhs_max()

    with open("out.txt", "w", encoding="UTF8") as f:
        for t in tables:
            f.writelines(t)
            f.write("\n")
