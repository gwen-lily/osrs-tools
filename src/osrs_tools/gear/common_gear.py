"""Useful and re-usable gear.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-25                                                         #
###############################################################################
"""

from osrs_tools.data import Slots
from osrs_tools.stats import AggressiveStats, DefensiveStats, PlayerLevels
from osrs_tools.tracked_value import EquipmentStat

from .gear import Gear
from .special_weapon import SpecialWeapon
from .weapon import Weapon

# void ########################################################################

VoidKnightHelm = Gear.from_bb("void knight helm")
VoidKnightTop = Gear.from_bb("void knight top")
VoidKnightRobe = Gear.from_bb("void knight robe")
VoidKnightGloves = Gear.from_bb("void knight gloves")

EliteVoidTop = Gear.from_bb("elite void top")
EliteVoidRobe = Gear.from_bb("elite void robe")

# misc ########################################################################

RingOfEndurance = Gear.no_stats("ring of endurance", Slots.RING)
KodaiWand = Weapon.from_bb("kodai wand")
BookOfTheDead = Gear(
    name="book of the dead",
    slot=Slots.SHIELD,
    aggressive_bonus=AggressiveStats(magic_attack=EquipmentStat(6)),
    defensive_bonus=DefensiveStats(),
    prayer_bonus=3,
    level_requirements=PlayerLevels.starting_stats(),
)
RingOfSufferingI = Gear.from_bb("ring of suffering (i)")

IbansStaff = Weapon.from_bb("iban staff (u)")
TridentOfTheSeas = Weapon.from_bb("trident of the seas")
TridentOfTheSwamp = Weapon.from_bb("trident of the swamp")

SanguinestiStaff = Weapon.from_bb("sanguinesti staff")
HarmonisedStaff = Weapon.from_bb("harmonised nightmare staff")
TumekensShadow = Weapon.from_bb("tumeken's shadow")

BlessedCoif = Gear.from_bb("god coif")
BlessedBody = Gear.from_bb("god d'hide body")
BlessedChaps = Gear.from_bb("god d'hide chaps")
BlessedBracers = Gear.from_bb("god bracers")
BlessedBoots = Gear.from_bb("blessed d'hide boots")

ZaryteVambraces = Gear.from_osrsbox("zaryte vambraces")
BarrowsGloves = Gear.from_bb("barrows gloves")

SalveAmuletI = Gear.from_bb("salve amulet (i)")
SalveAmuletEI = Gear.from_bb("salve amulet (ei)")

TorvaFullHelm = Gear.from_bb("torva full helm")
TorvaPlatebody = Gear.from_bb("torva platebody")
TorvaPlatelegs = Gear.from_bb("torva platelegs")

DharoksGreataxe = Gear.from_bb("dharok's greataxe")
DharoksPlatebody = Gear.from_bb("dharok's platebody")
DharoksPlatelegs = Gear.from_bb("dharok's platelegs")
DharoksGreataxe = Weapon.from_bb("dharok's greataxe")

NeitiznotFaceguard = Gear.from_bb("neitiznot faceguard")
BandosChestplate = Gear.from_bb("bandos chestplate")
BandosTassets = Gear.from_bb("bandos tassets")

InquisitorsGreatHelm = Gear.from_bb("inquisitor's great helm")
InquisitorsHauberk = Gear.from_bb("inquisitor's hauberk")
InquisitorsPlateskirt = Gear.from_bb("inquisitor's plateskirt")

JusticiarFaceguard = Gear.from_bb("justiciar faceguard")
JusticiarChestguard = Gear.from_bb("justiciar chestguard")
JusticiarLegguard = Gear.from_bb("justiciar legguard")

ObsidianHelm = Gear.from_bb("obsidian helm")
ObsidianPlatebody = Gear.from_bb("obsidian platebody")
ObsidianPlatelegs = Gear.from_bb("obsidian platelegs")

ObsidianDagger = Weapon.from_bb("obsidian dagger")
ObsidianMace = Weapon.from_bb("obsidian mace")
ObsidianMaul = Weapon.from_bb("obsidian maul")
ObsidianSword = Weapon.from_bb("obsidian sword")

LeafBladedSpear = Weapon.from_bb("leaf-bladed spear")
LeafBladedSword = Weapon.from_bb("leaf-bladed sword")
LeafBladedBattleaxe = Weapon.from_bb("leaf-bladed battleaxe")

Keris = Weapon.from_bb("keris")

CrystalHelm = Gear.from_bb("crystal helm")
CrystalBody = Gear.from_bb("crystal body")
CrystalLegs = Gear.from_bb("crystal legs")

CrystalBow = Weapon.from_bb("crystal bow")
BowOfFaerdhinen = Weapon.from_bb("bow of faerdhinen")
Bowfa = BowOfFaerdhinen

MysticSmokeStaff = Weapon.from_bb("mystic smoke staff")
SmokeBattlestaff = Weapon.from_bb("smoke battlestaff")

