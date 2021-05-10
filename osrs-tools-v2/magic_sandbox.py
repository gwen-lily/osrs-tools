from main import *

mage = Player.max_sang_brimstone()
mage.pray(PlayerStats.StatPrayer.augury())
mage.overload()

mage_hand = OlmMageHand(39, False)

dam = mage.damage_against_monster(mage_hand)
print(dam)

if __name__ == '__main__':
	pass
