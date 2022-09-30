"""Defines Rotation and all relevant combat and puzzle rotations

###############################################################################
# email:    noahgill409@gmail.com                                             #
###############################################################################
"""

from dataclasses import dataclass
from typing import Type

from .combat_rooms import (
    GuardiansEstimate,
    MuttadileEstimate,
    MysticsEstimate,
    ShamansEstimate,
    VanguardsEstimate,
    VespulaEstimate,
)
from .puzzle_rooms import (
    CrabsEstimate,
    IceDemonEstimate,
    RopeEstimate,
    ThievingEstimate,
)


@dataclass
class Rotation:
    name: str
    combat_rooms: list[type]
    puzzle_rooms: list[type]
    olm: type


###############################################################################
# combat rotations                                                            #
###############################################################################

CombatRotation = list[Type]

# 3c2p: 3 combat 2 puzzle
GMSRotation = [GuardiansEstimate, MysticsEstimate, ShamansEstimate]
MSMRotation = [MysticsEstimate, ShamansEstimate, MuttadileEstimate]
GVSRotation = [GuardiansEstimate, VespulaEstimate, ShamansEstimate]

# 4c2p or 4c1p
GMSMRotation = GMSRotation[:] + [MuttadileEstimate]

# 5c3p
GMSMVRotation = GMSMRotation[:] + [VanguardsEstimate]

###############################################################################
# puzzle rotations                                                            #
###############################################################################

PuzzleRotation = list[Type]

# 3c2p or 4c2p

# optimal
CropeRotation = [RopeEstimate, CrabsEstimate]
ThropeRotation = [RopeEstimate, ThievingEstimate]
RiceRotation = [RopeEstimate, IceDemonEstimate]

# sub-optimal
ThrabsRotation = [ThievingEstimate, CrabsEstimate]
ThiceRotation = [ThievingEstimate, IceDemonEstimate]
CriceRotation = [CrabsEstimate, IceDemonEstimate]

# 5c3p
DoubleRopeIceRotation = [RopeEstimate, IceDemonEstimate, RopeEstimate]
