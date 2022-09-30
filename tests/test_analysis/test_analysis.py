from osrs_tools.analysis.pvm_axes import PvmAxes
from osrs_tools.boost import Overload
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.data import Slots
from osrs_tools.gear import Equipment
from osrs_tools.gear.common_gear import AbyssalWhip, GhraziRapier
from osrs_tools.gear.gear import EquipableError
from osrs_tools.prayer import Piety


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
    assert ax.dims == (1, 1, 2, 0, 1, 1, 0, 2, 0, 0, 0)

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