GracefulHood = Gear.from_osrsbox("graceful hood")
GracefulTop = Gear.from_osrsbox("graceful top")
GracefulLegs = Gear.from_osrsbox("graceful legs")
GracefulGloves = Gear.from_osrsbox("graceful gloves")
GracefulBoots = Gear.from_osrsbox("graceful boots")
GracefulCape = Gear.from_osrsbox("graceful cape")

ArmadylCrossbow = weapon = SpecialWeapon.from_bb("armadyl crossbow")
ZaryteCrossbow = weapon = SpecialWeapon.from_bb("zaryte crossbow")

ScytheOfVitur = Weapon.from_bb("scythe of vitur")

Chinchompa = Weapon.from_bb("chinchompa")
RedChinchompa = Weapon.from_bb("red chinchompa")
BlackChinchompa = Weapon.from_bb("black chinchompa")
GreyChinchompa = Chinchompa

BrimstoneRing = Gear.from_bb("brimstone ring")

TomeOfFire = Gear.from_bb("tome of fire")
TomeOfWater = Gear.from_bb("tome of water")

StaffOfLight = SpecialWeapon.from_bb("staff of light")
StaffOfTheDead = SpecialWeapon.from_bb("staff of the dead")
ToxicStaffOfTheDead = SpecialWeapon.from_bb("toxic staff of the dead")

ElysianSpiritShield = Gear.from_bb("elysian spirit shield")

DinhsBulwark = SpecialWeapon.from_bb("dinh's bulwark")
AmuletofBloodFury = Gear.from_bb("amulet of blood fury")
AmuletofFury = Gear.from_bb("amulet of fury")

BoneDagger = SpecialWeapon.from_bb("bone dagger")
DorgeshuunCrossbow = SpecialWeapon.from_bb("dorgeshuun crossbow")
BoneCrossbow = DorgeshuunCrossbow

DragonClaws = SpecialWeapon.from_bb("dragon claws")
AbyssalBludgeon = SpecialWeapon.from_bb("abyssal bludgeon")
Arclight = SpecialWeapon.from_bb("arclight")

DragonHunterCrossbow = Weapon.from_bb("dragon hunter crossbow")
DragonHunterLance = Weapon.from_bb("dragon hunter lance")
GhraziRapier = Weapon.from_bb("ghrazi rapier")

SlayerHelmetI = Gear.from_bb("slayer helmet (i)")

CrawsBow = Weapon.from_bb("craw's bow")
ViggorasChainmace = Weapon.from_bb("viggora's chainmace")
ThammaronsSceptre = Weapon.from_bb("thammaron's sceptre")

TwistedBow = Weapon.from_bb("twisted bow")
BerserkerNecklace = Gear.from_bb("berserker necklace")
ChaosGauntlets = Gear.from_bb("chaos gauntlets")

AbyssalWhip = SpecialWeapon.from_bb("abyssal whip")
AbyssalTentacle = SpecialWeapon.from_bb("abyssal tentacle")
AbyssalDagger = SpecialWeapon.from_bb("abyssal dagger")
DragonDagger = SpecialWeapon.from_bb("dragon dagger")

Seercull = SpecialWeapon.from_bb("seercull")

DragonWarhammer = SpecialWeapon.from_bb("dragon warhammer")

# ammunition ##################################################################

RubyDragonBoltsE = Gear.from_bb("ruby dragon bolts (e)")
RubyBoltsE = Gear.from_bb("ruby bolts (e)")


DiamondDragonBoltsE = Gear.from_bb("diamond dragon bolts (e)")
DiamondBoltsE = Gear.from_bb("diamond bolts (e)")


DragonstoneDragonBoltsE = Gear.from_bb("dragonstone dragon bolts (e)")
DragonstoneBoltsE = Gear.from_bb("dragonstone bolts (e)")


OnyxDragonBoltsE = Gear.from_bb("onyx dragon bolts (e)")
OnyxBoltsE = Gear.from_bb("onyx bolts (e)")


# basic melee
AmuletOfTorture = Gear.from_bb("amulet of torture")
PrimordialBoots = Gear.from_bb("primordial boots")
GuardianBoots = Gear.from_bb("guardian boots")
InfernalCape = Gear.from_bb("infernal cape")
FerociousGloves = Gear.from_bb("ferocious gloves")
BrimstoneRing = Gear.from_bb("brimstone ring")
BerserkerRingI = Gear.from_bb("berserker (i)")

# basic ranged
AvasAssembler = Gear.from_bb("ava's assembler")
NecklaceOfAnguish = Gear.from_bb("necklace of anguish")
PegasianBoots = Gear.from_bb("pegasian boots")
ArchersRingI = Gear.from_bb("archer (i)")

# basic magic
GodCapeI = Gear.from_bb("god cape (i)")
OccultNecklace = Gear.from_bb("occult necklace")
ArcaneSpiritShield = Gear.from_bb("arcane spirit shield")
TormentedBracelet = Gear.from_bb("tormented bracelet")
EternalBoots = Gear.from_bb("eternal boots")
SeersRingI = Gear.from_bb("seers (i)")

