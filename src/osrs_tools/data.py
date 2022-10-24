"""Basic data ubiquitious to the program and OSRS.

All time values are in ticks unless otherwise noted.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:                                                                    #
###############################################################################
"""

from __future__ import annotations

from collections import namedtuple
from enum import Enum, auto, unique
from pathlib import Path

from osrsbox import items_api, monsters_api, prayers_api

###############################################################################
# project structure and resources                                             #
###############################################################################

_RESOURCES_DIRNAME = "resources"
_MONSTERS_DE0_FNAME = "cox_base_stats.csv"
_ITEMS_BB_FNAME = "bitterkoekje_items_bedevere_modified.csv"
_MONSTERS_BITTER_FNAME = "bitterkoekje_npcs.csv"

PROJECT_DIR = Path(__file__).absolute().parents[2]

RESOURCES_DIR = PROJECT_DIR.joinpath(_RESOURCES_DIRNAME)
MONSTERS_DE0 = RESOURCES_DIR.joinpath(_MONSTERS_DE0_FNAME)
ITEMS_BITTER_BED = RESOURCES_DIR.joinpath(_ITEMS_BB_FNAME)
MONSTERS_BITTER = RESOURCES_DIR.joinpath(_MONSTERS_BITTER_FNAME)

###############################################################################
# enums 'n' such                                                              #
###############################################################################

# osrsbox-db load
ITEMS = items_api.load()
PRAYERS = prayers_api.load()
MONSTERS = monsters_api.load()

# misc ########################################################################

DEFAULT_FLOAT_FMT = ".1f"
DEFAULT_TABLE_FMT = "fancy"

DWH_MODIFIER = 0.70
DWH_MODIFIER_TEKTON_MISS = 0.95

ARCLIGHT_FLAT_REDUCTION = 0.05
ARCLIGHT_FLAT_REDUCTION_DEMON = 0.10

BGS_FLAT_REDUCTION_TEKTON_MISS = 10

VULNERABILITY_MODIFIER = 0.90
VULNERABILITY_MODIFIER_TOME_OF_WATER = 0.85

PLAYER_MAX_COMBAT_LEVEL = 126
PLAYER_MAX_SKILL_LEVEL = 99

# made these up
PARTY_AVERAGE_MINING_LEVEL = 42
PARTY_AVERAGE_THIEVING_LEVEL = 42
COX_POINTS_PER_HITPOINT = 4.15

# toa values
TOA_RAID_LVL_MOD = 0.02  # per 5 raid levels
TOA_PATH_MOD_1 = 0.05
TOA_PATH_MOD_0 = 0.08
TOA_TEAM_MOD_LOW = 0.9
TOA_TEAM_MOD_HIGH = 0.6
TOA_MAX_RAID_LEVEL = 600
TOA_MAX_PARTY_SIZE = 8


# armour bonuses

CRYSTAL_PIECE_ARM = 0.06
CRYSTAL_PIECE_DM = 0.03
CRYSTAL_SET_ARM = 0.12
CRYSTAL_SET_DM = 0.06

INQUISITOR_PIECE_BONUS = 0.005
INQUISITOR_SET_BONUS = 0.01

ABYSSAL_BLUDGEON_DMG_MOD = 0.005

PVM_MAX_TARGETS = 11
PVP_MAX_TARGETS = 9

MUTTA_HP_RATIO_HEALED_PER_EAT = 0.60
MUTTA_EATS_PER_ROOM = 3

# made this up completely, #not true
TEKTON_HP_HEALED_PER_ANVIL_RATIO = 0.10

# olm #########################################################################

OLM_HEAD_MAX_HP = 13600
OLM_HAND_MAX_HP = 10200
DUMMY_NAME = "dummy"


CSV_SEP = "\t"

# time ########################################################################

SECONDS_PER_TICK = 0.6
TICKS_PER_SECOND = 1 / SECONDS_PER_TICK
TICKS_PER_MINUTE = 100
TICKS_PER_HOUR = 6000

HOURS_PER_SESSION = 6
TICKS_PER_SESSION = TICKS_PER_HOUR * HOURS_PER_SESSION

