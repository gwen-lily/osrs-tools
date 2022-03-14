from __future__ import annotations
from abc import abstractproperty

from numpy import isin
from osrs_tools.equipment import *
from osrs_tools.style import *
from osrs_tools.prayer import *
from osrs_tools.stats import *
from osrs_tools.damage import *
from osrs_tools.spells import *
from osrs_tools.exceptions import *
from osrs_tools.modifier import Roll, MaxHit, DamageModifier, AttackRollModifier, create_modifier_pair
import osrs_tools.resource_reader as rr
from osrsbox import monsters_api, monsters_api_examples



@define(frozen=True)
class _MonsterTypes:
    demon = field(default='demon', init=False)
    draconic = field(default='draconic', init=False)
    fiery = field(default='fiery', init=False)
    golem = field(default='golem', init=False)
    kalphite = field(default='kalphite', init=False)
    leafy = field(default='leafy', init=False)
    penance = field(default='penance', init=False)
    shade = field(default='shade', init=False)
    spectral = field(default='spectral', init=False)
    undead = field(default='undead', init=False)
    vampyre = field(default='vampyre', init=False)
    vampyre_tier_1 = field(default='vampyre - tier 1', init=False)
    vampyre_tier_2 = field(default='vampyre - tier 2', init=False)
    vampyre_tier_3 = field(default='vampyre - tier 3', init=False)
    xerician = field(default='xerician', init=False)

    wilderness = field(default='wilderness', init=False)


@define(frozen=True)
class _MonsterLocations:
    wilderness = field(default='wilderness', init=False)
    tob = field(default='theatre of blood', init=False)
    cox = field(default='chambers of xeric', init=False)


MonsterTypes = _MonsterTypes()
MonsterLocations = _MonsterLocations()
character_attrs_settings = {'order': False, 'frozen': False}


def player_equipment_level_requirements_validator(instance, attribute, value):
    if not instance.levels >= value.level_requirements:
        raise EquipableError(f'Player with {instance.levels=} cannot equip Equipment with {value.level_requirements=}')


@define(**character_attrs_settings)
class Character(ABC):
    name: str
    levels: Stats
    active_levels: Stats = field(init=False)
    last_attacked: Character | None = field(init=False, repr=False)
    last_attacked_by: Character | None = field(init=False, repr=False)
    # TODO: implement more general defence_floor with minimum_levels: Stats = field()

    def damage(self, other: Character, *amount: int):
        damage_dealt = 0

        for a in amount:
            if a <= 0:
                continue

            damage_allowed = min([self.active_levels.hitpoints, a])
            self.active_levels.hitpoints -= damage_allowed
            damage_dealt += damage_allowed

        return damage_dealt

    def heal(self, amount: int, overheal: bool = False):
        assert amount >= 0
        if overheal:
            self.active_levels.hitpoints += amount
        else:
            self.active_levels.hitpoints = min([self.levels.hitpoints, self.active_levels.hitpoints + amount])

    @abstractmethod
    def reset_stats(self):
        pass

    @property
    def alive(self) -> bool:
        return self.active_levels.hitpoints > 0

    @property
    @abstractmethod
    def effective_melee_attack_level(self) -> int:
        pass

    @property
    @abstractmethod
    def effective_melee_strength_level(self) -> int:
        pass

    @property
    @abstractmethod
    def effective_defence_level(self) -> int:
        pass

    @property
    @abstractmethod
    def effective_ranged_attack_level(self) -> int:
        pass

    @property
    @abstractmethod
    def effective_ranged_strength_level(self) -> int:
        pass

    @property
    @abstractmethod
    def effective_magic_attack_level(self) -> int:
        pass

    @property
    @abstractmethod
    def effective_magic_defence_level(self) -> int:
        pass

    def defence_roll(self, other: Character, special_defence_roll: str = None) -> Roll:
        """Returns the defence roll of self when attacked by other, optionally with a specific damage type.

        Args:
            other (Character): The attacking object which inherits Character.
            special_defence_roll (str, optional): Damage type that determines which levels and bonuses self will use
            to determine the defence roll, as in the case of special attacks. Defaults to None.

        Raises:
            StyleError: Raised when a Style's damage type is unsupported.

        Returns:
            Roll: The defence roll.
        """
        # Basic definitions and error handling
        db = self.defensive_bonus
        dt = special_defence_roll if special_defence_roll else other.active_style.damage_type

        if dt in Style.melee_damage_types or dt in Style.ranged_damage_types:
            defensive_stat = self.effective_defence_level
        elif dt in Style.magic_damage_types:
            defensive_stat = self.effective_magic_defence_level
        else:
            raise StyleError(f'damage type: {dt}')

        defensive_bonus = db.__getattribute__(dt)
        defensive_roll = self.maximum_roll(defensive_stat, defensive_bonus)

        if isinstance(other, Player):
            if other.equipment.brimstone_ring and dt in Style.magic_damage_types:
                reduction = math.floor(int(defensive_roll) / 10) / 4
                defensive_roll = Roll(math.floor(defensive_roll - reduction))

        return defensive_roll

    def apply_dwh(self, damage_dealt: bool = True) -> int:
        if damage_dealt:
            self.active_levels.defence = 0.70 * self.active_levels.defence
        return self.active_levels.defence

    def apply_bgs(self, amount: int):
        """

        :param amount: The amount of damage to reduce, almost but not always equal to the damage dealt (tekton)
        :return:
        """

        def reduce_stat(inner_stat: str, inner_amount: int, inner_floor: int = 0) -> tuple[int, int]:
            current_stat = self.active_levels.__getattribute__(inner_stat)
            possible_reduction = current_stat - inner_floor

            if inner_amount > possible_reduction:
                actual_reduction = possible_reduction
                remaining = inner_amount - actual_reduction
                self.active_levels.__setattr__(stat, stat_floor)
                return actual_reduction, remaining
            else:
                actual_reduction = inner_amount
                remaining = 0
                self.active_levels.__setattr__(stat, current_stat - actual_reduction)
                return actual_reduction, remaining

        reduction_available = amount
        try:
            def_floor = self.defence_floor
        except AttributeError:
            def_floor = 0

        stat_tuples = (
            (Skills.defence, def_floor),
            (Skills.strength, 0),
            (Skills.attack, 0),
            (Skills.magic, 0),
            (Skills.ranged, 0)
        )

        for stat, stat_floor in stat_tuples:
            if reduction_available <= 0:
                break

            amount_reduced, reduction_available = reduce_stat(stat, reduction_available, stat_floor)

    def apply_arclight(self, success: bool = True):
        if success:
            if isinstance(self, Player):
                reduction_mod = 0.05
            elif isinstance(self, Monster):
                reduction_mod = 0.10 if MonsterTypes.demon in self.special_attributes else 0.05
            else:
                return NotImplemented

            for skill in (Skills.attack, Skills.strength, Skills.defence):
                self.active_levels.__setattr__(skill, reduction_mod * self.active_levels.__getattribute__(skill))

    def apply_bone_weapon_special(self, amount: int):
        self.active_levels.defence -= amount

    def apply_vulnerability(self, success: bool = True, tome_of_water: bool = True):
        if success:
            multiplier = 0.85 if tome_of_water else 0.90
            self.active_levels.defence = self.active_levels.defence * multiplier    # TODO: Confirm converter w/ceil

        return self.active_levels.defence

    @staticmethod
    def effective_accuracy_level(invisible_level: int, style_bonus: int, void_modifier: float = 1):
        stance_level = invisible_level + style_bonus + 8
        void_level = math.floor(void_modifier * stance_level)
        effective_level = void_level
        return effective_level

    @staticmethod
    def effective_strength_level(invisible_level: int, style_bonus: int, void_modifier: float = 1):
        stance_level = invisible_level + style_bonus
        void_level = math.floor(void_modifier * stance_level)
        effective_level = void_level
        return effective_level

    @staticmethod
    def maximum_roll(effective_level: int, aggressive_or_defensive_bonus: int, *roll_modifiers: AttackRollModifier) -> Roll:
        """

        :param effective_level: A function of stat, (potion), prayers, other modifiers, and stance
        :param aggressive_or_defensive_bonus: The bonus a player gets from gear or monsters have innately
        :param roll_modifiers: A direct multiplier (or multipliers) on the roll, such as a BGS special attack.
        :return:
        """
        roll = Roll(effective_level * (aggressive_or_defensive_bonus + 64))
        for roll_mod in roll_modifiers:
            roll = roll * roll_mod

        return roll

    @staticmethod
    def accuracy(offensive_roll: Roll, defensive_roll: Roll) -> float:
        """

        :param offensive_roll: The maximum offensive roll of the attacker.
        :param defensive_roll: The maximum defensive roll of the defender.
        :return: Accuracy, or the chance that an attack is successful. This is NOT the chance to not deal 0 damage.
        """
        off_val = int(offensive_roll)
        def_val = int(defensive_roll)
        if off_val > def_val:
            return 1 - (def_val + 2) / (2 * (off_val + 1))
        else:
            return off_val / (2 * (def_val + 1))

    @staticmethod
    def base_damage(effective_strength_level: int, strength_bonus: int) -> float:
        """

        :param effective_strength_level: A function of strength, (potions), prayer, and stance.
        :param strength_bonus: damage-type-dependent bonus value, monsters have innately and players get from gear.
        :return: A float that represents basically the max hit except for special attacks.
        """
        term_1 = 1.3 + effective_strength_level / 10 + strength_bonus / 80
        term_2 = effective_strength_level * strength_bonus / 640
        base_damage = term_1 + term_2
        return base_damage

    @staticmethod
    def static_max_hit(base_damage: MaxHit, *damage_modifiers: DamageModifier) -> MaxHit:
        max_hit = base_damage
        for dmg_mod in damage_modifiers:
            max_hit = max_hit * dmg_mod

        return max_hit

    def __str__(self):
        return self.name


def default_active_styler_factory(instance):
    return instance.equipment.weapon.weapon_styles[0]


def active_style_validator(instance, attribute, value):
    if value not in instance.equipment.weapon.weapon_styles.styles:
        raise StyleError(f'{value=} not in {instance.equipment.weapon.weapon_styles=}')


