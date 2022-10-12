from osrs_tools.data import Slots
from osrs_tools.gear import Gear
from osrs_tools.stats.additional_stats import AggressiveStats, DefensiveStats
from osrs_tools.tracked_value.tracked_values import EquipmentStat

from .common_gear import InquisitorsGreatHelm, InquisitorsHauberk, InquisitorsPlateskirt

# setup

HELM, BODY, LEGS = InquisitorsGreatHelm, InquisitorsHauberk, InquisitorsPlateskirt

HELM_AGG = HELM.aggressive_bonus
BODY_AGG = BODY.aggressive_bonus
LEGS_AGG = LEGS.aggressive_bonus

# Sae Bae changes
# the set bonus and piece bonuses are applied elsewhere in code
#   1 piece:    1.5% max hit and accuracy
#   2 pieces:   3.0% max hit and accuracy
#   3 pieces:   5.0% max hit and accuracy

assert HELM_AGG.melee_strength.value == 4
assert BODY_AGG.crush.value == 12

HELM_AGG.melee_strength = EquipmentStat(6)  # previously 4
BODY_AGG.crush = EquipmentStat(16)  # previously 12

# 1.5, 3%, then 5%

SaeBaeInqHelm = Gear(
    name="Inquisitor's Great Helm",
    slot=Slots.HEAD,
    aggressive_bonus=HELM_AGG,
    defensive_bonus=HELM.defensive_bonus,
    prayer_bonus=HELM.prayer_bonus,
    level_requirements=HELM.level_requirements,
)

SaeBaeInqHauberk = Gear(
    name=BODY.name,
    slot=BODY.slot,
    aggressive_bonus=BODY_AGG,
    defensive_bonus=BODY.defensive_bonus,
    prayer_bonus=BODY.prayer_bonus,
    level_requirements=BODY.level_requirements,
)
