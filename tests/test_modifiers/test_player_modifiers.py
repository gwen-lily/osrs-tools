from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.data import Slayer, Styles
from osrs_tools.gear import AbyssalTentacle, AvernicDefender, EliteVoidSet, GhraziRapier
from osrs_tools.gear.common_gear import (
    AbyssalWhip,
    AncestralSet,
    Arclight,
    DinhsBulwark,
    DragonHunterCrossbow,
    DragonHunterLance,
    SalveAmuletEI,
    SlayerHelmetI,
    SmokeBattlestaff,
    TorvaSet,
)
from osrs_tools.modifiers.player import PlayerModifiers
from osrs_tools.spell import StandardSpells
from osrs_tools.style.all_weapon_styles import (
    BulwarkStyles,
    CrossbowStyles,
    PolearmStyles,
    SlashSwordStyles,
    SpearStyles,
)


def test_aggressive_bonus():
    pass


def test_salve_modifiers():
    player = Player()
    player.eqp += SalveAmuletEI
    player.eqp += AbyssalTentacle

    target = Monster.dummy()

    mods = PlayerModifiers.simple(player, target)

    arms, dms = mods.get_modifiers()

    assert len(arms) == 1
    assert len(dms) == 1

    assert arms[0].value == 1.2


def test_dinhs_strength_modifier():
    player = Player()
    player.eqp += TorvaSet
    player.eqp += DinhsBulwark
    player.style = BulwarkStyles[Styles.PUMMEL]

    target = Monster.dummy()

    mods = PlayerModifiers.simple(player, target)

    assert player.aggressive_bonus.melee_strength.value == 56
    assert mods.aggressive_bonus.melee_strength.value == 56 + 23


def test_smoke_modifier():
    player = Player()
    player.eqp += SmokeBattlestaff
    player.autocast = StandardSpells.FIRE_SURGE.value

    target = Monster.dummy()

    mods = PlayerModifiers.simple(player, target)
    arms, _ = mods.get_modifiers()

    assert len(arms) == 1
    assert arms[0].value == 1.1


def test_magic_damage_modifier():
    player = Player()
    player.eqp += AncestralSet
    player.autocast = StandardSpells.FIRE_SURGE.value

    target = Monster.dummy()

    mods = PlayerModifiers.simple(player, target)
    _, dms = mods.get_modifiers()

    assert len(dms) == 1
    assert dms[0].value == 1.06


def test_slayer_modifier():
    player = Player()
    player.eqp += SlayerHelmetI
    player.eqp += AbyssalWhip

    target = Monster.dummy()
    target.slayer_category = Slayer.DAGANNOTHS

    mods = PlayerModifiers.simple(player, target)
    arms, dms = mods.get_modifiers()

    assert len(arms) == len(dms) == 0

    player.slayer_task = Slayer.DAGANNOTHS

    mods = PlayerModifiers.simple(player, target)
    arms, dms = mods.get_modifiers()

    assert len(arms) == len(dms) == 1
    assert arms[0].value == dms[0].value == 7 / 6


def test_arclight_modifier():
    player = Player()
    player.eqp += Arclight
    player.style = SlashSwordStyles[Styles.SLASH]

    target = Monster.dummy()

    mods = PlayerModifiers.simple(player, target)
    arms, dms = mods.get_modifiers()

    assert len(arms) == len(dms) == 1
    assert arms[0].value == dms[0].value == 1.7


def test_draconic_modifier():
    player = Player()
    player.eqp += DragonHunterLance
    player.style = SpearStyles[Styles.LUNGE]

    target = Monster.dummy()

    mods = PlayerModifiers.simple(player, target)
    arms, dms = mods.get_modifiers()

    assert len(arms) == len(dms) == 1
    assert arms[0].value == dms[0].value == 1.2

    player.eqp += DragonHunterCrossbow
    player.style = CrossbowStyles[Styles.RAPID]

    mods = PlayerModifiers.simple(player, target)
    arms, dms = mods.get_modifiers()

    assert len(arms) == len(dms) == 1
    assert arms[0].value == dms[0].value == 1.3


def test_wilderness_modifier():
    pass


def test_twisted_bow_modifier():
    pass


def test_obsidian_modifier():
    pass


def test_berserker_necklace_damage_modifier():
    pass


def test_dharok_damage_modifier():
    pass


def test_leafy_modifier():
    pass


def test_keris_damage_modifier():
    pass


def test_crystal_armor_modifier():
    pass


def test_inquisitor_modifier():
    pass


def test_chin_modifier():
    pass


def test_vampyric_modifier():
    pass


def test_chaos_gauntlets_damage_bonus():
    pass


def test_guardians_damage_modifier():
    pass


def test_ice_demon_damage_modifier():
    pass


def test_abyssal_bludgeon_special_modifier():
    pass
