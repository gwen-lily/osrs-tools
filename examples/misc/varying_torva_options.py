from itertools import product

from osrs_tools.analysis_tools import DataMode, bedevere_2d
from osrs_tools.character import OlmMeleeHand, Player
from osrs_tools.equipment import Equipment, Gear, Slots
from osrs_tools.prayer import Piety
from osrs_tools.stats import AggressiveStats, DefensiveStats, Overload, PlayerLevels

book_of_the_dead = Gear(
    name="book of the dead",
    slot=Slots.SHIELD,
    aggressive_bonus=AggressiveStats(magic_attack=6),
    defensive_bonus=DefensiveStats.no_bonus(),
    prayer_bonus=3,
    level_requirements=PlayerLevels.no_requirements(),
)
torva_full_helm = Gear.from_bb("torva full helm")
torva_platebody = Gear.from_bb("torva platebody")
bgloves = Gear.from_bb("barrows gloves")
fgloves = Gear.from_bb("ferocious gloves")
bfury = Gear.from_bb("amulet of blood fury")
tort = Gear.from_bb("amulet of torture")
berserker_ring = Gear.from_bb("berserker (i)")
brimstone_ring = Gear.from_bb("brimstone ring")


def one_torva_options():
    # bring everything, 58 >> 60 with berserker ring (i)

    lad = Player()
    lad.equipment.equip_torva_set()
    lad.equipment.equip_basic_melee_gear(
        torture=False, ferocious=False, berserker=False
    )
    lad.active_style = lad.equipment.equip_lance(avernic=True)

    gear_tuples = ((bgloves, fgloves), (bfury, tort), (berserker_ring, brimstone_ring))
    switches = [Equipment.from_unordered(*g) for g in product(*gear_tuples)]
    boosts = Overload
    prayers = Piety

    target = OlmMeleeHand.from_de0(1)

    _, table = bedevere_2d(
        lad,
        target,
        equipment=switches,
        boosts=boosts,
        prayers=prayers,
        data_mode=DataMode.MAX_HIT,
        floatfmt=".0f",
    )
    print(table)


def one_torva_options():
    # torture / barrows gloves / brimstone ring big camp
    lad = Player()
    lad.equipment.equip_bandos_set()
    lad.equipment.equip(torva_full_helm)
    lad.equipment.equip_basic_melee_gear(
        torture=False, ferocious=False, berserker=False
    )
    lad.active_style = lad.equipment.equip_lance(avernic=True)

    gear_tuples = ((bgloves, fgloves), (bfury, tort), (berserker_ring, brimstone_ring))
    switches = [Equipment.from_unordered(*g) for g in product(*gear_tuples)]
    boosts = Overload
    prayers = Piety

    target = OlmMeleeHand.from_de0(1)

    (data_axes, indicies, data_ary), table = bedevere_2d(
        lad,
        target,
        equipment=switches,
        boosts=boosts,
        prayers=prayers,
        data_mode=DataMode.MAX_HIT,
        floatfmt=".0f",
        sort_cols=False,
    )
    print(table)
    print(data_ary)


def two_torva_options():
    #
    lad = Player()
    lad.equipment.equip_bandos_set()
    lad.equipment.equip(torva_full_helm, torva_platebody)
    lad.equipment.equip_basic_melee_gear(
        torture=False, ferocious=False, berserker=False
    )
    lad.active_style = lad.equipment.equip_lance(avernic=True)

    gear_tuples = ((bgloves, fgloves), (bfury, tort), (berserker_ring, brimstone_ring))
    switches = [Equipment.from_unordered(*g) for g in product(*gear_tuples)]
    boosts = Overload
    prayers = Piety

    target = OlmMeleeHand.from_de0(1)

    (data_axes, indicies, data_ary), table = bedevere_2d(
        lad,
        target,
        equipment=switches,
        boosts=boosts,
        prayers=prayers,
        data_mode=DataMode.MAX_HIT,
        floatfmt=".0f",
        sort_cols=False,
    )
    print(table)


def main():
    # two_torva_options()
    one_torva_options()
    # berserker_check()


if __name__ == "__main__":
    main()
