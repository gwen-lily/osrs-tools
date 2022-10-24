from itertools import product

import numpy as np
from osrs_tools.analysis.pvm_axes import PvmAxes, PvmAxesEquipmentStyle
from osrs_tools.analysis.utils import bedevere_the_wise
from osrs_tools.boost import SuperCombatPotion
from osrs_tools.character.monster.cox import OlmMeleeHand, RangedVanguard, Tekton, TektonEnraged
from osrs_tools.character.monster.cox.cox_monster import CoxMonster
from osrs_tools.character.monster.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.data import DataMode, Styles
from osrs_tools.gear import InquisitorsArmourSet, InquisitorsMace, InquisitorsPlateskirt, ScytheOfVitur
from osrs_tools.gear.common_gear import AvernicDefender, TorvaSet
from osrs_tools.gear.custom_gear import SaeBaeInqHauberk, SaeBaeInqHelm
from osrs_tools.gear.equipment import Equipment
from osrs_tools.prayer import Piety
from osrs_tools.prayer.prayers import Prayers
from osrs_tools.style.all_weapon_styles import ScytheStyles, SpikedWeaponsStyles


def main():
    player = Player()

    # targets
    monster_ary = [Tekton, TektonEnraged]
    ps_ary = list(range(1, 6))
    cm_ary = [False, True]
    hammer_ary = [0, 1, 2]

    target: list[Monster] = []

    for cox_monster in monster_ary:
        for cm in cm_ary:
            for ps in ps_ary:
                for hammers in hammer_ary:
                    monster = cox_monster.simple(ps, cm)
                    assert isinstance(monster, CoxMonster)

                    for _ in range(hammers):
                        monster.apply_dwh()

                    monster.name = f"{monster.name} ({hammers} hammers)"
                    target.append(monster)

    # equipment
    basic_eqp = Equipment().equip_bis_melee(torva_set=False).equip(ScytheOfVitur)
    # basic_eqp = Equipment().equip_bis_melee(torva_set=False).equip(InquisitorsMace, AvernicDefender)

    # pre-gaming
    player.eqp = basic_eqp
    # player.style = SpikedWeaponsStyles[Styles.PUMMEL]

    # options
    equipment = [
        # Equipment(name="inquisitor").equip(*InquisitorsArmourSet),
        Equipment(name="sae bae inq").equip(SaeBaeInqHelm, SaeBaeInqHauberk, InquisitorsPlateskirt),
        Equipment(name="torva").equip(*TorvaSet),
    ]

    style = [ScytheStyles[Styles.CHOP], ScytheStyles[Styles.JAB]]

    # others
    prayers = Prayers(name=Piety.name, prayers=[Piety])
    boosts = SuperCombatPotion
    special_attack = False

    full_axes = PvmAxes.create(
        player, target, equipment=equipment, style=style, prayers=prayers, boosts=boosts, special_attack=special_attack
    )
    full_axes = PvmAxesEquipmentStyle.from_pvm_axes(full_axes)

    axes = full_axes.squeezed_axes
    data = bedevere_the_wise(full_axes, DataMode.DPT)

    for ax in axes:
        print(ax.name)
        for val in getattr(full_axes, ax.name):
            print(val)

    print(data)

    dps_increase = np.mean(data[:, 1] / data[:, 2])
    print(dps_increase)


if __name__ == "__main__":
    main()
