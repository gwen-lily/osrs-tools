import math
from enum import Enum, auto
from random import random

import numpy as np
from matplotlib import pyplot as plt
from osrs_tools.analysis_tools import tabulate_enhanced
from osrs_tools.character import AbyssalPortal, DeathlyMage, DeathlyRanger, Guardian, Player, SkeletalMystic
from osrs_tools.damage import Damage
from osrs_tools.data import Level, Styles
from osrs_tools.equipment import Equipment
from osrs_tools.prayer import Piety, ProtectFromMagic, Rigour
from osrs_tools.stats import BastionPotion, Boost, Overload, PlayerLevels, SuperAttackPotion, SuperCombatPotion
from osrs_tools.style import ChinchompaStyles
from osrs_tools.unique_loot_calculator import individual_point_cap, zero_purple_chance

from scaled_smol_olms import solo_olm_ticks_and_points_estimate


def guardian_estimates(scale: int, boost: Boost, **kwargs) -> tuple[float, int]:
    """
    Simple guardian room estimate method at any scale or boost for scaled solos.

    This method initially had a lot more sugar and enums and procedures and trials going on, but then I realized if
    you're not chickening guardians or at the very least reducing its defence to zero for the whole kill you're trolling
    yourself.
    """
    options = {
        "party_average_mining_level": 61 * (15 / 31)
        + 85 * (5 / 31) * 1 * (11 / 31),  # hack math based on the alts I usually use
        "guardian_alts": 4,
        "guardian_alt_levels": PlayerLevels(attack=Level(99), strength=Level(99), mining=Level(61)),
    }
    options.update(kwargs)
    extra_lads = options["guardian_alts"]

    guardian = Guardian.from_de0(scale, party_average_mining_level=options["party_average_mining_level"])
    lad = Player(name="guardians fit")

    # gear
    lad.equipment.equip_basic_melee_gear(torture=False, brimstone=True)
    lad.equipment.equip_fury(blood=True)
    lad.equipment.equip_torva_set()
    lad.active_style = lad.equipment.equip_dragon_pickaxe()

    # boosts
    lad.prayers_coll.pray(Piety)
    lad.boost(boost)

    # dwh / bgs / zero defence assumed if you have enough alts
    guardian.levels.defence = 0
    lad_dpt = lad.damage_distribution(guardian).per_tick
    points_raw = guardian.points_per_room()

    if extra_lads:
        extra_lad = Player(name="guardian alt", base_levels=options["guardian_alt_levels"])
        extra_lad.equipment.equip_basic_melee_gear()
        extra_lad.equipment.equip_bandos_set()
        extra_lad.active_style = extra_lad.equipment.equip_dragon_pickaxe(avernic=True, berserker=True)
        assert extra_lad.equipment.full_set

        extra_lad.boost(boost)
        extra_lad.prayers_coll.pray(Piety)

        extra_lad_dpt = extra_lad.damage_distribution(guardian).per_tick

        dpt_ary = np.asarray([lad_dpt, *(extra_lad_dpt,) * extra_lads])
        dpt = dpt_ary.sum()
        damage_ticks = guardian.count_per_room() * guardian.base_levels.hitpoints / dpt
        #                       lads [unitless] * (ticks / room) * (damage / tick) * (points / damage) = points / room
        total_points = points_raw - extra_lads * damage_ticks * extra_lad_dpt * guardian.points_per_hitpoint

    else:
        dpt = lad.damage_distribution(guardian).per_tick
        damage_ticks = guardian.count_per_room() * guardian.base_levels.hitpoints / dpt
        total_points = points_raw

    setup_ticks = 20 * 6 + 100  # 100 for inefficiency and jank
    total_ticks = setup_ticks + damage_ticks
    return total_ticks, total_points


class MysticModes(Enum):
    tbow_thralls = auto()
    tbow_thralls_simulated_spec_transfer = auto()
    chin_six_by_two = auto()
    chin_ten = auto()


