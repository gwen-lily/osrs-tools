import math
from itertools import product
from random import random

import numpy as np
import pandas as pd
from osrs_tools import analysis_tools
from osrs_tools.analysis_tools import DataMode, bedevere_2d, tabulate_enhanced
from osrs_tools.character import OlmHead, OlmMageHand, OlmMeleeHand, Player
from osrs_tools.damage import Damage
from osrs_tools.equipment import Equipment, Gear, Slots, Weapon
from osrs_tools.prayer import Augury, Piety, Prayer, Rigour
from osrs_tools.stats import AggressiveStats, DefensiveStats, Overload, PlayerLevels
from osrs_tools.style import MonsterStyle
from tabulate import tabulate

avernic_defender = Gear.from_bb("avernic defender")
elysian_spirit_shield = Gear.from_bb("elysian spirit shield")
ring_of_endurance = Gear(
    name="ring of endurance",
    slot=Slots.RING,
    aggressive_bonus=AggressiveStats.no_bonus(),
    defensive_bonus=DefensiveStats.no_bonus(),
    prayer_bonus=0,
    level_requirements=PlayerLevels.no_requirements(),
)
book_of_the_dead = Gear(
    name="book of the dead",
    slot=Slots.SHIELD,
    aggressive_bonus=AggressiveStats(magic_attack=6),
    defensive_bonus=DefensiveStats.no_bonus(),
    prayer_bonus=3,
    level_requirements=PlayerLevels.no_requirements(),
)
torva_full_helm = Gear.from_bb("torva full helm")
bgloves = Gear.from_bb("barrows gloves")
fgloves = Gear.from_bb("ferocious gloves")
arcane_spirit_shield = Gear.from_bb("arcane spirit shield")
berserker_ring = Gear.from_bb("berserker (i)")


def solo_olm_ticks_and_points_estimate(scale: int, **kwargs):

    options = {
        "floatfmt": ".1f",
        "thrall_dpt": Damage.thrall().per_tick,
        "melee_hand_defence": 0,
    }
    options.update(kwargs)

    # MAGIC HAND #######################################################################################################
    mage_lad = Player(name="mage lad")
    mage_lad.boost(Overload)
    mage_lad.prayers_coll.pray(Augury)
    mage_lad.equipment.equip_basic_magic_gear(arcane=False, brimstone=False)
    mage_lad.active_style = mage_lad.equipment.equip(
        ring_of_endurance, book_of_the_dead, Weapon.from_bb("sanguinesti staff")
    )
    assert mage_lad.equipment.full_set

    magic_hand = OlmMageHand.from_de0(scale)
    dpt = mage_lad.damage_distribution(magic_hand).per_tick + options["thrall_dpt"]
    magic_damage_ticks_per_phase = magic_hand.base_hp / dpt
    specs_before_melee_starts = int(np.round(2 + magic_damage_ticks_per_phase / 250))

    magic_ticks = magic_hand.count_per_room() * magic_damage_ticks_per_phase
    magic_hand_points = magic_hand.points_per_room()

    # MELEE HAND #######################################################################################################
    melee_lad = Player(name="melee lad")
    melee_lad.boost(Overload)
    melee_lad.prayers_coll.pray(Piety)
    melee_lad.equipment.equip_basic_melee_gear(
        berserker=False, torture=False, ferocious=False
    )
    melee_lad.equipment.equip_fury(blood=True)
    melee_lad.equipment.equip_torva_set()
    melee_lad.active_style = melee_lad.equipment.equip_lance(berserker=False)
    melee_lad.equipment.equip(ring_of_endurance, bgloves)
    assert melee_lad.equipment.full_set

    melee_hand = OlmMeleeHand.from_de0(scale)
    melee_hand.levels.defence = options["melee_hand_defence"]

    dpt = melee_lad.damage_distribution(melee_hand).per_tick + options["thrall_dpt"]
    melee_damage_ticks_per_phase = melee_hand.base_hp / dpt

    melee_ticks = melee_hand.count_per_room() * melee_damage_ticks_per_phase
    melee_hand_points = melee_hand.points_per_room()

    # HEAD PHASE #######################################################################################################
    ranger_lad = Player(name="ranger lad")
    ranger_lad.boost(Overload)
    ranger_lad.prayers_coll.pray(Rigour)
    ranger_lad.equipment.equip_basic_ranged_gear(brimstone=False)
    ranger_lad.equipment.equip_arma_set(zaryte=False)
    ranger_lad.equipment.equip(ring_of_endurance, bgloves)
    ranger_lad.active_style = ranger_lad.equipment.equip_twisted_bow()
    assert ranger_lad.equipment.full_set

    olm_head = OlmHead.from_de0(scale)
    dpt = ranger_lad.damage_distribution(olm_head).per_tick + options["thrall_dpt"]
    ranged_ticks = olm_head.base_hp / dpt

    ranged_points = olm_head.points_per_room()

    total_ticks = magic_ticks + melee_ticks + ranged_ticks
    total_points = magic_hand_points + melee_hand_points + ranged_points
    return total_ticks, total_points


