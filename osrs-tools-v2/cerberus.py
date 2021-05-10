# osrs-tools-v2\cerberus.py
from main import *


def iron_comparison():
	player = Player.from_highscores(
		rsn='SirNargeth',
		equipment=Equipment(
			SpecialWeapon.from_bitterkoekje_bedevere('arclight'),
			Gear.from_bitterkoekje_bedevere('slayer helmet (i)'),
			Gear.from_bitterkoekje_bedevere('fire cape'),
			Gear.from_bitterkoekje_bedevere('amulet of fury'),
			Gear.from_bitterkoekje_bedevere('fighter torso'),
			Gear.from_bitterkoekje_bedevere('proselyte cuisse'),
			Gear.from_bitterkoekje_bedevere('dragon defender'),
			Gear.from_bitterkoekje_bedevere('barrows gloves'),
			Gear.from_bitterkoekje_bedevere('dragon boots'),
			Gear.from_bitterkoekje_bedevere('berserker (i)')
		)
	)

	player.weapon.choose_style_by_name(PlayerStyle.slash)
	player.pray(PlayerStats.StatPrayer.piety())
	player.super_combat_potion()

	monster = Monster.from_bitterkoekje('cerberus')
	player.weapon.choose_style_by_name(PlayerStyle.lunge)
	mc_nospec = attack_absorbing_markov_chain(player, monster)
	print('arclight (normal)', mc_nospec.expected_steps[0][0])

	# arclight spec
	player.weapon.choose_style_by_name(PlayerStyle.slash)
	mc_spec = attack_absorbing_markov_chain(player, monster, special_attack=True)
	cerb_health_states = mc_spec.transition_matrix[0, :]

	mean_hp = mc_spec.mean_state(cerb_health_states)
	mean_damage_dealt = math.floor(monster.stats.combat.hitpoints - mean_hp)
	monster.arclight_reduce()
	monster.damage(mean_damage_dealt)
	player.weapon.choose_style_by_name(PlayerStyle.lunge)
	mc_post_spec = attack_absorbing_markov_chain(player, monster)
	print(mean_hp)
	print('arclight (spec) + arclight', 1 + mc_post_spec.expected_steps[mean_damage_dealt, 0])

	monster = Monster.from_bitterkoekje('cerberus')
	player.equipment.equip(SpecialWeapon.from_bitterkoekje_bedevere('dragon dagger'))
	player.weapon.choose_style_by_name(PlayerStyle.lunge)
	mc_dds = attack_absorbing_markov_chain(player, monster, special_attack=True)
	cerb_starting_state = np.zeros(mc_dds.states.size)
	cerb_starting_state[0] = 1
	cerb_health_states = mc_dds.probability_distribution(cerb_starting_state, 2)
	mean_hp = np.dot(cerb_health_states, mc_dds.states)
	mean_damage_dealt = math.floor(monster.stats.combat.hitpoints - mean_hp)
	monster.damage(mean_damage_dealt)
	player.equipment.equip(SpecialWeapon.from_bitterkoekje_bedevere('arclight'))
	player.weapon.choose_style_by_name(PlayerStyle.lunge)
	mc_post_spec = attack_absorbing_markov_chain(player, monster)
	print(mean_hp)
	print('2 x dds + arclight', 2 + mc_post_spec.expected_steps[mean_damage_dealt, 0])







if __name__ == '__main__':
	iron_comparison()