def mystics_estimates(scale: int, mode: MysticModes, **kwargs) -> tuple[float, int]:
    """
    Simple mystic room estimate method for afk-tbow-thralling them as usual and chinning big stacks of large lads.

    Extended description.
    """
    options = {
        "scale_at_load_time": scale,
        "dwh_attempts_per_mystic": 3,
        "dwh_specialist_equipment": None,
        "dwh_specialist_target_strength_level": 13,
        "spec_transfer_alts": 6,
        "dwh_target_per_mystic": 3,
        "dwh_health_remaining_ratio_threshold": 0.50,
    }
    options.update(kwargs)

    # top level information
    mystic = SkeletalMystic.from_de0(options["scale_at_load_time"])
    mystics_per_room = mystic.count_per_room(options["scale_at_load_time"])
    trials = options["trials"]

    if mode is MysticModes.tbow_thralls:
        lad = Player(name="mystics fit")
        dwh_specialist = Player(name="dwh specialist")

        # gear
        lad.active_style = lad.equipment.equip_twisted_bow()
        lad.equipment.equip_arma_set(zaryte=True)
        lad.equipment.equip_basic_ranged_gear(anguish=False)
        lad.equipment.equip_salve()
        assert lad.equipment.full_set

        if options["dwh_specialist_equipment"] is None:
            dwh_specialist.equipment.equip_basic_melee_gear(torture=False, infernal=False, berserker=False)
            dwh_specialist.active_style = dwh_specialist.equipment.equip_dwh(
                inquisitor_set=True, avernic=True, tyrannical=True
            )
            dwh_specialist.equipment.equip_salve()
            dwh_specialist.equipment.equip(mythical_cape)
            assert dwh_specialist.equipment.full_set

        # boosts
        lad.boost(Overload)
        lad.prayers_coll.pray(Rigour, ProtectFromMagic)

        dwh_specialist.levels.strength = options["dwh_specialist_target_strength_level"]
        dwh_specialist.boost(SuperAttackPotion)
        dwh_specialist.prayers_coll.pray(Piety, ProtectFromMagic)

        # debuffs
        data = np.empty(shape=(trials,), dtype=int)

        for mys_index in range(trials):
            mystic.reset_stats()

            for _ in range(options["dwh_attempts_per_mystic"]):
                p = dwh_specialist.damage_distribution(mystic, special_attack=True).probability_nonzero_damage
                if random() < p:
                    mystic.apply_dwh()

            data[mys_index] = mystic.levels.defence

        mean_defence_level = math.floor(data.mean())
        mystic.levels.defence = Level(mean_defence_level, "mean lvl")

        thrall_dpt = 0.5
        dpt = lad.damage_distribution(mystic).per_tick + thrall_dpt
        assert isinstance(mystic.base_levels.hitpoints, Level)
        kill_ticks = mystic.base_levels.hitpoints / dpt
        damage_ticks = kill_ticks * mystic.count_per_room(options["scale_at_load_time"])
        tank_ticks = 200
        jank_ticks = 6 * options["dwh_attempts_per_mystic"]
        total_ticks = damage_ticks + tank_ticks + jank_ticks

    elif mode is MysticModes.tbow_thralls_simulated_spec_transfer:
        lad = Player(name="mystics fit")
        dwh_specialist = Player(name="dwh specialist")
        trials = options["trials"]
        scale_at_load_time = options["scale_at_load_time"]
        spec_transfer_alts = options["spec_transfer_alts"]
        dwh_target = options["dwh_target_per_mystic"]
        hp_threshold = options["dwh_health_remaining_ratio_threshold"]

        # gear
        lad.active_style = lad.equipment.equip_twisted_bow()
        lad.equipment.equip_arma_set(zaryte=True)
        lad.equipment.equip_basic_ranged_gear(anguish=False)
        lad.equipment.equip_salve()
        assert lad.equipment.full_set

        if options["dwh_specialist_equipment"] is None:
            dwh_specialist.equipment.equip_basic_melee_gear(torture=False, infernal=False, berserker=False)
            dwh_specialist.active_style = dwh_specialist.equipment.equip_dwh(
                inquisitor_set=True, avernic=True, tyrannical=True
            )
            dwh_specialist.equipment.equip_salve()
            dwh_specialist.equipment.equip(mythical_cape)
            assert dwh_specialist.equipment.full_set

        # prayers
        lad.pray(Rigour, ProtectFromMagic)
        dwh_specialist.pray(Piety, ProtectFromMagic)

        # data setup
        trials = np.arange(trials)
        data = np.empty(shape=trials.shape, dtype=int)

        ticks_per_lad_attack = lad.attack_speed()
        ticks_per_dwh_specialist_action = int(dwh_specialist.attack_speed() + 2)
        thrall_dam = Damage.thrall()

        for trial_index in trials:
            trial_ticks = 0

            mystics = [mystic.from_de0(ps) for ps in [scale_at_load_time] * mystics_per_room]
            st_alts = [Player(name=f"spec transfer alt {num}") for num in range(spec_transfer_alts)]
            tracked_spec_lads = [dwh_specialist, *st_alts]

            # boosts
            lad.reset_stats()
            dwh_specialist.reset_stats()

            lad.boost(Overload)
            dwh_specialist.levels.strength = options["dwh_specialist_target_strength_level"]
            dwh_specialist.boost(SuperAttackPotion)

            for mys_idx, mys in enumerate(mystics):
                tc = 0
                remaining_ticks = 0
                dwh_landed = 0

                cached_dam = lad.damage_distribution(mys)

                while mys.alive:
                    if dwh_landed == dwh_target:
                        remaining_ticks = mys.levels.hitpoints // (cached_dam.per_tick + thrall_dam.per_tick)
                        mys.levels.hitpoints = Level(0)

                    else:
                        if tc % ticks_per_lad_attack == 0:
                            mys.damage(lad, cached_dam.random_hit())

                        if tc % int(thrall_dam.attack_speed) == 0:
                            mys.damage(None, thrall_dam.random_hit())

                        if (
                            dwh_landed < dwh_target
                            and (hp_ratio := mys.levels.hitpoints / mys.base_levels.hitpoints) > hp_threshold
                        ):
                            if dwh_specialist.special_energy >= 50:
                                if tc % ticks_per_dwh_specialist_action == 0:
                                    p = dwh_specialist.damage_distribution(
                                        mys, special_attack=True
                                    ).probability_nonzero_damage
                                    dwh_specialist.special_energy -= 50  # TODO: Part of SpecialWeapon class

                                    if random() < p:
                                        dwh_landed += 1
                                        mys.apply_dwh()
                                        cached_dam = lad.damage_distribution(mys)

                            else:
                                for sta in st_alts:
                                    if sta.special_energy_full:
                                        try:
                                            sta.cast_energy_transfer(dwh_specialist)
                                        except PlayerError:
                                            sta.levels.hitpoints = (
                                                sta.base_levels.hitpoints
                                            )  # hp cape + regen bracelet = ez
                                            sta.cast_energy_transfer(dwh_specialist)

                        tc += 1
                        for spec_lad in tracked_spec_lads:
                            spec_lad.update_special_energy_counter()

                trial_ticks += tc + remaining_ticks

            data[trial_index] = trial_ticks

        mean_kill_ticks = data.mean()
        tank_ticks = 200
        total_ticks = mean_kill_ticks + tank_ticks

    elif mode is MysticModes.chin_six_by_two:
        pass
    elif mode is MysticModes.chin_ten:
        pass
    else:
        raise NotImplementedError

    return total_ticks, mystic.points_per_room(**options)