def duo_olm_ticks_and_points_estimate(scale: int, trials: int = 50, **kwargs):
    options = {
        "floatfmt": ".1f",
    }
    options.update(kwargs)

    # One Lad / Two Lad / Red Lad / Blue Lad  ##########################################################################
    # yuusuke: 	thralls
    # kuwabara: potshare + humidify
    # puusuke: 	the thrall
    lads = (yuusuke, kuwabara) = tuple(Player(name=n) for n in ("yuusuke", "kuwabara"))
    puusuke = Damage.thrall()

    # MAGE HAND ########################################################################################################
    magic_hand = OlmMageHand.from_de0(scale)

    yuusuke.equipment.equip(book_of_the_dead)
    kuwabara.equipment.equip(arcane_spirit_shield)

    for lad in lads:
        lad.equipment.equip_basic_magic_gear(arcane=False)
        lad.active_style = lad.equipment.equip_sang(arcane=False)
        assert lad.equipment.full_set

        lad.boost(Overload)
        lad.pray(Augury)

    yu_mage_dpt = yuusuke.damage_distribution(magic_hand).per_tick
    ku_mage_dpt = kuwabara.damage_distribution(magic_hand).per_tick
    pu_mage_dpt = puusuke.per_tick
    mage_dpt = sum([yu_mage_dpt, ku_mage_dpt, pu_mage_dpt])

    mage_tpp = magic_hand.base_hp / mage_dpt

    mage_total_ticks = magic_hand.count_per_room() * mage_tpp
    mage_total_points = magic_hand.points_per_room()

    # MELEE HAND #######################################################################################################
    melee_hand = OlmMeleeHand.from_de0(scale)

    ticks_per_spec = 250
    pre_melee_specs = int(np.round(2 + mage_tpp / ticks_per_spec))
    hammer_target = 3

    trials_ary = np.arange(trials)
    data_ary = np.empty(shape=trials_ary.shape, dtype=int)

    def switch_lads_to_bgs():
        for lad in lads:
            lad.active_style = lad.equipment.equip_bgs()
            lad.equipment.equip(berserker_ring)

    def switch_lads_to_lance():
        for lad in lads:
            lad.active_style = lad.equipment.equip_lance(berserker=True)

    for trial in trials_ary:
        melee_hand.reset_stats()
        hammers_landed = 0
        simulated_ticks = -1

        # prep the lads for hammer shenanigans
        for lad in lads:
            lad.equipment.equip_basic_melee_gear(berserker=False)
            lad.equipment.equip_torva_set()
            lad.active_style = lad.equipment.equip_dwh(avernic=True)

            lad.reset_stats()
            lad.reset_prayers()

            lad.pray(Piety)
            lad.boost(Overload)

        # drop hammers until target, then bgs
        for _ in range(pre_melee_specs):

            if yuusuke.equipment.dwh:
                p_yu = yuusuke.damage_distribution(
                    melee_hand, special_attack=True
                ).probability_nonzero_damage

                if random() < p_yu:
                    melee_hand.apply_dwh()
                    hammers_landed += 1

                    if hammers_landed == hammer_target:
                        switch_lads_to_bgs()
            else:
                dam = yuusuke.damage_distribution(
                    melee_hand, special_attack=True
                ).random_hit()

                assert isinstance(dam, int)
                melee_hand.apply_bgs(dam)
                melee_hand.damage(yuusuke, dam)

            if kuwabara.equipment.dwh:
                p_ku = kuwabara.damage_distribution(
                    melee_hand, special_attack=True
                ).probability_nonzero_damage

                if random() < p_ku:
                    melee_hand.apply_dwh()
                    hammers_landed += 1

                    if hammers_landed == hammer_target:
                        switch_lads_to_bgs()
            else:
                dam = kuwabara.damage_distribution(
                    melee_hand, special_attack=True
                ).random_hit()
                melee_hand.apply_bgs(dam)
                melee_hand.damage(kuwabara, dam)

        # prep the lads for damage and remaining bgs # TODO: Add additional dwh capability (not expected)
        switch_lads_to_lance()

        yu_cached_dam = None
        ku_cached_dam = None
        last_olm_def = melee_hand.levels.defence

        while int(melee_hand.levels.defence) > 0:
            simulated_ticks += 1

            # continue speccing until 0 defence
            if (simulated_ticks % ticks_per_spec) == 0:
                switch_lads_to_bgs()

                for lad in lads:
                    dam = lad.damage_distribution(
                        melee_hand, special_attack=True
                    ).random_hit()
                    melee_hand.apply_bgs(dam)
                    melee_hand.damage(lad, dam)

                switch_lads_to_lance()

            # if defence changed, re-calculate reference damage distributions
            if yu_cached_dam is None or melee_hand.levels.defence != last_olm_def:
                yu_cached_dam = yuusuke.damage_distribution(melee_hand)

            if ku_cached_dam is None or melee_hand.levels.defence != last_olm_def:
                ku_cached_dam = kuwabara.damage_distribution(melee_hand)

            # apply damage, all three lads
            if (simulated_ticks % yuusuke.attack_speed()) == 0:
                yu_dv = yu_cached_dam.random_hit()
                ku_dv = ku_cached_dam.random_hit()

                melee_hand.damage(yuusuke, yu_dv)
                melee_hand.damage(kuwabara, ku_dv)

            if (simulated_ticks % puusuke.attack_speed) == 0:
                pu_dv = puusuke.random_hit()
                melee_hand.damage(yuusuke, pu_dv)

            last_olm_def = melee_hand.levels.defence

        # simple calculation for the remainder
        switch_lads_to_lance()

        yu_melee_dpt = yuusuke.damage_distribution(melee_hand).per_tick
        ku_melee_dpt = kuwabara.damage_distribution(melee_hand).per_tick
        pu_melee_dpt = puusuke.per_tick
        melee_dpt = sum([yu_melee_dpt, ku_melee_dpt, pu_melee_dpt])

        remaining_tpp = melee_hand.levels.hitpoints / melee_dpt
        melee_tpp = simulated_ticks + remaining_tpp
        data_ary[trial] = melee_tpp

    melee_mean_tpp = math.floor(data_ary.mean())

    melee_total_ticks = melee_hand.count_per_room() * melee_mean_tpp
    melee_total_points = melee_hand.points_per_room()

    # HEAD PHASE #######################################################################################################
    for lad in lads:
        lad.equipment.equip_basic_ranged_gear()
        lad.equipment.equip_arma_set(zaryte=True)
        lad.active_style = lad.equipment.equip_twisted_bow()
        assert lad.equipment.full_set

        lad.reset_stats()
        lad.boost(Overload)

        lad.reset_prayers()
        lad.pray(Rigour)

    olm_head = OlmHead.from_de0(scale)

    yu_ranged_dpt = yuusuke.damage_distribution(olm_head).per_tick
    ku_ranged_dpt = kuwabara.damage_distribution(olm_head).per_tick
    pu_ranged_dpt = puusuke.per_tick
    ranged_dpt = sum([yu_ranged_dpt, ku_ranged_dpt, pu_ranged_dpt])

    ranged_tpp = melee_hand.base_hp / ranged_dpt

    ranged_total_ticks = olm_head.count_per_room() * ranged_tpp
    ranged_total_points = olm_head.points_per_room()

    # CLEANUP ##########################################################################################################
    total_olm_ticks = mage_total_ticks + melee_total_ticks + ranged_total_ticks
    total_olm_points = mage_total_points + melee_total_points + ranged_total_points

    # time
    olm_mins = total_olm_ticks / TICKS_PER_MINUTE
    mage_mpp = mage_tpp / TICKS_PER_MINUTE
    melee_mean_mpp = melee_mean_tpp / TICKS_PER_MINUTE
    ranged_mpp = ranged_tpp / TICKS_PER_MINUTE

    # 1 stam * (4 doses / 1 stam) * (2 minutes / 1 dose) * (100 ticks / 1 minute)
    minimum_stams_needed = math.ceil(total_olm_ticks / (1 * 4 * 2 * 100))

    # table data #
    table_data = [olm_mins, mage_mpp, melee_mean_mpp, ranged_mpp, minimum_stams_needed]
    col_labels = [
        "olm time (min)",
        "mage phase (min)",
        "melee phase (min)",
        "head phase (min)",
        "min. stams needed",
    ]

    return table_data, col_labels


