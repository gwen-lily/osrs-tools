"""Build all useful potion effects.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-22                                                        #
###############################################################################
"""

from copy import copy

from .data import Boost, BoostBuilder, SkillModifier, Skills

###############################################################################
# data 'n such                                                                #
###############################################################################

_SUPER_COMBAT_POTION_BUFF_SKILLS = [
    Skills.ATTACK,
    Skills.STRENGTH,
    Skills.DEFENCE,
]

_SARADOMIN_BREW_DEBUFF_SKILLS = [
    Skills.ATTACK,
    Skills.STRENGTH,
    Skills.RANGED,
    Skills.MAGIC,
]


_ANCIENT_BREW_DEBUFF_SKILLS = [Skills.ATTACK, Skills.STRENGTH, Skills.DEFENCE]

_OVERLOAD_BUFFS_SKILLS = [
    Skills.ATTACK,
    Skills.STRENGTH,
    Skills.DEFENCE,
    Skills.RANGED,
    Skills.MAGIC,
]

Builder = BoostBuilder()

_SKILLS_NO_PRAYER = [s for s in Skills]
_SKILLS_NO_PRAYER.remove(Skills.PRAYER)

###############################################################################
# callable & skill modifier creation                                          #
###############################################################################

# callables ###################################################################

super_attack_skillmod = Builder.create_skill_modifier(
    Skills.ATTACK, 5, 0.15, comment="super attack potion"
)
super_strength_skillmod = Builder.create_skill_modifier(
    Skills.STRENGTH, 5, 0.15, comment="super strength potion"
)
super_defence_skillmod = Builder.create_skill_modifier(
    Skills.DEFENCE, 5, 0.15, comment="super defence potion"
)

super_combat_callable = Builder.create_callable(5, 0.15, comment="super combat potion")


regular_attack_skillmod = Builder.create_skill_modifier(
    Skills.ATTACK, 3, 0.10, comment="attack potion"
)
regular_strength_skillmod = Builder.create_skill_modifier(
    Skills.STRENGTH, 3, 0.10, comment="strength potion"
)
regular_defence_skillmod = Builder.create_skill_modifier(
    Skills.DEFENCE, 3, 0.10, comment="defence potion"
)

combat_potion_callable = Builder.create_callable(3, 0.10, comment="combat potion")

super_restore_callable_no_wrench = Builder.create_callable(
    8, 0.25, comment="super restore"
)
sanfew_serum_callable_no_wrench = Builder.create_callable(
    4, 0.30, comment="sanfew serum"
)
saradomin_brew_debuff_callable = Builder.create_callable(
    2, 0.10, True, comment="sara brew (debuff)"
)
ancient_brew_debuff_callable = Builder.create_callable(
    2, 0.10, True, "ancient brew (debuff)"
)

overload_buff_callable = Builder.create_callable(6, 0.16, comment="overload (+)")

# skill modifiers #############################################################

super_attack_skillmod = Builder.create_skill_modifier(
    Skills.ATTACK, 5, 0.15, comment="super attack potion"
)
super_strength_skillmod = Builder.create_skill_modifier(
    Skills.STRENGTH, 5, 0.15, comment="super strength potion"
)
super_defence_skillmod = Builder.create_skill_modifier(
    Skills.DEFENCE, 5, 0.15, comment="super defence potion"
)

ranged_skillmod = Builder.create_skill_modifier(
    Skills.RANGED, 4, 0.10, comment="ranging potion"
)
magic_skillmod = Builder.create_skill_modifier(
    Skills.MAGIC, 4, 0, comment="magic potion"
)
imbued_heart_skillmod = Builder.create_skill_modifier(
    Skills.MAGIC, 1, 0.10, comment="imbued heart"
)

prayer_skillmod = Builder.create_skill_modifier(
    Skills.PRAYER, 7, 0.25, comment="prayer potion"
)
prayer_skillmod_wrench = Builder.create_skill_modifier(
    Skills.PRAYER, 7, 0.27, comment="prayer potion (wrench)"
)

super_restore_skillmod = Builder.create_skill_modifier(
    Skills.PRAYER, 8, 0.25, comment="super restore"
)
super_restore_skillmod_wrench = Builder.create_skill_modifier(
    Skills.PRAYER, 8, 0.27, comment="super restore (wrench)"
)

sanfew_serum_skillmod = Builder.create_skill_modifier(
    Skills.PRAYER, 4, 0.30, comment="sanfew serum"
)
sanfew_serum_skillmod_wrench = Builder.create_skill_modifier(
    Skills.PRAYER, 4, 0.32, comment="sanfew serum (wrench)"
)

saradomin_brew_defence_skillmod = Builder.create_skill_modifier(
    Skills.DEFENCE, 2, 0.20, comment="sara brew"
)
saradomin_brew_hitpoints_skillmod = Builder.create_skill_modifier(
    Skills.HITPOINTS, 2, 0.15, comment="sara brew"
)

ancient_brew_prayer_skillmod = Builder.create_skill_modifier(
    Skills.PRAYER, 2, 0.10, comment="ancient brew (buff)"
)
ancient_brew_magic_skillmod = Builder.create_skill_modifier(
    Skills.MAGIC, 2, 0.05, comment="ancient brew (buff)"
)

overload_hitpoints_skillmod = Builder.create_skill_modifier(
    Skills.HITPOINTS, 50, 0, True, "overload damage"
)