def shamans_estimates(
    scale: int,
    boost: Boost,
    vulnerability: bool = False,
    bone_crossbow_specs: int = 0,
    **kwargs,
) -> tuple[float, int]:
    """
    Simple shaman room estimate method for chinning big stacks of large lads.

    There's only one real way to do shamans, same as guardians, so easy method.
    """
    options = {}
    options.update(kwargs)

    shaman = LizardmanShaman.from_de0(scale)
    lad = Player(name="shamans fit")

    # gear
    lad.equipment.equip_basic_ranged_gear()
    lad.equipment.equip_arma_set(zaryte=True)
    lad.equipment.equip_slayer_helm()
    lad.task = True
    lad.active_style = lad.equipment.equip_black_chins()

    # boosts
    lad.pray(Rigour)
    lad.boost(boost)

    # def reduction
    if vulnerability:
        shaman.apply_vulnerability()

    dpt = lad.damage_distribution(shaman).per_tick
    damage_ticks = shaman.base_levels.hitpoints / dpt
    setup_ticks = 200 + bone_crossbow_specs * 10
    jank_ticks = 50  # cleanup n such
    total_ticks = damage_ticks + setup_ticks + jank_ticks
    return total_ticks, shaman.points_per_room()


class VespulaModes(Enum):
    TBOW = auto()
    ZCB = auto()


