from copy import copy
from itertools import product

from ..data import Slots
from .equipment import Equipment
from .gear import Gear


def generate_all_equipments(
    *gear: Gear | Equipment, sets: list[Equipment] | Equipment | None = None
) -> list[Equipment]:
    """Return a list of all possible Equipment setups given options.

    If optional sets are specified, any equipment set generated that does not contain all of the items in at least one
    set will be rejected.

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
        eqp = Equipment()
        eqp = eqp.equip(*loadout)
        eqp_list.append(eqp)

    if sets is None:
        return eqp_list

    # filter out slots that don't contain a set
    if isinstance(sets, Equipment):
        sets = [sets]

    filtered_eqp_list: list[Equipment] = []

    for eqp in eqp_list:
        for _set in sets:
            if all(g in eqp.equipped_gear for g in _set.equipped_gear):
                filtered_eqp_list.append(eqp)
                break

    return filtered_eqp_list