@define(**character_attrs_settings)
class Player(Character):
    levels: PlayerLevels = field(
        factory=PlayerLevels.maxed_player,
        validator=validators.instance_of(PlayerLevels),
        repr=False,
    )
    active_levels: PlayerLevels = field(
        init=False,
        validator=validators.instance_of(PlayerLevelsUnbounded),
        repr=False,
    )
    prayers: PrayerCollection = field(
        factory=PrayerCollection.no_prayers,
        validator=validators.instance_of(PrayerCollection),
        repr=False,
    )
    equipment: Equipment = field(
        factory=Equipment.no_equipment,
        validator=[validators.instance_of(Equipment), player_equipment_level_requirements_validator],
        repr=True,
    )
    active_style: PlayerStyle = field(
        init=False,
        validator=[validators.instance_of(PlayerStyle), active_style_validator],
        repr=True,
    )
    autocast: Spell = field(default=None, repr=False)   # , validator=validators.instance_of(Spell))
    task: bool = field(default=True, repr=False)    # TODO: Implement smarter task checking
    kandarin_hard: bool = field(default=True, repr=False)
    prayer_drain_counter: int = field(default=0, init=False, repr=False)
    charged: bool = field(default=False, init=False, repr=False)
    staff_of_the_dead_effect: bool = field(default=False, init=False, repr=False)
    weight: int = field(default=0, init=False, repr=False)
    run_energy: int = field(default=10000, init=False, converter=lambda v: min([max([0, v]), 10000]), repr=False)
    stamina_potion: bool = field(default=False, init=False, repr=False)
    special_energy: int = field(default=100, init=False, converter=lambda v: min([max([0, v]), 100]), repr=False)
    special_energy_counter: int = field(default=0, init=False, repr=False)

    def __attrs_post_init__(self):
        self.active_levels = self.levels.to_unbounded()
        self.active_style = self.equipment.weapon.weapon_styles.default

    # properties
    @property
    def aggressive_bonus(self) -> AggressiveStats:
        """Simple wrapper for Equipment.aggressive_bonus which accounts for edge cases.

        Dinh's Bulwark melee strength bonus and Smoke Staff's magic damage gear bonus are
        unique mechanics that don't fit into the usual DPS scheme.

        Returns:
            AggressiveStats: AggressiveStats object.
        """
        ab = copy(self.equipment.aggressive_bonus)
        ab.melee_strength += self._dinhs_modifier()
        ab.magic_strength += self._smoke_modifier()
        return ab


    @property
    def defensive_bonus(self) -> DefensiveStats:
        """Simple wrapper to match aggressive_bonus and provide Player level access.

        Returns:
            DefensiveStats: DefensiveStats object.
        """
        return self.equipment.defensive_bonus()

    @property
    def combat_level(self) -> int:
        base_level = (1/4) * (self.levels.defence + self.levels.hitpoints + math.floor(self.levels.prayer / 2))
        melee_level = (13/40) * (self.levels.attack + self.levels.strength)
        magic_level = (13/40) * (math.floor(self.levels.magic/2) + self.levels.magic)
        ranged_level = (13/40) * (math.floor(self.levels.ranged/2) + self.levels.ranged)
        type_level = max([melee_level, magic_level, ranged_level])
        return math.floor(base_level + type_level)

    @staticmethod
    def max_combat_level() -> int:
        return 126

    @property
    def special_energy_full(self) -> bool:
        return self.special_energy == 100

    @property
    def prayer_drain_resistance(self):
        return 2 * self.equipment.prayer_bonus + 60

    @property
    def ticks_per_pp_lost(self) -> float:
        try:
            value = self.prayer_drain_resistance / self.prayers.drain_effect
        except ZeroDivisionError:
            value = 0

        return value

    @property
    def defence_floor(self) -> int:
        _ = self
        return 0

    @property
    def visible_attack(self):
        return self.active_levels.attack

    @property
    def visible_strength(self):
        return self.active_levels.strength

    @property
    def visible_defence(self):
        return self.active_levels.defence

    @property
    def visible_magic(self):
        return self.active_levels.magic

    @property
    def visible_ranged(self):
        return self.active_levels.ranged

    @property
    def invisible_attack(self):
        return math.floor(self.visible_attack * self.prayers.attack)

    @property
    def invisible_strength(self):
        return math.floor(self.visible_strength * self.prayers.strength)

    @property
    def invisible_defence(self):
        return math.floor(self.visible_defence * self.prayers.defence)

    @property
    def invisible_magic(self):
        return math.floor(self.visible_magic * self.prayers.magic_attack)

    @property
    def invisible_ranged_attack(self):
        return math.floor(self.visible_ranged * self.prayers.ranged_attack)

    @property
    def invisible_ranged_strength(self) -> int:
        return math.floor(self.visible_ranged * self.prayers.ranged_strength)

    @property
    def effective_melee_attack_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.attack
        void_atk_lvl_mod, _ = self._void_modifiers()
        return self.effective_accuracy_level(self.invisible_attack, style_bonus, void_atk_lvl_mod)

    @property
    def effective_melee_strength_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.strength
        _, void_str_lvl_mod = self._void_modifiers()
        return self.effective_strength_level(self.invisible_strength, style_bonus, void_str_lvl_mod)

    @property
    def effective_defence_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.defence
        return self.effective_accuracy_level(self.invisible_defence, style_bonus)

    @property
    def effective_ranged_attack_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.ranged
        void_rng_atk_lvl_mod, _ = self._void_modifiers()
        return self.effective_accuracy_level(self.invisible_ranged_attack, style_bonus, void_rng_atk_lvl_mod)

    @property
    def effective_ranged_strength_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.ranged
        # jank_bonus = style_bonus + 8
        # TODO: Learn of the origin of the jank bonus and banish it.
        _, void_rng_str_lvl_mod = self._void_modifiers()
        return self.effective_strength_level(self.invisible_ranged_strength, style_bonus, void_rng_str_lvl_mod)

    @property
    def effective_magic_attack_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.magic
        void_mag_atk_lvl_mod, _ = self._void_modifiers()
        return self.effective_accuracy_level(self.invisible_magic, style_bonus, void_mag_atk_lvl_mod)

    @property   # TODO: Check these mechanics
    def effective_magic_defence_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.defence
        visible_magic_defence = math.floor(0.3*self.visible_defence + 0.7*self.visible_magic)
        invisible_magic_defence = math.floor(visible_magic_defence * self.prayers.magic_defence)
        return self.effective_accuracy_level(invisible_magic_defence, style_bonus)

    # accuracy & strength modifiers

    def _void_modifiers(self) -> ArmDmTuple:
        if self.equipment.elite_void_set:
            if (dt := self.active_style.damage_type) in Style.melee_damage_types:
                void_attack_level_modifier = 1.1
                void_strength_level_modifier = 1.1
            elif dt in Style.ranged_damage_types:
                void_attack_level_modifier = 1.1
                void_strength_level_modifier = 1.125
            elif dt in Style.magic_damage_types:
                void_attack_level_modifier = 1.45
                void_strength_level_modifier = 1.025
            else:
                raise StyleError(f'{self.active_style.damage_type=}')

        elif self.equipment.normal_void_set:
            if (dt := self.active_style.damage_type) in Style.melee_damage_types:
                void_attack_level_modifier = 1.1
                void_strength_level_modifier = 1.1
            elif dt in Style.ranged_damage_types:
                void_attack_level_modifier = 1.1
                void_strength_level_modifier = 1.1
            elif dt in Style.magic_damage_types:
                void_attack_level_modifier = 1.45
                void_strength_level_modifier = 1.1
            else:
                raise StyleError(f'{self.active_style.damage_type=}')

        else:
            void_attack_level_modifier = 1
            void_strength_level_modifier = 1

        return ArmDmTuple(void_attack_level_modifier, void_strength_level_modifier)

    def _salve_modifier(self, other: Character) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.equipment.salve and isinstance(other, Monster) and MonsterTypes.undead in other.special_attributes:
            comment = 'salve'
            if self.equipment.wearing(neck=Gear.from_bb('salve amulet (i)')):
                modifier = 7/6
            elif self.equipment.wearing(neck=Gear.from_bb('salve amulet (ei)')):
                modifier = 1.2

            return create_modifier_pair(modifier, comment)

    def _slayer_modifier(self, other: Character) -> tuple[AttackRollModifier, DamageModifier] | None:       
        if self.task and self.equipment.slayer and isinstance(other, Monster):
            comment = 'slayer'
            if (dt := self.active_style.damage_type) in Style.melee_damage_types:
                modifier = 7/6
            elif dt in Style.ranged_damage_types:
                modifier = 1.15
            elif dt in Style.magic_damage_types:
                modifier = 1.15
            else:
                raise StyleError(self.active_style)

            return create_modifier_pair(modifier, comment)

    def _arclight_modifier(self, other: Character) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.equipment.arclight and isinstance(other, Monster) and MonsterTypes.demon in other.special_attributes:
            modifier = 1.7
            comment = 'arclight'
            return create_modifier_pair(modifier, comment)

    def _draconic_modifier(self, other: Character) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.equipment.dragonbane_weapon and isinstance(other, Monster) and MonsterTypes.draconic in other.special_attributes:
            comment = 'draconic'
            if self.equipment.wearing(weapon=Weapon.from_bb('dragon hunter lance')):
                modifier = 1.2
            elif self.equipment.wearing(weapon=Weapon.from_bb('dragon hunter crossbow')):
                modifier = 1.3
            else:
                raise NotImplementedError

            return create_modifier_pair(modifier, comment)

    def _wilderness_modifier(self, other: Character) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.equipment.wilderness_weapon and isinstance(other, Monster) and other.location == MonsterLocations.wilderness:
            comment = 'wilderness'
            if self.equipment.wearing(weapon=Weapon.from_bb("craw's bow")):
                arm = 1.5
                dm = 1.5
            elif self.equipment.wearing(weapon=Weapon.from_bb("viggora's chainmace")):
                arm = 1.5
                dm = 1.5
            elif self.equipment.wearing(weapon=Weapon.from_bb("thammaron's sceptre")):
                arm = 2
                dm = 1.25
            else:
                raise NotImplementedError

            return AttackRollModifier(arm, comment), DamageModifier(dm, comment)

    def _twisted_bow_modifier(self, other: Character) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.equipment.twisted_bow:
            comment = 'twisted bow'
            accuracy_modifier_ceiling = 1.40    # 140%
            damage_modifier_ceiling = 2.50      # 250%
            magic_ceiling = 350 if isinstance(other, CoxMonster) else 250

            magic = min([max([other.active_levels.magic, other.aggressive_bonus.magic]), magic_ceiling])

            accuracy_modifier_percent = 140 + math.floor((10*3*magic/10 - 10)/100) - math.floor(
                ((3*magic/10 - 100)**2/100))
            damage_modifier_percent = 250 + math.floor((10*3*magic/10 - 14)/100) - math.floor(
                ((3*magic/10 - 140)**2/100))

            arm = min([accuracy_modifier_ceiling, accuracy_modifier_percent / 100])
            dm = min([damage_modifier_ceiling, damage_modifier_percent / 100])
            return AttackRollModifier(arm, comment), DamageModifier(dm, comment)

    def _obsidian_modifier(self) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.equipment.obsidian_armor_set and self.equipment.obsidian_weapon:
            modifier = 1.1
            comment = 'obsidian weapon & armour set'
            return create_modifier_pair(modifier, comment)

    def _berserker_necklace_damage_modifier(self) -> DamageModifier | None:
        if self.equipment.berserker_necklace and self.equipment.obsidian_weapon:
            modifier = 1.2
            comment = 'obsidian weapon & berserker necklace'
            return DamageModifier(modifier, comment)

    def _dharok_damage_modifier(self) -> DamageModifier | None:
        if self.equipment.dharok_set:
            modifier = 1 + (self.levels.hitpoints - self.active_levels.hitpoints)/100 * (self.levels.hitpoints/100)
            comment = "dharok's set"
            return DamageModifier(modifier, comment)

    def _leafy_modifier(self, other: Character) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.equipment.leafy_weapon and isinstance(other, Monster) and MonsterTypes.leafy in other.special_attributes
            modifier = 1.175
            comment = 'leafy'
            return create_modifier_pair(modifier, comment)

    def _keris_damage_modifier(self, other: Character) -> DamageModifier | None:
        if self.equipment.keris and isinstance(other, Monster) and MonsterTypes.kalphite in other.special_attributes:
            modifier = 4/3
            comment = 'keris'
            return DamageModifier(modifier, comment)

    def _crystal_armor_modifier(self) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.equipment.crystal_weapon:
            comment = "crystal weapon & armour"
            piece_arm_bonus = 0.06
            piece_dm_bonus = 0.03
            set_arm_bonus = 0.12
            set_dm_bonus = 0.06

            if self.equipment.crystal_armor_set:
                crystal_arm = 1 + set_arm_bonus + 3*piece_arm_bonus
                crystal_dm = 1 + set_dm_bonus + 3*piece_dm_bonus
            else:
                crystal_arm = 1
                crystal_dm = 1

                if self.equipment.wearing(head=Gear.from_bb('crystal helm')):
                    crystal_arm += piece_arm_bonus
                    crystal_dm += piece_dm_bonus
                if self.equipment.wearing(body=Gear.from_bb('crystal body')):
                    crystal_arm += piece_arm_bonus
                    crystal_dm += piece_dm_bonus
                if self.equipment.wearing(legs=Gear.from_bb('crystal legs')):
                    crystal_arm += piece_arm_bonus
                    crystal_dm += piece_dm_bonus

                # don't return if no crystal pieces are equipped
                if crystal_arm == 1 and crystal_dm == 1:
                    return

            return AttackRollModifier(crystal_arm, comment), DamageModifier(crystal_dm, comment)

    def _inquisitor_modifier(self) -> tuple[AttackRollModifier, DamageModifier] | None:
        if self.active_style.damage_type == Style.crush:
            comment = 'inquisitor'
            piece_bonus = 0.005
            set_bonus = 0.01

            if self.equipment.inquisitor_set:
                modifier = 1 + set_bonus + 3*piece_bonus
            else:
                modifier = 1

                if self.equipment.wearing(head=Gear.from_bb("inquisitor's great helm")):
                    modifier += piece_bonus
                if self.equipment.wearing(body=Gear.from_bb("inquisitor's hauberk")):
                    modifier += piece_bonus
                if self.equipment.wearing(legs=Gear.from_bb("inquisitor's plateskirt")):
                    modifier += piece_bonus

                # don't return if no inquisitor pieces are equipped
                if modifier == 1:
                    return

            return create_modifier_pair(modifier, comment)

    def _chin_attack_roll_modifier(self, distance: int = None) -> AttackRollModifier | None:
        if self.equipment.chinchompas and distance is not None:
            comment = 'chinchompa'
            if (style := self.active_style) == ChinchompaStyles.get_style(PlayerStyle.short_fuse):
                if 0 <= distance <= 3:
                    chin_arm = 1.00
                elif 4 <= distance <= 6:
                    chin_arm = 0.75
                else:
                    chin_arm = 0.50
            elif style == ChinchompaStyles.get_style(PlayerStyle.medium_fuse):
                if 4 <= distance <= 6:
                    chin_arm = 1.00
                else:
                    chin_arm = 0.75
            elif style == ChinchompaStyles.get_style(PlayerStyle.long_fuse):
                if 0 <= distance <= 3:
                    chin_arm = 0.50
                elif 4 <= distance <= 6:
                    chin_arm = 0.75
                else:
                    chin_arm = 1.00
            else:
                raise StyleError(style)

            return AttackRollModifier(chin_arm, comment)

    def _vampyric_modifier(self, other: Character):
        raise NotImplementedError

    def _tome_of_fire_damage_modifier(self, spell: Spell = None) -> DamageModifier | None:
        if self.equipment.tome_of_fire and spell in asdict(FireSpells):
            modifier = 1.5
            comment = 'tome of fire'
            return DamageModifier(modifier, comment)

    def _chaos_gauntlets_flat_damage_bonus(self, spell: Spell = None) -> int | None:
        """Returns the flat damage bonus provided by chaos gauntlets.

        Args:
            spell (Spell, optional): The spell being cast. Defaults to None.

        Returns:
            int | None: 
        """
        if self.equipment.chaos_gauntlets:
            spell = spell if spell is not None else self.autocast
            if spell in asdict(BoltsSpells):
                damage_boost = 3
                return damage_boost

    def _smoke_modifier(self, spell: Spell = None) -> tuple[AttackRollModifier, float] | None:
        # TODO: Implment ARM & DM float wrapper classes for simplicity & type security.

        spell = spell if spell is not None else self.autocast
        if self.equipment.smoke_staff and isinstance(spell, StandardSpell):
            arm = 1.1
            gear_damage_bonus = 0.1    # strange mechanic, applied to the gear bonus
            comment = 'smoke staff'

            return AttackRollModifier(arm, comment), gear_damage_bonus

    def _guardians_damage_modifier(self, other: Character) -> DamageModifier | None:
        if self.equipment.pickaxe and isinstance(other, Guardian):
            dm = (50 + min([100, self.active_levels.mining]) + self.equipment.weapon.level_requirements.mining) / 150
            comment = 'guardian'
            return DamageModifier(dm, comment)

    def _ice_demon_damage_modifier(self, other: Character, spell: None) -> DamageModifier | None:
        if isinstance(other, IceDemon):            
            damage_modifier = 1.5 if spell in asdict(FireSpells) else 0.33
            comment = 'ice demon'
            return DamageModifier(damage_modifier, comment)

    def _dinhs_modifier(self) -> int:
        """
        Bonus equipment strength bonus when using Dinh's offensively.

        Source: https://oldschool.runescape.wiki/w/Dinh's_bulwark#Strength_buff
        """
        if self.equipment.dinhs_bulwark and self.active_style == BulwarkStyles.get_style(PlayerStyle.pummel):
            db = self.equipment.defensive_bonus
            bonus = math.floor((math.floor(sum([db.stab, db.slash, db.crush, db.ranged])/4) - 200) / 3) - 38
        else:
            bonus = 0

        return bonus

    def _abyssal_bludgeon_special_modifier(self, special_attack: bool) -> DamageModifier | None:
        """Returns the damage modifier an abyssal bludgeon would apply under variable conditions.

        Args:
            special_attack (bool): True if performing a special attack, False otherwise.

        Returns:
            DamageModifier | None: 
        """
        if special_attack and self.equipment.abyssal_bludgeon:  # Abyssal Bludgeon: Penance
            pp_missing = min([0, self.levels.prayer - self.active_levels.prayer])
            damage_modifier = 1 + (0.005 * pp_missing)
            comment = 'abyssal bludgeon: penance'

            return DamageModifier(damage_modifier, comment)

    # combat methods
    def max_hit(self, other: Character, spell: Spell = None) -> MaxHit:
        # TODO: Documentation

        # basic defintions and error handling
        ab = self.aggressive_bonus

        if not isinstance(other, Character):
            raise PlayerError(other)

        if spell is not None:
            dt = Style.magic
        elif isinstance(self.autocast, Spell) and self.active_style.is_spell_style():
            spell = self.autocast
            dt = Style.magic
        else:
            dt = self.active_style.damage_type

        # Main logic tree, each damage type has its own particulars.
        if dt in Style.melee_damage_types or dt in Style.ranged_damage_types:
            if dt in Style.melee_damage_types:
                effective_level = self.effective_melee_strength_level
                bonus = ab.melee_strength
            else:
                effective_level = self.effective_ranged_strength_level
                bonus = ab.ranged_strength

            base_damage = self.base_damage(effective_level, bonus)
            return MaxHit(math.floor(base_damage))

        elif dt in Style.magic_damage_types:
            if spell is None:
                if self.equipment.weapon == Weapon.from_bb('sanguinesti staff'):
                    self.autocast = PoweredSpells.sanguinesti_staff
                elif self.equipment.weapon == Weapon.from_bb('trident of the swamp'):
                    self.autocast = PoweredSpells.trident_of_the_swamp
                elif self.equipment.weapon == Weapon.from_bb('trident of the seas'):
                    self.autocast = PoweredSpells.trident_of_the_seas

            if isinstance(spell, Spell):
                if isinstance(spell, StandardSpell) or isinstance(spell, AncientSpell):
                    base_damage = spell.max_hit()
                elif isinstance(spell, GodSpell):
                    base_damage = spell.max_hit(self.charged)
                elif isinstance(spell, PoweredSpell):
                    base_damage = spell.max_hit(self.visible_magic)
                else:
                    raise SpellError(f'{spell=} {self.autocast=}')

                return MaxHit(base_damage)

        else:
            raise StyleError(self.active_style)

    def attack_speed(self, spell: Spell = None) -> int:
        active_spell = spell if spell else self.autocast

        if isinstance(active_spell, Spell):
            if self.equipment.weapon == Weapon.from_bb('harmonised nightmare staff') and \
                    isinstance(active_spell, StandardSpell):
                return active_spell.attack_speed - 1
            else:
                return active_spell.attack_speed + self.active_style.attack_speed_modifier
        else:
            return self.equipment.weapon.attack_speed + self.active_style.attack_speed_modifier

    def attack_range(self) -> int:
        return min([max([0, self.equipment.weapon.attack_range]), 10])

    def damage_distribution(self, other: Character, special_attack: bool = False, distance: int = None, spell: Spell = None,
                            additional_targets: int | Character | list[Character] = 0, **kwargs,) -> Damage:
        """Returns a Damage object representing the damage distribution of a theoretical attack by self on other with additional parameters.

        Args:
            other (Character): An object which inherits Character which is the main target of the Player's attack.
            special_attack (bool, optional): True if the attack is a special attack, False otherwise. Defaults to False.
            distance (int, optional): Tile distance between Player and other. Only needed at the moment for Chinchompa calculations. Defaults to None.
            spell (Spell, optional): A Spell the Player casts instead of attacking with the equipped weapon or Player.autocast. Defaults to None.
            additional_targets (int | Character | list[Character], optional): An optional parameter for easily calculating AoE or multi-target attacks.
            Accepts integers for additional targets who are identical to other (such as in the case of maniacal monkeys). Accepts either Character or a
            list of Characters to get actual results, including with hitpoint cap / overkill numbers (such as in the case of chinning Kree'arra minions). 
            Defaults to 0 (no additional targets).

        Raises:
            SpecialWeaponError: Raised if the Player attempts to perform a special attack with anything other than a SpecialWeapon class.
            PlayerError: Raised if the other target is not a subclass of Character.
            NotImplementedError: Raised if a particular condition has specific behavior which has not been implemented.

        Returns:
            Damage: A Damage object representing a static damage distribution with values, probabilities, and additional properties.
        """
        # Error handling and simple reference assignments
        eqp = self.equipment
        wp = eqp.weapon
        ab = self.aggressive_bonus

        if not isinstance(other, Character):
            raise PlayerError(other)

        if special_attack:
            if not isinstance(wp, SpecialWeapon):
                raise SpecialWeaponError(wp)

        if spell is not None:
            spell = spell
            dt = Style.magic
        elif isinstance(self.autocast, Spell) and self.active_style.is_spell_style():
            spell = self.autocast
            dt = self.active_style.damage_type
        else:
            dt = self.active_style.damage_type

        if dt in Style.melee_damage_types:
            effective_accuracy_level = self.effective_melee_attack_level
            effective_strength_level = self.effective_melee_strength_level
            accuracy_bonus = ab.__getattribute__(dt)
            strength_bonus = ab.melee_strength
        elif dt in Style.ranged_damage_types:
            effective_accuracy_level = self.effective_ranged_attack_level
            effective_strength_level = self.effective_ranged_strength_level
            accuracy_bonus = ab.ranged
            strength_bonus = ab.ranged_strength
        elif dt in Style.magic_damage_types:
            effective_accuracy_level = self.effective_magic_attack_level
            accuracy_bonus = ab.magic
            strength_bonus = ab.magic_strength
        else:
            raise StyleError(self.active_style)

        def process_variable_modifiers(*args: AttackRollModifier | DamageModifier | tuple[AttackRollModifier, DamageModifier] | None) -> tuple[list[AttackRollModifier], list[DamageModifier]]:
            """Inner function for processing the return values offered by modifier methods.

            Raises:
                TypeError: Raised if an illegal type is passed as an argument.

            Returns:
                tuple[list[AttackRollModifier], list[DamageModifier]]: 
            """
            filtered_arms: list[AttackRollModifier] = []
            filtered_dms: list[DamageModifier] = []

            for item in args:
                if isinstance(item, AttackRollModifier):
                    filtered_arms.append(item)
                elif isinstance(item, DamageModifier):
                    filtered_dms.append(item)
                elif isinstance(item, tuple):
                    arm, dm = item
                    filtered_arms.append(arm)
                    filtered_dms.append(dm)
                elif item is None:
                    continue
                else:
                    raise TypeError(item)

            return filtered_arms, filtered_dms

        # basic attack roll and damage modifiers
        salve_modifiers = self._salve_modifier(other)
        slayer_modifiers = self._slayer_modifier(other)
        
        # Only one of slayer or salve bonus is allowed
        if salve_modifiers is not None:
            slayer_or_salve_modifiers = salve_modifiers
        elif slayer_modifiers is not None:
            slayer_or_salve_modifiers = slayer_modifiers
        else:
            slayer_or_salve_modifiers = None
        
        # Attack roll & damage modifiers
        crystal_modifiers = self._crystal_armor_modifier()
        arclight_modifiers = self._arclight_modifier(other)
        draconic_modifiers = self._draconic_modifier(other)
        wilderness_modifiers = self._wilderness_modifier(other)
        twisted_bow_modifiers = self._twisted_bow_modifier(other)
        obsidian_modifiers = self._obsidian_modifier()
        inquisitor_modifiers = self._inquisitor_modifier()

        # attack roll modifiers
        chinchompa_arm = self._chin_attack_roll_modifier(distance)

        # damage modifiers
        berserker_dm = self._berserker_necklace_damage_modifier()
        guardians_dm = self._guardians_damage_modifier(other)
        ice_demon_dm = self._ice_demon_damage_modifier(other, spell)
        tome_dm = self._tome_of_fire_damage_modifier(spell)

        # unique or tricky modifiers and bonuses
        smoke_arm, smoke_magic_damage_gear_bonus = self._smoke_modifier(spell)
        chaos_gauntlet_bonus_damage = self._chaos_gauntlets_flat_damage_bonus(spell)
        
        attack_roll_modifiers, damage_modifiers = process_variable_modifiers(
            slayer_or_salve_modifiers,
            crystal_modifiers,
            arclight_modifiers,
            draconic_modifiers,
            wilderness_modifiers,
            twisted_bow_modifiers,
            obsidian_modifiers,
            inquisitor_modifiers,
            chinchompa_arm,
            berserker_dm,
            guardians_dm,
            ice_demon_dm,
            tome_dm,
            smoke_arm,
        )

        # basic damage parameters, true in the general case, overwritten otherwise
        att_roll = self.maximum_roll(effective_accuracy_level, accuracy_bonus, *attack_roll_modifiers)
        def_roll = other.defence_roll(self)
        accuracy = self.accuracy(att_roll, def_roll)
        max_hit = self.max_hit(other, spell)    # base max

        # max hit calculation
        if dt in Style.melee_damage_types or dt in Style.ranged_damage_types:
            max_hit = self.static_max_hit(max_hit, *damage_modifiers)
        elif dt in Style.magic_damage_types:
            if chaos_gauntlet_bonus_damage is not None:
                max_hit = max_hit + chaos_gauntlet_bonus_damage

            gear_bonus_dm = DamageModifier(1 + strength_bonus + smoke_magic_damage_gear_bonus, 'gear')

            _, damage_modifiers = process_variable_modifiers(
                gear_bonus_dm,
                slayer_or_salve_modifiers,
                tome_dm,
                ice_demon_dm
            )
            max_hit = self.static_max_hit(max_hit, *damage_modifiers)   # max hit before special modifiers

        hitpoints_cap: int = other.active_levels.hitpoints
        attack_speed = self.attack_speed(spell)
        damage = None

        # Each sub-branch of the decision tree is handled via Equipment properties. By using these, we
        # standardize the conditions under which Normal & Special Attack behavior is defined and applied, and override
        # whichever Damage construction components we need to.
        if not (self.equipment.crossbow and self.equipment.enchanted_bolts_equipped):
            # General Special Weapons
            if special_attack:
                special_arms: list[AttackRollModifier] = []
                special_dms: list[DamageModifier] = []
                hs = None

                if self.equipment.dorgeshuun_special_weapon:   # Bone Dagger: Backstab & Dorgeshuun Crossbow: Snipe
                    accuracy = 1 if other.last_attacked_by != self else accuracy
                elif self.equipment.abyssal_bludgeon:
                    pp_missing = min([0, self.levels.prayer - self.active_levels.prayer])
                    dm = DamageModifier(1 + special_attack*(0.005 * pp_missing), 'Abyssal bludgeon: Penance')
                    special_dms.append(dm)
                elif self.equipment.dragon_claws:    # Dragon Claws: Slice and Dice
                    # scenario A: first attack is successful (4-2-1-1)
                    p_A = accuracy
                    min_hit_A = math.floor(max_hit.value / 2)
                    max_hit_A = max_hit.value - 1

                    dmg_val_A1 = list(range(min_hit_A, max_hit_A + 1))
                    dmg_val_A2 = [math.floor(dmg/2) for dmg in dmg_val_A1]
                    dmg_val_A3 = [math.floor(dmg/2) for dmg in dmg_val_A2]
                    dmg_val_A4 = [dmg for dmg in dmg_val_A3]    # TODO: probability of the 1 ocurring?
                    n_A = len(dmg_val_A1)

                    # scenario B: second attack is successful (0-4-2-2)
                    p_B = accuracy * (1 - accuracy)
                    min_hit_B = math.floor(max_hit.value * 3/8)
                    max_hit_B = math.floor(max_hit.value * 7/8)

                    dmg_val_B2 = list(range(min_hit_B, max_hit_B + 1))
                    dmg_val_B3 = [math.floor(dmg/2) for dmg in dmg_val_B2]
                    dmg_val_B4 = [dmg for dmg in dmg_val_A3]
                    n_B = len(dmg_val_B2)

                    # scenario C: third attack is successful (0-0-3-3)
                    p_C = accuracy * (1 - accuracy)**2
                    min_hit_C = math.floor(max_hit.value * 1/4)
                    max_hit_C = math.floor(max_hit.value * 3/4)

                    dmg_val_C3 = list(range(min_hit_C, max_hit_C + 1))
                    dmg_val_C4 = [dmg for dmg in dmg_val_C3]
                    n_C = len(dmg_val_C3)

                    # scenario D: fourth attack is successful (0-0-0-5)
                    p_D = accuracy * (1 - accuracy)**3
                    min_hit_D = math.floor(max_hit.value * 1/4)
                    max_hit_D = math.floor(max_hit.value * 5/4)

                    dmg_val_D4 = list(range(min_hit_D, max_hit_D + 1))
                    n_D = len(dmg_val_D4)

                    # scenario E: The big buh (0-0-0-0)
                    p_E = (1 - accuracy)**4
                    assert sum([p_A, p_B, p_C, p_D, p_E]) == 1

                    # Hitsplat 1
                    hs_1_min = 0
                    hs_1_max = max_hit_A
                    hs_1_dmg = np.arange(hs_1_min, hs_1_max+1)
                    hs_1_prb = np.zeros(shape=hs_1_dmg.shape)

                    hs_1_prb[0] = p_B + p_C + p_D + p_E
                    for idx, dv in enumerate(hs_1_dmg):
                        if dv in dmg_val_A1:
                            hs_1_prb[idx] += p_A / n_A

                    # Hitsplat 2
                    hs_2_min = 0
                    hs_2_max = max_hit_B
                    hs_2_dmg = np.arange(hs_2_min, hs_2_max+1)
                    hs_2_prb = np.zeros(shape=hs_2_dmg.shape)

                    hs_2_prb[0] = p_C + p_D + p_E
                    for idx, dv in enumerate(hs_2_dmg):
                        if dv in dmg_val_A2:
                            hs_2_prb[idx] += p_A / n_A
                        
                        if dv in dmg_val_B2:
                            hs_2_prb[idx] += p_B / n_B
                    
                    # Hitsplat 3
                    hs_3_min = 0
                    hs_3_max = max_hit_C
                    hs_3_dmg = np.arange(hs_3_min, hs_3_max+1)
                    hs_3_prb = np.zeros(shape=hs_3_dmg.shape)

                    hs_3_prb[0] += p_D + 0.5*p_E
                    hs_3_prb[1] += 0.5*p_E
                    for idx, dv in enumerate(hs_3_dmg):
                        if dv in dmg_val_A3:
                            hs_3_prb[idx] += p_A / n_A
                        
                        if dv in dmg_val_B3:
                            hs_3_prb[idx] += p_B / n_B
                        
                        if dv in dmg_val_C3:
                            hs_3_prb[idx] += p_C / n_C
                    
                    # Hitsplat 4
                    hs_4_min = 0
                    hs_4_max = max_hit_D
                    hs_4_dmg = np.arange(hs_4_min, hs_4_max+1)
                    hs_4_prb = np.zeros(shape=hs_4_dmg.shape)

                    hs_4_prb[0] += 0.5*p_E
                    hs_4_prb[1] += 0.5*p_E
                    for idx, dv in enumerate(hs_4_dmg):
                        if dv in dmg_val_A4:
                            hs_4_prb[idx] += p_A / n_A
                    
                        if dv in dmg_val_B4:
                            hs_4_prb[idx] += p_B / n_B
                        
                        if dv in dmg_val_C4:
                            hs_4_prb[idx] += p_C / n_C
                        
                        if dv in dmg_val_D4:
                            hs_4_prb[idx] += p_D / n_D
                    
                    hs = [Hitsplat(dmg, prb, hitpoints_cap) for dmg, prb in [
                        (hs_1_dmg, hs_1_prb),
                        (hs_2_dmg, hs_2_prb),
                        (hs_3_dmg, hs_3_prb),
                        (hs_4_dmg, hs_4_prb),
                    ]]

                elif self.equipment.abyssal_dagger:
                    special_arms = wp.special_attack_roll_modifiers
                    special_dms = wp.special_damage_modifiers
                    defence_roll_dt = wp.special_defence_roll if wp.special_defence_roll else dt

                    all_arms = attack_roll_modifiers.extend(special_arms)
                    att_roll = self.maximum_roll(effective_accuracy_level, accuracy_bonus, *all_arms)
                    def_roll = other.defence_roll(self, defence_roll_dt)
                    accuracy = self.accuracy(att_roll, def_roll)
                    max_hit = self.static_max_hit(max_hit, *special_dms)

                    hs_1 = Hitsplat.from_max_hit_acc(max_hit, accuracy, hitpoints_cap)

                    dmg_2 = np.arange(0, max_hit+1)
                    prb_2 = np.zeros(shape=dmg_2.shape)
                    n_2 = dmg_2.size
                    prb_2[0] += (1 - accuracy)    # second attack will always miss if the first does
                    for idx, dv in enumerate(dmg_2):
                        prb_2[idx] += accuracy**2 / n_2
                    
                    hs_2 = Hitsplat(dmg_2, prb_2, hitpoints_cap)
                    hs = [hs_1, hs_2]
                
                elif self.equipment.dragon_dagger:
                    special_arms = wp.special_attack_roll_modifiers
                    special_dms = wp.special_damage_modifiers
                    defence_roll_dt = wp.special_defence_roll if wp.special_defence_roll else dt

                    all_arms = attack_roll_modifiers.extend(special_arms)
                    att_roll = self.maximum_roll(effective_accuracy_level, accuracy_bonus, *all_arms)
                    def_roll = other.defence_roll(self, defence_roll_dt)
                    accuracy = self.accuracy(att_roll, def_roll)
                    max_hit = self.static_max_hit(max_hit, *special_dms)
                    hs = [Hitsplat.from_max_hit_acc(max_hit, accuracy, hitpoints_cap) for _ in range(2)]

                else:   # For non-specific special attack behavior
                    special_arms = wp.special_attack_roll_modifiers
                    special_dms = wp.special_damage_modifiers
                    defence_roll_dt = wp.special_defence_roll if wp.special_defence_roll else dt
                    
                    all_arms = attack_roll_modifiers.extend(special_arms)
                    att_roll = self.maximum_roll(effective_accuracy_level, accuracy_bonus, *all_arms)
                    def_roll = other.defence_roll(self, defence_roll_dt)
                    accuracy = self.accuracy(att_roll, def_roll)
                
                if damage is None:  # create Damage under variable conditions
                    if hs is not None:
                        damage = Damage(attack_speed, *hs)
                    else:
                        if special_dms:
                            max_hit = self.static_max_hit(max_hit, *special_dms)

                        damage = Damage.from_max_hit_acc(max_hit, accuracy, attack_speed, hitpoints_cap)

            # General Normal Weapons
            else:
                # definition / cases
                if self.equipment.scythe_of_vitur:
                    mh = tuple(math.floor(max_hit*2**modifier_power) for modifier_power in range(0, -3, -1))
                    hs = [Hitsplat.from_max_hit_acc(adj_mh, accuracy, hitpoints_cap) for adj_mh in mh]
                elif self.equipment.chinchompas and additional_targets:
                    max_targets = 9 if isinstance(other, Player) else 11
                    if isinstance(additional_targets, int):
                        targets = min([1 + additional_targets, max_targets])
                        hs = [Hitsplat.from_max_hit_acc(max_hit, accuracy, hitpoints_cap) for _ in range(targets)]
                    elif isinstance(additional_targets, Character):
                        additional_targets = [additional_targets]
                        targets = [other] + additional_targets
                        targets = targets if len(targets) <= max_targets else targets[:max_targets]
                        hs = [Hitsplat.from_max_hit_acc(max_hit, accuracy, t.active_levels.hitpoints) for t in targets]
                    else:
                        raise NotImplementedError
                
                # cleanup
                if hs:
                    damage = Damage(attack_speed, *hs)
                elif damage is None:
                    damage = Damage.from_max_hit_acc(max_hit, accuracy, attack_speed, hitpoints_cap)

        # Ammuntion / Bolt effects transcend Special Attack binary (Zaryte Crossbow especially), handle them here
        else:
            def modified_proc_chance(base_activation_chance: float):
                activation_chance = base_activation_chance

                if self.equipment.armadyl_crossbow and special_attack:
                    activation_chance = 2 * activation_chance
                
                if self.kandarin_hard:
                    activation_chance += (1/10) * base_activation_chance
                
                return activation_chance


            if self.equipment.enchanted_diamond_bolts:
                # TODO: Pester wiki admins about adding generic bolt_activation_chance for ammunition slot :3
                proc_chance = modified_proc_chance(0.10)

                damage_modifier = 1.15 + 0.015*self.equipment.zaryte_crossbow   # Ammunition Effect: Armour Piercing
                effect_max_hit = math.floor(damage_modifier * max_hit)

                damage_values = np.arange(effect_max_hit + 1)
                probabilities = np.zeros(damage_values.shape)

                for index, dv in enumerate(damage_values):
                    # each damage value assigned probability weights from unique
                    p_miss = (1 - modified_proc_chance) * (1 - accuracy) if dv == 0 else 0
                    p_norm = 0 if dv > max_hit else (1 - modified_proc_chance) * accuracy * 1 / (max_hit + 1)
                    p_effect = 0 if dv > effect_max_hit else modified_proc_chance * 1 / (effect_max_hit + 1)
                    probabilities[index] = p_miss + p_norm + p_effect

            elif self.equipment.enchanted_ruby_bolts:
                # TODO: Pester wiki admins about adding generic bolt_activation_chance for ammunition slot :3
                proc_chance = modified_proc_chance(0.06)
                target_hp = other.active_levels.hitpoints
                max_effective_hp = 500
                hp_ratio = 0.20 + 0.02*self.equipment.zaryte_crossbow

                effect_damage = min(map(lambda hp: math.floor(hp_ratio*hp), [max_effective_hp, target_hp]))
                true_max = max([max_hit, effect_damage])

                damage_values = np.arange(true_max+1)
                probabilities = np.zeros(damage_values.shape)

                for index, dv in enumerate(damage_values):
                    p_miss = 0 if dv > 0 else (1 - proc_chance) * (1 - accuracy)
                    p_norm = 0 if dv > max_hit else (1 - proc_chance) * accuracy * 1 / (max_hit + 1)
                    p_effect = proc_chance if dv == effect_damage else 0
                    probabilities[index] = p_miss + p_norm + p_effect

            else:
                raise NotImplementedError

            damage = Damage(attack_speed, Hitsplat(damage_values, probabilities, hitpoints_cap))

        # Full generic cases with no extra special behavior needed
        if damage is None:
            if hs is None:
                damage = Damage.from_max_hit_acc(max_hit, accuracy, attack_speed, hitpoints_cap)
            else:
                damage = Damage(attack_speed, *hs)

        return damage

    def attack(self, other: Character, special_attack: bool = False, distance: int = None, spell: Spell = None,
               additional_targets: int | Character | list[Character] = 0, **kwargs):
        dam = self.damage_distribution(other, special_attack, distance, spell, additional_targets, **kwargs)
        random_value = dam.random(attempts=1)
        other.damage(self, *random_value)

        if self.equipment.blood_fury and np.random.random() < (blood_fury_activation_chance := 0.20):
            self.heal(math.floor(random_value*0.30), overheal=False)

    def reset_stats(self):
        self.active_levels = self.levels.to_unbounded()
        self.run_energy = 10000
        self.special_energy = 100
        self.special_energy_counter = 0

    def boost(self, *effects: Boost | BoostCollection):
        for effect in effects:
            effect_coll = effect if isinstance(effect, BoostCollection) else BoostCollection(boosts=(effect, ))

            for b in effect_coll.boosts:
                boosted_from_base = self.levels + b

                differential = boosted_from_base - self.levels
                boosted_from_active = self.active_levels + differential

                for skill in astuple(Skills):
                    boosted_level = min((
                        boosted_from_base.__getattribute__(skill),
                        boosted_from_active.__getattribute__(skill)
                    ))
                    self.active_levels.__setattr__(skill, boosted_level)

    def pray(self, *prayers: Prayer | PrayerCollection):
        self.prayers.pray(*prayers)

    def regenerate_special_attack(self):
        self.special_energy += 10

    def update_special_energy_counter(self, ticks: int = 1):
        self.special_energy_counter += ticks
        if self.special_energy_counter >= 50:   # 30 seconds / 50 ticks
            self.special_energy_counter = 0
            self.regenerate_special_attack()

    def cast_energy_transfer(self, other: Player):
        if self.special_energy_full and self.active_levels.hitpoints > 10:
            self.active_levels.hitpoints -= 10

            self.special_energy = 0
            other.special_energy = 100

            self.special_energy_counter = 0
            other.special_energy_counter = 0
        else:
            raise PlayerError(f'{self.special_energy=}, {self.active_levels.hitpoints}')