# nonsense


def magic_shield_comparison(**kwargs):

    options = {
        "floatfmt": ".1f",
    }
    options.update(kwargs)

    lad = Player(name="lad")
    lad.boost(Overload)
    lad.prayers_coll.pray(Augury)

    lad.equipment.equip_basic_magic_gear(arcane=False, brimstone=False)
    lad.active_style = lad.equipment.equip(
        ring_of_endurance, Weapon.from_bb("sanguinesti staff")
    )

    equipment = [
        Equipment(shield=Gear.from_bb("arcane spirit shield")),
        Equipment(shield=book_of_the_dead),
    ]

    olms = [OlmMageHand.from_de0(ps) for ps in range(15, 32, 8)]

    indices, axes, data_ary = analysis_tools.bedevere_the_wise(
        players=lad,
        equipment=equipment,
        target=olms,
        data_mode=DataMode.DPS,
    )

    row_axis = 4
    col_axis = 6

    data = data_ary[0, 0, 0, 0, :, 0, :]
    table_data = []

    for index, row in enumerate(data):
        row_with_label = [axes[row_axis][index]] + list(row)
        table_data.append(row_with_label)

    headers = [f"Olm Mage Hand ({ps:.0f})" for ps in range(15, 32, 8)]
    table = tabulate(table_data, headers=headers, floatfmt=options["floatfmt"])
    print(table)


