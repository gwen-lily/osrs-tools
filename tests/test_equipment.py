from unittest import TestCase

from osrs_tools.equipment import *
from osrs_tools.stats import *


class TestGear(TestCase):
	def test_from_bb(self):
		tassets = Gear.from_bb('bandos tassets')
		self.assertEqual(tassets.prayer_bonus, 1)
		self.assertEqual(tassets.aggressive_bonus.melee_strength, 2)

	def test_from_osrsbox(self):
		self.fail()


class TestWeapon(TestCase):
	def test_choose_style_by_name(self):
		self.fail()

	def test_empty_slot(self):
		self.fail()

	def test_from_bb(self):
		scythe = Weapon.from_bb('scythe of vitur')

		self.assertEqual(scythe.aggressive_bonus.slash, 110)
		self.assertEqual(scythe.aggressive_bonus.melee_strength, 75)

		scythe.choose_style_by_name(PlayerStyle.chop)
		self.assertEqual(scythe.level_requirements.strength, 75)
		scythe.choose_style_by_name(PlayerStyle.jab)


class TestSpecialWeapon(TestCase):
	def test_from_bb(self):
		dwh = SpecialWeapon.from_bb('dragon warhammer')

		self.assertEqual(dwh.aggressive_bonus.crush, 95)
		dwh.choose_style_by_name(PlayerStyle.pound)

	def test_empty_slot(self):
		self.fail()


Torva = Equipment()
Torva.equip_basic_melee_gear()
Torva.equip_torva_set()
Torva.equip_scythe()


class TestEquipment(TestCase):
	def test_aggressive_bonus(self):
		self.assertEqual(Torva.aggressive_bonus.slash, 147)

	def test_defensive_bonus(self):
		self.fail()

	def test_prayer_bonus(self):
		self.fail()

	def test_combat_requirements(self):
		self.fail()

	def test_equip(self):
		self.fail()

	def test_unequip(self):
		self.fail()

	def test_wearing(self):
		self.assertTrue(Torva.torva_set)

	def test_normal_void_set(self):
		void = Equipment()
		void.equip_void_set(elite=False)
		self.assertTrue(void.normal_void_set)
		self.assertFalse(void.elite_void_set)

	def test_elite_void_set(self):
		void = Equipment()
		void.equip_void_set(elite=True)
		self.assertTrue(void.elite_void_set)
		self.assertFalse(void.normal_void_set)

	def test_dharok_set(self):
		self.fail()

	def test_bandos_set(self):
		self.fail()

	def test_inquisitor_set(self):
		self.fail()

	def test_torva_set(self):
		self.fail()

	def test_justiciar_set(self):
		self.fail()

	def test_obsidian_armor_set(self):
		self.fail()

	def test_obsidian_weapon(self):
		self.fail()

	def test_leafy_weapon(self):
		self.fail()

	def test_keris(self):
		self.fail()

	def test_crystal_armor_set(self):
		self.fail()

	def test_crystal_weapon(self):
		self.fail()

	def test_smoke_staff(self):
		self.fail()

	def test_graceful_set(self):
		self.fail()

	def test_zaryte_crossbow(self):
		self.fail()

	def test_scythe_of_vitur(self):
		self.fail()

	def test_enchanted_ruby_bolts(self):
		self.fail()

	def test_enchanted_diamond_bolts(self):
		self.fail()

	def test_brimstone_ring(self):
		self.fail()

	def test_tome_of_fire(self):
		self.fail()

	def test_tome_of_water(self):
		self.fail()

	def test_no_equipment(self):
		self.fail()



class TestEquipmentLoadout(TestCase):
	def test_equip_basic_melee_gear(self):
		lad_eqp = Equipment()
		lad_eqp.equip_basic_melee_gear(ferocious=False)
		self.assertFalse(lad_eqp.wearing(hands=Gear.from_bb('ferocious gloves')))

	def test_equip_basic_ranged_gear(self):
		self.fail()

	def test_equip_basic_magic_gear(self):
		self.fail()

	def test_equip_bandos_set(self):
		self.fail()

	def test_equip_inquisitor_set(self):
		self.fail()

	def test_equip_torva_set(self):
		self.fail()

	def test_equip_dwh(self):
		self.fail()

	def test_equip_scythe(self):
		self.fail()

	def test_equip_arclight(self):
		self.fail()

	def test_equip_arma_set(self):
		self.fail()

	def test_equip_void_set(self):
		self.fail()

	def test_equip_crystal_set(self):
		self.fail()

	def test_equip_twisted_bow(self):
		self.fail()

	def test_equip_blowpipe(self):
		self.fail()

	def test_equip_black_chins(self):
		self.fail()

	def test_equip_zaryte_crossbow(self):
		self.fail()

	def test_equip_crystal_bowfa(self):
		self.fail()

	def test_equip_ancestral_set(self):
		self.fail()

	def test_equip_sang(self):
		self.fail()

	def test_equip_harm(self):
		self.fail()