def vespula_estimates(
    scale: int, mode: VespulaModes, boost: Boost, vulnerability: bool = False, **kwargs
) -> tuple[float, int]:

    options = {}
    options.update(kwargs)

    lad = Player()
    lad.pray(Rigour)
    lad.boost(boost)

    portal = AbyssalPortal.from_de0(scale)
    assert isinstance(portal.base_levels.hitpoints, Level)
    assert isinstance(lad.equipment, Equipment)

    lad.equipment.equip_basic_ranged_gear()
    lad.equipment.equip_arma_set(zaryte=True)

    if mode is VespulaModes.TBOW:
        lad.active_style = lad.equipment.equip_twisted_bow()
    elif mode is VespulaModes.ZCB:
        lad.active_style = lad.equipment.equip_zaryte_crossbow(buckler=True, rubies=True)

    if vulnerability:
        portal.apply_vulnerability()

    dpt = lad.damage_distribution(portal).per_tick + Damage.thrall().per_tick

    damage_ticks = portal.base_levels.hitpoints / dpt
    setup_ticks = 50
    total_ticks = damage_ticks + setup_ticks
    return total_ticks, portal.points_per_room()


def muttadile_estimates(**kwargs):
    pass


class RopeModes(Enum):
    TBOW_THRALLS = auto()
    CHIN_BOTH = auto()


def rope_estimates(
    mode: RopeModes,
    scale: int,
    vulnerability: bool = False,
    bone_crossbow_specs: int = 0,
    **kwargs,
) -> tuple[float, int]:
    options = {}
    options.update(kwargs)

    # characters
    monster_classes = (DeathlyMage, DeathlyRanger)
    mage = DeathlyMage.from_de0(scale)
    ranger = DeathlyRanger.from_de0(scale)
    monsters = (mage, ranger) = tuple(mon.from_de0(scale) for mon in monster_classes)

    lad = Player(name="rope fit")
    lad.equipment.equip_basic_ranged_gear()
    lad.equipment.equip_arma_set(zaryte=True)

    # boosts / debuffs
    lad.pray(Rigour)
    lad.boost(Overload)

    if vulnerability:
        for mon in monsters:
            mon.apply_vulnerability()

    # combat
    if mode is RopeModes.TBOW_THRALLS:
        thrall_dpt = Damage.thrall().per_tick
        lad.active_style = lad.equipment.equip_twisted_bow()
        assert lad.equipment.full_set

        mage_dpt = lad.damage_distribution(mage).per_tick + thrall_dpt
        ranger_dpt = lad.damage_distribution(ranger).per_tick + thrall_dpt

        mage_damage_ticks = mage.count_per_room() * mage.base_levels.hitpoints / mage_dpt
        ranger_damage_ticks = ranger.count_per_room() * ranger.base_levels.hitpoints / ranger_dpt
        setup_ticks = 6 + 0 * vulnerability  # 10*bone_crossbow_specs    # lure ticks + nonsense
        total_ticks = mage_damage_ticks + ranger_damage_ticks + setup_ticks

    elif mode is RopeModes.CHIN_BOTH:
        lad.active_style = lad.equipment.equip_black_chins(style=ChinchompaStyles.get_by_style(Styles.LONG_FUSE))
        dpt_mage = lad.damage_distribution(mage).per_tick
        dpt_ranger = lad.damage_distribution(ranger).per_tick

        damage_ticks = mage.base_levels.hitpoints / dpt_mage + ranger.base_levels.hitpoints / dpt_ranger
        setup_ticks = 15 * vulnerability
        total_ticks = damage_ticks + setup_ticks
    else:
        raise NotImplementedError

    total_points = mage.points_per_room() + ranger.points_per_room()

    return total_ticks, total_points