DEFAULT_EFFECT_INTERVAL = 25
UPDATE_STATS_INTERVAL = TICKS_PER_MINUTE
UPDATE_STATS_INTERVAL_PRESERVE = 150

OVERLOAD_DURATION = 500
DIVINE_DURATION = 500

# energy ######################################################################

RUN_ENERGY_MIN = 0
RUN_ENERGY_MAX = 10000

SPECIAL_ENERGY_MIN = 0
SPECIAL_ENERGY_MAX = 100
SPECIAL_ENERGY_INCREMENT = 10
SPECIAL_ENERGY_UPDATE_INTERVAL = 50
SPECIAL_ENERGY_DAMAGE = 10

# ammunition ##################################################################

BOLT_PROC = "bolt proc"

DIAMOND_BOLTS_PROC = 0.10
DIAMOND_BOLTS_DMG = 1.15

RUBY_BOLTS_PROC = 0.06
RUBY_BOLTS_HP_CAP = 500
RUBY_BOLTS_HP_RATIO = 0.20

# damage types ################################################################


@unique
class DT(Enum):
    """Damage Type (DT) enumerator.
    Args:
        Enum (DT): Enumerator object.
    """

    # melee style class vars
    STAB = "stab"
    SLASH = "slash"
    CRUSH = "crush"

    # ranged style class vars
    RANGED = "ranged"

    # magic style class vars
    MAGIC = "magic"

    # typeless class vars
    TYPELESS = "typeless"


# I treat these uniformly as tuples, do as you see fit.
# I know not whether there are different classes of some of these
# Hey reader, check out the band Godspeed You! Black Emperor, they're gr!eat
MeleeDamageTypes = (DT.STAB, DT.SLASH, DT.CRUSH)
RangedDamageTypes = (DT.RANGED,)
MagicDamageTypes = (DT.MAGIC,)
TypelessDamageTypes = (DT.TYPELESS,)

# stance names ################################################################


@unique
class Stances(Enum):
    # type ambiguous class vars
    ACCURATE = "accurate"
    LONGRANGE = "longrange"
    DEFENSIVE = "defensive"
    NO_STYLE = "no style"
    # melee style class vars
    AGGRESSIVE = "aggressive"
    CONTROLLED = "controlled"
    # ranged style class vars
    RAPID = "rapid"
    # magic style class vars
    STANDARD = "standard"
    # npc stance
    NPC = "npc"


# style names #################################################################


@unique
class Styles(Enum):
    """The name of every style in OSRS (that matters)."""

    SLASH = "slash"
    STAB = "stab"
    ACCURATE = "accurate"
    RAPID = "rapid"
    LONGRANGE = "longrange"
    CHOP = "chop"
    SMASH = "smash"
    BLOCK = "block"
    HACK = "hack"
    LUNGE = "lunge"
    SWIPE = "swipe"
    POUND = "pound"
    PUMMEL = "pummel"
    SPIKE = "spike"
    IMPALE = "impale"
    JAB = "jab"
    FEND = "fend"
    BASH = "bash"
    REAP = "reap"
    PUNCH = "punch"
    KICK = "kick"
    FLICK = "flick"
    LASH = "lash"
    DEFLECT = "deflect"
    SHORT_FUSE = "short fuse"
    MEDIUM_FUSE = "medium fuse"
    LONG_FUSE = "long fuse"
    SPELL = "spell"
    FOCUS = "focus"
    STANDARD_SPELL = "standard spell"
    DEFENSIVE_SPELL = "defensive spell"

    # not official names
    NPC_MELEE = "monster melee"
    NPC_RANGED = "monster ranged"
    NPC_MAGIC = "monster magic"


MeleeStances = (
    Stances.ACCURATE,
    Stances.AGGRESSIVE,
    Stances.DEFENSIVE,
    Stances.CONTROLLED,
)
RangedStances = [Stances.ACCURATE, Stances.RAPID, Stances.LONGRANGE]
MagicStances = [Stances.ACCURATE, Stances.LONGRANGE, Stances.NO_STYLE, Stances.NO_STYLE]
SpellStylesNames = [Styles.STANDARD_SPELL, Styles.DEFENSIVE_SPELL]
ChinchompaStylesNames = [Styles.SHORT_FUSE, Styles.MEDIUM_FUSE, Styles.LONG_FUSE]


