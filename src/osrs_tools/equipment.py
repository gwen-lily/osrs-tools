from osrsbox import items_api
from osrsbox.items_api.item_properties import ItemEquipment, ItemProperties, ItemWeapon
import functools
import pandas as pd

from .style import *
from .stats import *
from .exceptions import *
import src.osrs_tools.resource_reader as rr


class GearError(OsrsException):
    pass


class EquipableError(GearError):
    def __init__(self, message: str):
        super().__init__(message)


class GearNotFoundError(GearError):
    def __init__(self, gear_name: str = None):
        self.message = f'Item not found by name lookup: {gear_name=}' if gear_name else None


class DuplicateGearError(GearError):
    def __init__(self, search_term: str = None, *matching_names: str):
        if search_term and len(matching_names) > 0:
            self.message = f'{search_term=} yielded: ' + ', '.join(matching_names)
        else:
            self.message = None


class WeaponError(GearError):
    pass


@define(order=True, frozen=True)
class _GearSlots:
    head = field(default='head', init=False)
    cape = field(default='cape', init=False)
    neck = field(default='neck', init=False)
    ammunition = field(default='ammunition', init=False)
    weapon = field(default='weapon', init=False)
    shield = field(default='shield', init=False)
    body = field(default='body', init=False)
    legs = field(default='legs', init=False)
    hands = field(default='hands', init=False)
    feet = field(default='feet', init=False)
    ring = field(default='ring', init=False)


GearSlots = _GearSlots()
Items = items_api.load()
default_one_field = field(default=1)


def slot_validator(instance, attribute, value):
    if value not in asdict(GearSlots):
        raise GearError(f'{attribute=} with {value=} not in {list(asdict(GearSlots))}')


def weapon_validator(instance, attribute, value):
    if not value == GearSlots.weapon:
        raise WeaponError(f'{attribute=} with {value=} not equal to {GearSlots.weapon=}')


def special_defence_roll_validator(instance, attribute, value):
    if value and value not in Style.all_damage_types:
        raise WeaponError(f'{attribute=} with {value=} not in {Style.all_damage_types}')


def lookup_gear_base_attributes_by_name(name: str, gear_df: pd.DataFrame = None):
    item_df = rr.lookup_gear(name, gear_df)

    if len(item_df) > 1:
        matching_names = tuple(item_df['name'].values)
        raise DuplicateGearError(name, *matching_names)
    elif len(item_df) == 0:
        raise GearNotFoundError(name)

    name = item_df['name'].values[0]
    slot = item_df['slot'].values[0]
    aggressive_bonus = AggressiveStats(
        stab=item_df['stab attack'].values[0],
        slash=item_df['slash attack'].values[0],
        crush=item_df['crush attack'].values[0],
        magic=item_df['magic attack'].values[0],
        ranged=item_df['ranged attack'].values[0],
        melee_strength=item_df['melee strength'].values[0],
        ranged_strength=item_df['ranged strength'].values[0],
        magic_strength=item_df['magic damage'].values[0]  # stored as float in bitterkoekje's sheet
    )
    defensive_bonus = DefensiveStats(
        stab=item_df['stab defence'].values[0],
        slash=item_df['slash defence'].values[0],
        crush=item_df['crush defence'].values[0],
        magic=item_df['magic defence'].values[0],
        ranged=item_df['ranged defence'].values[0]
    )
    prayer_bonus = item_df['prayer'].values[0]
    combat_requirements = PlayerLevels(mining=item_df['mining level req'].values[0])

    return name, slot, aggressive_bonus, defensive_bonus, prayer_bonus, combat_requirements


def lookup_weapon_attributes_by_name(name: str, gear_df: pd.DataFrame = None):
    item_df = rr.lookup_gear(name, gear_df)
    default_attack_range = 0

    if len(item_df) > 1:
        matching_names = tuple(item_df['name'].values)
        raise DuplicateGearError(name, *matching_names)
    elif len(item_df) == 0:
        raise GearNotFoundError(name)

    attack_speed = item_df['attack speed'].values[0]
    attack_range = default_attack_range
    two_handed = item_df['two handed'].values[0]
    weapon_styles = WeaponStyles.from_weapon_type(item_df['weapon type'].values[0])

    special_accuracy_modifier = 1 + item_df['special accuracy'].values[0]
    special_damage_modifier_1 = 1 + item_df['special damage 1'].values[0]
    special_damage_modifier_2 = 1 + item_df['special damage 2'].values[0]
    special_defence_roll = item_df['special defence roll'].values[0]

    return attack_speed, attack_range, two_handed, weapon_styles, special_accuracy_modifier, \
           special_damage_modifier_1, special_damage_modifier_2, special_defence_roll


