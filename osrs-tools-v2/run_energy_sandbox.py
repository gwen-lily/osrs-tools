from main import *


def two_zero_lance():
	raider = Player.max_lance_inquisitor()
	raider.weight = 100     # weight doesn't matter for loss after 64 kg

	#       0   1   2   3   4   5   6   7
	#   olm _   _   _   t   _   _   _   t (t: turn)
	#   hit _   h   _   _   _   h   _   _
	#   run r   r   _   _   _   _   r   r

	gain_per_cycle = raider.energy_recovered(4)
	loss_per_cycle = raider.energy_lost(4)
	raider.stamina = True
	loss_per_stam_cycle = raider.energy_lost(4)

	normal_cycle_change = gain_per_cycle - loss_per_cycle
	stam_cycle_change = gain_per_cycle - loss_per_stam_cycle

	print(normal_cycle_change, 'energy lost per cycle (no stamina)')
	print(stam_cycle_change, 'energy lost per cycle (stamina)')

	ticks_per_minute = 100
	ticks_per_cycle = 8
	cycles_per_minute = ticks_per_minute / ticks_per_cycle
	cycles_per_stam_sip = int(2 * cycles_per_minute)

	print(cycles_per_stam_sip, "cycles per stam sip")

	net_change_per_stam_sip_cycle = 2000 + stam_cycle_change*cycles_per_stam_sip
	print(net_change_per_stam_sip_cycle, "net change per two minute stam sip cycle")


def four_zero_lance():
	raider = Player.max_lance_inquisitor()
	raider.weight = 100     # weight doesn't matter for loss after 64 kg

	#       0   1   2   3   4   5   6   7   8   9   a   b   c   d   e   f (hexadecimal)
	#   olm _   _   _   e   _   _   _   t   _   _   _   a   _   _   _   t (e: melee attack | a: mage attack | t: turn)
	#   hit _   h   _   _   _   h   _   _   _   h   _   _   _   h   _   _
	#   run _   _   r   r   r   r   r   r   r   r   _   _   _   _   _   _

	gain_per_cycle = raider.energy_recovered(8)
	loss_per_cycle = raider.energy_lost(8)
	raider.stamina = True
	loss_per_stam_cycle = raider.energy_lost(8)

	normal_cycle_change = gain_per_cycle - loss_per_cycle
	stam_cycle_change = gain_per_cycle - loss_per_stam_cycle

	print(normal_cycle_change, 'energy lost per cycle (no stamina)')
	print(stam_cycle_change, 'energy lost per cycle (stamina)')

	ticks_per_minute = 100
	ticks_per_cycle = 16
	cycles_per_minute = ticks_per_minute / ticks_per_cycle
	cycles_per_stam_sip = 2 * cycles_per_minute

	print(cycles_per_stam_sip, "cycles per stam sip")

	net_change_per_stam_sip_cycle = 2000 + stam_cycle_change*cycles_per_stam_sip
	print(net_change_per_stam_sip_cycle, "net change per two minute stam sip cycle")


def three_zero_scythe():
	raider = Player.max_scythe_inquisitor()
	raider.weight = 100     # weight doesn't matter for loss after 64 kg

	#       0   1   2   3   4   5   6   7   8   9   a   b   c   d   e   f (hexadecimal)
	#   olm _   _   _   e   _   _   _   t   _   _   _   a   _   _   _   t (e: melee attack | a: mage attack | t: turn)
	#   hit _   _   _   _   h   _   _   _   _   h   _   _   _   _   h   _
	#   run _   _   _   r   r   r   r   r   r   _   _   _   _   _   _   _

	gain_per_cycle = raider.energy_recovered(10)
	loss_per_cycle = raider.energy_lost(6)
	raider.stamina = True
	loss_per_stam_cycle = raider.energy_lost(6)

	normal_cycle_change = gain_per_cycle - loss_per_cycle
	stam_cycle_change = gain_per_cycle - loss_per_stam_cycle

	print(normal_cycle_change, 'energy lost per cycle (no stamina)')
	print(stam_cycle_change, 'energy lost per cycle (stamina)')

	ticks_per_minute = 100
	ticks_per_cycle = 16
	cycles_per_minute = ticks_per_minute / ticks_per_cycle
	cycles_per_stam_sip = 2 * cycles_per_minute

	print(cycles_per_stam_sip, "cycles per stam sip")

	net_change_per_stam_sip_cycle = 2000 + stam_cycle_change*cycles_per_stam_sip
	print(net_change_per_stam_sip_cycle, "net change per two minute stam sip cycle")


if __name__ == '__main__':
	two_zero_lance()
	print('\n')
	four_zero_lance()
	print('\n')
	three_zero_scythe()

