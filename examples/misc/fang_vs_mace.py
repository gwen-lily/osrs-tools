from osrs_tools.analysis import PvmAxes
from osrs_tools.analysis.utils import bedevere_the_wise
from osrs_tools.boost import Boost, Overload, SuperCombatPotion
from osrs_tools.character.monster.cox import OlmMageHand, Tekton
from osrs_tools.character.monster.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.data import DataMode, Styles
from osrs_tools.gear import InquisitorsMace, OsmumtensFang
from osrs_tools.gear.common_gear import BrimstoneRing, TumekensShadow
from osrs_tools.gear.equipment import Equipment
from osrs_tools.prayer.all_prayers import Augury, Piety
from osrs_tools.prayer.prayers import Prayers
from osrs_tools.spell.spell import TumekenPoweredSpell
from osrs_tools.spell.spells import PoweredSpells
from osrs_tools.style.all_weapon_styles import PoweredStaffStyles, SpikedWeaponsStyles, StabSwordStyles


def main():
    player = Player()
    player.eqp = Equipment().equip_bis_melee()

    party_size = 1

    targets: list[Monster] = [Tekton.simple(party_size) for _ in range(2 + 1)]

    for idx, target in enumerate(targets):
        for _ in range(idx):
            target.apply_dwh()

    equipment = [Equipment().equip(OsmumtensFang), Equipment().equip(InquisitorsMace)]

    styles = [
        StabSwordStyles[Styles.LUNGE],
        SpikedWeaponsStyles[Styles.PUMMEL],
    ]

    prayers = Prayers(prayers=[Piety])
    boosts = [
        Overload,
        SuperCombatPotion,
    ]

    full_axes = PvmAxes.create(player, targets, equipment=equipment, style=styles, prayers=prayers, boosts=boosts)

    axes, data = bedevere_the_wise(full_axes, DataMode.DAMAGE_PER_TICK)

    for idx, ax in enumerate(axes):
        print(ax.name)
        values = getattr(full_axes, ax.name)

        for jdx, val in enumerate(values):
            print(jdx, str(val))

    print(data[:, :, :, 0])


def augury_comparison():
    player = Player()
    target = OlmMageHand.simple(1)

    player.eqp = Equipment().equip_bis_mage(arcane=False)
    player.eqp += TumekensShadow
    player.eqp += BrimstoneRing
    player.autocast = PoweredSpells.TUMEKENS_SHADOW.value
    player.style = PoweredStaffStyles[Styles.ACCURATE]

    prayers = [Prayers(name="none", prayers=[]), Prayers(name="augury", prayers=[Augury])]

    boosts: list[Boost] = [Overload]

    full_axes = PvmAxes.create(player, target, prayers=prayers, boosts=boosts)

    axes, data = bedevere_the_wise(full_axes, DataMode.DAMAGE_PER_TICK)

    for axis_idx, (axis, axis_len) in enumerate(zip(full_axes.squeezed_axes, full_axes.squeezed_dims)):
        print(axis.name)
        values = getattr(full_axes, axis.name)

        for idx, val in enumerate(values):
            print(f"\t{idx}:\t{val}")

    print(data)
    print(data[1] / data[0])


if __name__ == "__main__":
    # main()
    augury_comparison()