def olm_damage_estimate(**kwargs):
    options = {
        "floatfmt": ".1f",
        "scales": range(15, 32, 8),
    }
    options.update(kwargs)

    melee_lad = Player(name="melee_lad")
    mage_lad = Player(name="mage_lad")

    # equipment
    melee_lad.equipment.equip_basic_melee_gear(berserker=False, torture=False)
    melee_lad.equipment.equip_torva_set()
    melee_lad.active_style = melee_lad.equipment.equip_lance(avernic=False)
    melee_lad.equipment.equip_fury(blood=True)
    melee_lad.equipment.equip(ring_of_endurance, avernic_defender)
    assert melee_lad.equipment.full_set

    # boosts / inits
    melee_lad.boost(Overload)
    melee_lad.prayers_coll.pray(Piety)

    olms = [OlmHead.from_de0(ps) for ps in options["scales"]]
    ref_olm = olms[0]

    def switch_to_last(player: Player, last_auto: MonsterStyle):
        if last_auto == ref_olm.styles_coll.get_style(Style.ranged):
            player.prayers_coll.reset_prayers()
            player.pray(Piety, Prayer.protect_from_missiles())
        elif last_auto == ref_olm.styles_coll.get_style(Style.magic):
            player.prayers_coll.reset_prayers()
            player.prayers_coll.pray(Piety, Prayer.protect_from_magic())
        else:
            raise NotImplementedError(f"{last_auto}")

    def camp_mage(player: Player, last_auto: MonsterStyle):
        if (
            Prayer.protect_from_magic() in player.prayers_coll
            and Piety in player.prayers_coll
        ):
            pass
        else:
            player.prayers_coll.reset_prayers()
            player.pray(Piety, Prayer.protect_from_magic())

    for olm in olms:
        scale = olm.party_size

        # praying magic
        melee_lad.prayers_coll.reset_prayers()
        melee_lad.pray(Piety, Prayer.protect_from_magic())

        olm.active_style = olm.styles_coll.get_style(Style.magic)
        magic_mean_dmg = (
            olm.chance_to_attack_magic() * olm.damage_distribution(melee_lad).mean
        )

        olm.active_style = olm.styles_coll.get_style(Style.ranged)
        ranged_mean_dmg = (1 - olm.chance_to_attack_magic()) * olm.damage_distribution(
            melee_lad
        ).mean

        print(f"{scale}, {magic_mean_dmg}, {ranged_mean_dmg}, (praying magic)")

        # praying ranged
        melee_lad.prayers_coll.reset_prayers()
        melee_lad.pray(Piety, Prayer.protect_from_missiles())
        magic_mean_dmg = (
            olm.chance_to_attack_magic() * olm.damage_distribution(melee_lad).mean
        )

        olm.active_style = olm.styles_coll.get_style(Style.magic)
        magic_mean_dmg = (
            olm.chance_to_attack_magic() * olm.damage_distribution(melee_lad).mean
        )

        olm.active_style = olm.styles_coll.get_style(Style.ranged)
        ranged_mean_dmg = (1 - olm.chance_to_attack_magic()) * olm.damage_distribution(
            melee_lad
        ).mean

        print(f"{scale}, {magic_mean_dmg}, {ranged_mean_dmg}, (praying ranged)")


