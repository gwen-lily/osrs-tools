from osrs_tools.character import Player, Guardian
from osrs_tools.equipment import Equipment, Gear
from osrs_tools.prayer import Piety
from osrs_tools.stats import Overload, SuperCombatPotion, SuperStrengthPotion
from osrs_tools.analysis_tools import DataMode, bedevere_2d

def rsn_hits(rsn: str):
    lad = Player.from_rsn(rsn)
    guardian = Guardian.from_de0(26)

    lad.equipment.equip_basic_melee_gear(brimstone=True)
    lad.equipment.equip_bandos_set()
    lad.equipment.equip(torva_full_helm)
    lad.active_style = lad.equipment.equip_dragon_pickaxe()
    assert lad.equipment.full_set

    equipments = (eqp1, eqp2) = [Equipment() for _ in range(2)]
    eqp1.equip(berserker_ring)
    eqp2.equip(brimstone_ring)

    boosts = [Overload, SuperStrengthPotion]
    prayers = Piety

    _, table = bedevere_2d(
        lad,
        guardian,
        equipment=equipments,
        boosts=boosts,
        prayers=prayers,
        data_mode=DataMode.MAX_HIT,
        floatfmt='.0f'
    )
    print(table)



def main():
    rsn_hits('SirBedevere')

if __name__ == '__main__':
    torva_full_helm = Gear.from_bb('torva full helm')
    berserker_ring = Gear.from_bb('berserker (i)')
    brimstone_ring = Gear.from_bb('brimstone ring')

    main()
