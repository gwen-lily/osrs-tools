from unittest import TestCase

from src.osrs_tools.prayer import *

piety = Prayer.piety()
rigour = Prayer.rigour()
augury = Prayer.augury()
chivalry = Prayer.chivalry()
eagle_eye = Prayer.eagle_eye()
mystic_might = Prayer.mystic_might()


class TestPrayer(TestCase):

	def test_from_osrsbox(self):
		pass

	def test_piety(self):
		self.assertIsInstance(piety, Prayer)
		self.assertEqual(piety.attack, 1.2)
		self.assertEqual(piety.strength, 1.23)
		self.assertEqual(piety.defence, 1.25)

	def test_rigour(self):
		self.assertIsInstance(rigour, Prayer)
		self.assertEqual(rigour.ranged_attack, 1.2)
		self.assertEqual(rigour.ranged_strength, 1.23)
		self.assertEqual(rigour.defence, 1.25)

	def test_augury(self):
		self.assertIsInstance(augury, Prayer)
		self.assertEqual(augury.magic_attack, 1.25)
		self.assertEqual(augury.defence, 1.25)
		self.assertEqual(augury.magic_defence, 1.25)

	def test_attack(self):
		self.assertEqual(piety.attack, 1.2)
		self.assertEqual(chivalry.attack, 1.15)

	def test_strength(self):
		self.assertEqual(piety.strength, 1.23)
		self.assertEqual(chivalry.strength, 1.18)

	def test_defence(self):
		self.assertEqual(piety.defence, 1.25)
		self.assertEqual(chivalry.defence, 1.20)

	def test_ranged_attack(self):
		self.assertEqual(rigour.ranged_attack, 1.20)
		self.assertEqual(eagle_eye.ranged_attack, 1.15)

	def test_ranged_strength(self):
		self.assertEqual(rigour.ranged_strength, 1.23)
		self.assertEqual(eagle_eye.ranged_strength, 1)

	def test_magic_attack(self):
		self.assertEqual(augury.magic_attack, 1.25)
		self.assertEqual(mystic_might.magic_attack, 1.15)

	def test_magic_strength(self):
		self.assertEqual(augury.magic_strength, 1)
		self.assertEqual(mystic_might.magic_strength, 1)

	def test_magic_defence(self):
		self.assertEqual(augury.magic_defence, 1.25)
		self.assertEqual(mystic_might.magic_defence, 1)


class TestPrayerCollection(TestCase):

	def test_drain_effect(self):
		pass

	def test_no_prayers(self):
		no_prayers = PrayerCollection.no_prayers()
		self.assertIsInstance(no_prayers, PrayerCollection)

	def test_attack(self):
		PC = PrayerCollection(name='piety', prayers=(piety, ))
		self.assertEqual(PC.attack, piety.attack)

