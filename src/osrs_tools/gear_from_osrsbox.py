import enum
from matplotlib.axes import Axes
from osrsbox import items_api
from osrsbox.items_api.item_properties import ItemProperties, ItemEquipment, ItemWeapon, ItemSpecialWeapon, Modifier
from pathlib import Path
from osrs_tools.resource_reader import RESOURCES_DIR


from osrs_tools.stats import PlayerLevels, AggressiveStats, DefensiveStats
from osrs_tools.style import Style, PlayerStyle, Styles
from osrs_tools.equipment import Gear, Weapon, SpecialWeapon, Slots, GearError, WeaponError
from osrs_tools.modifier import Modifier, AttackRollModifier, DamageModifier, LevelModifier
from osrs_tools.modifier import Level

# TODO: submodule for style imports
from osrs_tools.style import TwoHandedStyles, AxesStyles, BluntStyles, BludgeonStyles, BulwarkStyles
from osrs_tools.style import ClawStyles, PickaxeStyles, PolearmStyles, ScytheStyles, SlashSwordStyles
from osrs_tools.style import SpearStyles, SpikedWeaponsStyles, StabSwordStyles, UnarmedStyles, WhipStyles
from osrs_tools.style import BowStyles, ChinchompaStyles, CrossbowStyles, ThrownStyles, BladedStaffStyles
from osrs_tools.style import PoweredStaffStyles, StaffStyles

import logging




def convert_all_equippable_items(*items: ItemProperties):
    gear, weapons, special_weapons = [], [], []

    for item in items:
        if not item.equipable_by_player:
            continue

        eqp = item.equipment
        name = item.name.lower()
        slot = None
        two_handed = None

        # slot validation & weapon / 2h validation
        for sl in Slots:
            # specific cases > general
            if eqp.slot == 'ammo':
                slot = Slots.ammunition
            elif eqp.slot == '2h':
                slot = Slots.weapon
                two_handed = True
            elif eqp.slot == Slots.weapon.name:
                slot = Slots.weapon
                two_handed = False
            elif eqp.slot == sl.name:
                slot = sl
        
        if slot is None:
            raise GearError(f'{eqp.slot}')

        ab = AggressiveStats(
            stab=eqp.attack_stab,
            slash=eqp.attack_slash,
            crush=eqp.attack_crush,
            magic_attack=eqp.attack_magic,
            ranged_attack=eqp.attack_ranged,
            melee_strength=eqp.melee_strength,
            ranged_strength=eqp.ranged_strength,
            magic_strength=eqp.magic_damage / 100,
        )
        db = DefensiveStats(
            stab=eqp.defence_stab,
            slash=eqp.defence_slash,
            crush=eqp.defence_crush,
            magic=eqp.defence_magic,
            ranged=eqp.defence_ranged
        )
        pb = eqp.prayer
        
        if eqp.requirements is not None:
            combat_key = 'combat'
            if combat_key in eqp.requirements:
                eqp.requirements.pop(combat_key)
            
            reqs = PlayerLevels(**{k: Level(v) for k, v in eqp.requirements.items()})
        else:
            reqs = PlayerLevels.no_requirements()

        # last step for non-weapons
        if not item.equipable_weapon:
            gear.append(Gear(name, slot, ab, db, pb, reqs))
            continue

        assert two_handed is not None
        wp = item.weapon
        attack_speed = wp.attack_speed
        weapon_styles = None

        if (wt := wp.weapon_type) == None:
            raise WeaponError(wt)
        elif wt == "2h_sword":
            weapon_styles = TwoHandedStyles
        elif wt == "axe":
            weapon_styles = AxesStyles
        elif wt == "blunt":
            weapon_styles = BluntStyles
        elif wt == "bludgeon":
            weapon_styles = BludgeonStyles
        elif wt == "bulwark":
            weapon_styles = BulwarkStyles
        elif wt == "claw":
            weapon_styles = ClawStyles
        elif wt == "pickaxe":
            weapon_styles = PickaxeStyles
        elif wt == "polearm":
            weapon_styles = PolearmStyles
        elif wt == "scythe":
            weapon_styles = ScytheStyles
        elif wt == "slash_sword":
            weapon_styles = SlashSwordStyles
        elif wt == "spear":
            weapon_styles = SpearStyles
        elif wt == "spiked":
            weapon_styles = SpikedWeaponsStyles
        elif wt == "stab_sword":
            weapon_styles = StabSwordStyles
        elif wt == "unarmed":
            weapon_styles = UnarmedStyles
        elif wt == "whip":
            weapon_styles = WhipStyles
        elif wt == "bow":
            weapon_styles = BowStyles
        elif wt == "chinchompas":
            weapon_styles = ChinchompaStyles
        elif wt == "crossbow":
            weapon_styles = CrossbowStyles
        elif wt == "thrown":
            weapon_styles = ThrownStyles
        elif wt == "bladed_staff":
            weapon_styles = BladedStaffStyles
        elif wt == "powered_staff":
            weapon_styles = PoweredStaffStyles
        elif wt == "staff":
            weapon_styles = StaffStyles
        else:
            logging.log(logging.INFO, f'{wt} not recognized as weapon type, possibly on purpose')
            continue

        weapons.append(
            Weapon(name, slot, ab, db, pb, reqs, weapon_styles, attack_speed, two_handed)
        )

        if item.special_weapon is not None:
            pass
    
    return gear, weapons, special_weapons
    

def write_gear_definition(out_file: str | Path, *gear: Gear):

    if isinstance(out_file, str):
        out_fp = Path(out_file)
    elif isinstance(out_file, Path):
        out_fp = out_file
    else:
        raise TypeError(out_file)

    if out_fp.exists():
        raise FileExistsError()

    gear_definition = RESOURCES_DIR.joinpath('gear_definition.txt')

    with gear_definition.open() as f:
        lines = f.readlines()

    return lines            
    
    for g in gear:
        if issubclass(g, Gear):
            raise GearError()


    


if __name__ == '__main__':
    # items = items_api.load()
    # gear, weapons, special_weapons = convert_all_equippable_items(*items)
    out_file = RESOURCES_DIR.joinpath('all_gear.txt')
    lines = write_gear_definition(out_file)

    g = Gear.from_osrsbox('torva full helm')

    for idx, line in enumerate(lines):
        print(line.format(g))

    # for g in gear[:10]:
    #     print(g)
    
    # for w in weapons[:10]:
    #     print(w)



    # # Used to help generate the decision tree for weapon stances
    # weapon_example_names = [
    #     'bandos godsword',
    #     "dharok's greataxe",
    #     "dragon warhammer",
    #     "abyssal bludgeon",
    #     "dinh's bulwark",
    #     "dragon claws",
    #     "dragon pickaxe",
    #     "crystal halberd",
    #     "scythe of vitur",
    #     "arclight",
    #     "dragon hunter lance",
    #     "viggora's chainmace",
    #     "swift blade",
    #     "event rpg",
    #     "abyssal whip",
    #     "twisted bow",
    #     "black chinchompa",
    #     "zaryte crossbow",
    #     "toxic blowpipe",
    #     "staff of the dead",
    #     "sanguinesti staff",
    #     "kodai wand",
    # ]

    # weapons = [items.lookup_by_item_name(n) for n in weapon_example_names]

    # for wp in weapons:
    #     print(f'{wp.weapon.weapon_type}')
    
