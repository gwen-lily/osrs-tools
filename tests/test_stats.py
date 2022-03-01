from unittest import TestCase
from copy import copy

from osrs_tools.equipment import *
from osrs_tools.stats import *

PlayerA = PlayerLevels(*(99,) * 23)
PlayerB = PlayerLevels(*(1,) * 23)
PlayerC = PlayerLevels(*range(30, 52 + 1))
PlayerD = PlayerLevels(*range(31, 53 + 1))
PlayerE = PlayerLevels(*range(98, 76 - 1, -1))
TheFiveLads = (PlayerA, PlayerB, PlayerC, PlayerD, PlayerE,)

PlayerX = PlayerLevels(attack=20, agility=69, slayer=99)
PlayerY = PlayerLevels(strength=30, mining=61)
PlayerXY = PlayerLevels(attack=20, strength=30, agility=69, slayer=99, mining=61)

maxed_rsn = 'lynx titan'


class TestPlayerLevels(TestCase):

	def test_to_unbounded(self):
		PlayerBUnbounded = PlayerB.to_unbounded()
		PlayerBRebounded = PlayerBUnbounded.to_bounded()
		self.assertEqual(PlayerBUnbounded, PlayerLevelsUnbounded(*(1,) * 23))
		self.assertEqual(PlayerBRebounded, PlayerB)

	def test_maxed_player(self):
		self.assertEqual(PlayerA, PlayerLevels.maxed_player())

	def test_from_rsn(self):
		self.assertEqual(PlayerA, PlayerLevels.from_rsn(maxed_rsn))

	def test_no_requirements(self):
		self.assertEqual(PlayerLevels.no_requirements(), PlayerB)

	def test_add(self):
		self.assertEqual(PlayerC + PlayerB, PlayerD)
		self.assertEqual(PlayerB + PlayerC, PlayerD)

		self.assertEqual(PlayerA + Boost.super_attack_potion(), PlayerLevelsUnbounded(118, *(99,) * 22))
		self.assertEqual(PlayerA + Boost.super_strength_potion(), PlayerLevelsUnbounded(99, 118, *(99,) * 21))
		self.assertEqual(PlayerA + Boost.super_defence_potion(), PlayerLevelsUnbounded(99, 99, 118, *(99,) * 20))

	def test_sub(self):
		self.assertEqual(PlayerD - PlayerB, PlayerC)
		self.assertEqual(PlayerD - PlayerC, PlayerB)

	def test_mul(self):
		self.assertEqual(PlayerA, PlayerA * PlayerB)
		self.assertEqual(PlayerB * PlayerY, PlayerY)
		self.assertEqual((PlayerB * PlayerX) * PlayerA, PlayerA)

		self.assertEqual(PlayerC * PlayerD, PlayerD)

	def test_copy(self):
		for P in TheFiveLads:
			self.assertEqual(P, copy(P))

	def test_le(self):
		for P in TheFiveLads:
			self.assertLessEqual(PlayerB, P)

		self.assertLessEqual(PlayerC, PlayerD)
		self.assertLessEqual(PlayerC, PlayerE)

	def test_ge(self):
		for P in TheFiveLads:
			self.assertGreaterEqual(PlayerA, P)

		self.assertGreaterEqual(PlayerD, PlayerC)
		self.assertGreaterEqual(PlayerE, PlayerB)


class TestPlayerLevelsUnbounded(TestCase):

	def test_to_bounded(self):
		self.assertEqual(PlayerA, PlayerLevelsUnbounded(*(99,) * 23).to_bounded())


class TestBoost(TestCase):
	def test_super_combat_potion(self):
		C_scb = PlayerC + Boost.super_combat_potion()
		C_individual = PlayerC + Boost.super_attack_potion() + Boost.super_strength_potion() + Boost.super_defence_potion()
		self.assertEqual(C_scb, C_individual)

	def test_bastion_potion(self):
		D_bastion = PlayerD + Boost.bastion_potion()
		D_individual = PlayerD + Boost.ranging_potion() + Boost.super_defence_potion()
		self.assertEqual(D_bastion, D_individual)

	def test_battlemage_potion(self):
		E_battlemage = PlayerE + Boost.battlemage_potion()
		E_individual = PlayerE + Boost.magic_potion() + Boost.super_defence_potion()
		self.assertEqual(E_battlemage, E_individual)

	def test_imbued_heart(self):
		self.assertEqual(PlayerA + Boost.imbued_heart(), PlayerLevelsUnbounded(*(99,)*5, 109, *(99,)*17))

	def test_prayer_potion(self):
		self.fail()

	def test_super_restore(self):
		self.fail()

	def test_sanfew_serum(self):
		self.fail()

	def test_saradomin_brew(self):
		self.fail()

	def test_zamorak_brew(self):
		self.fail()

	def test_ancient_brew(self):
		self.fail()

	def test_super_attack_potion(self):
		self.fail()

	def test_super_strength_potion(self):
		self.fail()

	def test_super_defence_potion(self):
		self.fail()

	def test_ranging_potion(self):
		self.fail()

	def test_magic_potion(self):
		self.fail()

	def test_combat_potion(self):
		self.fail()

	def test_attack_potion(self):
		self.fail()

	def test_strength_potion(self):
		self.fail()

	def test_defence_potion(self):
		self.fail()


class TestMonsterCombatLevels(TestCase):
	def test_from_bb(self):
		self.fail()


class TestStyleStats(TestCase):
	def test_no_style_bonus(self):
		self.fail()

	def test_npc_style_bonus(self):
		self.fail()


class TestAggressiveStats(TestCase):
	def test_no_bonus(self):
		self.assertEqual(AggressiveStats(), AggressiveStats.no_bonus())

	def test_from_bb(self):
		bandos_tassets = Gear.from_bb('bandos tassets')
		self.assertEqual(bandos_tassets, AggressiveStats(0, 0, 0, -21, -7, 2, 0, 0))



class TestDefensiveStats(TestCase):
	def test_no_bonus(self):
		self.assertEqual(DefensiveStats(), DefensiveStats.no_bonus())

	def test_from_bb(self):
		bandos_tassets = Gear.from_bb('bandos tassets')
		self.assertEqual(bandos_tassets, DefensiveStats(71, 63, 66, -4, 93))
