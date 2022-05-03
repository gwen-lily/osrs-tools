"""Definition of DamageCalculation.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-30                                                         #
###############################################################################
"""

from abc import ABC, abstractmethod

from osrs_tools.character.character import Character
from osrs_tools.damage import Damage


class DamageCalculation(ABC):
    attacker: Character
    defender: Character
    thralls: bool = False

    @abstractmethod
    def get_damage() -> Damage:
        ...
