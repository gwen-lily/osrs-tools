from osrs_tools.character import *
from osrs_tools.analysis_tools import ComparisonMode, DataMode, tabulate_enhanced, bedevere_the_wise

from itertools import product
import math
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

def shaun_vs_normie(**kwargs):
    shaun_rsn = '31 pray btw'
    shaun_levels = PlayerLevels.from_rsn(shaun_rsn)
    shaun_prayers = PrayerCollection(Prayer.mystic_lore())
    old_shaun = Player(name=f'{shaun_rsn} (trident)', base_levels=shaun_levels, prayers_coll=shaun_prayers)
    shaun = Player(name=f'{shaun_rsn} (sang)', base_levels=shaun_levels, prayers_coll=shaun_prayers)
    normie = Player(name='normie', base_levels=PlayerLevels.maxed_player(), prayers_coll=PrayerCollection(Prayer.augury()))
    lads = (old_shaun, shaun, normie)

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

    old_shaun.equipment = copy(shaun.equipment)
    old_shaun.active_style = old_shaun.equipment.equip(Weapon.from_bb('trident of the swamp'))

    assert shaun.aggressive_bonus.magic == 133
    assert shaun.aggressive_bonus.magic_strength == 0.17

    normie.equipment.equip_basic_magic_gear()
    normie.active_style = normie.equipment.equip_sang()

    # boosts / etc
    for lad in lads:
        assert lad.equipment.full_set
        lad.boost(Overload.overload())
    
    scale_data = np.arange(1, 101)
    olms = tuple(OlmMageHand.from_de0(ps) for ps in scale_data)
    
    indices, axes, data_ary = bedevere_the_wise(lads, target=olms, comparison_mode=ComparisonMode.CARTESIAN, data_mode=DataMode.DPS)

    row_labels = axes[0]
    col_labels = axes[-1]
    data = data_ary[:, 0, 0, 0, 0, 0, :]

    old_shaun_data = data[0, :]
    shaun_data = data[1, :]
    normie_data = data[2, :]
    # ratio_data = [sd / nd for sd, nd in zip(shaun_data, normie_data)]

    fig, ax1 = plt.subplots(1, 1)   # , sharex=True)  # (ax1, ax2)
    ax1.set_xlabel('scale')
    ax1.set_ylabel('dps')
    ax1.set_title('Normie & Shaun DPS against Olm Mage Hand vs scale')
    ax1.plot(scale_data, old_shaun_data)
    ax1.plot(scale_data, shaun_data)
    ax1.plot(scale_data, normie_data)
    ax1.legend([str(lad) for lad in lads])

    # ax2.plot(scale_data, ratio_data)
    # ax2.set_title('ratio of normie dps / shaun dps')
    plt.show()
    fig.savefig('shaun.png')


class Routine(ABC):

    @abstractmethod
    def routine(self, *args, **kwargs):
        """Abstract routine with generic *args & **kwargs.
        """


class PrayerRoutine(Routine):

    @abstractmethod
    def routine(self, player: Player, last_auto: Style, boost: Prayer | PrayerCollection):
        """A method that alters player behavior based on the last attack.

        Args:
            player (Player): A player.
            last_auto (Style): The last style an NPC used.
            boost (Prayer | PrayerCollection): A prayer, such as piety, that player uses in addition to protect prayers.
        """

class SwitchPrayers(PrayerRoutine):

    def routine(self, player: Player, last_auto: Style, boost: Prayer | PrayerCollection):
        """Switches prayers to counter the last observed style.

        Args:
            player (Player): A Player.
            last_auto (Style): The last style an NPC used.
            boost (Prayer | PrayerCollection): A prayer, such as piety, that player uses in addition to protect prayers.
        """
        if isinstance(boost, Prayer):
            pc = PrayerCollection(prayers=(boost, ))
        elif isinstance(boost, PrayerCollection):
            pc = boost

        if last_auto.damage_type in Style.magic_damage_types:
            pc.pray(Prayer.protect_from_magic())
        elif last_auto.damage_type in Style.ranged_damage_types:
            pc.pray(Prayer.protect_from_missiles())
        elif last_auto.damage_type in Style.melee_damage_types:
            pc.pray(Prayer.protect_from_melee())
        
        player.prayers_coll = pc