# noinspection PyArgumentList
@define(order=True, frozen=True)
class Gear:
    name: str
    slot: str = field(validator=slot_validator)
    aggressive_bonus: AggressiveStats = field(validator=validators.instance_of(AggressiveStats))
    defensive_bonus: DefensiveStats = field(validator=validators.instance_of(DefensiveStats))
    prayer_bonus: int
    combat_requirements: PlayerLevels = field(validator=validators.instance_of(PlayerLevels))

    @classmethod
    def from_bb(cls, name: str):
        name, slot, aggressive_bonus, defensive_bonus, prayer_bonus, combat_requirements = \
            lookup_gear_base_attributes_by_name(name)

        return cls(
            name=name,
            slot=slot,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            prayer_bonus=prayer_bonus,
            combat_requirements=combat_requirements,
        )

    @classmethod
    def from_osrsbox(cls, name: str = None, item_id: int = None, **kwargs):

        if name:
            item = Items.lookup_by_item_name(name)
        elif item_id:
            item = Items.lookup_by_item_id(item_id)
        else:
            raise GearNotFoundError(f'{kwargs=}')

        eqp = item.equipment
        slot = eqp.slot
        slot = 'ammunition' if slot == 'ammo' else slot

        try:
            assert isinstance(eqp, ItemEquipment)
            assert item.equipable
            assert item.equipable_by_player
            assert not item.equipable_weapon
        except AssertionError as exc:
            raise GearError(f'{exc=}')

        magic_strength = 0.01 * eqp.magic_damage

        if eqp.requirements:
            reqs = eqp.requirements
        else:
            reqs = {}

        return cls(
            name=item.name.lower(),
            slot=slot,
            aggressive_bonus=AggressiveStats(
                stab=eqp.attack_stab,
                slash=eqp.attack_slash,
                crush=eqp.attack_crush,
                magic=eqp.attack_magic,
                ranged=eqp.attack_ranged,
                melee_strength=eqp.melee_strength,
                ranged_strength=eqp.ranged_strength,
                magic_strength=magic_strength
            ),
            defensive_bonus=DefensiveStats(
                stab=eqp.defence_stab,
                slash=eqp.defence_slash,
                crush=eqp.defence_crush,
                magic=eqp.defence_magic,
                ranged=eqp.defence_ranged
            ),
            prayer_bonus=eqp.prayer,
            combat_requirements=PlayerLevels(**reqs),
        )

    @classmethod
    def empty_slot(cls, slot: str):
        if slot == GearSlots.weapon:
            return Weapon.empty_slot()
        else:
            return cls(
                name='empty ' + slot,
                slot=slot,
                aggressive_bonus=AggressiveStats.no_bonus(),
                defensive_bonus=DefensiveStats.no_bonus(),
                prayer_bonus=0,
                combat_requirements=PlayerLevels.no_requirements(),
            )

    def __str__(self):
        message = f'Gear({self.name})'
        return message


class SpecialWeaponError(WeaponError):
    def __init__(self, gear: Gear):
        self.message = f'{gear=} {isinstance(gear, SpecialWeapon)=}'


class EquipmentError(OsrsException):
    pass


class TwoHandedError(EquipmentError):
    pass


