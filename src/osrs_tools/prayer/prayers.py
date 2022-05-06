"""Definition of all useful prayers (almost)

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""
from .prayer import Prayer

Augury = Prayer.from_osrsbox(
    prayer_id=29, defence=25, magic_defence=25, drain_effect=24
)
Rigour = Prayer.from_osrsbox(prayer_id=28, drain_effect=24)
Piety = Prayer.from_osrsbox(prayer_id=27, drain_effect=24)
Chivalry = Prayer.from_osrsbox(prayer_id=26, drain_effect=24)
Preserve = Prayer.from_osrsbox(prayer_id=25, drain_effect=2)
Smite = Prayer.from_osrsbox(prayer_id=24, drain_effect=18)
Redemption = Prayer.from_osrsbox(prayer_id=23, drain_effect=6)
Retribution = Prayer.from_osrsbox(prayer_id=22, drain_effect=3)
MysticMight = Prayer.from_osrsbox(prayer_id=21, drain_effect=12)
EagleEye = Prayer.from_osrsbox(prayer_id=20, drain_effect=12)
ProtectFromMelee = Prayer.from_osrsbox(prayer_id=19, drain_effect=12)
ProtectFromMissiles = Prayer.from_osrsbox(prayer_id=18, drain_effect=12)
ProtectFromMagic = Prayer.from_osrsbox(prayer_id=17, drain_effect=12)
IncredibleReflexes = Prayer.from_osrsbox(prayer_id=16, drain_effect=12)
MysticLore = Prayer.from_osrsbox(prayer_id=13, drain_effect=6)
