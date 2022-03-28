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
        lad.active_style = lad.equipment.equip_zaryte_crossbow(
            buckler=True, rubies=True
        )

    if vulnerability:
        portal.apply_vulnerability()

    dpt = lad.damage_distribution(portal).per_tick + Damage.thrall().per_tick

    damage_ticks = portal.base_levels.hitpoints / dpt
    setup_ticks = 50
    total_ticks = damage_ticks + setup_ticks
    return total_ticks, portal.points_per_room()