# skills & monster combat skills ##############################################


@unique
class Skills(Enum):
    ATTACK = "attack"
    STRENGTH = "strength"
    DEFENCE = "defence"
    RANGED = "ranged"
    PRAYER = "prayer"
    MAGIC = "magic"
    RUNECRAFT = "runecraft"
    HITPOINTS = "hitpoints"
    CRAFTING = "crafting"
    MINING = "mining"
    SMITHING = "smithing"
    FISHING = "fishing"
    COOKING = "cooking"
    FIREMAKING = "firemaking"
    WOODCUTTING = "woodcutting"
    AGILITY = "agility"
    HERBLORE = "herblore"
    THIEVING = "thieving"
    FLETCHING = "fletching"
    SLAYER = "slayer"
    FARMING = "farming"
    CONSTRUCTION = "construction"
    HUNTER = "hunter"


MonsterCombatSkills = (
    Skills.ATTACK,
    Skills.STRENGTH,
    Skills.DEFENCE,
    Skills.RANGED,
    Skills.MAGIC,
    Skills.HITPOINTS,
)

BgsReducedSkills = (
    Skills.DEFENCE,
    Skills.STRENGTH,
    Skills.ATTACK,
    Skills.MAGIC,
    Skills.RANGED,
)

ArclightReducedSkills = (Skills.ATTACK, Skills.STRENGTH, Skills.DEFENCE)

# monster types & locations ###################################################


@unique
class MonsterTypes(Enum):
    DEMON = "demon"
    DRACONIC = "draconic"
    FIERY = "fiery"
    GOLEM = "golem"
    KALPHITE = "kalphite"
    LEAFY = "leafy"
    PENANCE = "penance"
    SHADE = "shade"
    SPECTRAL = "spectral"
    UNDEAD = "undead"
    VAMPYRE_TIER_1 = "vampyre - tier 1"
    VAMPYRE_TIER_2 = "vampyre - tier 2"
    VAMPYRE_TIER_3 = "vampyre - tier 3"
    XERICIAN = "xerician"
    WILDERNESS = "wilderness"
    TOA = "toa"


VampyreMonsterTypes = (
    MonsterTypes.VAMPYRE_TIER_1,
    MonsterTypes.VAMPYRE_TIER_2,
    MonsterTypes.VAMPYRE_TIER_3,
)


@unique
class MonsterLocations(Enum):
    NONE = ""
    WILDERNESS = "wilderness"
    TOB = "tob"
    COX = "cox"
    TOA = "toa"


@unique
class Slayer(Enum):
    """An incomplete list of slayer assignment categories."""

    NONE = auto()

    ABERRANT_SPECTRES = auto()
    ABYSSAL_DEMONS = auto()
    ADAMANT_DRAGONS = auto()
    ANKOUS = auto()
    AVIANSIE = auto()
    BANDITS = auto()
    BANSHEES = auto()
    BASILISKS = auto()
    BATS = auto()
    BEARS = auto()
    BIRDS = auto()
    BLACK_DEMONS = auto()
    BLACK_DRAGONS = auto()
    BLACK_KNIGHTS = auto()
    BLOODVELDS = auto()
    BLUE_DRAGONS = auto()
    BRINE_RATS = auto()
    BRONZE_DRAGONS = auto()
    CATABLEPON = auto()
    CAVE_BUGS = auto()
    CAVE_CRAWLERS = auto()
    CAVE_HORRORS = auto()
    CAVE_SLIMES = auto()
    CAVE_KRAKEN = auto()
    CHAOS_DRUIDS = auto()
    COCKATRICES = auto()
    COWS = auto()
    DAGANNOTHS = auto()

    # done doing the bs ones for now

    DUST_DEVILS = auto()
    FOSSIL_ISLAND_WYVERNS = auto()
    GOBLINS = auto()
    GREATER_DEMONS = auto()
    GREEN_DRAGONS = auto()
    HELLHOUNDS = auto()
    HYDRAS = auto()
    JELLIES = auto()
    KALPHITES = auto()
    KURASKS = auto()
    LAVA_DRAGONS = auto()
    LIZARDMEN = auto()
    MITHRIL_DRAGONS = auto()
    NECHRYAEL = auto()
    RED_DRAGONS = auto()
    REVENANTS = auto()
    RUNE_DRAGONS = auto()
    SCORPIONS = auto()
    SHADES = auto()
    SKELETAL_WYVERNS = auto()
    SKELETONS = auto()
    SMOKE_DEVILS = auto()
    SUQAHS = auto()
    TROLLS = auto()
    VAMPYRES = auto()
    WYRMS = auto()