# noinspection PyArgumentList
@define(**character_attrs_settings)
class Monster(Character):
    levels: MonsterCombatLevels = field(validator=validators.instance_of(MonsterCombatLevels), repr=False)
    active_levels: MonsterCombatLevels = field(init=False, validator=validators.instance_of(MonsterCombatLevels), repr=False)
    aggressive_bonus: AggressiveStats = field(validator=validators.instance_of(AggressiveStats), repr=False)
    defensive_bonus: DefensiveStats = field(validator=validators.instance_of(DefensiveStats), repr=False)
    styles: NpcAttacks = field(init=False, validator=validators.instance_of(NpcAttacks), repr=False)
    active_style: NpcStyle = field(init=False, validator=validators.instance_of(NpcStyle), repr=False)
    location: str = field(factory=None, repr=False)
    exp_modifier: float = field(default=1, repr=False)
    combat_level: int = field(default=None, repr=False)
    defence_floor: int = field(default=0, repr=False)
    special_attributes: tuple[str, ...] = field(factory=tuple, repr=True)

    def __attrs_post_init__(self):
        self.active_levels = copy(self.levels)
        self.styles = NpcAttacks('', (NpcStyle.default_style(), ))
        self.active_style = NpcStyle.default_style()

    def reset_stats(self):
        self.active_levels = copy(self.levels)

    @property
    def effective_melee_attack_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.attack
        return self.effective_accuracy_level(self.active_levels.attack, style_bonus)

    @property
    def effective_melee_strength_level(self) -> int:
        monster_jank_bonus = 8
        style_bonus = self.active_style.combat_bonus.strength + monster_jank_bonus
        return self.effective_strength_level(self.active_levels.strength, style_bonus)

    @property
    def effective_defence_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.defence
        return self.effective_accuracy_level(self.active_levels.defence, style_bonus)

    @property
    def effective_ranged_attack_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.ranged
        return self.effective_accuracy_level(self.active_levels.ranged, style_bonus)

    @property
    def effective_ranged_strength_level(self) -> int:
        monster_jank_bonus = 8
        style_bonus = self.active_style.combat_bonus.ranged + monster_jank_bonus
        return self.effective_strength_level(self.active_levels.ranged, style_bonus)

    @property
    def effective_magic_attack_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.magic
        return self.effective_accuracy_level(self.active_levels.magic, style_bonus)

    @property
    def effective_magic_strength_level(self) -> int:
        monster_jank_bonus = 8
        style_bonus = self.active_style.combat_bonus.magic + monster_jank_bonus
        return self.effective_strength_level(self.active_levels.magic, style_bonus)

    @property
    def effective_magic_defence_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.magic
        return self.effective_accuracy_level(self.active_levels.magic, style_bonus)

    @staticmethod
    def base_damage(effective_strength_level: int, strength_bonus: int) -> float:
        """
        De0 formula for monster max hit
        """
        base_damage = (math.floor(effective_strength_level * (strength_bonus+64)/64) + 5) / 10
        return base_damage

    def max_hit(self, other: Player) -> int:
        aggressive_cb = self.aggressive_bonus

        if (dt := self.active_style.damage_type) in Style.melee_damage_types or dt in Style.ranged_damage_types:
            if dt in Style.melee_damage_types:
                effective_level = self.effective_melee_strength_level
                bonus = aggressive_cb.melee_strength
            else:
                effective_level = self.effective_ranged_strength_level
                bonus = aggressive_cb.ranged_strength

            base_damage = self.base_damage(effective_level, bonus)
            all_roll_modifiers = []
            active_roll_modifiers = [float(x) for x in all_roll_modifiers if not x == 1]
            max_hit = self.static_max_hit(base_damage, *active_roll_modifiers)

        elif dt in Style.magic_damage_types:
            effective_level = self.effective_magic_attack_level
            bonus = aggressive_cb.magic_strength
            base_damage = self.base_damage(effective_level, bonus)
            max_hit = math.floor(base_damage)

        elif dt in Style.typeless_damage_types:
            raise NotImplementedError

        else:
            raise StyleError(f'{self.active_style.damage_type=}')

        prot_prayers = other.prayers.prayers
        if dt in Style.melee_damage_types and Prayer.protect_from_melee() in prot_prayers:
            modifier = 0.5 if self.active_style.ignores_prayer else 0
        elif dt in Style.ranged_damage_types and Prayer.protect_from_missiles() in prot_prayers:
            modifier = 0.5 if self.active_style.ignores_prayer else 0
        elif dt in Style.magic_damage_types and Prayer.protect_from_magic() in prot_prayers:
            modifier = 0.5 if self.active_style.ignores_prayer else 0
        else:
            modifier = 1

        max_hit = math.floor(max_hit * modifier)

        return max_hit

    def damage_distribution(self, other: Player, **kwargs) -> Damage:
        dt = self.active_style.damage_type
        assert dt in PlayerStyle.all_damage_types

        att_roll = self.attack_roll(other)
        def_roll = other.defence_roll(self)
        accuracy = self.accuracy(att_roll, def_roll)

        max_hit = self.max_hit(other)
        hitpoints_cap = other.active_levels.hitpoints
        attack_speed = self.active_style.attack_speed

        elysian_reduction_modifier = 0.25 if other.equipment.elysian_spirit_shield else 0
        sotd_reduction_modifier = 0.5 if dt in Style.melee_damage_types and other.staff_of_the_dead_effect and \
            other.equipment.staff_of_the_dead else 0

        justiciar_style_bonus = other.equipment.defensive_bonus.__getattribute__(dt)
        justiciar_style_bonus_cap = 3000
        justiciar_reduction_modifier = justiciar_style_bonus/justiciar_style_bonus_cap if \
            other.equipment.justiciar_set else 0

        dinhs_reduction_modifier = 0.20 if other.equipment.dinhs_bulwark and \
            other.active_style == BulwarkStyles.get_style(PlayerStyle.block) else 0

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

            damage_values = np.arange(unactivated_max+1)
            probabilities = np.zeros(damage_values.shape)
            probabilities[0] += 1 - accuracy

            for unreduced_hit in range(0, unreduced_max+1):
                unactivated_damage = reduced_hit(unreduced_hit, False)
                activated_damage = reduced_hit(unreduced_hit, True)

                probabilities[activated_damage] += activation_chance * unreduced_hit_chance
                probabilities[unactivated_damage] += (1 - activation_chance) * unreduced_hit_chance

            damage = Damage(attack_speed, Hitsplat(damage_values, probabilities, hitpoints_cap), **kwargs)

        else:
            unreduced_max = max_hit
            reduced_max = reduced_hit(unreduced_max)
            unreduced_hit_chance = accuracy * (1 / (unreduced_max + 1))

            damage_values = np.arange(reduced_max+1)
            probabilities = np.zeros(damage_values.shape)
            probabilities[0] += 1 - accuracy

            for unreduced_hit in range(0, unreduced_max+1):
                reduced_damage = reduced_hit(unreduced_hit)
                probabilities[reduced_damage] += unreduced_hit_chance

            damage = Damage(attack_speed, Hitsplat(damage_values, probabilities, hitpoints_cap), **kwargs)

        return damage

    @classmethod
    def from_bb(cls, name: str, **kwargs):

        options = {
            'ignores_defence': False,
            'ignores_prayer': False,
            'attack_speed_modifier': False,
            'attack_range_modifier': False,
            'style_index': 0,
            'defence_floor': 0,
        }
        options.update(kwargs)

        name = name.lower()
        mon_df = rr.lookup_normal_monster_by_name(name)

        if mon_df['location'].values[0] == 'raids':
            raise MonsterError(f'{name=} must be an instance of {CoxMonster}')

        # attack style parsing
        damage_types_str: str = mon_df['main attack style'].values[0]
        damage_types = damage_types_str.split(' and ')
        styles = []

        for dt in damage_types:
            if not dt:
                continue

            styles.append(NpcStyle(
                damage_type=dt,
                name=dt,
                attack_speed=mon_df['attack speed'].values[0],
                ignores_defence=options['ignores_defence'],
                ignores_prayer=options['ignores_prayer'],
                attack_speed_modifier=options['attack_speed_modifier'],
                attack_range_modifier=options['attack_range_modifier'],
            ))

        attack_styles = NpcAttacks(name=damage_types_str, styles=tuple(styles))
        if len(attack_styles.styles) > 0:
            active_style = attack_styles.styles[0]
        else:
            active_style = NpcStyle.default_style()

        # type parsing
        raw_type_value = mon_df['type'].values[0]
        special_attributes = []

        if raw_type_value == 'demon':
            special_attributes.append(MonsterTypes.demon)
        elif raw_type_value == 'dragon':
            special_attributes.append(MonsterTypes.draconic)
        elif raw_type_value == 'fire':
            special_attributes.append(MonsterTypes.fiery)
        elif raw_type_value == 'kalphite':
            special_attributes.append(MonsterTypes.kalphite)
        elif raw_type_value == 'kurask':
            special_attributes.append(MonsterTypes.leafy)
        elif raw_type_value == 'vorkath':
            special_attributes.extend([MonsterTypes.leafy, MonsterTypes.undead])
        elif raw_type_value == 'undead':
            special_attributes.append(MonsterTypes.undead)
        elif raw_type_value == 'vampyre - tier 1':
            special_attributes.extend([MonsterTypes.vampyre, MonsterTypes.vampyre_tier_1])
        elif raw_type_value == 'vampyre - tier 2':
            special_attributes.extend([MonsterTypes.vampyre, MonsterTypes.vampyre_tier_2])
        elif raw_type_value == 'vampyre - tier 3':
            special_attributes.extend([MonsterTypes.vampyre, MonsterTypes.vampyre_tier_3])
        elif raw_type_value == 'guardian':
            raise MonsterError(f'{name=} must be an instance of {Guardian}')
        elif raw_type_value == '':
            pass
        else:
            raise MonsterError(f'{name=} {raw_type_value=} is an unsupported or undefined type')

        exp_modifier = 1 + mon_df['exp bonus'].values[0]

        return cls(
            name=name,
            levels=MonsterCombatLevels.from_bb(name),
            aggressive_bonus=AggressiveStats.from_bb(name),
            defensive_bonus=DefensiveStats.from_bb(name),
            styles=attack_styles,
            active_style=active_style,
            location=mon_df['location'].values[0],
            exp_modifier=exp_modifier,
            combat_level=mon_df['combat level'].values[0],
            defence_floor=options['defence_floor'],
            special_attributes=tuple(special_attributes),
            **options
        )


