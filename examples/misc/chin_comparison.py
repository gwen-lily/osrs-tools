from osrs_tools.boost import Overload, RangingPotion
from osrs_tools.character import Player
from osrs_tools.character.monster.cox import LizardmanShaman
from osrs_tools.combat import PvMCalc
from osrs_tools.data import Styles
from osrs_tools.gear.common_gear import BowOfFaerdhinen, CrystalArmorSet, RedChinchompa
from osrs_tools.gear.equipment import Equipment
from osrs_tools.prayer import Rigour
from osrs_tools.style.all_weapon_styles import BowStyles, ChinchompaStyles


def havoq_comparison():
    player = Player()
    target = LizardmanShaman.simple(15)

    player.eqp = Equipment().equip_bis_ranged(arma_set=False, zaryte=False)
    player.eqp += CrystalArmorSet
    player.eqp += BowOfFaerdhinen
    player.style = BowStyles[Styles.RAPID]

    player.boost(Overload)
    player.pray(Rigour)

    calc = PvMCalc(player, target)

    dam1 = calc.get_damage()

    player.eqp += RedChinchompa
    player.style = ChinchompaStyles[Styles.MEDIUM_FUSE]

    calc = PvMCalc(player, target)

    dam2 = calc.get_damage(distance=10, additional_targets=4)

    print(dam1.per_tick, dam2.per_tick)


if __name__ == "__main__":
    havoq_comparison()
