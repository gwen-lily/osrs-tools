from osrs_tools.analysis import PvmAxes
from osrs_tools.analysis.utils import bedevere_the_wise, tabulate_enhanced
from osrs_tools.boost import Overload
from osrs_tools.character import Player
from osrs_tools.character.monster.cox import OlmMeleeHand
from osrs_tools.data import DataMode, Styles
from osrs_tools.gear.common_gear import AvernicDefender, DragonHunterLance, OsmumtensFang, ScytheOfVitur
from osrs_tools.gear.equipment import Equipment
from osrs_tools.prayer import Piety
from osrs_tools.style.all_weapon_styles import ScytheStyles, SpearStyles, StabSwordStyles


def test_olm_melee():
    ps = 15

    player = Player()
    target = OlmMeleeHand.simple(ps)

    assert target.hp.value == 3900
    assert target.lvl.attack.value == 337
    assert target.lvl.magic.value == 236
    assert target.lvl.defence.value == 196

    player.eqp += Equipment().equip_bis_melee()

    equipment = [
        Equipment().equip(ScytheOfVitur),
        Equipment().equip(DragonHunterLance, AvernicDefender),
        Equipment().equip(OsmumtensFang, AvernicDefender),
    ]

    style1 = ScytheStyles[Styles.CHOP]
    style2 = SpearStyles[Styles.LUNGE]
    style3 = StabSwordStyles[Styles.LUNGE]
    styles = [style1, style2, style3]

    prayer = Piety
    boost = Overload

    special_attack = False

    ax = PvmAxes.create(
        player, target, equipment=equipment, style=styles, prayers=prayer, boosts=boost, special_attack=special_attack
    )

    assert len(ax.squeezed_dims) == 2

    axes, dam_ary = bedevere_the_wise(ax, DataMode.MAX_HIT)

    assert len(axes) == 2
    assert dam_ary.shape == (3, 3)

    meta_header = "test header"
    row_labels = [e.weapon.name for e in equipment]
    col_labels = [s.name.value for s in styles]

    table = tabulate_enhanced(dam_ary, col_labels, row_labels, meta_header)

    with open("out.txt", mode="w", encoding="UTF-8") as f:
        f.writelines(table)
