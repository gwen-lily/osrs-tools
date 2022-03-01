from .equipment import *
from .style import *
from .prayer import *
from .stats import *
from .damage import *
from .spells import *
from .exceptions import *
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


class ArmDmTuple(NamedTuple):
    """
    Tuple containing an attack roll modifier (ARM) and damage_multiplier(DM)
    """
    attack_roll_modifier: float
    damage_multiplier: float


@define(**character_attrs_settings)
class Character(ABC):
    name: str
    levels: Stats
    active_levels: Stats = field(init=False)
    # TODO: implement more general defence_floor with minimum_levels: Stats = field()

    def damage(self, other, amount: int):
        assert amount >= 0
        damage_allowed = min([self.active_levels.hitpoints, amount])
        self.active_levels.hitpoints = max([0, self.active_levels.hitpoints - damage_allowed])
        return damage_allowed

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
    def effective_attack_level(self) -> int:
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

    @abstractmethod
    def attack_roll(self, other, special_attack: bool = False) -> int:
        pass

    @abstractmethod
    def defence_roll(self, other, special_attack: bool = False):
        pass

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
    def maximum_roll(effective_level: int, aggressive_or_defensive_bonus: int, *roll_modifiers: float) -> int:
        """

        :param effective_level: A function of stat, (potion), prayers, other modifiers, and stance
        :param aggressive_or_defensive_bonus: The bonus a player gets from gear or monsters have innately
        :param roll_modifiers: A direct multiplier (or multipliers) on the roll, such as a BGS special attack.
        :return:
        """
        roll = effective_level * (aggressive_or_defensive_bonus + 64)
        for step in roll_modifiers:
            roll = math.floor(roll * step)

        return roll

    @staticmethod
    def accuracy(offensive_roll: int, defensive_roll: int) -> float:
        """

        :param offensive_roll: The maximum offensive roll of the attacker.
        :param defensive_roll: The maximum defensive roll of the defender.
        :return: Accuracy, or the chance that an attack is successful. This is NOT the chance to not deal 0 damage.
        """
        if offensive_roll > defensive_roll:
            return 1 - (defensive_roll + 2) / (2 * (offensive_roll + 1))
        else:
            return offensive_roll / (2 * (defensive_roll + 1))

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
    def static_max_hit(base_damage: float, *damage_modifiers: float) -> int:
        max_hit = math.floor(base_damage)
        for step in damage_modifiers:
            max_hit = math.floor(max_hit * step)

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

    def __attrs_post_init__(self):
        self.active_levels = self.levels.to_unbounded()
        self.active_style = self.equipment.weapon.weapon_styles.default

    def reset_stats(self):
        self.active_levels = self.levels.to_unbounded()

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
    def effective_attack_level(self) -> int:
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

    def _salve_modifier(self, other: Character) -> ArmDmTuple:
        if isinstance(other, Monster):
            if MonsterTypes.undead in other.special_attributes:
                if self.equipment.wearing(neck=Gear.from_bb('salve amulet (i)')):
                    modifier = 7/6
                elif self.equipment.wearing(neck=Gear.from_bb('salve amulet (ei)')):
                    modifier = 1.2
                else:
                    modifier = 1
            else:
                modifier = 1

        elif isinstance(other, Player):
            modifier = 1
        else:
            raise PlayerError(f'{other=}')

        return ArmDmTuple(modifier, modifier)

    def _slayer_modifier(self, other: Character) -> ArmDmTuple:
        if isinstance(other, Monster):
            if self.task:
                if self.equipment.wearing(head=Gear.from_bb('slayer helmet (i)')):
                    if (dt := self.active_style.damage_type) in Style.melee_damage_types:
                        modifier = 7/6
                    elif dt in Style.ranged_damage_types:
                        modifier = 1.15
                    elif dt in Style.magic_damage_types:
                        modifier = 1.15
                    else:
                        raise StyleError(f'{self.active_style.damage_type=}')
                # elif self.equipment.wearing(head=Gear.from_bb('slayer helmet')):
                #     raise NotImplemented('slayer helmet / black mask / black mask (i) / ...')
                else:
                    modifier = 1
            else:
                modifier = 1
        elif isinstance(other, Player):
            modifier = 1
        else:
            raise PlayerError(f'{other=}')

        return ArmDmTuple(modifier, modifier)

    def _arclight_modifier(self, other: Character) -> ArmDmTuple:
        if isinstance(other, Monster):
            arclight = SpecialWeapon.from_bb('arclight')
            modifier = 1.7 if MonsterTypes.demon in other.special_attributes and \
                              self.equipment.wearing(weapon=arclight) else 1
        elif isinstance(other, Player):
            modifier = 1
        else:
            raise PlayerError(f'{other=}')

        return ArmDmTuple(modifier, modifier)

    def _draconic_modifier(self, other: Character) -> ArmDmTuple:
        if isinstance(other, Monster):
            if MonsterTypes.draconic in other.special_attributes:
                if self.equipment.wearing(weapon=Weapon.from_bb('dragon hunter lance')):
                    modifier = 1.2
                elif self.equipment.wearing(weapon=Weapon.from_bb('dragon hunter crossbow')):
                    modifier = 1.3
                else:
                    modifier = 1
            else:
                modifier = 1

        elif isinstance(other, Player):
            modifier = 1
        else:
            raise PlayerError(f'{other=}')

        return ArmDmTuple(modifier, modifier)

    def _wilderness_modifier(self, other: Character) -> ArmDmTuple:
        if isinstance(other, Monster):
            if other.location == MonsterLocations.wilderness:
                if self.equipment.wearing(weapon=Weapon.from_bb("craw's bow")):
                    arm = 1.5
                    sm = 1.5
                elif self.equipment.wearing(weapon=Weapon.from_bb("viggora's chainmace")):
                    arm = 1.5
                    sm = 1.5
                elif self.equipment.wearing(weapon=Weapon.from_bb("thammaron's sceptre")):
                    arm = 2
                    sm = 1.25
                else:
                    arm = 1
                    sm = 1
            else:
                arm = 1
                sm = 1

        elif isinstance(other, Player):
            arm = 1
            sm = 1
        else:
            raise PlayerError(f'{other=}')

        return ArmDmTuple(arm, sm)

    def _twisted_bow_modifier(self, other: Character) -> ArmDmTuple:
        if self.equipment.wearing(weapon=Weapon.from_bb('twisted bow')):
            accuracy_modifier_ceiling = 1.40
            damage_modifier_ceiling = 2.50

            if isinstance(other, Monster):
                if MonsterTypes.xerician in other.special_attributes:
                    magic_ceiling = 350
                else:
                    magic_ceiling = 250
            elif isinstance(other, CoxMonster):
                magic_ceiling = 350
            elif isinstance(other, Player):
                magic_ceiling = 250
            else:
                raise PlayerError(f'{other=}')

            magic = min([max([other.active_levels.magic, other.aggressive_bonus.magic]), magic_ceiling])

            accuracy_modifier_percent = 140 + math.floor((10*3*magic/10 - 10)/100) - math.floor(
                ((3*magic/10 - 100)**2/100))
            damage_modifier_percent = 250 + math.floor((10*3*magic/10 - 14)/100) - math.floor(
                ((3*magic/10 - 140)**2/100))

            twisted_bow_arm = min([accuracy_modifier_ceiling, accuracy_modifier_percent / 100])
            twisted_bow_dm = min([damage_modifier_ceiling, damage_modifier_percent / 100])
        else:
            twisted_bow_arm = 1
            twisted_bow_dm = 1

        return ArmDmTuple(twisted_bow_arm, twisted_bow_dm)

    def _obsidian_armor_modifier(self) -> ArmDmTuple:
        if self.equipment.obsidian_armor_set and self.equipment.obsidian_weapon:
            modifier = 1.1
        else:
            modifier = 1

        return ArmDmTuple(modifier, modifier)

    def _berserker_necklace_modifier(self) -> float:
        if self.equipment.wearing(neck=Gear.from_osrsbox('berserker necklace')) and self.equipment.obsidian_weapon:
            return 1.2
        else:
            return 1

    def _dharok_damage_modifier(self) -> float:
        if self.equipment.dharok_set:
            return 1 + (self.levels.hitpoints - self.active_levels.hitpoints)/100 * (self.levels.hitpoints/100)
        else:
            return 1

    def _leafy_modifier(self, other: Character) -> ArmDmTuple:
        if isinstance(other, Monster) and MonsterTypes.leafy in other.special_attributes \
                and self.equipment.leafy_weapon:
            modifier = 1.175
        else:
            modifier = 1

        return ArmDmTuple(modifier, modifier)

    def _keris_damage_modifier(self, other: Character) -> float:
        if self.equipment.keris and isinstance(other, Monster) and MonsterTypes.kalphite in other.special_attributes:
            modifier = 4/3
        else:
            modifier = 1

        return modifier

    def _crystal_armor_modifier(self) -> ArmDmTuple:
        if self.equipment.crystal_weapon:
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
        else:
            crystal_arm = 1
            crystal_dm = 1

        return ArmDmTuple(crystal_arm, crystal_dm)

    def _inquisitor_modifier(self) -> ArmDmTuple:
        if self.active_style.damage_type == Style.crush:
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

        else:
            modifier = 1

        return ArmDmTuple(modifier, modifier)

    def _chinchompa_arm_modifier(self, distance: int = None) -> float:
        if distance:
            if self.active_style == ChinchompaStyles.get_style(PlayerStyle.short_fuse):
                if 0 <= distance <= 3:
                    chin_arm = 1.00
                elif 4 <= distance <= 6:
                    chin_arm = 0.75
                else:
                    chin_arm = 0.50

            elif self.active_style == ChinchompaStyles.get_style(PlayerStyle.medium_fuse):
                if 4 <= distance <= 6:
                    chin_arm = 1.00
                else:
                    chin_arm = 0.75
            elif self.active_style.name == ChinchompaStyles.get_style(PlayerStyle.long_fuse):
                if 0 <= distance <= 3:
                    chin_arm = 0.50
                elif 4 <= distance <= 6:
                    chin_arm = 0.75
                else:
                    chin_arm = 1.00
            else:
                raise StyleError(f'{self.active_style} not in {ChinchompaStyles}')

        else:
            chin_arm = 1

        return chin_arm

    def _vampyric_modifier(self, other: Character) -> ArmDmTuple:
        raise NotImplemented

    def _tome_of_fire_dm(self, spell: Spell = None):
        dm = 1.5 if spell in asdict(FireSpells) and self.equipment.tome_of_fire else 1
        return dm

    def _chaos_gauntlets_bonus(self, spell: Spell = None) -> int:
        if spell in asdict(BoltsSpells) and self.equipment.wearing(hands=Gear.from_bb('chaos gauntlets')):
            damage_boost = 3
        else:
            damage_boost = 0
        return damage_boost

    def _smoke_modifier(self, spell: Spell = None):
        if self.equipment.smoke_staff and isinstance(spell, StandardSpell):
            arm = 1.1
            db = 0.1
        else:
            arm = 1
            db = 0
        return arm, db

    def _guardians_modifier(self, other: Character) -> float:
        if isinstance(other, Guardian) and 'pickaxe' in self.equipment.weapon.name:
            modifier = (50 + min([100, self.active_levels.mining]) + self.equipment.weapon.level_requirements.mining) \
                       / 150
        else:
            modifier = 1

        return modifier

    def attack_roll(self, other: Character, special_attack: bool = False, distance: int = None) -> int:

        aggressive_cb = self.equipment.aggressive_bonus

        if (dt := self.active_style.damage_type) in Style.melee_damage_types:
            effective_level = self.effective_attack_level
            bonus = aggressive_cb.__getattribute__(dt)
        elif dt in Style.ranged_damage_types:
            effective_level = self.effective_ranged_attack_level
            bonus = aggressive_cb.ranged
        elif dt in Style.magic_damage_types:
            effective_level = self.effective_magic_attack_level
            bonus = aggressive_cb.magic
        else:
            raise StyleError(f'{self.active_style.damage_type=}')

        salve_arm, _ = self._salve_modifier(other)
        slayer_arm, _ = self._slayer_modifier(other)

        # salve and slayer helm cannot stack, only use salve effect
        if salve_arm > 1 and slayer_arm > 1:
            slayer_arm = 1

        arclight_arm, _ = self._arclight_modifier(other)
        draconic_arm, _ = self._draconic_modifier(other)
        wilderness_arm, _ = self._wilderness_modifier(other)
        twisted_bow_arm, _ = self._twisted_bow_modifier(other)
        obsidian_arm, _ = self._obsidian_armor_modifier()
        crystal_arm, _ = self._crystal_armor_modifier()
        chin_arm = self._chinchompa_arm_modifier(distance)
        inquisitor_arm, _ = self._inquisitor_modifier()

        if dt in Style.magic_damage_types and self.active_style.is_spell_style():
            smoke_arm, _ = self._smoke_modifier(self.autocast)
        else:
            smoke_arm = 1

        all_roll_modifiers = [
            salve_arm,
            slayer_arm,
            arclight_arm,
            draconic_arm,
            wilderness_arm,
            twisted_bow_arm,
            obsidian_arm,
            crystal_arm,
            chin_arm,
            inquisitor_arm,
            smoke_arm
        ]

        if special_attack:
            if isinstance(self.equipment.weapon, SpecialWeapon):
                all_roll_modifiers.append(self.equipment.weapon.special_accuracy_modifier)
            else:
                raise GearError(f'{self.equipment.weapon=} is not {SpecialWeapon}')

        active_roll_modifiers = [float(x) for x in all_roll_modifiers if not x == 1]
        return self.maximum_roll(effective_level, bonus, *active_roll_modifiers)

    def defence_roll(self, other: Character, special_attack: bool = False) -> int:
        if isinstance(other, Player):
            dt = other.active_style.damage_type
            weapon = other.equipment.weapon

            if dt in Style.melee_damage_types or dt in Style.ranged_damage_types:
                stat = self.effective_defence_level
            elif dt in Style.magic_damage_types:
                stat = self.effective_magic_defence_level
            else:
                return NotImplemented

            if special_attack:
                if not isinstance(weapon, SpecialWeapon):
                    raise SpecialWeaponError(weapon)

                dt_def_roll = weapon.special_defence_roll if weapon.special_defence_roll else dt
            else:
                dt_def_roll = dt

            bonus = self.equipment.defensive_bonus.__getattribute__(dt_def_roll)
            roll = self.maximum_roll(stat, bonus)

            if other.equipment.brimstone_ring and dt in Style.magic_damage_types:
                reduction = math.floor(roll / 10) / 4
                roll = math.floor(roll - reduction)

            return roll

        elif isinstance(other, Monster):
            dt = other.active_style.damage_type
            dt_def_roll = dt

            if (dt := other.active_style.damage_type) in Style.melee_damage_types or dt in Style.ranged_damage_types:
                stat = self.effective_defence_level
            elif dt in Style.magic_damage_types:
                stat = self.effective_magic_defence_level
            else:
                return NotImplemented

            bonus = self.equipment.defensive_bonus.__getattribute__(dt_def_roll)
            roll = self.maximum_roll(stat, bonus)

            return roll

        else:
            raise NotImplementedError

    def max_hit(self, other: Character, special_attack: bool = False, spell: Spell = None) -> int:
        if isinstance(other, Character):
            dt = self.active_style.damage_type
            aggressive_cb = self.equipment.aggressive_bonus

            if dt in Style.melee_damage_types or dt in Style.ranged_damage_types:
                if dt in Style.melee_damage_types:
                    effective_level = self.effective_melee_strength_level
                    bonus = aggressive_cb.melee_strength
                else:
                    effective_level = self.effective_ranged_strength_level
                    bonus = aggressive_cb.ranged_strength

                base_damage = self.base_damage(effective_level, bonus)

                _, salve_dm = self._salve_modifier(other)
                _, slayer_dm = self._slayer_modifier(other)

                # salve and slayer helm cannot stack, only use salve effect
                if salve_dm > 1 and slayer_dm > 1:
                    slayer_dm = 1

                _, crystal_dm = self._crystal_armor_modifier()
                _, arclight_dm = self._arclight_modifier(other)
                _, draconic_dm = self._draconic_modifier(other)
                _, wilderness_dm = self._wilderness_modifier(other)
                _, twisted_bow_dm = self._twisted_bow_modifier(other)
                _, obsidian_dm = self._obsidian_armor_modifier()
                _, inquisitor_dm = self._inquisitor_modifier()
                berserker_dm = self._berserker_necklace_modifier()
                guardians_dm = self._guardians_modifier(other)

                ice_demon_dm = 0.33 if isinstance(other, IceDemon) else 1

                all_roll_modifiers = [
                    salve_dm,
                    slayer_dm,
                    arclight_dm,
                    draconic_dm,
                    wilderness_dm,
                    twisted_bow_dm,
                    obsidian_dm,
                    crystal_dm,
                    inquisitor_dm,
                    berserker_dm,
                    ice_demon_dm,
                    guardians_dm
                ]

                if special_attack:
                    if isinstance(self.equipment.weapon, SpecialWeapon):
                        all_roll_modifiers.extend([
                            self.equipment.weapon.special_damage_modifier_1,
                            self.equipment.weapon.special_damage_modifier_2
                        ])
                    else:
                        raise PlayerError(f'{self.equipment.weapon=} is not {SpecialWeapon}')

                active_roll_modifiers = [float(x) for x in all_roll_modifiers if not x == 1]
                max_hit = self.static_max_hit(base_damage, *active_roll_modifiers)
            elif dt in Style.magic_damage_types:
                if spell is None:
                    if self.equipment.weapon == Weapon.from_bb('sanguinesti staff'):
                        self.autocast = PoweredSpells.sanguinesti_staff
                    elif self.equipment.weapon == Weapon.from_bb('trident of the swamp'):
                        self.autocast = PoweredSpells.trident_of_the_swamp
                    elif self.equipment.weapon == Weapon.from_bb('trident of the seas'):
                        self.autocast = PoweredSpells.trident_of_the_seas

                spell = spell if spell else self.autocast

                if isinstance(spell, Spell):
                    if isinstance(spell, StandardSpell) or isinstance(spell, AncientSpell):
                        base_damage = spell.max_hit()
                    elif isinstance(spell, GodSpell):
                        base_damage = spell.max_hit(self.charged)
                    elif isinstance(spell, PoweredSpell):
                        base_damage = spell.max_hit(self.visible_magic)
                    else:
                        raise SpellError(f'{spell=} {self.autocast=}')

                    cg_bonus = self._chaos_gauntlets_bonus(spell)
                    _, smoke_db = self._smoke_modifier(spell)
                    gear_bonus_modifier = 1 + self.equipment.aggressive_bonus.magic_strength + smoke_db
                    _, salve_dm = self._salve_modifier(other)
                    _, slayer_dm = self._slayer_modifier(other)
                    tome_dm = self._tome_of_fire_dm(spell)

                    max_hit = base_damage + cg_bonus
                    max_hit = math.floor(max_hit * gear_bonus_modifier)

                    if salve_dm > 1:
                        max_hit = math.floor(max_hit * salve_dm)
                    elif slayer_dm > 1:
                        max_hit = math.floor(max_hit * slayer_dm)

                    max_hit = math.floor(max_hit * tome_dm)

                    if isinstance(other, IceDemon):
                        ice_demon_dm = 1.5 if spell in asdict(FireSpells) else 0.33
                        max_hit = math.floor(max_hit * ice_demon_dm)

                else:
                    raise NotImplemented
            else:
                raise StyleError(f'{self.active_style.damage_type=}')

            return max_hit
        else:
            raise PlayerError(f'{other=}')

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

    def damage_distribution(
            self,
            other: Character,
            special_attack: bool = False,
            distance: int = None,
            spell: Spell = None,
            additional_targets: int | Character | list[Character] = 0,
            **kwargs,
    ) -> Damage:
        if isinstance(other, Character):
            dt = self.active_style.damage_type

            if special_attack:
                if not isinstance(self.equipment.weapon, SpecialWeapon):
                    raise GearError(f'{self.equipment.weapon=} not {SpecialWeapon}')

            att_roll = self.attack_roll(other, special_attack, distance)
            def_roll = other.defence_roll(self, special_attack)
            accuracy = self.accuracy(att_roll, def_roll)

            max_hit = self.max_hit(other, special_attack, spell)
            hitpoints_cap = other.active_levels.hitpoints

            attack_speed = self.attack_speed(spell)

            if self.equipment.scythe_of_vitur:
                hs = [Hitsplat.from_max_hit_acc(math.floor(max_hit*2**n), accuracy, hitpoints_cap)
                      for n in range(0, -3, -1)]

                damage = Damage(attack_speed, *hs, **kwargs)
            elif self.equipment.chinchompas and additional_targets:
                max_targets = 9 if isinstance(other, Player) else 11

                if isinstance(additional_targets, int):
                    targets = min([1 + additional_targets, max_targets])
                    hs = [Hitsplat.from_max_hit_acc(max_hit, accuracy, hitpoints_cap) for _ in range(targets)]
                    damage = Damage(attack_speed, *hs, **kwargs)
                else:
                    if isinstance(additional_targets, Character):
                        additional_targets = [additional_targets]

                    targets = [other] + additional_targets
                    targets = targets if len(targets) <= max_targets else targets[:max_targets]

                    hs = [Hitsplat.from_max_hit_acc(max_hit, accuracy, t.active_levels.hitpoints) for t in targets]
                    damage = Damage(attack_speed, *hs, **kwargs)

            elif self.equipment.enchanted_diamond_bolts and dt in Style.ranged_damage_types:
                activation_chance = 0.11 if self.kandarin_hard else 0.10
                damage_modifier = 1.15 + 0.015*self.equipment.zaryte_crossbow
                effect_max_hit = math.floor(damage_modifier * max_hit)

                damage_values = np.arange(effect_max_hit + 1)
                probabilities = np.zeros(damage_values.shape)

                for index, dv in enumerate(damage_values):
                    p_miss = (1 - activation_chance) * (1 - accuracy) if dv == 0 else 0
                    p_norm = 0 if dv > max_hit else (1 - activation_chance) * accuracy * 1 / (max_hit + 1)
                    p_effect = activation_chance * 1 / (effect_max_hit + 1)
                    probabilities[index] = p_miss + p_norm + p_effect

                damage = Damage(attack_speed, Hitsplat(damage_values, probabilities, hitpoints_cap), **kwargs)
            elif self.equipment.enchanted_ruby_bolts and dt in Style.ranged_damage_types:
                activation_chance = 0.06 + 0.006*self.kandarin_hard
                target_hp = other.active_levels.hitpoints
                max_effective_hp = 500
                hp_ratio = 0.20 + 0.02*self.equipment.zaryte_crossbow

                effect_damage = min(map(lambda hp: math.floor(hp_ratio*hp), [max_effective_hp, target_hp]))
                true_max = max([max_hit, effect_damage])

                damage_values = np.arange(true_max+1)
                probabilities = np.zeros(damage_values.shape)

                for index, dv in enumerate(damage_values):
                    p_miss = 0 if dv > 0 else (1 - activation_chance) * (1 - accuracy)
                    p_norm = 0 if dv > max_hit else (1 - activation_chance) * accuracy * 1 / (max_hit + 1)
                    p_effect = activation_chance if dv == effect_damage else 0
                    probabilities[index] = p_miss + p_norm + p_effect

                damage = Damage(attack_speed, Hitsplat(damage_values, probabilities, hitpoints_cap), **kwargs)
            elif special_attack and self.equipment.wearing(weapon=SpecialWeapon.from_bb('dorgeshuun crossbow')):
                accuracy = 1
                damage = Damage.from_max_hit_acc(max_hit, accuracy, attack_speed, hitpoints_cap, **kwargs)
            else:
                damage = Damage.from_max_hit_acc(max_hit, accuracy, attack_speed, hitpoints_cap, **kwargs)

            return damage

        else:
            raise PlayerError(f'{other=}')

    def attack(
            self,
            other: Character,
            special_attack: bool = False,
            distance: int = None,
            spell: Spell = None,
            additional_targets: int | Character | list[Character] = 0,
            **kwargs,
    ):
        dam = self.damage_distribution(other, special_attack, distance, spell, additional_targets, **kwargs)
        random_value = dam.random(attempts=1)[0]
        other.damage(random_value)

        if self.equipment.blood_fury and np.random.random() < (blood_fury_activation_chance := 0.20):
            self.heal(math.floor(random_value*0.30), overheal=False)




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
    def effective_attack_level(self) -> int:
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

    def attack_roll(self, other: Character, special_attack: bool = False) -> int:
        aggressive_cb = self.aggressive_bonus

        if (dt := self.active_style.damage_type) in Style.melee_damage_types:
            effective_level = self.effective_attack_level
            bonus = aggressive_cb.__getattribute__(dt)
        elif dt in Style.ranged_damage_types:
            effective_level = self.effective_ranged_attack_level
            bonus = aggressive_cb.ranged
        elif dt in Style.magic_damage_types:
            effective_level = self.effective_magic_attack_level
            bonus = aggressive_cb.magic
        elif dt in Style.typeless_damage_types:
            raise NotImplemented
        else:
            raise StyleError(f'{self.active_style.damage_type=}')

        all_roll_modifiers = []
        active_roll_modifiers = [float(x) for x in all_roll_modifiers if not x == 1]
        return self.maximum_roll(effective_level, bonus, *active_roll_modifiers)

    def defence_roll(self, other: Character, special_attack: bool = False) -> int:
        if isinstance(other, Player):
            dt = other.active_style.damage_type
            weapon = other.equipment.weapon

            if dt in Style.melee_damage_types or dt in Style.ranged_damage_types:
                stat = self.effective_defence_level
            elif dt in Style.magic_damage_types:
                stat = self.effective_magic_defence_level
            else:
                return NotImplemented

            if special_attack:
                if not isinstance(weapon, SpecialWeapon):
                    raise SpecialWeaponError(weapon)

                dt_def_roll = weapon.special_defence_roll if weapon.special_defence_roll else dt
            else:
                dt_def_roll = dt

            bonus = self.defensive_bonus.__getattribute__(dt_def_roll)
            roll = self.maximum_roll(stat, bonus)

            if other.equipment.brimstone_ring and dt in Style.magic_damage_types:
                reduction = math.floor(roll / 10) / 4
                roll = math.floor(roll - reduction)

            return roll

        elif isinstance(other, Monster):
            return NotImplemented

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

        count = np.floor(3 + scale_at_load_time/3)
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


# noinspection PyArgumentList
@define(**character_attrs_settings)
class Olm(CoxMonster, ABC):

    def player_hp_scaling_factor(self):
        _ = self
        return 1

    def party_offensive_scaling_factor(self):
        n = self.party_size
        return (1 + (0.07 * (1 + math.floor(n/5)))) + 0.01*(n-1)

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
