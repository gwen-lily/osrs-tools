"""Helper utilities for creating and defining modifiers

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-05-03                                                         #
###############################################################################
"""

from .tracked_values import DamageModifier, RollModifier

###############################################################################
# helper functions                                                            #
###############################################################################


def create_modifier_pair(
    value: float | None = None, comment: str | None = None
) -> tuple[RollModifier, DamageModifier]:
    """Create a RollModifier and DamageModifier with the same value/comment.

    Often (but not always) these two values are the same, this function
    simplifies the creation process.

    Parameters
    ----------
    value : float | None, optional
        The float value, by default None
    comment : str | None, optional
        A description of the modifier's source, by default None

    Returns
    -------
    tuple[RollModifier, DamageModifier]
    """
    value = 1.0 if value is None else value
    return RollModifier(value, comment), DamageModifier(value, comment)