DATAMODE_TYPE = namedtuple("datamode", ["key", "dtype", "attribute"])


class DataMode(Enum):
    """DataMode enums for the analysis_tools module"""

    DPT = DATAMODE_TYPE("damage per tick", float, "per_tick")
    DPS = DATAMODE_TYPE("damage per second", float, "per_second")
    DPM = DATAMODE_TYPE("damage per minute", float, "per_minute")
    DPH = DATAMODE_TYPE("damage per hour", float, "per_hour")
    MAX = DATAMODE_TYPE("max hit", int, "max_hit")
    MIN = DATAMODE_TYPE("min hit", int, "min_hit")
    MEAN = DATAMODE_TYPE("mean hit", float, "mean")
    POSITIVE_DAMAGE = DATAMODE_TYPE("chance to deal positive damage", float, "probability_nonzero_damage")
    TICKS_TO_KILL = DATAMODE_TYPE("ticks to kill", float, None)
    SECONDS_TO_KILL = DATAMODE_TYPE("seconds to kill", float, None)
    MINUTES_TO_KILL = DATAMODE_TYPE("minutes to kill", float, None)
    HOURS_TO_KILL = DATAMODE_TYPE("hours to kill", float, None)
    DAMAGE_PER_TICK = DPT
    DAMAGE_PER_SECOND = DPS
    DAMAGE_PER_MINUTE = DPM
    DAMAGE_PER_HOUR = DPH
    MAX_HIT = MAX
    MIN_HIT = MIN
    MEAN_HIT = MEAN
    DWH_SUCCESS = POSITIVE_DAMAGE
    TTK = TICKS_TO_KILL
    STK = SECONDS_TO_KILL
    MTK = MINUTES_TO_KILL
    HTK = HOURS_TO_KILL


@unique
class DataAxes(Enum):
    """DataAxes enums for the analysis_tools module"""

    PLAYER = "player"
    TARGET = "target"
    EQUIPMENT = "equipment"
    STYLE = "style"
    PRAYERS = "prayers"
    BOOSTS = "boosts"
    LEVELS = "levels"
    SPECIAL_ATTACK = "special_attack"
    DISTANCE = "distance"
    SPELL = "spell"
    ADDITIONAL_TARGETS = "additional_targets"


# slots ######################################################################


@unique
class Slots(Enum):
    """Complete list of gear slots in order from top to bottom, left to right."""

    HEAD = "head"
    CAPE = "cape"
    NECK = "neck"
    AMMUNITION = "ammunition"
    WEAPON = "weapon"
    BODY = "body"
    SHIELD = "shield"
    LEGS = "legs"
    HANDS = "hands"
    FEET = "feet"
    RING = "ring"


# effects #####################################################################


class Effect(Enum):
    """Enumerator of timed effect classifications."""

    # weapons
    STAFF_OF_THE_DEAD = auto()

    # potions
    STAMINA_POTION = auto()
    DIVINE_POTION = auto()
    OVERLOAD = auto()

    # character
    REGEN_SPECIAL_ENERGY = auto()
    UPDATE_STATS = auto()

    # olm phase specific effects
    OLM_BURN = auto()
    OLM_ACID = auto()
    OLM_FALLING_CRYSTAL = auto()

    # prayer
    PRAYER_DRAIN = auto()

    # misc
    FROZEN = auto()
