"""Monster modifiers

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-07                                                        #
###############################################################################
"""

from dataclasses import dataclass
import math

from osrs_tools import gear
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.data import DT, MagicDamageTypes, Slots
from osrs_tools.tracked_value import Roll

from .character import CharacterModifiers


@dataclass
class MonsterModifiers(CharacterModifiers):
    monster: Monster
    player: Player
    dt: DT

    # properties

    def defence_roll(self) -> Roll:
        _roll = self.monster.defence_roll(self.player, self.dt)

        if self.dt in MagicDamageTypes:
            if self.player.eqp[Slots.RING] == gear.BrimstoneRing:
                reduction = _roll // 10 / 4
                _roll = Roll(math.floor(_roll.value - reduction))

        return _roll
