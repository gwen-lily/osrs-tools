from osrs_tools import analysis_tools
from osrs_tools.analysis_tools import DataMode, bedevere_2d, bedevere_the_wise
from osrs_tools.character import AbyssalPortal, BigMuttadile, Player
from osrs_tools.equipment import Gear
from osrs_tools.modifier import DT
from osrs_tools.prayer import (
    Augury,
    Prayer,
    ProtectFromMelee,
    ProtectFromMissiles,
    Rigour,
)
from osrs_tools.stats import Overload
from osrs_tools.style import BladedStaffStyles, Style


def mutta_tank_mean_hit(**kwargs):
    # baby = SmallMuttadile.from_de0(31)
    momma = BigMuttadile.from_de0(31)

    dinhs_tank = Player(name="dinhs lad")
    ely_tank = Player(name="ely lad")

    lads = [dinhs_tank, ely_tank]

    for lad in lads:
        lad.boost(Overload)
        lad.equipment.equip_justi_set()
        lad.equipment.equip(
            fury,
            hp_cape,
            bgloves,
            gboots,
            suffering,
        )

    dinhs_tank.active_style = dinhs_tank.equipment.equip_dinhs()
    dinhs_tank.prayers_coll.pray(Augury, ProtectFromMelee)

    ely_tank.active_style = ely_tank.equipment.equip_sotd(
        style=BladedStaffStyles.default
    )
    ely_tank.equipment.equip(Gear.from_bb("elysian spirit shield"))
    ely_tank.prayers_coll.pray(Augury, ProtectFromMissiles)
    ely_tank.staff_of_the_dead_effect = True

    # baby_dinh = baby.damage_distribution(dinhs_tank)

    momma.active_style = momma.styles_coll.get_by_dt(DT.crush)
    momma_dinh_melee = momma.damage_distribution(dinhs_tank)

    momma.active_style = momma.styles_coll.get_by_dt(DT.ranged)
    momma_dinh_ranged = momma.damage_distribution(dinhs_tank)
    momma_ely_ranged = momma.damage_distribution(ely_tank)

    # baby_ely = baby.damage_distribution(ely_tank)
    # momma_ely = momma.damage_distribution(ely_tank)

    print(
        *(
            dam.max_hit
            for dam in (momma_dinh_melee, momma_dinh_ranged, momma_ely_ranged)
        )
    )


def momma_kill_ticks(**kwargs):
    momma = BigMuttadile.from_de0(31)
    lad = Player(name="lad")
    lad.equipment.equip_basic_ranged_gear()
    lad.equipment.equip_arma_set(zaryte=True)
    lad.active_style = lad.equipment.equip_twisted_bow()
    lad.boost(Overload)
    lad.prayers_coll.pray(Rigour)

    dam = lad.damage_distribution(momma)
    print(
        f"{dam.per_tick=}, {momma.base_levels.hitpoints=}, {momma.base_levels.hitpoints / dam.per_tick}"
    )


def portal_kill_time(**kwargs):
    options = {
        "floatfmt": ".0f",
        "datamode": DataMode.MINUTES_TO_KILL,
        "scales": range(15, 40, 4),
    }
    options.update(kwargs)

    lad = Player()
    lad.equipment.equip_basic_ranged_gear()
    lad.equipment.equip_arma_set(zaryte=True)
    lad.active_style = lad.equipment.equip_twisted_bow()

    portals = [AbyssalPortal.from_de0(ps) for ps in options["scales"]]

    for portal in portals:
        portal.apply_vulnerability()

    _, table = bedevere_2d(
        lad,
        portals,
        boosts=Overload,
        prayers=Rigour,
        data_mode=options["datamode"],
        float_fmt=options["floatfmt"],
    )
    print(table)

    print([ap.points_per_room() for ap in portals])


if __name__ == "__main__":
    fury = Gear.from_osrsbox("amulet of fury")
    hp_cape = Gear.from_bb("skill cape (t)")
    bgloves = Gear.from_osrsbox("barrows gloves")
    gboots = Gear.from_osrsbox("guardian boots")
    suffering = Gear.from_osrsbox("ring of suffering (i)")

    portal_kill_time()
    # mutta_tank_mean_hit()
    # momma_kill_ticks()
