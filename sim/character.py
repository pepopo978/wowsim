import functools
import random
from dataclasses import fields, dataclass

from sim.cooldown_usages import CooldownUsages
from sim.env import Environment
from sim.equipped_items import EquippedItems
from sim.spell import Spell
from sim.spell_school import DamageType
from sim.talent_school import TalentSchool


class Character:
    def __init__(self,
                 tal: dataclass,
                 name: str,
                 sp: int,
                 crit: float,
                 hit: float,
                 haste: float,
                 lag: float,
                 equipped_items: EquippedItems = None,
                 ):

        self.name = name
        self.sp = sp
        self.crit = crit
        self.hit = hit
        self.haste = haste
        self.lag = lag
        self.env = None

        self.tal = tal

        self.damage_type_sp = {
            DamageType.PHYSICAL: 0,
            DamageType.FIRE: 0,
            DamageType.FROST: 0,
            DamageType.ARCANE: 0,
            DamageType.NATURE: 0,
            DamageType.SHADOW: 0,
            DamageType.HOLY: 0
        }

        self.damage_type_haste = {
            DamageType.PHYSICAL: 0,
            DamageType.FIRE: 0,
            DamageType.FROST: 0,
            DamageType.ARCANE: 0,
            DamageType.NATURE: 0,
            DamageType.SHADOW: 0,
            DamageType.HOLY: 0
        }

        self.damage_type_hit = {
            DamageType.PHYSICAL: 0,
            DamageType.FIRE: 0,
            DamageType.FROST: 0,
            DamageType.ARCANE: 0,
            DamageType.NATURE: 0,
            DamageType.SHADOW: 0,
            DamageType.HOLY: 0
        }

        self.damage_type_crit = {
            DamageType.PHYSICAL: 0,
            DamageType.FIRE: 0,
            DamageType.FROST: 0,
            DamageType.ARCANE: 0,
            DamageType.NATURE: 0,
            DamageType.SHADOW: 0,
            DamageType.HOLY: 0
        }

        self.damage_type_crit_mult = {
            DamageType.PHYSICAL: 0,
            DamageType.FIRE: 0,
            DamageType.FROST: 0,
            DamageType.ARCANE: 0,
            DamageType.NATURE: 0,
            DamageType.SHADOW: 0,
            DamageType.HOLY: 0
        }

        self.talent_school_haste = {
            TalentSchool.Affliction: {},
            TalentSchool.Demonology: {},
            TalentSchool.Destruction: {},
        }

        # avoid circular import
        from sim.cooldowns import Cooldowns
        self.cds = Cooldowns(self)

        self.equipped_items = equipped_items
        self.item_proc_handler = None

        # buff name -> uptime
        self.buff_uptimes = {}

        # buff name -> start time
        self.buff_start_times = {}

        self._dmg_modifier = 1
        self._trinket_haste = {}
        self._cooldown_haste = {}
        self._consume_haste = {}
        self._sp_bonus = 0
        self._crit_bonus = 0

        self.used_cds = {}
        self.num_partials = 0
        self.num_resists = 0

    def get_class(self):
        raise NotImplementedError("Subclasses should implement this method")

    def attach_env(self, env: Environment):
        self.env = env
        if self.equipped_items:
            # avoid circular import
            from sim.item_proc_handler import ItemProcHandler
            self.item_proc_handler = ItemProcHandler(self, self.env, self.equipped_items)

    def add_remaining_buff_uptime(self):
        for buff_name, start_time in self.buff_start_times.items():
            if buff_name not in self.buff_uptimes:
                self.buff_uptimes[buff_name] = 0

            self.buff_uptimes[buff_name] += self.env.now - start_time

    def reset(self):
        # avoid circular import
        from sim.cooldowns import Cooldowns
        self.cds = Cooldowns(self)

        self._dmg_modifier = 1
        self._trinket_haste = {}
        self._cooldown_haste = {}
        self._consume_haste = {}
        self._sp_bonus = 0
        self.num_partials = 0
        self.num_resists = 0

        self.buff_uptimes = {}
        self.buff_start_times = {}

        self.used_cds = {}

    def has_trinket_or_cooldown_haste(self):
        return len(self._trinket_haste) > 20 or len(self._cooldown_haste) > 20

    def get_haste_factor_for_damage_type(self, damage_type: DamageType):
        haste_factor = 1 + self.haste / 100

        trinket_haste_factor = 1
        for haste in self._trinket_haste.values():
            trinket_haste_factor *= 1 + haste / 100

        cooldown_haste_factor = 1
        for haste in self._cooldown_haste.values():
            cooldown_haste_factor *= 1 + haste / 100

        consume_haste_factor = 1
        for haste in self._consume_haste.values():
            consume_haste_factor *= 1 + haste / 100

        damage_type_haste_factor = 1 + self.damage_type_haste[damage_type] / 100

        return haste_factor * trinket_haste_factor * cooldown_haste_factor * consume_haste_factor * damage_type_haste_factor

    def get_haste_factor_for_talent_school(self, talent_school: TalentSchool, damage_type: DamageType):
        base_haste_factor = self.get_haste_factor_for_damage_type(damage_type)
        if talent_school == TalentSchool.Affliction:
            ts_haste_factor = 1
            for haste in self.talent_school_haste[TalentSchool.Affliction].values():
                ts_haste_factor *= 1 + haste / 100

            return base_haste_factor * ts_haste_factor

        return base_haste_factor

    def _get_cast_time(self, base_cast_time: float, damage_type: DamageType):
        if base_cast_time <= 0:
            return 0

        haste_scaling_factor = self.get_haste_factor_for_damage_type(damage_type)

        return base_cast_time / haste_scaling_factor + self.lag

    def _rotation_callback(self, mage, name, *args, **kwargs):
        rotation = getattr(mage, '_' + name)
        return rotation(*args, **kwargs)

    def _set_rotation(self, name, *args, **kwargs):
        self.rotation = functools.partial(self._rotation_callback, name=name, *args, **kwargs)

    def _random_delay(self, secs=2):
        if secs:
            delay = round(random.random() * secs, 2)
            self.print(f"Random initial delay of {delay} seconds")
            yield self.env.timeout(delay)

    def _use_cds(self, cooldown_usages: CooldownUsages = CooldownUsages()):
        for field in fields(cooldown_usages):
            cooldown_obj = getattr(self.cds, field.name)
            use_times = getattr(cooldown_usages, field.name, None)
            if isinstance(use_times, list):
                for index, use_time in enumerate(use_times):
                    if use_time is not None and cooldown_obj.usable and self.env.now >= use_time:
                        if field.name not in self.used_cds:
                            self.used_cds[field.name] = {
                                use_time: True
                            }
                            cooldown_obj.activate()
                        elif use_time not in self.used_cds[field.name]:
                            self.used_cds[field.name][use_time] = True
                            cooldown_obj.activate()

            else:
                use_time = use_times
                if use_time is not None and cooldown_obj.usable and self.env.now >= use_time:
                    if field.name not in self.used_cds:
                        self.used_cds[field.name] = {
                            use_time: True
                        }
                        cooldown_obj.activate()
                    elif use_time not in self.used_cds[field.name]:
                        self.used_cds[field.name][use_time] = True
                        cooldown_obj.activate()

    def _roll_proc(self, proc_chance: float):
        return random.randint(1, 1000) <= 10 * proc_chance

    def _roll_hit(self, hit_chance: float, damage_type: DamageType):
        return random.randint(1, 1000) <= 10 * (hit_chance + self.damage_type_hit[damage_type])

    def _roll_crit(self, crit_chance: float, damage_type: DamageType):
        return random.randint(1, 1000) <= 10 * (crit_chance + self._crit_bonus + self.damage_type_crit[damage_type])

    def roll_spell_dmg(self, min_dmg: int, max_dmg: int, spell_coeff: float, damage_type: DamageType):
        dmg = random.randint(min_dmg, max_dmg)
        dmg += (self.sp + self._sp_bonus + self.damage_type_sp[damage_type]) * spell_coeff

        return dmg

    def _get_crit_multiplier(self, talent_school: TalentSchool, damage_type: DamageType):
        return 1.5 + self.damage_type_crit_mult[damage_type]

    def _check_for_procs(self, spell: Spell, damage_type: DamageType):
        if self.item_proc_handler:
            self.item_proc_handler.check_for_procs(self.env.now, spell, damage_type)

    def roll_partial(self, is_dot: bool, is_binary: bool):
        if is_binary or self.env.mob_level < 63:
            return 1

        roll = random.random()
        if is_dot:
            # No partial: 98.53 %
            # 25 % partial: 1.1 %
            # 50 % partial: .366 %
            # 75 % partial: 0 %
            if roll <= .9853:
                return 1
            elif roll <= .9963:
                self.num_partials += 1
                return .75
            elif roll <= 1:
                self.num_partials += 1
                return .5
        else:
            # No partial: 82.666 %
            # 25 % partial: 13 %
            # 50 % partial: 4.166 %
            # 75 % partial: 1 %
            if roll <= .82666:
                return 1
            elif roll <= .95666:
                self.num_partials += 1
                return .75
            elif roll <= .99832:
                self.num_partials += 1
                return .5
            elif roll <= 1:
                self.num_partials += 1
                return .25

    def modify_dmg(self, dmg: int, damage_type: DamageType, is_periodic: bool):
        if self._dmg_modifier != 1:
            dmg *= self._dmg_modifier
        # apply env debuffs
        return self.env.debuffs.modify_dmg(self, dmg, damage_type, is_periodic)

    def print(self, msg):
        if self.env.print:
            self.env.p(f"{self.env.time()} - ({self.name}) {msg}")

    def add_trinket_haste(self, haste_key, haste_value):
        self._trinket_haste[haste_key] = haste_value

    def remove_trinket_haste(self, haste_key):
        del self._trinket_haste[haste_key]

    def add_cooldown_haste(self, haste_key, haste_value):
        self._cooldown_haste[haste_key] = haste_value

    def remove_cooldown_haste(self, haste_key):
        del self._cooldown_haste[haste_key]

    def add_consume_haste(self, haste_key, haste_value):
        self._consume_haste[haste_key] = haste_value

    def remove_consume_haste(self, haste_key):
        del self._consume_haste[haste_key]

    def add_talent_school_haste(self, school, haste_key, haste_value):
        self.talent_school_haste[school][haste_key] = haste_value

    def remove_talent_school_haste(self, school, haste_key):
        del self.talent_school_haste[school][haste_key]

    def add_sp_bonus(self, sp):
        self._sp_bonus += sp

    def remove_sp_bonus(self, sp):
        self._sp_bonus -= sp

    def add_crit_bonus(self, crit):
        self._crit_bonus += crit

    def remove_crit_bonus(self, crit):
        self._crit_bonus -= crit

    @property
    def dmg_modifier(self):
        return self._dmg_modifier

    @property
    def eff_sp(self):
        return self.sp + self._sp_bonus

    def add_dmg_modifier(self, mod):
        self._dmg_modifier += mod

    def remove_dmg_modifier(self, mod):
        self._dmg_modifier -= mod
