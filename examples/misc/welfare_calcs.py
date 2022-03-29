from osrs_tools.analysis_tools import bedevere_2d, bedevere_the_wise, table_2d
from osrs_tools.character import LizardmanShaman, Player
from osrs_tools.equipment import Gear
from osrs_tools.style import ChinchompaStyles, PlayerStyle


@table_2d
def chinchompa_estimates(scale: int, task: bool = True, vulnerability: bool = True, style: PlayerStyle):
    shaman = LizardmanShaman.from_de0(scale)

    if vulnerability:
        shaman.apply_vulnerability()
    
    lad = Player()

    lad.equipment.equip_basic_ranged_gear()
    lad.equipment.equip_arma_set(zaryte=True)
    lad.active_style = lad.equipment.equip_chins(black=True)

    if task:
        lad.equipment.equip_slayer_helm()


    
