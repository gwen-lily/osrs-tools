from osrs_tools.stats import PlayerLevels
from osrs_tools.tracked_value import Level, LevelModifier
from osrs_tools.boost import SuperAttackPotion, SuperCombatPotion, DivineBastion, Overload
from osrs_tools.character.player import Player
from osrs_tools.data import Skills


def test_boost():
    player = Player()

    levels = PlayerLevels.maxed_player()
    attack_level = levels[Skills.ATTACK]
