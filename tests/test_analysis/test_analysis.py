from osrs_tools.analysis.pvm_axes import PvmAxes
from osrs_tools.analysis.utils import bedevere_the_wise, tabulate_enhanced
from osrs_tools.boost import Overload
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.data import DataMode, Slots, Styles
from osrs_tools.gear import Equipment
from osrs_tools.gear.common_gear import AbyssalWhip, BerserkerRingI, GhraziRapier
from osrs_tools.gear.gear import EquipableError
from osrs_tools.prayer import Piety
from osrs_tools.style.all_weapon_styles import StabSwordStyles, WhipStyles
from osrs_tools.style.style import PlayerStyle


def test_pvm_axes():
    player = Player()
    target = Monster.dummy()

    equipment = [
        Equipment().equip(AbyssalWhip),
        Equipment().equip(GhraziRapier),
    ]
    prayer = Piety
    boost = Overload

    special_attack = [False, True]

    ax = PvmAxes.create(
        player, target, equipment=equipment, prayers=prayer, boosts=boost, special_attack=special_attack
    )

    assert len(ax.axes) == 11
    assert ax.dims == (1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1)

    assert len(ax.squeezed_axes) == 2
    assert ax.squeezed_dims == (2, 2)

    eqp_0, spec_0 = ax[0, 0]
    assert isinstance(eqp_0, Equipment)
    assert eqp_0[Slots.WEAPON] == AbyssalWhip
    assert spec_0 is False

    eqp_1, spec_0 = ax[1, 0]
    assert isinstance(eqp_1, Equipment)
    assert eqp_1[Slots.WEAPON] == GhraziRapier
    assert spec_0 is False


def test_bedevere_the_wise():
    player = Player()
    target = Monster.dummy()

    equipment = [
        Equipment().equip(AbyssalWhip),
        Equipment().equip(GhraziRapier),
    ]
    style1 = StabSwordStyles[Styles.LUNGE]
    style2 = WhipStyles[Styles.LASH]
    styles = [style1, style2]
    prayer = Piety
    boost = Overload

    special_attack = False

    ax = PvmAxes.create(
        player, target, equipment=equipment, style=styles, prayers=prayer, boosts=boost, special_attack=special_attack
    )

    assert len(ax.squeezed_dims) == 2

    axes, dam_ary = bedevere_the_wise(ax, DataMode.MAX_HIT)

    assert len(axes) == 2
    assert dam_ary.shape == (2, 2)

    meta_header = "test header"
    row_labels = [e.weapon.name for e in equipment]
    col_labels = [s.name.value for s in styles]

    table = tabulate_enhanced(dam_ary, col_labels, row_labels, meta_header)

    with open("out.txt", mode="w", encoding="UTF-8") as f:
        f.writelines(table)
