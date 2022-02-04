import unittest

test_rsn = 'microhybrid'


class StatTest(unittest.TestCase):
	def test_stats(self):

		combat_a = StatsDeprecated.Combat(10, 20, 30, 40, 50, 60)
		combat_b = StatsDeprecated.Combat(5, 10, 15, 20, 25, 30)
		combat_c = StatsDeprecated.Combat(15, 30, 45, 60, 75, 90)

		combat_add = combat_a + combat_b
		combat_sum = sum([combat_a, combat_b])
		combat_sub = combat_a - combat_b

		self.assertEqual(combat_add, combat_sum)
		self.assertEqual(combat_add, combat_c)
		self.assertEqual(combat_sub, combat_b)

		combat_micro = PlayerStatsDeprecated.Combat.from_highscores(test_rsn)
		combat_maxed = PlayerStatsDeprecated.Combat.maxed_combat()
		self.assertEqual(combat_micro, combat_maxed)

		piety = PlayerStatsDeprecated.StatPrayer.piety()
		self.assertEqual(piety.attack, 1.2)
		self.assertEqual(piety.strength, 1.23)

		rigour = PlayerStatsDeprecated.StatPrayer.rigour()
		self.assertEqual(rigour.ranged_attack, 1.2)
		self.assertEqual(rigour.ranged_strength, 1.23)

		augury = PlayerStatsDeprecated.StatPrayer.augury()
		self.assertEqual(augury.magic_attack, 1.25)
		self.assertEqual(augury.magic_defence, 1.25)
		self.assertEqual(augury.magic_strength, 1)
		self.assertEqual(augury.defence, 1.25)

		cerb_stats = MonsterStatsDeprecated.from_bitterkoekje('cerberus')
		cerb_combat_manual = MonsterStatsDeprecated.Combat(600, 220, 220, 100, 220, 220)
		self.assertEqual(cerb_stats.combat, cerb_combat_manual)
		cerb_cc = cerb_stats.current_combat
		cerb_cc.reduce_defence_ratio(0.70)
		self.assertEqual(cerb_cc.defence, 70)
		cerb_cc.reduce_defence_flat(25)
		self.assertEqual(cerb_cc.defence, 45)
		cerb_cc = MonsterStatsDeprecated.CurrentCombat.from_combat(cerb_stats.combat)
		self.assertEqual(cerb_cc.defence, 100)

		myst_stats = MonsterStatsDeprecated.from_de0('skeletal mystic')
		print(myst_stats)
		myst_combat_manual = MonsterStatsDeprecated.Combat(160, 140, 140, 187, 140, 1)
		self.assertEqual(myst_stats.combat, myst_combat_manual)

		olm_mel_stats = MonsterStatsDeprecated.from_de0('great olm (left/melee claw)')
		olm_mel_combat_manual = MonsterStatsDeprecated.Combat(600, 250, 250, 175, 175, 250)
		self.assertEqual(olm_mel_stats.combat, olm_mel_combat_manual)


class StyleTest(unittest.TestCase):
	def test_style(self):
		pass


class PotionTest(unittest.TestCase):
	def test_pots(self):
		p = Player.max_scythe_bandos()
		p.overload()
		self.assertEqual(p.stats.potion_modifiers.magic, 21)
		p.tick_down_potion_modifiers(1)
		self.assertEqual(p.stats.potion_modifiers.strength, 20)
		p.tick_down_potion_modifiers(2)
		self.assertEqual(p.stats.potion_modifiers.ranged, 18)


class IronGearTest(unittest.TestCase):
	def test_cerb(self):
		nargeth = Player.from_highscores(
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
		nargeth.equipment.weapon.choose_style_by_name(PlayerStyle.slash)
		self.assertEqual(nargeth.equipment.aggressive_bonus().slash, 85)
		self.assertEqual(nargeth.equipment.aggressive_bonus().melee_strength, 54)
		nargeth.equipment.weapon.choose_style_by_name(PlayerStyle.lunge)
		self.assertEqual(nargeth.equipment.aggressive_bonus().stab, 58)
		self.assertEqual(nargeth.equipment.aggressive_bonus().melee_strength, 54)

		cerb = Monster.from_bitterkoekje('cerberus')
		self.assertEqual(cerb.stats.defensive.slash, 100)
		self.assertEqual(cerb.stats.combat.hitpoints, 600)

class MagicTest(unittest.TestCase):
	def test_sang(self):
		mage = Player.max_sang_brimstone()
		self.assertEqual(mage.equipment.aggressive_bonus().magic, 165)
		# _tolerance self.assertEqual(mage.equipment.aggressive_bonus().magic_strength, 0.23)
		mage_hand = OlmMageHand(39, False)
		self.assertEqual(mage_hand.stats.combat.hitpoints, 8400)
		self.assertEqual(mage_hand.stats.combat.magic, 156)

		dam = mage.damage_against_monster(mage_hand)




if __name__ == '__main__':
	unittest.main()