# noinspection PyArgumentList
@define(**character_attrs_settings)
class CoxMonster(Monster):
    party_size: int = field()
    location: str = field(factory=None, repr=False)
    exp_modifier: float = field(default=1, repr=False)
    combat_level: int = field(default=None, repr=False)
    defence_floor: int = field(default=0, repr=False)
    special_attributes: tuple[str, ...] = field(factory=tuple, repr=False)
    challenge_mode: bool = field(default=False)
    party_max_combat_level: int = field(default=126, repr=False)
    party_max_hitpoints_level: int = field(default=99, repr=False)
    party_average_mining_level: int = field(default=99, repr=False)
    points_per_hitpoint: float = field(default=4.15, repr=False, init=False)

    def __str__(self):
        message = f'{self.name} ({self.party_size})'
        return message

    def __attrs_post_init__(self):
        self.levels = self._convert_cox_combat_levels()
        self.active_levels = copy(self.levels)
        self.styles = NpcAttacks('', (NpcStyle.default_style(), ))
        self.active_style = NpcStyle.default_style()

    def player_hp_scaling_factor(self):
        return self.party_max_combat_level / Player.max_combat_level()

    def player_offensive_defensive_scaling_factor(self):
        return (math.floor(self.party_max_hitpoints_level * 4 / 9) + 55) / 99

    def party_hp_scaling_factor(self):
        n = self.party_size
        return 1 + math.floor(n / 2)

    def party_offensive_scaling_factor(self):
        n = self.party_size
        return (7 * math.floor(math.sqrt(n - 1)) + (n - 1) + 100) / 100

    def party_defensive_scaling_factor(self):
        n = self.party_size
        return (math.floor(math.sqrt(n - 1)) + math.floor((7/10) * (n - 1)) + 100) / 100

    def challenge_mode_hp_scaling_factor(self):
        factor = 3/2 if self.challenge_mode else 1
        return factor

    def challenge_mode_offensive_scaling_factor(self):
        factor = 3/2 if self.challenge_mode else 1
        return factor

    def challenge_mode_defensive_scaling_factor(self):
        factor = 3/2 if self.challenge_mode else 1
        return factor

    @staticmethod
    def get_base_levels_and_stats(name: str) -> tuple[MonsterCombatLevels, AggressiveStats, DefensiveStats]:
        mon_df = rr.get_cox_monster_base_stats_by_name(name)

        levels = MonsterCombatLevels(
            attack=mon_df['melee'].values[0],
            strength=mon_df['melee'].values[0],
            defence=mon_df['defence'].values[0],
            ranged=mon_df['ranged'].values[0],
            magic=mon_df['magic'].values[0],
            hitpoints=mon_df['hp'].values[0],
        )
        aggressive_melee_bonus = mon_df['melee att+'].values[0]
        aggressive_bonus = AggressiveStats(
            stab=aggressive_melee_bonus,
            slash=aggressive_melee_bonus,
            crush=aggressive_melee_bonus,
            magic=mon_df['magic att+'].values[0],
            ranged=mon_df['ranged att+'].values[0],
            melee_strength=mon_df['melee str+'].values[0],
            ranged_strength=mon_df['ranged str+'].values[0],
            magic_strength=mon_df['magic str+'].values[0]
        )
        defensive_bonus = DefensiveStats(
            stab=mon_df['stab def+'].values[0],
            slash=mon_df['slash def+'].values[0],
            crush=mon_df['crush def+'].values[0],
            magic=mon_df['magic def+'].values[0],
            ranged=mon_df['ranged def+'].values[0]
        )
        return levels, aggressive_bonus, defensive_bonus

    @classmethod
    def from_bb(cls, name: str, **kwargs):
        raise MonsterError(f'{name=} must be instantiated as a {CoxMonster}, see {CoxMonster.from_de0}')

    @classmethod
    def from_de0(
            cls,
            name: str,
            party_size: int,
            challenge_mode: bool = False,
            *special_attributes: str,
            **kwargs,
    ):

        if name == 'great olm':
            return OlmHead.from_de0(party_size, challenge_mode, **kwargs)
        elif name == 'great olm (left/melee claw)':
            return OlmMeleeHand.from_de0(party_size, challenge_mode, **kwargs)
        elif name == 'great olm (right/mage claw)':
            return OlmMageHand.from_de0(party_size, challenge_mode, **kwargs)
        elif name == 'guardian':
            options = {'party_average_mining_level': PlayerLevels.max_skill_level}
            options.update(kwargs)
            return Guardian.from_de0(party_size, challenge_mode, options['party_average_mining_level'], **options)
        elif name == 'skeletal mystic':
            return SkeletalMystic.from_de0(party_size, challenge_mode, **kwargs)
        elif name == 'tekton':
            return Tekton.from_de0(party_size, challenge_mode, **kwargs)
        elif name == 'tekton (enraged)':
            return TektonEnraged.from_de0(party_size, challenge_mode, **kwargs)
        elif name == 'ice demon':
            return IceDemon.from_de0(party_size, challenge_mode, **kwargs)
        else:
            base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)

            cox_monster_attributes = list(special_attributes)
            if MonsterTypes.xerician not in cox_monster_attributes:
                cox_monster_attributes.append(MonsterTypes.xerician)
            cox_monster_attributes = tuple(cox_monster_attributes)

            return cls(
                name=name,
                levels=base_levels,
                aggressive_bonus=aggressive_bonus,
                defensive_bonus=defensive_bonus,
                location=MonsterLocations.cox,
                special_attributes=cox_monster_attributes,
                party_size=party_size,
                challenge_mode=challenge_mode,
                **kwargs
            )

    def count_per_room(self, **kwargs) -> int:
        raise NotImplementedError

    def points_per_room(self, **kwargs) -> int:
        return math.floor(self.count_per_room(**kwargs) * self.levels.hitpoints * self.points_per_hitpoint)

    def _convert_cox_combat_levels(self) -> MonsterCombatLevels:
        # order matters, floor each intermediate value

        hitpoints_scaled = math.floor(
            self.challenge_mode_hp_scaling_factor() * math.floor(
                self.party_hp_scaling_factor() * math.floor(
                    self.player_hp_scaling_factor() * self.levels.hitpoints
                )
            )
        )
        if isinstance(self, OlmHead):
            hitpoints_scaled = min([hitpoints_scaled, 13600])
        elif isinstance(self, OlmMeleeHand) or isinstance(self, OlmMageHand):
            hitpoints_scaled = min([hitpoints_scaled, 10200])

        # attack and strength
        melee_scaled = math.floor(
            self.challenge_mode_offensive_scaling_factor() * math.floor(
                self.party_offensive_scaling_factor() * math.floor(
                    self.player_offensive_defensive_scaling_factor() * self.levels.attack
                )
            )
        )

        magic_scaled = math.floor(
            self.challenge_mode_offensive_scaling_factor() * math.floor(
                self.party_offensive_scaling_factor() * math.floor(
                    self.player_offensive_defensive_scaling_factor() * self.levels.magic
                )
            )
        )

        ranged_scaled = math.floor(
            self.challenge_mode_offensive_scaling_factor() * math.floor(
                self.party_offensive_scaling_factor() * math.floor(
                    self.player_offensive_defensive_scaling_factor() * self.levels.ranged
                )
            )
        )

        defence_scaled = math.floor(
            self.challenge_mode_defensive_scaling_factor() * math.floor(
                self.party_defensive_scaling_factor() * math.floor(
                    self.player_offensive_defensive_scaling_factor() * self.levels.defence
                )
            )
        )

        return MonsterCombatLevels(
            attack=melee_scaled,
            strength=melee_scaled,
            defence=defence_scaled,
            ranged=ranged_scaled,
            magic=magic_scaled,
            hitpoints=hitpoints_scaled,
        )


