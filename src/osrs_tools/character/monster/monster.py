"""Gossip, gossip, * just stop it / Everybody knows I'm a mother fuckin monster

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-27                                                        #
###############################################################################
"""
from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field

from osrs_tools import gear, utils
from osrs_tools import utils_combat as cmb
from osrs_tools.character import Character, CharacterError
from osrs_tools.character.player import Player
from osrs_tools.data import DT, DUMMY_NAME, MagicDamageTypes, MonsterLocations, MonsterTypes, Slayer, Slots, Stances
from osrs_tools.stats import AggressiveStats, DefensiveStats, MonsterLevels
from osrs_tools.style import MonsterStyle, MonsterStyles
from osrs_tools.timers import Timer
from osrs_tools.tracked_value import Level, Roll, StyleBonus
from typing_extensions import Self

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
    _aggressive_bonus: AggressiveStats = field(default_factory=AggressiveStats)
    combat_level: Level | None = field(default=None, repr=False)
    _defensive_bonus: DefensiveStats = field(default_factory=DefensiveStats)
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
        _val = copy(self)
        assert isinstance(_val, Monster)

        return _val

    # event and effect methods ################################################

    # properties ##############################################################

    @property
    def lvl(self) -> MonsterLevels:
        return self.levels

    @lvl.setter
    def lvl(self, __value: MonsterLevels) -> None:
        self.levels = __value

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
    def effective_melee_strength_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.melee_strength
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.levels.strength, style_bonus)

    @property
    def effective_defence_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.defence
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.levels.defence, style_bonus)

    @property
    def effective_ranged_attack_level(self) -> Level:
        astyle = self._active_style
        if astyle is not None and astyle._combat_bonus is not None:
            style_bonus = astyle._combat_bonus.ranged_attack
        else:
            style_bonus = StyleBonus(0)

        return cmb.effective_level(self.levels.ranged, style_bonus)

    @property
    def effective_ranged_strength_level(self) -> Level:
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

    @property
    def aggressive_bonus(self) -> AggressiveStats:
        return self._aggressive_bonus

    @property
    def defensive_bonus(self) -> DefensiveStats:
        return self._defensive_bonus

    # combat methods

    def defence_roll(self, other: Character, _dt: DT) -> Roll:

        _roll = super().defence_roll(other, _dt)

        if isinstance(other, Player) and _dt in MagicDamageTypes:
            if other.eqp[Slots.RING] == gear.BrimstoneRing:
                reduction = _roll // 10 / 4
                _roll -= reduction

        return _roll

    # class methods

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
        mon_df = utils.lookup_normal_monster_by_name(name)

        if mon_df["location"].values[0] == "raids":
            raise TypeError(cls)

        # attack style parsing
        _dts = mon_df["main attack style"]
        damage_types_str = _dts.values[0]
        assert isinstance(damage_types_str, str)
        damage_types = damage_types_str.split(" and ")
        styles = []

        for dt in damage_types:
            if not dt:
                continue

            for _dt in DT:
                if _dt.value == dt:
                    dt_enum = _dt
                    break
            else:
                raise ValueError(dt)

            styles.append(
                MonsterStyle(
                    name=dt_enum.value,
                    damage_type=dt_enum,
                    stance=Stances.NPC,
                    _attack_speed=mon_df["attack speed"].values[0],
                    ignores_defence=options["ignores_defence"],
                    ignores_prayer=options["ignores_prayer"],
                    attack_speed_modifier=options["attack_speed_modifier"],
                    attack_range_modifier=options["attack_range_modifier"],
                )
            )

        attack_styles = MonsterStyles(name=name, styles=styles, default=styles[0])

        if len(attack_styles.styles) > 0:
            active_style = attack_styles.default
        else:
            active_style = None

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
            special_attributes.extend([MonsterTypes.VAMPYRE_TIER_1])
        elif raw_type_value == "vampyre - tier 2":
            special_attributes.extend([MonsterTypes.VAMPYRE_TIER_2])
        elif raw_type_value == "vampyre - tier 3":
            special_attributes.extend([MonsterTypes.VAMPYRE_TIER_3])
        elif raw_type_value == "guardian":
            raise TypeError(cls)
        elif raw_type_value == "":
            pass
        else:
            raise MonsterError(f"{name=} {raw_type_value=} is an unsupported or undefined type")

        _exp_mod = mon_df["exp bonus"].values[0]
        assert isinstance(_exp_mod, (float, int))
        exp_modifier = 1 + _exp_mod

        location_enum = None
        location_src = mon_df["location"].values[0]

        for loc in MonsterLocations:
            if location_src == loc.name:
                location_enum = loc
                break
        else:
            raise ValueError(location_src)

        return cls(
            name=name,
            _levels=MonsterLevels.from_bb(name),
            _aggressive_bonus=AggressiveStats.from_bb(name),
            _defensive_bonus=DefensiveStats.from_bb(name),
            _styles=attack_styles,
            _active_style=active_style,
            location=location_enum,
            exp_modifier=exp_modifier,
            combat_level=mon_df["combat level"].values[0],
            special_attributes=special_attributes,
            **options,
        )

    @classmethod
    def dummy(cls) -> Monster:
        _lvls = MonsterLevels.dummy_levels()
        _name = DUMMY_NAME
        _location = MonsterLocations.WILDERNESS
        _spec_attrs = [_t for _t in MonsterTypes]

        return cls(
            name=_name,
            _levels=_lvls,
            location=_location,
            special_attributes=_spec_attrs,
        )

    # foo methods

    def _initialize_timers(self, reinitialize: bool = False) -> Self:
        return self

    def _update_stats(self) -> Self:
        return super()._update_stats()
