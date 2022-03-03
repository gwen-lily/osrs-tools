from osrs_tools.character import *
from osrs_tools.analysis_tools import ComparisonMode, DataMode, tabulate_wrapper, generic_comparison_better

from itertools import product
import math
import matplotlib.pyplot as plt

def shaun_vs_normie(**kwargs):
    shaun_rsn = '31 pray btw'
    shaun = Player(name=shaun_rsn, levels=PlayerLevels.from_rsn(shaun_rsn), prayers=PrayerCollection(Prayer.mystic_lore()))
    normie = Player(name='normie', levels=PlayerLevels.maxed_player(), prayers=PrayerCollection(Prayer.augury()))
    lads = (shaun, normie)

    # equipment
    shaun.active_style = shaun.equipment.equip_sang(arcane=False)
    shaun.equipment.equip_basic_magic_gear(
        ancestral_set=False, 
        god_cape=True, 
        occult=True, 
        arcane=False, 
        tormented=True, 
        eternal=False, 
        brimstone=True
        )
    shaun.equipment.equip(
        Gear.from_osrsbox("dagon'hai hat"),
        Gear.from_osrsbox("infinity top"),
        Gear.from_osrsbox("mage's book"),
        Gear.from_osrsbox("dagon'hai robe bottom"),
        Gear.from_osrsbox("infinity boots")
    )

    assert shaun.equipment.aggressive_bonus.magic == 133
    assert shaun.equipment.aggressive_bonus.magic_strength == 0.17

    normie.equipment.equip_basic_magic_gear()
    normie.active_style = normie.equipment.equip_sang()

    # boosts / etc
    for lad in lads:
        assert lad.equipment.full_set
        lad.boost(Overload.overload())
    
    scale_data = np.arange(1, 51)
    olms = tuple(OlmMageHand.from_de0(ps) for ps in scale_data)
    
    indices, axes, data_ary = generic_comparison_better(lads, target=olms, comparison_mode=ComparisonMode.CARTESIAN, data_mode=DataMode.DPS)

    row_labels = axes[0]
    col_labels = axes[-1]
    data = data_ary[:, 0, 0, 0, 0, 0, :]

    shaun_data = data[0, :]
    normie_data = data[1, :]
    ratio_data = [sd / nd for sd, nd in zip(shaun_data, normie_data)]

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    ax1.set_xlabel('scale')
    ax1.set_ylabel('dps')
    ax1.set_title('Normie & Shaun DPS against Olm Mage Hand vs scale')
    ax1.plot(scale_data, shaun_data)
    ax1.plot(scale_data, normie_data)
    ax1.legend([str(lad) for lad in lads])

    ax2.plot(scale_data, ratio_data)
    ax2.set_title('ratio of normie dps / shaun dps')
    plt.show()
    fig.savefig('shaun.png')


if __name__ == '__main__':
    shaun_vs_normie()
    