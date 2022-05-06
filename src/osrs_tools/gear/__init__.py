"""The gear submodule defines Gear, Weapon, SpecialWeapon, and Equipment.

Much like Player, this used to be one bloated file (with Equipment being the
worst offender). Now, it looks like this.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-05-02                                                        #
###############################################################################
"""

from .common_gear import *
from .equipment import Equipment
from .gear import Gear
from .special_weapon import SpecialWeapon, SpecialWeaponError
from .weapon import Weapon
