from unittest import TestCase
from src.osrs_tools.character import *
from src.osrs_tools.equipment import *
from src.osrs_tools.stats import *

Torva = Player(name='torva')
Torva.equipment = EquipmentLoadout()
Torva.equipment.equip_basic_melee_gear()
Torva.equipment.equip_torva_set()
Torva.active_style = Torva.equipment.equip_scythe()


class TestPlayer(TestCase):
	def test_reset_stats(self):
		player = Player('name')
		player.boost(Boost.super_combat_potion())
		self.assertEqual(player.active_levels.strength, 118)
		player.reset_stats()
		self.assertEqual(player.active_levels.strength, 99)

	def test_apply_boost_effect(self):
		player = Player('name')
		player.boost(Boost.imbued_heart())
		self.assertEqual(player.active_levels.magic, 109)
		player.boost(*(Boost.imbued_heart(),) * 2)
		self.assertEqual(player.active_levels.magic, 109)

	def test_defence_floor(self):
		self.fail()

	def test_effective_attack_level(self):
		Torva.reset_stats()
		Torva.prayers.reset_prayers()
		Torva.boost(Overload.overload())
		Torva.prayers.pray(Prayer.piety())
		self.assertEqual(Torva.effective_attack_level, 152)

	def test_effective_melee_strength_level(self):
		self.fail()

	def test_effective_defence_level(self):
		self.fail()

	def test_effective_ranged_attack_level(self):
		self.fail()

	def test_effective_ranged_strength_level(self):
		self.fail()

	def test_effective_magic_level(self):
		self.fail()

	def test_effective_magic_defence_level(self):
		self.fail()

	def test__twisted_bow_modifier(self):
		self.fail()

	def test__dharok_damage_modifier(self):
		self.fail()

	def test__leafy_modifier(self):
		self.fail()

	def test__crystal_armor_modifier(self):
		self.fail()

	def test_attack_roll(self):
		self.fail()

	def test_defence_roll(self):
		self.fail()

	def test_max_hit(self):
		self.fail()

	def test_attack_speed(self):
		self.fail()

	def test_damage_distribution(self):
		self.fail()

	def test_twisted_bow(self, party_size: int = 5):
		ArmaLad = Player(name='tbow lad')
		VoidLad = Player(name='void lad')
		lads = [ArmaLad, VoidLad]

		for lad in lads:
			lad.equipment.equip_basic_ranged_gear()
			lad.active_style = lad.equipment.equip_twisted_bow()
			lad.prayers.pray(Prayer.rigour())
			lad.boost(Overload.overload())

		ArmaLad.equipment.equip_arma_set(zaryte=True)
		VoidLad.equipment.equip_void_set(elite=True)

		olm = OlmHead.from_de0(party_size)
		self.assertEqual(ArmaLad.damage_distribution(olm).max_hit, 85)
		self.assertEqual(VoidLad.damage_distribution(olm).max_hit, 95)

		mom = CoxMonster.from_de0('muttadile (big)', party_size)
		self.assertEqual(ArmaLad.damage_distribution(mom).max_hit, 85)
		self.assertEqual(VoidLad.damage_distribution(mom).max_hit, 95)

		for lad in lads:
			lad.equipment.equip_salve()

		mystic = SkeletalMystic.from_de0(party_size)
		void_dam = VoidLad.damage_distribution(mystic)

		self.assertEqual(ArmaLad.damage_distribution(mystic).max_hit, 74)
		self.assertEqual(VoidLad.damage_distribution(mystic).max_hit, 83)
		self.assertLess(VoidLad.damage_distribution(mystic).per_second, ArmaLad.damage_distribution(mystic).per_second)


	def test_tbow_mystic_interaction(self, party_size: int = 5):
		ArmaLad = Player(name='tbow lad')
		VoidLad = Player(name='void lad')
		lads = [ArmaLad, VoidLad]

		for lad in lads:
			lad.equipment.equip_basic_ranged_gear()
			lad.equipment.equip_salve()
			lad.active_style = lad.equipment.equip_twisted_bow()
			lad.prayers.pray(Prayer.rigour())
			lad.boost(Overload.overload())

		ArmaLad.equipment.equip_arma_set(zaryte=True)
		VoidLad.equipment.equip_void_set(elite=True)

		mystic = SkeletalMystic.from_de0(party_size)
		void_dam = VoidLad.damage_distribution(mystic)
		arma_dam = ArmaLad.damage_distribution(mystic)

		self.assertEqual(ArmaLad.damage_distribution(mystic).max_hit, 74)
		self.assertEqual(VoidLad.damage_distribution(mystic).max_hit, 79)
		self.assertLess(VoidLad.damage_distribution(mystic).per_second, ArmaLad.damage_distribution(mystic).per_second)









class TestMonster(TestCase):
	def test_reset_stats(self):
		self.fail()

	def test_attack_roll(self):
		self.fail()

	def test_defence_roll(self):
		self.fail()

	def test_from_bb(self):
		self.fail()


class TestCoxMonster(TestCase):
	def test_player_hp_scaling_factor(self):
		self.fail()

	def test_player_offensive_defensive_scaling_factor(self):
		self.fail()

	def test_party_hp_scaling_factor(self):
		self.fail()

	def test_party_offensive_scaling_factor(self):
		self.fail()

	def test_party_defensive_scaling_factor(self):
		self.fail()

	def test_challenge_mode_hp_scaling_factor(self):
		self.fail()

	def test_challenge_mode_offensive_scaling_factor(self):
		self.fail()

	def test_challenge_mode_defensive_scaling_factor(self):
		self.fail()

	def test_get_base_levels_and_stats(self):
		self.fail()

	def test_from_bb(self):
		self.fail()

	def test_from_de0(self):
		self.fail()

	def test__convert_cox_combat_levels(self):
		self.fail()


class TestIceDemon(TestCase):
	def test_effective_magic_defence_level(self):
		self.fail()

	def test_from_de0(self):
		self.fail()


class TestOlmHead(TestCase):
	def test_from_de0(self):
		self.fail()


class TestOlmMeleeHand(TestCase):
	def test_from_de0(self):
		self.fail()

	def test_cripple(self):
		self.fail()


class TestOlmMageHand(TestCase):
	def test_from_de0(self):
		olm = OlmMageHand.from_de0(15)
		self.assertEqual(olm.levels.hitpoints, 3900)
		self.assertEqual(olm.levels.magic, 117)
		self.assertEqual(olm.levels.defence, 196)


class TestGuardian(TestCase):
	def test_from_de0(self):
		for scale in range(7, 55, 8):
			guardian = Guardian.from_de0(scale, party_average_mining_level=30)


class TestSkeletalMystic(TestCase):
	def test_from_de0(self):
		myst = SkeletalMystic.from_de0(15)
		self.assertEqual(myst.levels.hitpoints, 1280)

		myst = SkeletalMystic.from_de0(23)
		self.assertEqual(myst.levels.magic, 210)

		myst = SkeletalMystic.from_de0(31)
		self.assertEqual(myst.levels.defence, 235)

		myst = SkeletalMystic.from_de0(100)
		self.assertEqual(myst.levels.hitpoints, 8160)