# noinspection PyArgumentList
@define(**character_attrs_settings)
class IceDemon(CoxMonster):

    @property
    def effective_magic_defence_level(self) -> int:
        style_bonus = self.active_style.combat_bonus.magic
        return self.effective_accuracy_level(self.active_levels.defence, style_bonus)

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'ice demon'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, MonsterTypes.demon)

        return cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )


# noinspection PyARgumentList
@define(**character_attrs_settings)
class DeathlyRanger(CoxMonster):

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'deathly ranger'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, )

        attack_style = NpcStyle(
            PlayerStyle.ranged,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )

        ranger = cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )
        ranger.styles = NpcAttacks(ranger.name, (attack_style, ))
        ranger.active_style = ranger.styles.styles[0]
        return ranger

    def count_per_room(self) -> int:
        """
        source: @JagexAsh
        https://twitter.com/JagexAsh/status/1386459382834139136
        """
        count = np.floor(1 + self.party_size/5)
        count = min([count, 4])
        return count


# noinspection PyARgumentList
@define(**character_attrs_settings)
class DeathlyMage(CoxMonster):

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'deathly mage'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, )

        attack_style = NpcStyle(
            PlayerStyle.magic,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )

        mage = cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )
        mage.styles = NpcAttacks(mage.name, (attack_style,))
        mage.active_style = mage.styles.styles[0]
        return mage

    def count_per_room(self) -> int:
        """
        source: @JagexAsh
        https://twitter.com/JagexAsh/status/1386459382834139136
        """
        count = np.floor(1 + self.party_size/5)
        count = min([count, 4])
        return count


