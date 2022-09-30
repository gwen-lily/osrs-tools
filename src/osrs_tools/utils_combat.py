import math

from osrs_tools.tracked_value import (
    DamageModifier,
    DamageValue,
    EquipmentStat,
    Level,
    LevelModifier,
    Roll,
    RollModifier,
    StyleBonus,
    TrackedInt,
)


def maximum_roll(
    level: Level, bonus: int | EquipmentStat, *roll_modifiers: RollModifier
) -> Roll:
    """The roll made by a character to determine accuracy.

    Parameters
    ----------
    level : Level
        The effective level.
    bonus : int
        The aggressive or defensive bonus conferred from equipment for
        players and innately from monsters.

    Returns
    -------
    Roll
    """
    roll = Roll(int(level * (int(bonus) + 64)))

    for roll_mod in roll_modifiers:
        roll *= roll_mod

    return roll


def accuracy(offensive_roll: Roll, defensive_roll: Roll) -> float:
    """The probability of a "successful" attack.

    This is not to be confused with the chance to deal positive damage.
    There are subtleties between the two for special weapons.

    Parameters
    ----------
    offensive_roll : Roll
        The roll made by the attacker.
    defensive_roll : Roll
        The roll made by the defender.

    Returns
    -------
    float
        The probability of a "successful" attack.
    """
    off_val = int(offensive_roll)
    def_val = int(defensive_roll)
    if off_val > def_val:
        return 1 - (def_val + 2) / (2 * (off_val + 1))
    else:
        return off_val / (2 * (def_val + 1))


def base_damage(
    effective_strength_level: Level, strength_bonus: int | EquipmentStat
) -> float:
    """Bitterkoekje damage formula.

    source:
        https://docs.google.com/document/d/1hk7FxOAOFT4oxguC8411QQhE4kk-_GzqWcwkaPmaYns/edit

    Parameters
    ----------
    effective_strength_level : Level
        The attacker's effective strength level, dependent upon attack style.
    strength_bonus : int | EquipmentStat
        The strength bonus.

    Returns
    -------
    float
        An un-floored value representing the max hit before modifiers.
    """
    esl_val = int(effective_strength_level)
    _base_damage = 0.5 + esl_val * (int(strength_bonus) + 64) / 640

    return _base_damage


def max_hit(
    base_damage: DamageValue | int | float, *damage_modifiers: DamageModifier
) -> DamageValue:
    """Multiply a base damage calculation by damage modifiers, flooring between.

    Parameters
    ----------
    base_damage : DamageValue | int | float
        The base damage, before modifiers.

    Returns
    -------
    DamageValue

    Raises
    ------
    TypeError
    """
    if isinstance(base_damage, DamageValue):
        max_hit = base_damage
    elif isinstance(base_damage, (int, float)):
        max_hit = DamageValue(math.floor(base_damage))
    else:
        raise TypeError(base_damage)

    for dmg_mod in damage_modifiers:
        max_hit *= dmg_mod

    return max_hit


def effective_level(
    invisible_level: Level,
    style_bonus: StyleBonus | None,
    void_modifier: LevelModifier | None = None,
) -> Level:
    effective_level = invisible_level + TrackedInt(8, "invisible 8")

    if style_bonus is not None:
        effective_level += style_bonus

    if void_modifier is not None:
        effective_level *= void_modifier

    return effective_level