def thieving_estimates(scale: int, **kwargs) -> tuple[float, int]:
    options = {
        "ticks_per_grub": 5,
        "party_average_thieving_level_at_load": 50
        # TODO: Implement scales with accounts with skills to make this bit automatic
    }
    options.update(kwargs)

    def flat_grub_estimate(inner_scale: int) -> int:
        return 16 * inner_scale - 1

    def jank_grub_estimate(modifier: float = None):
        modifier = 268 / flat_grub_estimate(28) if modifier is None else modifier  # my one data point
        return math.floor(flat_grub_estimate(scale) * modifier)

    grub_estimate = jank_grub_estimate()
    points_per_grub = 100
    ticks_per_grub = options["ticks_per_grub"]

    ticks_estimate = ticks_per_grub * grub_estimate
    points_estimate = points_per_grub * grub_estimate
    return ticks_estimate, points_estimate


class CombatRotations(Enum):
    GMS = (guardian_estimates, mystics_estimates, shamans_estimates)
    SMG = (shamans_estimates, mystics_estimates, guardian_estimates)
    MUTT_SHAM_MYST = auto()
    MYST_SHAM_MUTT = auto()
    GVS = (guardian_estimates, vespula_estimates, shamans_estimates)
    SVG = (shamans_estimates, vespula_estimates, guardian_estimates)
    MGV = (muttadile_estimates, guardian_estimates, vespula_estimates)
    VGM = (vespula_estimates, guardian_estimates, muttadile_estimates)


class PuzzleRotations(Enum):
    THROPE: auto()
    RICE: auto()
    CROPE: auto()


def main(
    rotation: CombatRotations,
    scale: int,
    cap_overload: bool = True,
    cap_food: bool = True,
    **kwargs,
) -> tuple[float, int, float]:
    options = {
        "trials": int(1e0),
        "setup_ticks_meta": 15 * 100,  # 30 minutes to wrangle a reasonable scale + scalers + gear the lads
        "spec_transfer_alts": 0,
        "guardian_alts": 4,
        "bone_crossbow_specs": 0,
        "dwh_specialist_strength_level": 13,
        "dwh_target_per_mystic": 3,
        "dwh_health_remaining_ratio_threshold": 0.50,
        "points_per_overload_dose": 600,
        "points_per_food": 90,
    }
    options.update(kwargs)

    if rotation is CombatRotations.GMS or rotation is CombatRotations.GVS:
        guardian_boost = SuperCombatPotion
        shamans_boost = Overload
    elif rotation is CombatRotations.SMG or rotation is CombatRotations.SVG:
        guardian_boost = Overload
        shamans_boost = BastionPotion
    else:
        raise NotImplementedError

    guardians_ticks, guardian_points = guardian_estimates(
        scale=scale,
        boost=guardian_boost,
        **options,
    )
    mystics_ticks, mystics_points = mystics_estimates(
        scale=scale,
        mode=MysticModes.tbow_thralls_simulated_spec_transfer,
        **options,
    )
    shamans_ticks, shamans_points = shamans_estimates(
        scale=scale,
        boost=shamans_boost,
        **options,
    )

    rope_ticks, rope_points = rope_estimates(
        mode=RopeModes.CHIN_BOTH,
        scale=scale,
        **options,
    )
    thieving_ticks, thieving_points = thieving_estimates(
        scale=scale,
        **options,
    )

    olm_ticks, olm_points = solo_olm_ticks_and_points_estimate(
        scale=scale,
        **options,
    )

    # 1 stam * (4 doses / 1 stam) * (4 minutes / 1 dose) * (100 ticks / 1 minute)
    minimum_stams_needed = math.ceil(olm_ticks / (1 * 4 * 4 * 100))

    # ticks ############################################################################################################
    tick_data = [
        guardians_ticks,
        mystics_ticks,
        shamans_ticks,
        rope_ticks,
        thieving_ticks,
        olm_ticks,
    ]
    tick_data.insert(0, sum(tick_data[:]) + options["setup_ticks_meta"])
    tick_data.append(minimum_stams_needed)

    data_minutes = [d / 100 for d in tick_data[:-1]]
    data_hours = [d / 6000 for d in tick_data[:-1]]
    col_labels = [
        "time unit",
        "total",
        "guardians",
        "mystics",
        "shamans",
        "rope",
        "thieving",
        "olm",
        "minimum stamina pots",
    ]
    row_labels = ["ticks", "minutes", "hours"]

    list_of_data = [tick_data, data_minutes, data_hours]
    header_title = f"scale:{scale:3.0f}"

    time_table = tabulate_enhanced(
        list_of_data,
        col_labels=col_labels,
        row_labels=row_labels,
        meta_header=header_title,
        floatfmt=".1f",
    )

    # points ###########################################################################################################

    pt_data = [
        guardian_points,
        mystics_points,
        shamans_points,
        rope_points,
        thieving_points,
        olm_points,
    ]
    col_labels = [""] + col_labels[1:-1]

    if cap_overload:
        overload_points = options["points_per_overload_dose"] * 5 * (scale - 1)
        pt_data.append(overload_points)
        col_labels.append("overload")

    if cap_food:
        food_points = options["points_per_food"] * 20 * (scale - 1)
        pt_data.append(food_points)
        col_labels.append("food")

    pt_data.insert(0, sum(pt_data) - individual_point_cap)  # loss from leaving

    row_labels = ["points"]
    list_of_data = [pt_data]
    points_table = tabulate_enhanced(list_of_data, col_labels, row_labels, floatfmt=".0f")

    # points per hour ##################################################################################################
    adjusted_total_points = pt_data[0]
    total_hours = data_hours[0]
    points_per_hour = adjusted_total_points / total_hours

    print(
        "\n".join(
            [
                "\n",
                time_table,
                "\n",
                points_table,
                "\n",
                f"points per hr: {points_per_hour:.0f}",
            ]
        )
    )
    return points_per_hour, adjusted_total_points, total_hours