# noinspection PyArgumentList
@define(**character_attrs_settings)
class SkeletalMystic(CoxMonster):

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'skeletal mystic'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, MonsterTypes.undead)

        magic_style = NpcStyle(
            PlayerStyle.magic,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )
        melee_style = NpcStyle(
            PlayerStyle.crush,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )

        skeleton = cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )
        skeleton.styles = NpcAttacks(skeleton.name, (magic_style, melee_style))
        skeleton.active_style = magic_style
        return skeleton

    def count_per_room(self, scale_at_load_time: int = None, **kwargs) -> int:
        """
        source: @JagexAsh
        https://twitter.com/JagexAsh/status/1386459382834139136
        """
        scale_at_load_time = self.party_size if scale_at_load_time is None else scale_at_load_time

        count = math.floor(3 + scale_at_load_time/3)
        count = min([count, 12])
        return count


# noinspection PyArgumentList
@define(**character_attrs_settings)
class LizardmanShaman(CoxMonster):

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'lizardman shaman'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, )

        ranged_style = NpcStyle(
            PlayerStyle.ranged,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=False
        )
        melee_style = NpcStyle(
            PlayerStyle.crush,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=False
        )

        shaman = cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )
        shaman.styles = NpcAttacks(shaman.name, (ranged_style, melee_style))
        shaman.active_style = ranged_style
        return shaman

    def count_per_room(self, scale_at_load_time: int = None) -> int:
        """
        source: @JagexAsh
        https://twitter.com/JagexAsh/status/1386459382834139136
        """
        scale_at_load_time = self.party_size if scale_at_load_time is None else scale_at_load_time

        count = np.floor(2 + scale_at_load_time/5)
        count = min([count, 12])
        return count