# noinspection PyArgumentList
@define(order=True, frozen=True)
class Weapon(Gear):
    name: str
    slot: str = field(validator=weapon_validator)
    aggressive_bonus: AggressiveStats = field(validator=validators.instance_of(AggressiveStats))
    defensive_bonus: DefensiveStats = field(validator=validators.instance_of(DefensiveStats))
    prayer_bonus: int
    combat_requirements: PlayerLevels = field(validator=validators.instance_of(PlayerLevels))
    weapon_styles: WeaponStyles = field(validator=validators.instance_of(WeaponStyles))
    attack_speed: int
    two_handed: bool

    def choose_style_by_name(self, name: str):
        for style in self.weapon_styles.styles:
            if style.name == name:
                return style

        raise StyleError(f'{name=} not in {self.weapon_styles.styles=}')

    @classmethod
    def empty_slot(cls, slot: str = None):
        slot = 'weapon'
        return cls(
            name='empty ' + slot,
            slot=slot,
            aggressive_bonus=AggressiveStats.no_bonus(),
            defensive_bonus=DefensiveStats.no_bonus(),
            prayer_bonus=0,
            combat_requirements=PlayerLevels.no_requirements(),
            weapon_styles=UnarmedStyles,
            attack_speed=4,
            two_handed=False,
        )

    @classmethod
    def from_bb(cls, name: str):
        name, slot, aggressive_bonus, defensive_bonus, prayer_bonus, combat_requirements = \
            lookup_gear_base_attributes_by_name(name)
        attack_speed, attack_range, two_handed, weapon_styles, _, _, _, _ = lookup_weapon_attributes_by_name(name)

        if not slot == GearSlots.weapon:
            raise WeaponError(f'{name=}{slot=}')

        return cls(
            name=name,
            slot=slot,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            prayer_bonus=prayer_bonus,
            combat_requirements=combat_requirements,
            weapon_styles=weapon_styles,
            attack_speed=attack_speed,
            two_handed=two_handed,
        )

    def __str__(self):
        message = f'Weapon({self.name}, {self.weapon_styles})'
        return message


# noinspection PyArgumentList
@define(order=True, frozen=True)
class SpecialWeapon(Weapon):
    special_accuracy_modifier: float
    special_damage_modifier_1: float
    special_damage_modifier_2: float
    special_defence_roll: str = field(validator=special_defence_roll_validator, factory=str)

    @classmethod
    def from_bb(cls, name: str):
        name, slot, aggressive_bonus, defensive_bonus, prayer_bonus, combat_requirements = \
            lookup_gear_base_attributes_by_name(name)
        attack_speed, attack_range, two_handed, weapon_styles, special_accuracy_modifier, special_damage_modifier_1, \
            special_damage_modifier_2, special_defence_roll = lookup_weapon_attributes_by_name(name)

        if not slot == GearSlots.weapon:
            raise WeaponError(f'{name=}{slot=}')

        return cls(
            name=name,
            slot=slot,
            aggressive_bonus=aggressive_bonus,
            defensive_bonus=defensive_bonus,
            prayer_bonus=prayer_bonus,
            combat_requirements=combat_requirements,
            weapon_styles=weapon_styles,
            attack_speed=attack_speed,
            two_handed=two_handed,
            special_accuracy_modifier=special_accuracy_modifier,
            special_damage_modifier_1=special_damage_modifier_1,
            special_damage_modifier_2=special_damage_modifier_2,
            special_defence_roll=special_defence_roll,
        )

    @classmethod
    def empty_slot(cls, slot: str = None):
        raise WeaponError(f'Attempt to create empty special weapon')

    def __str__(self):
        message = f'SpecialWeapon({self.name}, {self.weapon_styles})'
        return message


def gear_slot_validator(instance, attribute, value: Gear):
    if not attribute.name == value.slot:
        raise GearError(f'{attribute=} & {value.slot=} should be the same')


def weapon_slot_validator(instance, attribute: str, value: Weapon):
    if not isinstance(value, Weapon):
        raise WeaponError(f'Weapon was initialized as {value.__class__=}')

    try:
        if value.two_handed and not instance.shield == Gear.empty_slot(GearSlots.shield):
            raise TwoHandedError(f'{value=} equipped with {instance.shield=}')
    except AttributeError:
        pass


def shield_slot_validator(instance, attribute: str, value: Gear):
    try:
        if instance.weapon.two_handed and not value == Gear.empty_slot(GearSlots.shield):
            raise TwoHandedError(f'{value=} equipped with {instance.weapon}')
    except AttributeError:
        pass


def equipment_field(slot: str):
    return field(validator=gear_slot_validator, default=Gear.empty_slot(slot))