class CampPrayer(PrayerRoutine):

    def routine(self, player: Player, prayer_collection: PrayerCollection):
        """_summary_

        Args:
            player (Player): A Player.
            prayer_collection (PrayerCollection): A complete PrayerCollection, including protect prayer & boosts.
        """
        if player.prayers_coll.prayers != prayer_collection.prayers:
            player.prayers_coll = prayer_collection


def prayer_routine_comparison(scale: int, trials: int):
    olm = OlmHead.from_de0(scale)
    piety = Prayer.piety()
    augury = Prayer.augury()

    prot_ranged = Prayer.protect_from_missiles()
    prot_magic = Prayer.protect_from_magic()

    olm_ranged = olm.styles_coll.get_style(Style.ranged)
    olm_magic = olm.styles_coll.get_style(Style.magic)


    def switch_to_last(player: Player, last_auto: NpcStyle, boost_prayer: Prayer):
        if last_auto == olm.styles_coll.get_style(Style.ranged):
            player.prayers_coll.reset_prayers()
            player.pray(boost_prayer, prot_ranged)
        elif last_auto == olm.styles_coll.get_style(Style.magic):
            player.prayers_coll.reset_prayers()
            player.prayers_coll.pray(boost_prayer, prot_magic)
        else:
            raise NotImplementedError(f'{last_auto}')

    def camp_prot_magic(player: Player, last_auto: NpcStyle, boost_prayer: Prayer):
        if prot_magic in player.prayers_coll:
            pass
        else:
            player.prayers_coll.reset_prayers()
            player.pray(boost_prayer, prot_magic)

    def camp_prot_ranged(player: Player, last_auto: NpcStyle, boost_prayer: Prayer):
        if prot_ranged in player.prayers_coll:
            pass
        else:
            player.prayers_coll.reset_prayers()
            player.pray(boost_prayer, prot_ranged)

    # lads
    lads = (melee_lad, blood_fury_lad, magic_lad) = [Player(name=lad) for lad in ('melee lad', 'blood fury lad', 'magic lad')]

    # equipment
    melee_lad.equipment.equip_basic_melee_gear()
    melee_lad.equipment.equip_torva_set()
    melee_lad.active_style = melee_lad.equipment.equip_scythe()
    
    blood_fury_lad.equipment.equip_basic_melee_gear(torture=False)
    blood_fury_lad.equipment.equip_fury(blood=True)
    blood_fury_lad.equipment.equip_torva_set()
    blood_fury_lad.active_style = blood_fury_lad.equipment.equip_scythe()

    magic_lad.equipment.equip_basic_magic_gear()
    magic_lad.active_style = magic_lad.equipment.equip_sang()

    # boosts & checks
    for lad in lads:
        lad.boost(Overload.overload())
        assert lad.equipment.full_set

    
    melee_prayer_routines = (switch_to_last, camp_prot_magic)
    magic_prayer_routines = (switch_to_last, camp_prot_ranged)
    routine_switch_idx = 0
    routine_camp_idx = 1

    data = np.empty(shape=(len(lads), len(melee_prayer_routines), trials), dtype=int)
    melee_lad_idx, blood_fury_lad_idx, magic_lad_idx = range(len(lads))

    for routine_idx, (melee_routine, magic_routine) in enumerate(zip(melee_prayer_routines, magic_prayer_routines, strict=True)):
        # initial values, any leading influence should disappear with sufficiently large trial size
        for lad in lads:
            lad.prayers_coll.reset_prayers()
        
        melee_lad.pray(prot_magic, piety)
        blood_fury_lad.pray(prot_magic, piety)
        magic_lad.pray(prot_ranged, augury)

        olm.active_style = olm_ranged

        for trial_idx in range(trials):
            last_auto = olm.active_style

            if random.random() < olm.chance_to_switch_style():
                if last_auto == olm_ranged:
                    olm.active_style = olm_magic
                elif last_auto == olm_magic:
                    olm.active_style = olm_ranged
                else:
                    raise NotImplementedError(f'{last_auto}')

            melee_dam = olm.damage_distribution(melee_lad)
            blood_fury_dam = olm.damage_distribution(blood_fury_lad)
            magic_dam = olm.damage_distribution(magic_lad)

            data[:, routine_idx, trial_idx] = [
                melee_dam.random()[0],
                blood_fury_dam.random()[0],
                magic_dam.random()[0]
            ]

            melee_routine(melee_lad, olm.active_style, piety)
            melee_routine(blood_fury_lad, olm.active_style, piety)
            magic_routine(magic_lad, olm.active_style, augury)
    
    melee_lad_mean_damage_switch = data[melee_lad_idx, routine_switch_idx, :].mean()
    melee_lad_mean_damage_camp = data[melee_lad_idx, routine_camp_idx, :].mean()

    blood_fury_lad_mean_damage_switch = data[blood_fury_lad_idx, routine_switch_idx, :].mean()
    blood_fury_lad_mean_damage_camp = data[blood_fury_lad_idx, routine_camp_idx, :].mean()

    magic_lad_mean_damage_switch = data[magic_lad_idx, routine_switch_idx, :].mean()
    magic_lad_mean_damage_camp = data[magic_lad_idx, routine_camp_idx, :].mean()

    table_data = [
        [melee_lad_mean_damage_switch, melee_lad_mean_damage_camp],
        [blood_fury_lad_mean_damage_switch, blood_fury_lad_mean_damage_camp],
        [magic_lad_mean_damage_switch, magic_lad_mean_damage_camp]
    ]

    col_labels = ['lad', 'switch prayer', 'camp prayer']
    row_labels = [p.name for p in lads]
    meta_header = 'Prayer routine mean damage expected'

    print(tabulate_enhanced(table_data, col_labels, row_labels, meta_header))
    # print(f'{melee_lad_mean_damage_switch}, {melee_lad_mean_damage_camp}, {magic_lad_mean_damage_switch}, {magic_lad_mean_damage_camp}')

    return np.asarray(table_data), col_labels, row_labels, meta_header