# noinspection PyArgumentList
@define(**character_attrs_settings)
class Guardian(CoxMonster):

    def damage(self, other: Player, amount: int) -> int:
        if 'pickaxe' not in other.equipment.weapon.name:
            return 0
        else:
            damage_allowed = min([self.active_levels.hitpoints, amount])
            self.active_levels.hitpoints = max([0, self.active_levels.hitpoints - damage_allowed])
            return damage_allowed

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            party_average_mining_level: int = None,
            **kwargs,
    ):
        name = 'guardian'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician,)

        if party_average_mining_level:
            kwargs.update({'party_average_mining_level': party_average_mining_level})
        else:
            party_average_mining_level = PlayerLevels.max_skill_level

        reduction = party_average_mining_level
        base_levels.hitpoints = base_levels.hitpoints - (99 - reduction)

        return cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )

    @staticmethod
    def count_per_room() -> int:
        return 2


# noinspection PyArgumentList
@define(**character_attrs_settings)
class SmallMuttadile(CoxMonster):

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'muttadile (small)'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, )

        ranged_style = NpcStyle(
            Style.ranged,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )
        melee_style = NpcStyle(
            Style.crush,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=False
        )

        smol_mutta = cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )
        smol_mutta.styles = NpcAttacks(smol_mutta.name, (ranged_style, melee_style))
        smol_mutta.active_style = ranged_style
        return smol_mutta


