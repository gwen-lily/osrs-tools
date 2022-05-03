"""Handles the bulk of combat calculations for monsters.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created: 2022-04-30                                                         #
###############################################################################
"""

from osrs_tools.combat.player import DamageCalculation


class MvPCalc(DamageCalculation):
    def max_hit(self, other: Player) -> int:
        # basic defintions and error handling
        ab = self.aggressive_bonus
        dt = self._active_style.damage_type
        prot_prayers = other.prayers_coll.prayers
        ignores_prayer = self._active_style.ignores_prayer
        prayer_damage_modifier = None

        if dt in MeleeDamageTypes:
            effective_level = self.effective_melee_strength_level
            bonus = ab.melee_strength
            if ignores_prayer and ProtectFromMelee in prot_prayers:
                prayer_damage_modifier = DamageModifier(0.5, ProtectFromMelee.name)
        elif dt in RangedDamageTypes:
            effective_level = self.effective_ranged_strength_level
            bonus = ab.ranged_strength
            if ignores_prayer and ProtectFromMissiles in prot_prayers:
                prayer_damage_modifier = DamageModifier(0.5, ProtectFromMissiles.name)
        elif dt in MagicDamageTypes:
            effective_level = self.effective_magic_attack_level
            bonus = ab.magic_strength
            if ignores_prayer and ProtectFromMagic in prot_prayers:
                prayer_damage_modifier = DamageModifier(0.5, ProtectFromMagic.name)

        base_damage = self.base_damage(effective_level, bonus)
        max_hit = self.static_max_hit(base_damage, prayer_damage_modifier)
        return max_hit

    def damage_distribution(self, other: Player, **kwargs) -> Damage:
        dt = self._active_style.damage_type
        assert dt in PlayerStyle.all_damage_types

        att_roll = self.attack_roll(other)
        def_roll = other.defence_roll(self)
        accuracy = self.accuracy(att_roll, def_roll)

        max_hit = self.max_hit(other)
        hitpoints_cap = other.hp
        attack_speed = self._active_style.attack_speed

        elysian_reduction_modifier = (
            0.25 if other.equipment.elysian_spirit_shield else 0
        )
        sotd_reduction_modifier = (
            0.5
            if dt in MeleeDamageTypes
            and other.staff_of_the_dead_effect
            and other.equipment.staff_of_the_dead
            else 0
        )

        justiciar_style_bonus = other.equipment.defensive_bonus.__getattribute__(
            dt.value
        )
        justiciar_style_bonus_cap = 3000
        justiciar_reduction_modifier = (
            justiciar_style_bonus / justiciar_style_bonus_cap
            if other.equipment.justiciar_set
            else 0
        )

        dinhs_reduction_modifier = (
            0.20
            if other.equipment.dinhs_bulwark
            and other.active_style == BulwarkStyles.get_style(PlayerStyle.block)
            else 0
        )

        def reduced_hit(x: int, elysian_activated: bool = False) -> int:
            if elysian_activated:
                x = math.floor(x * (1 - elysian_reduction_modifier))
            x = math.floor(x * (1 - justiciar_reduction_modifier))
            x = math.floor(x * (1 - sotd_reduction_modifier))
            x = math.floor(x * (1 - dinhs_reduction_modifier))
            return x

        if other.equipment.elysian_spirit_shield:
            activation_chance = 0.70
            unreduced_max = max_hit
            unactivated_max = reduced_hit(unreduced_max, False)
            unreduced_hit_chance = accuracy * (1 / (unreduced_max + 1))

            damage_values = np.arange(unactivated_max + 1)
            probabilities = np.zeros(damage_values.shape)
            probabilities[0] += 1 - accuracy

            for unreduced_hit in range(0, unreduced_max + 1):
                unactivated_damage = reduced_hit(unreduced_hit, False)
                activated_damage = reduced_hit(unreduced_hit, True)

                probabilities[activated_damage] += (
                    activation_chance * unreduced_hit_chance
                )
                probabilities[unactivated_damage] += (
                    1 - activation_chance
                ) * unreduced_hit_chance

            damage = Damage(
                attack_speed,
                Hitsplat.basic_constructor(damage_values, probabilities, hitpoints_cap),
            )

        else:
            unreduced_max = max_hit
            reduced_max = reduced_hit(unreduced_max)
            unreduced_hit_chance = accuracy * (1 / (unreduced_max + 1))

            damage_values = np.arange(reduced_max + 1)
            probabilities = np.zeros(damage_values.shape)
            probabilities[0] += 1 - accuracy

            for unreduced_hit in range(0, unreduced_max + 1):
                reduced_damage = reduced_hit(unreduced_hit)
                probabilities[reduced_damage] += unreduced_hit_chance

            damage = Damage(
                attack_speed,
                Hitsplat.basic_constructor(damage_values, probabilities, hitpoints_cap),
            )

        return damage
