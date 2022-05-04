"""Utilities for reading bitterkoekje-bedevere gear csvs.

This code is a little old and jank, but it gets the job done.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-02                                                         #
###############################################################################
"""
from osrs_tools import utils as rr
from osrs_tools.data import DT, DamageModifier, Level, RollModifier, Slots
from osrs_tools.stats.stats import AggressiveStats, DefensiveStats, PlayerLevels
from osrs_tools.style.style import AllWeaponStylesCollections, WeaponStyles

###############################################################################
# utilities                                                                   #
###############################################################################


def lookup_gear_bb_by_name(
    __name: str,
) -> tuple[str, Slots, AggressiveStats, DefensiveStats, int, PlayerLevels]:
    """Return a tuple of attributes of a gear item.

    Parameters
    ----------
    __name : str
        The name of the gear

    Returns
    -------

    Raises
    ------
    GearError
    ValueError
    TypeError
    """
    item_df = rr.lookup_gear(__name)

    if len(item_df) > 1:
        matching_names = tuple(item_df["name"].values)
        raise ValueError(matching_names)
    elif len(item_df) == 0:
        raise ValueError(__name)

    df_item = item_df["name"]
    name = df_item.values[0]
    assert isinstance(name, str)

    aggressive_bonus = AggressiveStats(
        stab=item_df["stab attack"].values[0],
        slash=item_df["slash attack"].values[0],
        crush=item_df["crush attack"].values[0],
        magic_attack=item_df["magic attack"].values[0],
        ranged_attack=item_df["ranged attack"].values[0],
        melee_strength=item_df["melee strength"].values[0],
        ranged_strength=item_df["ranged strength"].values[0],
        magic_strength=item_df["magic damage"].values[
            0
        ],  # stored as float in bitterkoekje's sheet
    )
    defensive_bonus = DefensiveStats(
        stab=item_df["stab defence"].values[0],
        slash=item_df["slash defence"].values[0],
        crush=item_df["crush defence"].values[0],
        magic=item_df["magic defence"].values[0],
        ranged=item_df["ranged defence"].values[0],
    )
    prayer_bonus = item_df["prayer"].values[0]
    level_requirements = PlayerLevels(
        _mining=Level(item_df["mining level req"].values[0])
    )

    slot_src = item_df["slot"].values[0]
    slot_enum = None

    for slot_e in Slots:
        if slot_e.value == slot_src:
            slot_enum = slot_e
            break

    if slot_enum is None:
        raise TypeError(slot_src)

    return (
        name,
        slot_enum,
        aggressive_bonus,
        defensive_bonus,
        prayer_bonus,
        level_requirements,
    )


def _get_weapon_styles(__wpn_type: str, /) -> WeaponStyles:
    """"""
    for _styles_col in AllWeaponStylesCollections:
        if _styles_col.name == __wpn_type:
            return _styles_col

    raise ValueError(__wpn_type)


def lookup_weapon_attrib_bb_by_name(name: str):
    item_df = rr.lookup_gear(name)
    default_attack_range = 0
    comment = "bitter"

    if len(item_df) > 1:
        matching_names = tuple(item_df["name"].values)
        raise ValueError(matching_names)
    elif len(item_df) == 0:
        raise ValueError(name)

    attack_speed = item_df["attack speed"].values[0]
    attack_range = default_attack_range
    two_handed = item_df["two handed"].values[0]

    weapon_type = item_df["weapon type"].values[0]
    weapon_styles = _get_weapon_styles(weapon_type)

    special_accuracy_modifiers = []
    special_damage_modifiers = []
    sdr_enum = None

    if (raw_sarm := item_df["special accuracy"].values[0]) != 0:
        assert raw_sarm is not None
        special_accuracy_modifiers.append(RollModifier(1 + raw_sarm, comment))

    if (raw_sdm1 := item_df["special damage 1"].values[0]) != 0:
        assert raw_sdm1 is not None
        special_damage_modifiers.append(DamageModifier(1 + raw_sdm1, comment))

    if (raw_sdm2 := item_df["special damage 2"].values[0]) != 0:
        assert raw_sdm2 is not None
        special_damage_modifiers.append(DamageModifier(1 + raw_sdm2, comment))

    if (raw_sdr := item_df["special defence roll"].values[0]) != "":
        for dt in DT:
            if dt.name == raw_sdr:
                sdr_enum = dt
                break

    return (
        attack_speed,
        attack_range,
        two_handed,
        weapon_styles,
        special_accuracy_modifiers,
        special_damage_modifiers,
        sdr_enum,
    )
