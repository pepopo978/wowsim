import random

from sim.dot import Dot
from sim.spell import Spell
from sim.spell_school import DamageType
from sim.talent_school import TalentSchool


class WarlockShadowDot(Dot):
    @property
    def time_between_ticks(self):
        haste_factor = self.owner.get_haste_factor_for_talent_school(
            TalentSchool.Affliction, DamageType.SHADOW)

        if haste_factor > 1:
            return round(self.base_time_between_ticks / haste_factor, 2)

        return self.base_time_between_ticks

class CorruptionDot(WarlockShadowDot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__(Spell.CORRUPTION.value, owner, env, DamageType.SHADOW, cast_time)

        self.coefficient = 0.1666
        self.base_time_between_ticks = 3


        
        # Base duration is 18 seconds (6 ticks * 3 seconds)
        # Eye of Dormant Corruption adds 3 seconds (1 extra tick)
        base_ticks = 6
        if owner.opts.eye_of_dormant_corruption:
            base_ticks += 1
        # Nemesis 5pc adds 3 seconds
        if owner.opts.nemesis_duration_bonus_2:
            base_ticks += 1

        self.ticks_left = base_ticks
        self.starting_ticks = base_ticks
        self.base_tick_dmg = 137

        #Corrupted soul (nemesis 8pc) increases damage of your next corruption by 15% on proc
        if owner.corrupted_soul:
            self.base_tick_dmg = 137 * 1.15
            self.coefficient = 0.1666 * 1.15 #Don't know if it also increases sp scaling
            owner.corrupted_soul = False

    def _do_dmg(self):
        super()._do_dmg()

        if hasattr(self.owner.tal, "nightfall") and self.owner.tal.nightfall > 0:
                if random.randint(1, 100) <= self.owner.tal.nightfall * 2:
                    self.owner.nightfall_proc()


class CurseOfAgonyDot(WarlockShadowDot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__(Spell.CURSE_OF_AGONY.value, owner, env, DamageType.SHADOW, cast_time)

        self.coefficient = 0.0833
        self.base_time_between_ticks = 2
        self.ticks_left = 12
        self.starting_ticks = 12
        self.base_tick_dmg = 87

        if self.owner.opts.doomcaller_coa_bonus_25:
            # 5% more Curse of Agony damage
            self.base_tick_dmg *= 1.05

    def _get_effective_tick_dmg(self):
        standard_tick_dmg = super()._get_effective_tick_dmg()

        if self.owner.tal.improved_curse_of_agony == 3:
            # 3/6/10% damage per point
            standard_tick_dmg *= 1.1
        elif self.owner.tal.improved_curse_of_agony == 2:
            # 3/6/10% damage per point
            standard_tick_dmg *= 1.06
        elif self.owner.tal.improved_curse_of_agony == 1:
            # 3/6/10% damage per point
            standard_tick_dmg *= 1.03

        # first four ticks each deal 1/24 of the damage each (about 4.2%),
        # the next four deal 1/12 of the damage (about 8.3%),
        # and then the last four each deal 1/8 of the damage (12.5%).
        # In other words, the first four ticks combine to 1/6 (16.6%) of the damage,
        # the next four to 1/3 (33.3%),
        # and the last four together to about one half of the total damage."
        # https://wowwiki-archive.fandom.com/wiki/Curse_of_Agony
        if self.ticks_left >= 8:
            # instead of 1/12 of the damage use 1/24 for tick 11,10,9,8
            return int(standard_tick_dmg * 0.5)
        elif self.ticks_left >= 4:
            # 1/12 of the damage for tick 7,6,5,4
            return int(standard_tick_dmg)
        elif self.ticks_left >= 0:
            # 1/8 of the damage for tick 3,2,1,0
            return int(standard_tick_dmg * 1.5)
        else:
            return 0


class SiphonLifeDot(WarlockShadowDot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__(Spell.SIPHON_LIFE.value, owner, env, DamageType.SHADOW, cast_time)

        self.coefficient = .1
        self.base_time_between_ticks = 3
        self.ticks_left = 10  # 30 seconds total / 3 seconds per tick = 10 ticks
        self.starting_ticks = 10
        self.base_tick_dmg = 45  # 450 damage total / 10 ticks = 45 damage per tick

    def _get_effective_tick_dmg(self):
        dmg = self.base_tick_dmg + self.sp * self.coefficient
        if self.owner.opts.siphon_life_bonus_35:
            # 50% more siphon
            dmg *= 1.5

        return int(self.owner.modify_dmg(dmg, self.damage_type, is_periodic=True))


class FeastOfHakkarDot(Dot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__("Feast of Hakkar", owner, env, DamageType.SHADOW, cast_time)

        self.coefficient = 0  # No spell power scaling
        self.base_time_between_ticks = 1  # Ticks every 1 second
        self.ticks_left = 10  # 10 total ticks
        self.starting_ticks = 10
        self.base_tick_dmg = 30  # 30 damage per tick