def melee_hand_mean_defence(scale: int, total_specs: int, hammers_first: int, **kwargs):
    options = {
        "trials": 1e3,
    }
    options.update(kwargs)
    trials = int(options["trials"])

    lad_1 = Player(name="lad 1")
    lad_2 = Player(name="lad 2")
    lads = [lad_1, lad_2]

    for lad in lads:
        lad.boost(Overload)
        lad.prayers_coll.pray(Piety)

        lad.equipment.equip_basic_melee_gear(berserker=False, torture=False)
        lad.equipment.equip_torva_set()
        lad.equipment.equip(Gear.from_bb("amulet of fury"))

    lad_1.active_style = lad_1.equipment.equip_dwh(
        inquisitor_set=False, avernic=True, brimstone=False
    )
    lad_2.active_style = lad_2.equipment.equip(SpecialWeapon.from_bb("bandos godsword"))

    defence_data = np.empty(shape=(trials,), dtype=int)
    olm = OlmMeleeHand.from_de0(party_size=scale)

    defence_range = np.arange(0, olm.base_levels.defence + 1)
    dwh_p_ary = np.empty(shape=defence_range.shape, dtype=float)
    bgs_dam_ary = np.empty(shape=defence_range.shape, dtype=Damage)

    for index, defence in enumerate(defence_range):
        olm.levels.defence = defence
        dwh_p_ary[index] = lad_1.damage_distribution(
            olm, special_attack=True
        ).chance_to_deal_positive_damage
        bgs_dam_ary[index] = lad_2.damage_distribution(olm, special_attack=True)

    for index in range(trials):
        olm.reset_stats()
        dwh_landed = 0

        for _ in range(total_specs):
            if dwh_landed < hammers_first:
                p = dwh_p_ary[olm.levels.defence]

                if random() < p:
                    dwh_landed += 1
                    olm.apply_dwh()
            else:
                bgs_dam: Damage = bgs_dam_ary[olm.levels.defence]
                olm.apply_bgs(bgs_dam.random()[0])

        defence_data[index] = olm.levels.defence

    return defence_data.mean()


def melee_max_hits():
    lad = Player(name="olm solo fit")
    lad.equipment.equip_bandos_set()
    lad.equipment.equip_basic_melee_gear(
        torture=False, ferocious=False, berserker=False
    )
    lad.equipment.equip_fury(blood=True)
    lad.equipment.equip(ring_of_endurance, torva_full_helm)
    lad.active_style = lad.equipment.equip_lance()

    gear_swap_tuples = ((bgloves, fgloves),)

    equipment_axis = list(
        [
            Equipment(**{g.slot.name: g for g in gear_tuple})
            for gear_tuple in product(*gear_swap_tuples)
        ]
    )

    olm = OlmMeleeHand.from_de0(1)

    _, table = bedevere_2d(
        lad,
        olm,
        equipment=equipment_axis,
        boost=Overload,
        prayers=Piety,
        data_mode=DataMode.MAX_HIT,
        floatfmt=".0f",
    )

    print(table)


def olm_max_hits(**kwargs):
    options = {
        "scales": range(1, 101),
    }
    options.update(kwargs)
    lad = Player(name="dummy")
    data = []
    headers = ["scale", "normal", "crippled", "enraged", "head phase"]

    for ps in options["scales"]:
        olm = OlmHead.from_de0(ps)
        row = [
            olm.party_size,
            olm.max_hit(lad),
            olm.max_hit(lad, crippled=True),
            olm.max_hit(lad, enraged=True),
            olm.max_hit(lad, head_phase=True),
        ]
        data.append(row)

    df = pd.DataFrame(data, columns=headers, dtype=int)
    df.to_csv("olm max hits.csv", sep="\t")

    table = tabulate(data, headers, floatfmt=".0f")
    print(table)


if __name__ == "__main__":
    scales_range = range(15, 40, 4)

    outer_table_data = []

    for my_scale in scales_range:
        table_data, col_labels = duo_olm_ticks_and_points_estimate(my_scale, trials=1)
        outer_table_data.append(table_data)

    col_labels.insert(0, "scale")
    row_labels = [str(s) for s in scales_range]
    meta_header = "duo olm estimates"

    table = tabulate_enhanced(
        outer_table_data,
        col_labels=col_labels,
        row_labels=row_labels,
        meta_header=meta_header,
        floatfmt=".1f",
    )
    print(table)
