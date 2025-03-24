"""Definition of some type aliases

###############################################################################
# email:    orchid.lilith@proton.me                                           #
# created:  2022                                                              #
###############################################################################
"""

from osrs_tools.tracked_value import EquipmentStat, TrackedFloat

StatBonusPair = tuple[EquipmentStat, EquipmentStat | TrackedFloat]
NormalStatBonusPair = tuple[EquipmentStat, EquipmentStat]
MagicStatBonusPair = tuple[EquipmentStat, TrackedFloat]