zbrew_attack_skillmod = Builder.create_skill_modifier(
    Skills.ATTACK, 2, 0.20, comment="zamorak brew (buff)"
)
zbrew_strength_skillmod = Builder.create_skill_modifier(
    Skills.STRENGTH, 2, 0.12, comment="zamorak brew (buff)"
)
zbrew_defence_skillmod = Builder.create_skill_modifier(
    Skills.DEFENCE, 2, 0.10, True, "zamorak brew (debuff)"
)
zbrew_hitpoints_skillmod = Builder.create_skill_modifier(
    Skills.HITPOINTS, 0, 0.12, True, "zamorak brew damage"
)
zbrew_prayer_skillmod = Builder.create_skill_modifier(
    Skills.PRAYER, 0, 0.10, comment="zamorak brew (buff)"
)


# modifier collections ########################################################

# ancient brew
ancient_brew_modifiers: list[SkillModifier] = []
ancient_brew_modifiers += [ancient_brew_prayer_skillmod, ancient_brew_magic_skillmod]

for skill in _ANCIENT_BREW_DEBUFF_SKILLS:
    ancient_brew_modifiers.append(SkillModifier(skill, ancient_brew_debuff_callable))

# saradomin brew
saradomin_brew_modifiers: list[SkillModifier] = []
saradomin_brew_modifiers += [
    saradomin_brew_defence_skillmod,
    saradomin_brew_hitpoints_skillmod,
]

for skill in _SARADOMIN_BREW_DEBUFF_SKILLS:
    saradomin_brew_modifiers.append(
        SkillModifier(skill, saradomin_brew_debuff_callable)
    )

# zamorak brew
zamorak_brew_modifiers = [
    zbrew_attack_skillmod,
    zbrew_strength_skillmod,
    zbrew_defence_skillmod,
    zbrew_hitpoints_skillmod,
    zbrew_prayer_skillmod,
]

# overload
overload_modifiers: list[SkillModifier] = []
overload_modifiers.append(overload_hitpoints_skillmod)

for skill in _OVERLOAD_BUFFS_SKILLS:
    overload_modifiers.append(SkillModifier(skill, overload_buff_callable))

# super restore / sanfew serum
super_restore_modifiers: list[SkillModifier] = []
sanfew_modifiers: list[SkillModifier] = []

for skill in _SKILLS_NO_PRAYER:
    restore_skillmod = SkillModifier(skill, super_restore_callable_no_wrench)
    sanfew_skillmod = SkillModifier(skill, sanfew_serum_callable_no_wrench)

    super_restore_modifiers.append(restore_skillmod)
    sanfew_modifiers.append(sanfew_skillmod)

super_restore_modifiers_wrench = copy(super_restore_modifiers)
sanfew_modifiers_wrench = copy(sanfew_modifiers)

appenderonis = [
    (super_restore_modifiers, super_restore_skillmod),
    (super_restore_modifiers_wrench, super_restore_skillmod_wrench),
    (sanfew_modifiers, sanfew_serum_skillmod),
    (sanfew_modifiers_wrench, sanfew_serum_skillmod_wrench),
]

for modifiers, modifier in appenderonis:
    modifiers.append(modifier)


###############################################################################
# skill modifiers and boosts                                                  #
###############################################################################

SuperAttackPotion = Boost("super attack potion", [super_attack_skillmod])
SuperStrengthPotion = Boost("super strength potion", [super_strength_skillmod])
SuperDefencePotion = Boost("super defence potion", [super_defence_skillmod])
SuperCombatPotion = Boost.uniform_boost(
    "super combat", _SUPER_COMBAT_POTION_BUFF_SKILLS, super_combat_callable
)

AttackPotion = Boost("attack potion", [regular_attack_skillmod])
StrengthPotion = Boost("strength potion", [regular_strength_skillmod])
DefencePotion = Boost("defence potion", [regular_defence_skillmod])
CombatPotion = Boost(
    "combat potion", [regular_attack_skillmod, regular_strength_skillmod]
)

RangingPotion = Boost("ranging potion", [ranged_skillmod])
BastionPotion = Boost("bastion potion", [ranged_skillmod, super_defence_skillmod])

MagicPotion = Boost("magic potion", [magic_skillmod])
BattlemagePotion = Boost("battlemage potion", [super_defence_skillmod, magic_skillmod])
ImbuedHeart = Boost("imbued heart", [imbued_heart_skillmod])

PrayerPotion = Boost("prayer potion", [prayer_skillmod])
PrayerPotionWrench = Boost("prayer potion (holy wrench)", [prayer_skillmod_wrench])

SuperRestore = Boost("super restore", super_restore_modifiers)
SuperRestoreWrench = Boost(
    "super restore (holy wrench)", super_restore_modifiers_wrench
)

SanfewSerum = Boost("sanfew serum", sanfew_modifiers)
SanfewSerumWrench = Boost("sanfew serum (holy wrench)", sanfew_modifiers_wrench)

SaradominBrew = Boost("saradomin brew", saradomin_brew_modifiers)
ZamorakBrew = Boost("zamorak brew", zamorak_brew_modifiers)
AncientBrew = Boost("ancient brew", ancient_brew_modifiers)

Overload = Boost("overload (+)", overload_modifiers)