AvernicDefender = Gear.from_bb("avernic defender")
TyrannicalRingI = Gear.from_bb("tyrannical (i)")

BandosGodsword = SpecialWeapon.from_bb("bandos godsword")
ZamorakianHasta = SpecialWeapon.from_bb("zamorakian hasta")
DragonPickaxe = SpecialWeapon.from_bb("dragon pickaxe")
DragonArrows = Gear.from_bb("dragon arrow")

ToxicBlowpipe = SpecialWeapon.from_bb("toxic blowpipe")
DragonDarts = Gear.from_bb("dragon dart")
TwistedBuckler = Gear.from_bb("twisted buckler")
BoneBolts = Gear.from_bb("bone bolts")


NeitiznotFaceguard = Gear.from_bb("neitiznot faceguard")
BandosChestplate = Gear.from_bb("bandos chestplate")
BandosTassets = Gear.from_bb("bandos tassets")

InquisitorsGreatHelm = Gear.from_bb("inquisitor's great helm")
InquisitorsHauberk = Gear.from_bb("inquisitor's hauberk")
InquisitorsPlateskirt = Gear.from_bb("inquisitor's plateskirt")

ArmadylHelmet = Gear.from_bb("armadyl helmet")
ArmadylChestplate = Gear.from_bb("armadyl chestplate")
ArmadylChainskirt = Gear.from_bb("armadyl chainskirt")

AncestralHat = Gear.from_bb("ancestral hat")
AncestralRobeTop = Gear.from_bb("ancestral robe top")
AncestralRobeBottoms = Gear.from_bb("ancestral robe bottoms")

NeitiznotHelm = Gear.from_bb("neitiznot")
FireCape = Gear.from_bb("fire cape")
DragonDefender = Gear.from_bb("dragon defender")
RegenBracelet = Gear.from_bb("regen bracelet")
DragonBoots = Gear.from_bb("dragon boots")

DwarvenHelmet = Gear.from_bb("dwarven helmet")
MythicalCape = Gear.from_bb("mythical cape")
TyrannicalRingI = Gear.from_bb("tyrannical (i)")

BookOfLaw = Gear.from_bb("book of law")
RuneCrossbow = Weapon.from_bb("rune crossbow")

# gear shorthand ##############################################################

Dwh = DragonWarhammer
Bgs = BandosGodsword
ZerkRing = BerserkerRingI


# gear sets ###################################################################

BandosSet = [NeitiznotFaceguard, BandosChestplate, BandosTassets]
InquisitorSet = [InquisitorsGreatHelm, InquisitorsHauberk, InquisitorsPlateskirt]

TorvaSet = [TorvaFullHelm, TorvaPlatebody, TorvaPlatelegs]

DharoksSet = [
    DharoksGreataxe,
    DharoksPlatebody,
    DharoksPlatelegs,
    DharoksGreataxe,
]

NormalVoidSet = [
    VoidKnightHelm,
    VoidKnightTop,
    VoidKnightRobe,
    VoidKnightGloves,
]

EliteVoidSet = [
    VoidKnightHelm,
    EliteVoidTop,
    EliteVoidRobe,
    VoidKnightGloves,
]

JusticiarSet = [
    JusticiarFaceguard,
    JusticiarChestguard,
    JusticiarLegguard,
]

ObsidianArmorSet = [
    ObsidianHelm,
    ObsidianPlatebody,
    ObsidianPlatelegs,
]

ObsidianWeapons = [
    ObsidianDagger,
    ObsidianMace,
    ObsidianMaul,
    ObsidianSword,
]

LeafBladedWeapons = [
    LeafBladedSpear,
    LeafBladedSword,
    LeafBladedBattleaxe,
]

CrystalArmorSet = [
    CrystalHelm,
    CrystalBody,
    CrystalLegs,
]

SmokeStaves = [SmokeBattlestaff, MysticSmokeStaff]

GracefulSet = [
    GracefulHood,
    GracefulTop,
    GracefulLegs,
    GracefulGloves,
    GracefulBoots,
    GracefulCape,
]

Chinchompas = [
    Chinchompa,
    RedChinchompa,
    BlackChinchompa,
]

StavesOfTheDead = [
    StaffOfLight,
    StaffOfTheDead,
    ToxicStaffOfTheDead,
]

DragonbaneWeapons = [
    DragonHunterCrossbow,
    DragonHunterLance,
]

WildernessWeapons = [
    CrawsBow,
    ViggorasChainmace,
    ThammaronsSceptre,
]

ArmadylSet = [
    ArmadylHelmet,
    ArmadylChestplate,
    ArmadylChainskirt,
]

BlessedDragonhide = [
    BlessedCoif,
    BlessedBody,
    BlessedChaps,
    BlessedBracers,
    BlessedBoots,
]

AncestralSet = [AncestralHat, AncestralRobeTop, AncestralRobeBottoms]
