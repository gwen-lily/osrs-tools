from main import *

zuk = Monster.from_bitterkoekje('tzkal-zuk')

me = Player.arma_tbow()

me.bastion_potion()
me.pray(PlayerStats.StatPrayer.rigour())

me.attack_monster(zuk)

print(me)

if __name__ == '__main__':
	pass