if __name__ == "__main__":
    # my_scale = 27
    # my_spec_transfer_alts = 6
    # dwh_target_range = np.arange(0, 5+1)
    # my_trials = int(1e0)
    # mythical_cape = Gear.from_bb('mythical cape')
    # mystic_sim_data = np.empty(shape=dwh_target_range.shape, dtype=float)

    # for alts_index, dwh_target in enumerate(dwh_target_range):
    # 	my_kwargs = {
    # 		'trials': my_trials,
    # 		'spec_transfer_alts': my_spec_transfer_alts,
    # 		'dwh_target_per_mystic': dwh_target,
    # 		'dwh_health_remaining_ratio_threshold': 0.50,
    # 	}

    # 	room_ticks, _ = mystics_estimates(my_scale, mode=MysticModes.tbow_thralls_simulated_spec_transfer, **my_kwargs)
    # 	mystic_sim_data[alts_index] = room_ticks

    # plt.plot(dwh_target_range, mystic_sim_data)
    # plt.show()

    # sys.exit(0)

    my_rot = CombatRotations.GMS
    my_scales = list(range(14, 18, 1))
    outer_cap_ovl = True
    outer_cap_food = False

    my_kwargs = {
        "trials": int(1),
        "setup_ticks_meta": 15 * 100,  # 30 minutes to wrangle a reasonable scale + scalers + gear the lads
        "spec_transfer_alts": 6,
        "guardian_alts": 4,
        "dwh_target_per_mystic": 2,
    }

    mythical_cape = Gear.from_bb("mythical cape")

    scales_ary = np.asarray(my_scales)
    pph_data = np.empty(shape=scales_ary.shape, dtype=float)
    uph_data = np.empty(shape=scales_ary.shape, dtype=float)

    for index, my_scale in enumerate(my_scales):
        pph, total_pts, total_hrs = main(
            rotation=my_rot,
            scale=my_scale,
            cap_overload=outer_cap_ovl,
            cap_food=outer_cap_food,
            **my_kwargs,
        )
        pph_data[index] = pph
        any_unique_chance = 1 - zero_purple_chance(total_pts)
        uph_data[index] = any_unique_chance / total_hrs

    # graph
    fig, ax1 = plt.subplots()

    ax1.set_xlabel("scale")
    ax1.set_ylabel("points per hr (pph)", color="red")
    ax1.plot(scales_ary, pph_data, color="red")
    ax1.tick_params(axis="y", labelcolor="red")

    ax2 = ax1.twinx()
    ax2.set_ylabel("uniques per hr (uph)", color="blue")
    ax2.plot(scales_ary, uph_data, color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")

    plot_title = "Points and Uniques per hour for scaled solo iron gimmick raids"
    plt.title(plot_title)
    fig.savefig(plot_title + ".png", format="png")
    plt.show()
