from osrs_tools.character import *
from osrs_tools import analysis_tools
from osrs_tools.analysis_tools import ComparisonMode, DataMode

from tabulate import tabulate

def mutta_tank_mean_hit(**kwargs):
	# baby = SmallMuttadile.from_de0(31)
	momma = BigMuttadile.from_de0(31)


	dinhs_tank = Player(name='dinhs lad')
	ely_tank = Player(name='ely lad')

	lads = [dinhs_tank, ely_tank]

	for lad in lads:
		lad.boost(Overload.overload())
		lad.equipment.equip_justi_set()
		lad.equipment.equip(
			fury,
			hp_cape,
			bgloves,
			gboots,
			suffering,
		)

	dinhs_tank.active_style = dinhs_tank.equipment.equip_dinhs()
	dinhs_tank.prayers.pray(Prayer.augury(), Prayer.protect_from_melee())

	ely_tank.active_style = ely_tank.equipment.equip_sotd(style=BladedStaffStyles.styles[-1])
	ely_tank.equipment.equip(Gear.from_bb('elysian spirit shield'))
	ely_tank.prayers.pray(Prayer.augury(), Prayer.protect_from_missiles())
	ely_tank.staff_of_the_dead_effect = True

	# baby_dinh = baby.damage_distribution(dinhs_tank)

	momma.active_style = momma.styles.get_style(Style.crush)
	momma_dinh_melee = momma.damage_distribution(dinhs_tank)

	momma.active_style = momma.styles.get_style(Style.ranged)
	momma_dinh_ranged = momma.damage_distribution(dinhs_tank)
	momma_ely_ranged = momma.damage_distribution(ely_tank)

	# baby_ely = baby.damage_distribution(ely_tank)
	# momma_ely = momma.damage_distribution(ely_tank)

	print(*(dam.max_hit for dam in (momma_dinh_melee, momma_dinh_ranged, momma_ely_ranged)))


def momma_kill_ticks(**kwargs):
	momma = BigMuttadile.from_de0(31)
	lad = Player(name='lad')
	lad.equipment.equip_basic_ranged_gear()
	lad.equipment.equip_arma_set(zaryte=True)
	lad.active_style = lad.equipment.equip_twisted_bow()
	lad.boost(Overload.overload())
	lad.prayers.pray(Prayer.rigour())

	dam = lad.damage_distribution(momma)
	print(f'{dam.per_tick=}, {momma.levels.hitpoints=}, {momma.levels.hitpoints / dam.per_tick}')




def portal_kill_time(**kwargs):
	options = {
		'floatfmt': '.0f',
		'datamode': DataMode.TICKS_TO_KILL,
		'scales': range(15, 32, 8),
	}

	lad = Player(name='portal lad')
	lad.boost(Overload.overload())
	lad.prayers.pray(Prayer.rigour())

	lad.equipment.equip_basic_ranged_gear()
	lad.equipment.equip_arma_set(zaryte=True)
	lad.active_style = lad.equipment.equip_twisted_bow()

	portals = [CoxMonster.from_de0('abyssal portal', ps) for ps in options['scales']]

	for portal in portals:
		portal.apply_vulnerability()

	indices, axes, data_ary = analysis_tools.generic_comparison_better(
		lad,
		target=portals,
		comparison_mode=ComparisonMode.CARTESIAN,
		data_mode=options['datamode'],
	)

	player_by_portals = data_ary[:, 0, 0, 0, 0, 0, :]
	col_labels = [options['datamode'].name] + portals
	row_labels = [lad.name]
	print(analysis_tools.tabulate_wrapper(player_by_portals, col_labels, row_labels, **options))


if __name__ == '__main__':
	fury = Gear.from_osrsbox('amulet of fury')
	hp_cape = Gear.from_bb('skill cape (t)')
	bgloves = Gear.from_osrsbox('barrows gloves')
	gboots = Gear.from_osrsbox('guardian boots')
	suffering = Gear.from_osrsbox('ring of suffering (i)')


	# portal_kill_time()
	mutta_tank_mean_hit()
	momma_kill_ticks()
