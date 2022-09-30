from abc import ABC
from dataclasses import dataclass, field

from osrs_tools.data import MonsterLocations
from osrs_tools.stats.combat_stats import MonsterLevels

from ..monster import Monster


@dataclass
class ToaMonster(Monster, ABC):

    _levels: MonsterLevels = field(repr=False)
    location: MonsterLocations = MonsterLocations.TOA
    party_size: int = field(default=1)

    # dunder and helper methods