@define(order=True)
class Equipment:
    """
    The Equipment class has attributes for each piece of Gear a player can use as well as methods to query and change
    the gear.
    """
    head: Gear = equipment_field(GearSlots.head)
    cape: Gear = equipment_field(GearSlots.cape)
    neck: Gear = equipment_field(GearSlots.neck)
    ammunition: Gear = equipment_field(GearSlots.ammunition)
    weapon: Weapon = field(validator=[weapon_slot_validator, gear_slot_validator], default=Weapon.empty_slot())
    shield: Gear = field(validator=[shield_slot_validator, gear_slot_validator], default=Gear.empty_slot(GearSlots.shield))
    body: Gear = equipment_field(GearSlots.body)
    legs: Gear = equipment_field(GearSlots.legs)
    hands: Gear = equipment_field(GearSlots.hands)
    feet: Gear = equipment_field(GearSlots.feet)
    ring: Gear = equipment_field(GearSlots.ring)

    @classmethod
    def from_unordered(cls, *gear: Gear | Weapon | SpecialWeapon):
        gear_dict = {g.slot: g for g in gear if isinstance(g, Gear)}
        return cls(**gear_dict)

    @property
    def aggressive_bonus(self) -> AggressiveStats:
        return sum([g.aggressive_bonus for g in astuple(self, recurse=False)])

    @property
    def defensive_bonus(self) -> DefensiveStats:
        return sum([g.defensive_bonus for g in astuple(self, recurse=False)])

    @property
    def prayer_bonus(self) -> int:
        return sum([g.prayer_bonus for g in astuple(self, recurse=False)])

    @property
    def combat_requirements(self) -> PlayerLevels:
        # x * y defined by PlayerLevels class to combine requirements.
        return functools.reduce(lambda x, y: x * y, [x.combat_requirements for x in astuple(self, recurse=False)])

    def equip(self, *gear: Gear | Weapon | SpecialWeapon, style: PlayerStyle = None, **kwargs) -> PlayerStyle | None:
        weapon_style = None

        for g in (x for x in gear if isinstance(x, Gear)):
            if self.__getattribute__(g.slot) == g or g == Gear.empty_slot(g.slot):
                continue
            else:
                if isinstance(g, Weapon):
                    weapon_style = style if style else g.weapon_styles.default

                    if weapon_style not in g.weapon_styles.styles:
                        raise WeaponError(f'{weapon_style} not in {g.weapon_styles}')
                    else:
                        try:
                            self.weapon = g
                        except TwoHandedError:
                            self.shield = Gear.empty_slot(GearSlots.shield)
                            self.weapon = g

                else:
                    try:
                        self.__setattr__(g.slot, g)
                    except TwoHandedError:
                        assert g.slot == GearSlots.shield
                        self.weapon = Weapon.empty_slot()
                        self.shield = g

        return weapon_style

    def unequip(self, *slots: str, style: PlayerStyle = None):
        return_style = None

        for slot in slots:
            if slot == GearSlots.weapon:
                return_style = style if style else UnarmedStyles.default

            self.__setattr__(slot, Gear.empty_slot(slot))

    def wearing(self, **kwargs) -> bool:
        return all([self.__getattribute__(k) == v for k, v in kwargs.items()])

    # wearing properties, if any Character methods needs to know it I'll define it here for re-use and standardization

    @property
    def normal_void_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb('void knight helm'),
            body=Gear.from_bb('void knight top'),
            legs=Gear.from_bb('void knight robe'),
            hands=Gear.from_bb('void knight gloves'),
        )

    @property
    def elite_void_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb('void knight helm'),
            body=Gear.from_bb('elite void top'),
            legs=Gear.from_bb('elite void robe'),
            hands=Gear.from_bb('void knight gloves'),
        )

    @property
    def dharok_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("dharok's greataxe"),
            body=Gear.from_bb("dharok's platebody"),
            legs=Gear.from_bb("dharok's platelegs"),
            weapon=Weapon.from_bb("dharok's greataxe"),
        )

    @property
    def bandos_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb('neitiznot faceguard'),
            body=Gear.from_bb('bandos chestplate'),
            legs=Gear.from_bb('bandos tassets'),
        )

    @property
    def inquisitor_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("inquisitor's great helm"),
            body=Gear.from_bb("inquisitor's hauberk"),
            legs=Gear.from_bb("inquisitor's plateskirt"),
        )

    @property
    def torva_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb('torva full helm'),
            body=Gear.from_bb('torva platebody'),
            legs=Gear.from_bb('torva platelegs'),
        )

    @property
    def justiciar_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("justiciar faceguard"),
            body=Gear.from_bb("justiciar chestguard"),
            legs=Gear.from_bb("justiciar legguard"),
        )

    @property
    def obsidian_armor_set(self) -> bool:
        # weapon_bool = self.weapon.name in ["obsidian dagger", "obsidian mace", "obsidian maul", "obsidian sword"]
        return self.wearing(
            head=Gear.from_bb("obsidian helm"),
            body=Gear.from_bb("obsidian platebody"),
            legs=Gear.from_bb("obsidian platelegs"),
        )

    @property
    def obsidian_weapon(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb("obsidian dagger"),
            Weapon.from_bb("obsidian mace"),
            Weapon.from_bb("obsidian maul"),
            Weapon.from_bb("obsidian sword"),
        )
        return self.weapon in qualifying_weapons

    @property
    def leafy_weapon(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb("leaf-bladed spear"),
            Weapon.from_bb("leaf-bladed sword"),
            Weapon.from_bb("leaf-bladed battleaxe"),
        )
        return self.weapon in qualifying_weapons

    @property
    def keris(self) -> bool:
        return self.wearing(weapon=Weapon.from_bb('keris'))

    @property
    def crystal_armor_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("crystal helm"),
            body=Gear.from_bb("crystal body"),
            legs=Gear.from_bb("crystal legs"),
        )

    @property
    def crystal_weapon(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb('crystal bow'),
            Weapon.from_bb('bow of faerdhinen'),
        )
        return self.weapon in qualifying_weapons

    @property
    def smoke_staff(self) -> bool:
        qualifying_weapons = (
            Weapon.from_bb('mystic smoke staff'),
            Weapon.from_bb('smoke battlestaff'),
        )
        return self.weapon in qualifying_weapons

    @property
    def graceful_set(self) -> bool:
        return self.wearing(
            head=Gear.from_bb("graceful hood"),
            body=Gear.from_bb("graceful top"),
            legs=Gear.from_bb("graceful legs"),
            hands=Gear.from_bb("graceful gloves"),
            feet=Gear.from_bb("graceful boots"),
            cape=Gear.from_bb("graceful cape"),
        )

    @property
    def zaryte_crossbow(self) -> bool:
        return self.wearing(weapon=Weapon.from_bb('zaryte crossbow'))

    @property
    def scythe_of_vitur(self) -> bool:
        return self.wearing(weapon=Weapon.from_bb('scythe of vitur'))

    @property
    def chinchompas(self) -> bool:
        grey = Weapon.from_bb('chinchompa')
        red = Weapon.from_bb('red chinchompa')
        black = Weapon.from_bb('black chinchompa')
        return self.weapon in (black, red, grey)

    @property
    def enchanted_ruby_bolts(self) -> bool:
        return self.wearing(ammunition=Gear.from_bb('ruby dragon bolts (e)')) or \
               self.wearing(ammunition=Gear.from_bb('ruby bolts (e)'))

    @property
    def enchanted_diamond_bolts(self) -> bool:
        return self.wearing(ammunition=Gear.from_bb('diamond dragon bolts (e)')) or \
               self.wearing(ammunition=Gear.from_bb('diamond bolts (e)'))

    @property
    def brimstone_ring(self) -> bool:
        return self.wearing(ring=Gear.from_bb('brimstone ring'))

    @property
    def tome_of_fire(self) -> bool:
        return self.wearing(shield=Gear.from_bb('tome of fire'))

    @property
    def tome_of_water(self) -> bool:
        return self.wearing(shield=Gear.from_bb('tome of water'))

    @property
    def staff_of_the_dead(self) -> bool:
        bb_names = (
            'staff of light',
            'staff of the dead',
            'toxic staff of the dead',
        )
        options = [SpecialWeapon.from_bb(name) for name in bb_names]

        if self.weapon in options:
            return True
        else:
            return False

    @property
    def elysian_spirit_shield(self) -> bool:
        return self.wearing(shield=Gear.from_bb('elysian spirit shield'))

    @property
    def dinhs_bulwark(self) -> bool:
        return self.wearing(weapon=SpecialWeapon.from_bb("dinh's bulwark"))

    @property
    def blood_fury(self) -> bool:
        return self.wearing(neck=Gear.from_bb('amulet of blood fury'))

    @classmethod
    def no_equipment(cls):
        return cls()

    def __add__(self, other):
        """
        Directional addition, right-hand operand has priority except in the case of empty slots.
        :param other:
        :return:
        """
        if isinstance(other, self.__class__):
            for gear in astuple(other, recurse=False):
                if not gear == Gear.empty_slot(gear.slot):
                    self.equip(gear)
            return self
        else:
            return NotImplemented

    def __sub__(self, other):
        """
        Directional subtraction, remove right-hand gear if and only if it exists in the left-hand set. Pass otherwise.
        :param other:
        :return:
        """
        if isinstance(other, self.__class__):
            for slot, gear in asdict(other).items():
                if self.__getattribute__(slot) == gear:
                    self.unequip(slot)
                else:
                    continue

    def __str__(self):
        notable_gear = [g.name for g in astuple(self, recurse=False) if 'empty' not in g.name]
        message = f'{self.__class__.__name__}({str(notable_gear)})'
        return message

    def __repr__(self):
        return self.__str__()

    def __copy__(self):
        gear_items = astuple(self, recurse=False)
        return self.__class__(*gear_items)

    # general gear swaps

    def equip_basic_melee_gear(self, torture: bool = True, primordial: bool = True, infernal: bool = True,
                               ferocious: bool = True, berserker: bool = True, brimstone: bool = False):
        gear_options = [
            Gear.from_bb('amulet of torture'),
            Gear.from_bb('primordial boots'),
            Gear.from_bb('infernal cape'),
            Gear.from_bb('ferocious gloves'),
        ]
        gear_bools = [torture, primordial, infernal, ferocious]
        gear = [g for g, b in zip(gear_options, gear_bools) if b]

        # sus ordering again with the rings
        if brimstone:
            ring = Gear.from_bb('brimstone ring')
            gear.append(ring)
        elif berserker:
            ring = Gear.from_bb('berserker (i)')
            gear.append(ring)

        self.equip(*gear)

    def equip_basic_ranged_gear(self, avas: bool = True, anguish: bool = True, pegasian: bool = True,
                                brimstone: bool = True, archers: bool = False):
        gear_options = (
            Gear.from_bb("ava's assembler"),
            Gear.from_bb('necklace of anguish'),
            Gear.from_bb('pegasian boots'),
        )
        gear_bools = (avas, anguish, pegasian)
        gear = [g for g, b in zip(gear_options, gear_bools) if b]

        # sus ordering again with the rings
        if archers:
            ring = Gear.from_bb('archers (i)')
            gear.append(ring)
        elif brimstone:
            ring = Gear.from_bb('brimstone ring')
            gear.append(ring)

        self.equip(*gear)

    def equip_basic_magic_gear(self, ancestral_set: bool = True, god_cape: bool = True, occult: bool = True,
                               arcane: bool = True, tormented: bool = True, eternal: bool = True,
                               brimstone: bool = True, seers: bool = False):
        if ancestral_set:
            self.equip_ancestral_set()

        gear_options = (
            Gear.from_bb('god cape (i)'),
            Gear.from_bb('occult necklace'),
            Gear.from_bb('arcane spirit shield'),
            Gear.from_bb('tormented bracelet'),
            Gear.from_bb('eternal boots'),
        )
        gear_bools = (god_cape, occult, arcane, tormented, eternal)
        gear = [g for g, b in zip(gear_options, gear_bools) if b]

        # sus ordering again with the rings
        if seers:
            ring = Gear.from_bb('seers (i)')
            gear.append(ring)
        elif brimstone:
            ring = Gear.from_bb('brimstone ring')
            gear.append(ring)

        self.equip(*gear)

    def equip_slayer_helm(self, imbued: bool = True):
        self.equip(
            Gear.from_bb('slayer helmet (i)'),
        )

    def equip_salve(self, e: bool = True, i: bool = True):
        if e and i:
            self.equip(Gear.from_bb('salve amulet (ei)'))
        elif i:
            self.equip(Gear.from_bb('salve amulet (i)'))
        else:
            raise NotImplementedError

    def equip_fury(self, blood: bool = False):
        fury = Gear.from_bb('amulet of blood fury') if blood else Gear.from_bb('amulet of fury')
        self.equip(fury)

    # melee gear swaps

    def equip_bandos_set(self):
        self.equip(
            Gear.from_bb('neitiznot faceguard'),
            Gear.from_bb('bandos chestplate'),
            Gear.from_bb('bandos tassets'),
        )

    def equip_inquisitor_set(self):
        self.equip(
            Gear.from_bb("inquisitor's great helm"),
            Gear.from_bb("inquisitor's hauberk"),
            Gear.from_bb("inquisitor's plateskirt"),
        )

    def equip_torva_set(self):
        self.equip(
            Gear.from_bb('torva full helm'),
            Gear.from_bb('torva platebody'),
            Gear.from_bb('torva platelegs'),
        )

    def equip_justi_set(self):
        self.equip(
            Gear.from_bb('justiciar faceguard'),
            Gear.from_bb('justiciar chestguard'),
            Gear.from_bb('justiciar legguard'),
        )

    def equip_dwh(self, *,
                  inquisitor_set: bool = False,
                  avernic: bool = True,
                  brimstone: bool = True,
                  tyrannical: bool = False,
                  style: PlayerStyle = None) -> PlayerStyle:

        if inquisitor_set:
            self.equip_inquisitor_set()

        gear = []

        if avernic:
            gear.append(Gear.from_bb('avernic defender'))

        # ordering a little sus here ngl
        if tyrannical:
            gear.append(Gear.from_bb('tyrannical (i)'))
        elif brimstone:
            gear.append(Gear.from_bb('brimstone ring'))

        style = style if style else BluntStyles.default

        return self.equip(
            SpecialWeapon.from_bb('dragon warhammer'),
            *gear,
            style=style
        )

    def equip_bgs(self, style: PlayerStyle = None) -> PlayerStyle:
        if style is not None:
            weapon_style = style
        elif self.inquisitor_set:
            weapon_style = TwoHandedStyles.get_style(PlayerStyle.smash)
        else:
            weapon_style = TwoHandedStyles.default

        gear = []

        return self.equip(
            SpecialWeapon.from_bb('bandos godsword'),
            style=style
        )

    def equip_scythe(self, berserker: bool = False, style: PlayerStyle = None) -> PlayerStyle:
        if style:
            weapon_style = style
        else:
            if self.inquisitor_set:
                weapon_style = ScytheStyles.get_style(PlayerStyle.jab)
            else:
                weapon_style = ScytheStyles.default

        gear = (Gear.from_bb('berserker (i)'),) if berserker else tuple()
        return self.equip(
            Weapon.from_bb('scythe of vitur'),
            *gear,
            style=weapon_style
        )

    def equip_lance(self, avernic: bool = True, berserker: bool = False, style: PlayerStyle = None) -> PlayerStyle:
        if style is not None:
            weapon_style = style
        elif self.inquisitor_set:
            weapon_style = SpearStyles.get_style(PlayerStyle.pound)
        else:
            weapon_style = SpearStyles.default

        gear_options = (Gear.from_bb('avernic defender'), Gear.from_bb('berserker (i)'),)
        gear_bools = (avernic, berserker)
        gear = (g for g, b in zip(gear_options, gear_bools) if b)
        return self.equip(
            Weapon.from_bb('dragon hunter lance'),
            *gear,
            style=weapon_style
        )

    def equip_dragon_pickaxe(self, avernic: bool = True, berserker: bool = False, style: PlayerStyle = None) \
            -> PlayerStyle:
        weapon_style = style if style is not None else PickaxeStyles.default
        gear_options = [Gear.from_bb('avernic defender'), Gear.from_bb('berserker (i)')]
        gear_bools = (avernic, berserker)

        gear = (g for g, b in zip(gear_options, gear_bools) if b)
        return self.equip(
            Weapon.from_bb('dragon pickaxe'),
            *gear,
            style=weapon_style
        )

    def equip_arclight(self, style: PlayerStyle = None) -> PlayerStyle:
        style = style if style else SlashSwordStyles.default
        return self.equip(
            SpecialWeapon.from_bb('arclight'),
            style=style
        )

    def equip_dinhs(self, style: PlayerStyle = None) -> PlayerStyle:
        style = BulwarkStyles.default if style is None else style

        return self.equip(
            SpecialWeapon.from_bb("dinh's bulwark"),
            style=style
        )

    def equip_sotd(self, style: PlayerStyle = None) -> PlayerStyle:
        style = BladedStaffStyles.default if style is None else style

        return self.equip(
            SpecialWeapon.from_bb('staff of the dead'),
            style=style
        )

    # ranged gear swaps

    def equip_arma_set(self, zaryte: bool = False, barrows: bool = False):
        if zaryte:
            gear = (Gear.from_bb('zaryte vambraces'),)
        elif barrows:
            gear = (Gear.from_bb('barrows gloves'),)
        else:
            gear = tuple()

        self.equip(
            Gear.from_bb('armadyl helmet'),
            Gear.from_bb('armadyl chestplate'),
            Gear.from_bb('armadyl chainskirt'),
            *gear
        )

    def equip_god_dhide(self):
        self.equip(
            Gear.from_bb("god coif"),
            Gear.from_bb("god d'hide body"),
            Gear.from_bb("god d'hide chaps"),
            Gear.from_bb('god bracers'),
            Gear.from_bb("blessed d'hide boots"),
        )

    def equip_void_set(self, elite: bool = True):
        body, legs = ('elite void top', 'elite void robe') if elite else ('void knight top', 'void knight robe')
        self.equip(
            Gear.from_bb('void knight helm'),
            Gear.from_bb(body),
            Gear.from_bb(legs),
            Gear.from_bb('void knight gloves'),
        )

    def equip_crystal_set(self, zaryte: bool = False, barrows: bool = False):
        if zaryte:
            gear = (Gear.from_bb('zaryte vambraces'),)
        elif barrows:
            gear = (Gear.from_bb('barrows gloves'),)
        else:
            gear = tuple()

        self.equip(
            Gear.from_bb('crystal helm'),
            Gear.from_bb('crystal body'),
            Gear.from_bb('crystal legs'),
            *gear
        )

    def equip_twisted_bow(self, dragon_arrows: bool = True, style: PlayerStyle = None) -> PlayerStyle:
        gear = (Gear.from_bb('dragon arrow'),) if dragon_arrows else tuple()
        style = style if style else BowStyles.default
        return self.equip(
            Weapon.from_bb('twisted bow'),
            *gear,
            style=style
        )

    def equip_blowpipe(self, dragon_darts: bool = True, style: PlayerStyle = None) -> PlayerStyle:
        gear = (Gear.from_bb('dragon darts'),) if dragon_darts else tuple()
        style = style if style else ThrownStyles.default
        return self.equip(
            SpecialWeapon.from_bb('toxic blowpipe'),
            *gear,
            style=style
        )

    def equip_black_chins(self, buckler: bool = True, style: PlayerStyle = None) -> PlayerStyle:
        # TODO: Look into ammunition problems with chinchompa calculations
        gear = (Gear.from_bb('twisted buckler'), ) if buckler else tuple()
        style = style if style else ChinchompaStyles.default

        self.unequip(GearSlots.ammunition)

        return self.equip(
            Weapon.from_bb('black chinchompa'),
            *gear,
            style=style
        )

    def equip_zaryte_crossbow(self, buckler: bool = True, rubies: bool = False, diamonds: bool = False,
                              style: PlayerStyle = None) -> PlayerStyle:
        gear = []

        if rubies:
            gear.append(Gear.from_bb('ruby dragon bolts (e)'))
        elif diamonds:
            gear.append(Gear.from_bb('diamond dragon bolts (e)'))

        if buckler:
            gear.append(Gear.from_bb('twisted buckler'))

        style = style if style else CrossbowStyles.default
        return self.equip(
            SpecialWeapon.from_bb('zaryte crossbow'),
            *gear,
            style=style,
        )

    def equip_dorgeshuun_crossbow(self, buckler: bool = True, bone_bolts: bool = True, style: PlayerStyle = None) \
            -> PlayerStyle:
        if style is not None:
            weapon_style = style
        else:
            weapon_style = CrossbowStyles.get_style(PlayerStyle.accurate)

        gear_options = (Gear.from_bb('twisted buckler'), Gear.from_bb('bone bolts'))
        gear_bools = (buckler, bone_bolts)
        gear = [g for g, b in zip(gear_options, gear_bools) if b]

        return self.equip(
            SpecialWeapon.from_bb('dorgeshuun crossbow'),
            *gear,
            style=weapon_style
        )

    def equip_crystal_bowfa(self, crystal_set: bool = True, style: PlayerStyle = None) -> PlayerStyle:
        if crystal_set:
            self.equip_crystal_set()

        style = style if style else BowStyles.default
        return self.equip(
            Weapon.from_bb('bow of faerdhinen'),
            style=style
        )

    # magic gear swaps

    def equip_ancestral_set(self):
        self.equip(
            Gear.from_bb('ancestral hat'),
            Gear.from_bb('ancestral robe top'),
            Gear.from_bb('ancestral robe bottoms')
        )

    def equip_sang(self, arcane: bool = True, style: PlayerStyle = None) -> PlayerStyle:
        gear = (Gear.from_bb('arcane spirit shield'),) if arcane else tuple()
        style = style if style else PoweredStaffStyles(PlayerStyle.accurate)
        return self.equip(
            Weapon.from_bb('sanguinesti staff'),
            *gear,
            style=style
        )

    def equip_harm(self, tome: bool = True, style: PlayerStyle = None) -> PlayerStyle:
        gear = (Gear.from_bb('tome of fire'),) if tome else tuple()
        style = style if style else StaffStyles.default
        return self.equip(
            Weapon.from_bb('harmonised staff'),
            *gear,
            style=style
        )
