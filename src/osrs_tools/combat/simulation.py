"""Definition of Simulation.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-30                                                         #
###############################################################################
"""

from osrs_tools.character.character import Character


class Simulation:
    attackers: list[Character]
    defenders: list[Character]
