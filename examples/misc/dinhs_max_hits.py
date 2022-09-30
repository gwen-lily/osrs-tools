from osrs_tools.analysis.pvm_axes import PvmAxes
from osrs_tools.analysis.utils import DataMode, bedevere_2d, bedevere_the_wise
from osrs_tools.boost import Overload
from osrs_tools.character.monster import Monster
from osrs_tools.character.player import Player
from osrs_tools.data import Styles
from osrs_tools.gear import (
    AmuletofFury,
    AmuletOfTorture,
    BarrowsGloves,
    BerserkerRingI,
    DinhsBulwark,
    FerociousGloves,
    GuardianBoots,
    InfernalCape,
    JusticiarSet,
    PrimordialBoots,
    RingOfSufferingI,
    SalveAmuletEI,
    SlayerHelmetI,
    TorvaSet,
)
from osrs_tools.gear.utils_2 import generate_all_equipments
from osrs_tools.prayer import Piety
from osrs_tools.style import PlayerStyle
from osrs_tools.style.all_weapon_styles import BulwarkStyles


def dinhs_max(**kwargs):

    eligible_gear = (
        [
            # helm
            SlayerHelmetI,
            # cape
            InfernalCape,
            # necklace
            AmuletofFury,
            AmuletOfTorture,
            SalveAmuletEI,
            # weapons
            DinhsBulwark,
            # boots
            PrimordialBoots,
            GuardianBoots,
            # gloves
            BarrowsGloves,
            FerociousGloves,
            # rings
            RingOfSufferingI,
            BerserkerRingI,
        ]
        # sets
        + JusticiarSet
        + TorvaSet
    )

    options = {
        "prayers": Piety,
        "boosts": Overload,
        # "data_mode": DataMode.MAX_HIT,
        # "floatfmt": ".0f",
        "special_attack": True,
    }
    options.update(kwargs)
    data_mode = DataMode.MAX_HIT

    equipment_options = generate_all_equipments(*eligible_gear)

    player = Player()
    dummy = Monster.dummy()

    attack_style = BulwarkStyles[Styles.PUMMEL]
    assert isinstance(attack_style, PlayerStyle)

    axes = PvmAxes.create(player, dummy, equipment=equipment_options, style=attack_style, **options)

    # justi, torva, torva (slayer)
    _, normal_table = bedevere_the_wise(axes, data_mode)
    print(normal_table)

    return normal_table


if __name__ == "__main__":

    table = dinhs_max()

    print(table)