if __name__ == '__main__':
    # shaun_vs_normie()
    scales = np.arange(15, 52, 4)
    my_trials = int(1e4)

    m = 6   # unique lads * unique routines
    n = scales.size

    scale_data = np.empty(shape=(m, n), dtype=float)
    
    for scale_idx, scale in enumerate(scales):
        data, col_labels, row_labels, meta_header = prayer_routine_comparison(scale, my_trials)
        scale_data[:, scale_idx] = data.reshape((m, ))
    
    melee_lad_switch = scale_data[0, :]
    melee_lad_camp = scale_data[1, :]

    bfury_lad_switch = scale_data[2, :]
    bfury_lad_camp = scale_data[3, :]

    magic_lad_switch = scale_data[4, :]
    magic_lad_camp = scale_data[5, :]

    fig, ax = plt.subplots()

    ax.set_xlabel('party size')
    ax.set_ylabel('expected damage per hit')
    ax.set_title('Expected damage per hit vs party size for different prayer routines')

    ax.plot(scales, melee_lad_switch)
    ax.plot(scales, melee_lad_camp)
    ax.plot(scales, bfury_lad_switch)
    ax.plot(scales, bfury_lad_camp)
    ax.plot(scales, magic_lad_switch)
    ax.plot(scales, magic_lad_camp)
    ax.text(100, 100, f'{my_trials=}')

    ax.legend(['melee (switch)', 'melee (camp)', 'melee [blood fury] (switch)', 'melee [blood fury] (camp)', 'mage (switch)', 'mage (camp)'])

    fig.savefig(ax.get_title() + '.png')
    fig.show()