# noinspection PyArgumentList
@define(**character_attrs_settings)
class BigMuttadile(CoxMonster):

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'muttadile (big)'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, )

        ranged_style = NpcStyle(
            Style.ranged,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )
        magic_style = NpcStyle(
            Style.magic,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )
        melee_style = NpcStyle(
            Style.crush,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=False
        )

        big_mutta = cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )
        big_mutta.styles = NpcAttacks(big_mutta.name, (ranged_style, magic_style, melee_style))
        big_mutta.active_style = ranged_style
        return big_mutta


# noinspection PyArgumentList
@define(**character_attrs_settings)
class Tekton(CoxMonster):
    # TODO: Tekton BGS & DWH corrections

    def challenge_mode_defensive_scaling_factor(self):
        _ = self    # avoid static warning
        return 12 / 10

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'tekton'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician,)

        return cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )


# noinspection PyArgumentList
@define(**character_attrs_settings)
class TektonEnraged(Tekton):

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'tekton (enraged)'
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician,)

        return cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )


def AbyssalPortal(CoxMonster):

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        raise NotImplementedError

    def party_offensive_scaling_factor(self):
        return self.defensive_scaling_factor()


# noinspection PyArgumentList
@define(**character_attrs_settings)
class Olm(CoxMonster, ABC):

    def player_hp_scaling_factor(self):
        _ = self
        return 1

    def player_offensive_defensive_scaling_factor(self):
        _ = self
        return 1

    def party_hp_scaling_factor(self):
        n = self.party_size
        return ((n + 1) - 3*math.floor(n/8)) / 2

    def challenge_mode_hp_scaling_factor(self):
        _ = self
        return 1

    def phases(self) -> int:
        return min([9, 3 + math.floor(self.party_size / 8)])

    @classmethod
    @abstractmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        pass

    def total_hitpoints(self, head: bool = True, melee: bool = True, mage: bool = True) -> int:
        """
        Returns the total HP of Olm throughout all phases as specified.
        :param head: Count the final (Head) phase HP.
        :param melee: Count each phase's melee hand HP.
        :param mage: Count each phase's mage hand HP.
        :return: olm_hitpoints: int
        """
        olm_hitpoints = 0
        scale = self.party_size
        cm = self.challenge_mode
        phases = self.phases()

        if head:
            olm_hitpoints += OlmHead.from_de0(scale, cm).levels.hitpoints

        if melee:
            olm_hitpoints += OlmMeleeHand.from_de0(scale, cm).levels.hitpoints * phases

        if mage:
            olm_hitpoints += OlmMageHand.from_de0(scale, cm).levels.hitpoints * phases

        return olm_hitpoints


# noinspection PyArgumentList
@define(**character_attrs_settings)
class OlmHead(Olm):

    def max_hit(self, other: Player, crippled: bool = False, enraged: bool = False, head_phase: bool = False) -> int:
        aggressive_cb = self.aggressive_bonus

        if (dt := self.active_style.damage_type) in Style.ranged_damage_types:
            effective_level = self.effective_ranged_strength_level
            bonus = aggressive_cb.ranged_strength
        elif dt in Style.magic_damage_types:
            effective_level = self.effective_magic_attack_level
            bonus = aggressive_cb.magic_strength
        elif dt in Style.typeless_damage_types:
            raise NotImplementedError
        else:
            raise StyleError(f'{self.active_style.damage_type=}')

        base_damage = self.base_damage(effective_level, bonus)

        def olm_max(x: float) -> int:
            return math.floor(
                math.floor(base_damage) * (x + min([6, math.floor(self.party_size / 8)])) / 100
            )

        if head_phase:
            max_hit = olm_max(112)
        elif enraged:
            max_hit = olm_max(108)
        elif crippled:
            max_hit = olm_max(105)
        else:
            max_hit = olm_max(100)

        prot_prayers = other.prayers.prayers
        if dt in Style.melee_damage_types and Prayer.protect_from_melee() in prot_prayers:
            prot_modifier = 0.5 if self.active_style.ignores_prayer else 0
        elif dt in Style.ranged_damage_types and Prayer.protect_from_missiles() in prot_prayers:
            prot_modifier = 0.5 if self.active_style.ignores_prayer else 0
        elif dt in Style.magic_damage_types and Prayer.protect_from_magic() in prot_prayers:
            prot_modifier = 0.5 if self.active_style.ignores_prayer else 0
        else:
            prot_modifier = 1

        max_hit = math.floor(max_hit * prot_modifier)

        return max_hit

    def count_per_room(self) -> int:
        _ = self
        return 1

    def chance_to_switch_style(self) -> float:
        """The probability that Olm will switch main attack styles, either from ranged to magic or magic to ranged.

        Returns:
            float: The probability that Olm will switch main attack styles, either from ranged to magic or magic to ranged.
        """
        return 0.75     # source: me: 1785 data points w/ 95% confidence interval (0.72, 0.76)

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'great olm'
        combat_level = 1043
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, MonsterTypes.draconic)

        ranged_style = NpcStyle(
            PlayerStyle.ranged,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )
        magic_style = NpcStyle(
            PlayerStyle.magic,
            attack_speed=4,
            ignores_defence=False,
            ignores_prayer=True
        )

        olm_head = cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            combat_level=combat_level,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )
        olm_head.styles = NpcAttacks(olm_head.name, (ranged_style, magic_style))
        olm_head.active_style = ranged_style
        return olm_head


# noinspection PyArgumentList
@define(**character_attrs_settings)
class OlmMeleeHand(Olm):

    def count_per_room(self) -> int:
        return self.phases()

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'great olm (left/melee claw)'
        combat_level = 750
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, MonsterTypes.draconic)

        return cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            combat_level=combat_level,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
        )

    def cripple(self):
        pass


# noinspection PyArgumentList
@define(**character_attrs_settings)
class OlmMageHand(Olm):

    def count_per_room(self) -> int:
        return self.phases()

    @classmethod
    def from_de0(
            cls,
            party_size: int,
            challenge_mode: bool = False,
            **kwargs,
    ):
        name = 'great olm (right/mage claw)'
        combat_level = 549
        base_levels, aggressive_bonus, defensive_bonus = cls.get_base_levels_and_stats(name)
        special_attributes = (MonsterTypes.xerician, MonsterTypes.draconic)

        return cls(
            name=name,
            levels=base_levels,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            location=MonsterLocations.cox,
            combat_level=combat_level,
            special_attributes=special_attributes,
            party_size=party_size,
            challenge_mode=challenge_mode,
            **kwargs
        )


class CharacterError(OsrsException):
    pass


class PlayerError(CharacterError):
    pass


class MonsterError(CharacterError):
    pass
