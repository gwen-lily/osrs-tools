"""Gossip, gossip, * just stop it / Everybody knows I'm a mother fuckin monster

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-27                                                        #
###############################################################################
"""
from __future__ import annotations

from dataclasses import dataclass, field

from osrs_tools.combat import combat as cmb
from osrs_tools.data import Level, MonsterLocations, MonsterTypes, Slayer, StyleBonus
from osrs_tools.stats.stats import AggressiveStats, DefensiveStats, MonsterLevels
from osrs_tools.style.style import MonsterStyle, MonsterStyles
from osrs_tools.timers.timers import Timer

from ..character import Character, CharacterError

###############################################################################
# exceptions                                                                  #
###############################################################################


class MonsterError(CharacterError):
    ...


###############################################################################
# main class                                                                  #
###############################################################################


@dataclass
class Monster(Character):
    _levels: MonsterLevels = field(repr=False)
    _attack_delay: int = field(init=False, default=0)
    _active_style: MonsterStyle | None = None
    _aggressive_bonus: AggressiveStats = field(default_factory=AggressiveStats.no_bonus)
    combat_level: Level | None = field(default=None, repr=False)
    _defensive_bonus: DefensiveStats = field(default_factory=DefensiveStats.no_bonus)
    exp_modifier: float = 1.0
    levels: MonsterLevels = field(init=False)
    location: MonsterLocations = MonsterLocations.NONE
    _min_levels: MonsterLevels = field(repr=False, default_factory=MonsterLevels.zeros)
    slayer_category: Slayer = Slayer.NONE
    special_attributes: list[MonsterTypes] = field(default_factory=list)
    _styles: MonsterStyles | None = None
    _timers: list[Timer] = field(init=False, default_factory=list)

    # dunder and helper methods ###############################################

    def __post_init__(self):
        self.reset_stats()

        if self._styles is not None:
            self._active_style = self.styles.default

    def __copy__(self) -> Monster:
        _val = super().__copy__()
        assert isinstance(_val, Monster)

        return _val

    # event and effect methods ################################################

    # properties ##############################################################

    @property
    def styles(self) -> MonsterStyles:
        assert isinstance(self._styles, MonsterStyles)
        return self._styles

    @styles.setter
    def styles(self, __value: MonsterStyles, /) -> None:
        self._styles = __value

    @property
    def effective_melee_attack_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.melee_attack
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.levels.attack, style_bonus)

    @property
    def _effective_melee_strength_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.melee_strength
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.levels.strength, style_bonus)

    @property
    def _effective_defence_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.defence
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.levels.defence, style_bonus)

    @property
    def _effective_ranged_attack_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.ranged_attack
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.levels.ranged, style_bonus)

    @property
    def _effective_ranged_strength_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.ranged_strength
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.levels.ranged, style_bonus)

    @property
    def effective_magic_attack_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.magic_attack
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.lvl.magic, style_bonus)

    @property
    def effective_magic_strength_level(self) -> Level:
        return self.effective_magic_attack_level

    @property
    def effective_magic_defence_level(self) -> Level:
        defensive_level = self.levels.magic
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.magic_attack
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(defensive_level, style_bonus)

    @classmethod
    def from_bb(cls, name: str, **kwargs):

        options = {
            "ignores_defence": False,
            "ignores_prayer": False,
            "attack_speed_modifier": False,
            "attack_range_modifier": False,
            "style_index": 0,
            "defence_floor": 0,
        }
        options.update(kwargs)

        name = name.lower()
        mon_df = rr.lookup_normal_monster_by_name(name)

        if mon_df["location"].values[0] == "raids":
            raise MonsterError(f"{name=} must be an instance of {CoxMonster}")

        # attack style parsing
        damage_types_str: str = mon_df["main attack style"].values[0]
        damage_types = damage_types_str.split(" and ")
        styles = []

        for dt in damage_types:
            if not dt:
                continue

            styles.append(
                MonsterStyle(
                    damage_type=dt,
                    name=dt,
                    attack_speed=mon_df["attack speed"].values[0],
                    ignores_defence=options["ignores_defence"],
                    ignores_prayer=options["ignores_prayer"],
                    attack_speed_modifier=options["attack_speed_modifier"],
                    attack_range_modifier=options["attack_range_modifier"],
                )
            )

        attack_styles = StylesCollection(name=damage_types_str, styles=tuple(styles))
        if len(attack_styles.styles) > 0:
            active_style = attack_styles.styles[0]
        else:
            active_style = MonsterStyle.default_style()

        # type parsing
        raw_type_value = mon_df["type"].values[0]
        special_attributes = []

        if raw_type_value == "demon":
            special_attributes.append(MonsterTypes.DEMON)
        elif raw_type_value == "dragon":
            special_attributes.append(MonsterTypes.DRACONIC)
        elif raw_type_value == "fire":
            special_attributes.append(MonsterTypes.FIERY)
        elif raw_type_value == "kalphite":
            special_attributes.append(MonsterTypes.KALPHITE)
        elif raw_type_value == "kurask":
            special_attributes.append(MonsterTypes.LEAFY)
        elif raw_type_value == "vorkath":
            special_attributes.extend([MonsterTypes.DRACONIC, MonsterTypes.UNDEAD])
        elif raw_type_value == "undead":
            special_attributes.append(MonsterTypes.UNDEAD)
        elif raw_type_value == "vampyre - tier 1":
            special_attributes.extend(
                [MonsterTypes.VAMPYRE, MonsterTypes.VAMPYRE_TIER_1]
            )
        elif raw_type_value == "vampyre - tier 2":
            special_attributes.extend(
                [MonsterTypes.VAMPYRE, MonsterTypes.VAMPYRE_TIER_2]
            )
        elif raw_type_value == "vampyre - tier 3":
            special_attributes.extend(
                [MonsterTypes.VAMPYRE, MonsterTypes.VAMPYRE_TIER_3]
            )
        elif raw_type_value == "guardian":
            raise MonsterError(f"{name=} must be an instance of {Guardian}")
        elif raw_type_value == "":
            pass
        else:
            raise MonsterError(
                f"{name=} {raw_type_value=} is an unsupported or undefined type"
            )

        exp_modifier = 1 + mon_df["exp bonus"].values[0]

        location_enum = None
        location_src = mon_df["location"].values[0]

        for loc in MonsterLocations:
            if location_src == loc.name:
                location_enum = loc

        return cls(
            name=name,
            levels=MonsterLevels.from_bb(name),
            aggressive_bonus=AggressiveStats.from_bb(name),
            defensive_bonus=DefensiveStats.from_bb(name),
            styles=attack_styles,
            active_style=active_style,
            location=location_enum,
            exp_modifier=exp_modifier,
            combat_level=mon_df["combat level"].values[0],
            defence_floor=options["defence_floor"],
            special_attributes=tuple(special_attributes),
            **options,
        )


@define(**character_attrs_settings)
class Dummy(Monster):
    base_levels = field(factory=MonsterLevels.dummy_levels, repr=False)
    levels = field(init=False, repr=False)
    name: str = field(default="dummy")
    level_bounds = field(factory=MonsterLevels.zeros, repr=False)
    styles_coll = None
    active_style = None
    last_attacked: Character | None = field(repr=False, default=None)
    last_attacked_by: Character | None = field(repr=False, default=None)
    aggressive_bonus = field(factory=AggressiveStats.no_bonus, repr=False)
    defensive_bonus = field(factory=DefensiveStats.no_bonus, repr=False)

    styles = field(default=None, repr=False)
    active_style = field(default=None, repr=False)
    location = field(default=MonsterLocations.WILDERNESS, repr=False)
    exp_modifier = field(default=None, repr=False)
    combat_level = field(default=None, repr=False)
    special_attributes = field(default=tuple(t for t in MonsterTypes), repr=False)


class CoxMonster(Monster):
    ...


class SpecificCoxMonster(CoxMonster):
    ...
