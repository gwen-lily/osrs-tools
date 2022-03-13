from matplotlib.axes import Axes
from osrsbox import items_api
from osrsbox.items_api.item_properties import ItemProperties, ItemEquipment, ItemWeapon, ItemSpecialWeapon, Modifier
from osrs_tools.stats import PlayerLevels, AggressiveStats, DefensiveStats
from osrs_tools.style import *
from osrs_tools.equipment import Gear, Weapon, SpecialWeapon, GearSlots, GearError

import logging

def main():
    gear, weapons, special_weapons = [], [], []

    for item in items:
        if not item.equipable_by_player:
            continue

        eqp = item.equipment
        name = eqp.name.lower()
        slot = None
        two_handed = None

        for sl in GearSlots.to_tuple():
            # specific cases > general
            if eqp.slot == 'ammo':
                slot = GearSlots.ammunition
            elif eqp.slot == '2h':
                slot = GearSlots.weapon
                two_handed = True
            elif eqp.slot == 'weapon':
                slot = GearSlots.weapon
                two_handed = False
            elif eqp.slot == sl:
                slot = eqp.slot
        
        if slot is None:
            raise GearError(f'{eqp.slot}')

        ab = AggressiveStats(
            stab=eqp.attack_stab,
            slash=eqp.attack_slash,
            crush=eqp.attack_crush,
            magic=eqp.attack_magic,
            ranged=eqp.attack_ranged,
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
        reqs = PlayerLevels(**eqp.requirements)

        if item.equipable_weapon:
            assert two_handed is not None
            wp = item.weapon
            attack_speed = wp.attack_speed
            weapon_styles = None

            if (wt := eqp.weapon_type) == None:
                pass
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

            if item.special_weapon is not None:
                pass

            weapons.append(
                Weapon(name, slot, ab, db, pb, reqs, weapon_styles, attack_speed, two_handed)
            )

        else:
            gear.append(Gear(name, slot, ab, db, pb, reqs))



if __name__ == '__main__':
    items = items_api.load()
    main()

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
    
