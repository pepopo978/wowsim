import random
from functools import partial

from sim.character import Character, CooldownUsages
from sim.cooldowns import Cooldown
from sim.decorators import simclass, simrotation
from sim.env import Environment
from sim.equipped_items import EquippedItems
from sim.fire_dots import ImmolateDot
from sim.shadow_dots import CorruptionDot, CurseOfAgonyDot, SiphonLifeDot
from sim.spell import Spell, SPELL_COEFFICIENTS, SPELL_HITS_MULTIPLE_TARGETS, SPELL_TRIGGERS_ON_HIT, \
    SPELL_PROJECTILE_SPEED
from sim.spell_school import DamageType
from sim.talent_school import TalentSchool
from sim.warlock_options import WarlockOptions
from sim.warlock_talents import WarlockTalents


class ConflagrateCooldown(Cooldown):
    def __init__(self, character: Character):
        super().__init__(character)

    @property
    def duration(self):
        return 0

    @property
    def cooldown(self):
        return 10


class SoulFireCooldown(Cooldown):
    def __init__(self, character: Character):
        super().__init__(character)

    @property
    def duration(self):
        return 0

    @property
    def cooldown(self):
        return 30


class DarkHarvestCooldown(Cooldown):
    def __init__(self, character: Character):
        super().__init__(character)

    @property
    def duration(self):
        return 0

    @property
    def cooldown(self):
        return 30


@simclass(WarlockTalents, WarlockOptions)
class Warlock(Character):
    def __init__(self,
                 tal: WarlockTalents,
                 opts: WarlockOptions = WarlockOptions(),
                 name: str = '',
                 sp: int = 0,
                 crit: float = 0,
                 hit: float = 0,
                 haste: float = 0,
                 lag: float = 0.07,  # lag added by server tick time
                 equipped_items: EquippedItems = None,
                 ):
        super().__init__(tal, name, sp, crit, hit, haste, lag, equipped_items)
        self.tal = tal
        self.opts = opts

        # Warlock
        self.nightfall = False

        if self.tal:
            if self.tal.rapid_deterioration:
                self.talent_school_haste[TalentSchool.Affliction]["rapid_deterioration"] = 6

    def get_class(self):
        return self.__class__.__name__

    def _setup_cds(self):
        self.conflagrate_cd = ConflagrateCooldown(self)
        self.soul_fire_cd = SoulFireCooldown(self)
        self.dark_harvest_cd = DarkHarvestCooldown(self)

    def attach_env(self, env: Environment):
        super().attach_env(env)

        self._setup_cds()

    def _get_hit_chance(self, spell: Spell):
        hit = self.hit
        # if affliction add suppression
        if spell in [Spell.CORRUPTION, Spell.CURSE_OF_AGONY, Spell.CURSE_OF_SHADOW, Spell.SIPHON_LIFE,
                     Spell.DRAIN_SOUL_CHANNEL,
                     Spell.DARK_HARVEST_CHANNEL]:
            hit += self.tal.suppression * 2

        return min(83 + self.hit, 99)

    def _get_crit_multiplier(self, damage_type: DamageType, talent_school: TalentSchool):
        mult = super()._get_crit_multiplier(talent_school, damage_type)
        if self.opts.crit_dmg_bonus_35:
            mult += 0.1
        if talent_school == TalentSchool.Destruction and self.tal.ruin:
            mult += 0.5
        return mult

    def modify_dmg(self, dmg: int, damage_type: DamageType, is_periodic: bool):
        dmg = super().modify_dmg(dmg, damage_type, is_periodic)

        if self.tal.soul_entrapment:
            dmg *= (1 + 0.02 * self.tal.soul_entrapment)

        if self.tal.imp_sacrifice:
            dmg *= 1.04

        if damage_type == DamageType.SHADOW:
            if self.tal.shadow_mastery:
                dmg *= 1.1

        if damage_type == DamageType.FIRE:
            if self.tal.emberstorm:
                dmg *= 1 + self.tal.emberstorm * 0.02
            if self.tal.improved_soul_fire and self.soul_fire_cd.on_cooldown:
                # while soul fire is on cooldown, the buff is active
                dmg *= 1 + self.tal.improved_soul_fire * 0.1

        return int(dmg)

    # resolve damage when spell reaches the target
    def _spell_resolve(self,
                       travel_time: float,
                       spell: Spell,
                       damage_type: DamageType,
                       talent_school: TalentSchool,
                       hit: bool,
                       crit: bool,
                       dmg: int,
                       partial_amount: float,
                       casting_time: float,
                       gcd_wait_time: float,
                       resolved_callback):

        if travel_time:
            yield self.env.timeout(travel_time)

        description = ""
        if self.env.print:
            if travel_time:
                description = f"({round(travel_time, 2)} travel)"
            else:
                description = f"({round(casting_time, 2)} cast)"
            if gcd_wait_time:
                description += f" ({round(gcd_wait_time, 2)} gcd)"
            if partial_amount != 1:
                description += f" ({int(partial_amount * 100)}% partial)"

            if damage_type == DamageType.SHADOW and self.env.debuffs.improved_shadow_bolt.is_active:
                description += " (ISB)"

            if not hit:
                self.print(f"{spell.value} {description} RESIST")
            elif not crit:
                self.print(f"{spell.value} {description} {dmg}")
            else:
                self.print(f"{spell.value} {description} **{dmg}**")

        if hit and SPELL_TRIGGERS_ON_HIT.get(spell, False):
            self._check_for_procs(
                spell=spell,
                damage_type=damage_type)

        if hit and self.cds.zhc.is_active():
            self.cds.zhc.use_charge()

        if hit and spell == Spell.CORRUPTION:
            # avoid calling register_spell_dmg as dots will register already
            self.env.debuffs.add_dot(CorruptionDot, self, max(casting_time, self.env.GCD))
        elif hit and spell == Spell.IMMOLATE:
            # avoid calling register_spell_dmg as dots will register already
            self.env.debuffs.add_dot(ImmolateDot, self, 0)

            self.env.meter.register_spell_dmg(
                char_name=self.name,
                spell_name=spell.value,
                dmg=dmg,
                cast_time=round(casting_time + gcd_wait_time, 2),
                aoe=False)

        else:
            self.env.meter.register_spell_dmg(
                char_name=self.name,
                spell_name=spell.value,
                dmg=dmg,
                cast_time=round(casting_time + gcd_wait_time, 2),
                aoe=spell in SPELL_HITS_MULTIPLE_TARGETS)

        if resolved_callback:
            resolved_callback(spell, hit, crit, dmg, partial_amount)
        else:
            raise Exception("missing spell resolved callback")

    # caller must handle any gcd cooldown
    # handle spell cast
    def _spell(self,
               spell: Spell,
               damage_type: DamageType,
               talent_school: TalentSchool,
               min_dmg: int,
               max_dmg: int,
               base_cast_time: float,
               crit_modifier: float,
               custom_gcd: float | None,
               on_gcd: bool,
               resolved_callback,
               calculate_cast_time: bool = True):

        casting_time = self._get_cast_time(base_cast_time, damage_type) if calculate_cast_time else base_cast_time

        gcd = custom_gcd if custom_gcd is not None else self.env.GCD
        gcd_wait_time = 0

        # account for gcd
        if on_gcd and casting_time < gcd:
            gcd_wait_time = gcd - casting_time if casting_time > self.lag else gcd

        # wait for cast
        if casting_time:
            yield self.env.timeout(casting_time)

        hit = self._roll_hit(self._get_hit_chance(spell), damage_type)
        crit = False
        dmg = 0

        if hit:
            if spell != Spell.CORRUPTION:
                crit = self._roll_crit(self.crit + crit_modifier, damage_type)

            dmg = self.roll_spell_dmg(min_dmg, max_dmg, SPELL_COEFFICIENTS.get(spell, 0), damage_type)
            dmg = self.modify_dmg(dmg, damage_type, is_periodic=False)
        else:
            self.num_resists += 1

        is_binary_spell = False

        partial_amount = self.roll_partial(is_dot=False, is_binary=is_binary_spell)
        if partial_amount < 1:
            dmg = int(dmg * partial_amount)

        # trigger spell resolve when it hits the target
        travel_time = 0
        if spell in SPELL_PROJECTILE_SPEED:
            travel_time = self.opts.distance_from_mob / SPELL_PROJECTILE_SPEED[spell]

        if crit:
            mult = self._get_crit_multiplier(damage_type, talent_school)
            dmg = int(dmg * mult)

        if spell in SPELL_PROJECTILE_SPEED:
            self.print(f"{spell.value} ({round(casting_time, 2)} cast)")

            self.env.process(
                self._spell_resolve(
                    travel_time=travel_time,
                    spell=spell,
                    damage_type=damage_type,
                    talent_school=talent_school,
                    hit=hit,
                    crit=crit,
                    dmg=dmg,
                    partial_amount=partial_amount,
                    casting_time=casting_time,
                    gcd_wait_time=gcd_wait_time,
                    resolved_callback=resolved_callback)
            )
        else:
            # spell hits target immediately
            yield from self._spell_resolve(
                travel_time=travel_time,
                spell=spell,
                damage_type=damage_type,
                talent_school=talent_school,
                hit=hit,
                crit=crit,
                dmg=dmg,
                partial_amount=partial_amount,
                casting_time=casting_time,
                gcd_wait_time=gcd_wait_time,
                resolved_callback=resolved_callback)

        # wait for gcd
        if gcd_wait_time:
            yield self.env.timeout(gcd_wait_time)

    def _fire_spell_resolved(self, spell, hit, crit, dmg, partial_amount):
        if spell == Spell.SOUL_FIRE:
            self.soul_fire_cd.activate()
        elif spell == Spell.CONFLAGRATE:
            self.conflagrate_cd.activate()

    def _fire_spell(self,
                    spell: Spell,
                    min_dmg: int,
                    max_dmg: int,
                    base_cast_time: float,
                    crit_modifier: float,
                    custom_gcd: float | None = None,
                    on_gcd: bool = True):

        yield from self._spell(spell=spell,
                               damage_type=DamageType.FIRE,
                               talent_school=TalentSchool.Destruction,
                               min_dmg=min_dmg,
                               max_dmg=max_dmg,
                               base_cast_time=base_cast_time,
                               crit_modifier=crit_modifier,
                               custom_gcd=custom_gcd,
                               on_gcd=on_gcd,
                               resolved_callback=self._fire_spell_resolved)

    def _shadow_spell_resolved(self, spell, hit, crit, dmg, partial_amount):
        if self.tal.improved_shadow_bolt and spell == Spell.SHADOWBOLT:
            if crit:
                if self._roll_proc(self.tal.improved_shadow_bolt * 20):
                    self.env.debuffs.improved_shadow_bolt.refresh(self)
            elif hit:
                if self._roll_proc(self.tal.improved_shadow_bolt * 2):
                    self.env.debuffs.improved_shadow_bolt.refresh(self)

    def _shadow_spell(self,
                      spell: Spell,
                      talent_school: TalentSchool,
                      min_dmg: int,
                      max_dmg: int,
                      base_cast_time: float,
                      crit_modifier: float,
                      custom_gcd: float | None = None,
                      on_gcd: bool = True,
                      calculate_cast_time: bool = True):
        yield from self._spell(spell=spell,
                               damage_type=DamageType.SHADOW,
                               talent_school=talent_school,
                               min_dmg=min_dmg,
                               max_dmg=max_dmg,
                               base_cast_time=base_cast_time,
                               crit_modifier=crit_modifier,
                               custom_gcd=custom_gcd,
                               on_gcd=on_gcd,
                               resolved_callback=self._shadow_spell_resolved,
                               calculate_cast_time=calculate_cast_time)

    def _shadow_dot(self,
                    spell: Spell,
                    base_cast_time: float,
                    cooldown: float = 0.0):
        casting_time = 0

        if base_cast_time > 0:
            casting_time = self._get_cast_time(base_cast_time, DamageType.SHADOW)

        # account for gcd
        if casting_time < self.env.GCD and cooldown == 0:
            cooldown = self.env.GCD - casting_time

        hit_chance = self._get_hit_chance(spell)
        hit = random.randint(1, 100) <= hit_chance

        if casting_time:
            yield self.env.timeout(casting_time)

        description = ""
        if self.env.print:
            description = f"({round(casting_time, 2)} cast)"
            if cooldown:
                description += f" ({round(cooldown, 2)} gcd)"

        if not hit:
            self.print(f"{spell.value} {description} RESIST")

            # register the cast
            self.env.meter.register_dot_cast(
                char_name=self.name,
                spell_name=spell.value,
                cast_time=max(casting_time, self.env.GCD))
        else:
            if hit and SPELL_TRIGGERS_ON_HIT.get(spell, False):
                self._check_for_procs(
                    spell=spell,
                    damage_type=DamageType.SHADOW)

            self.print(f"{spell.value} {description}")
            if spell == Spell.CURSE_OF_SHADOW:
                self.env.debuffs.add_curse_of_shadow_dot()
                if self.tal.malediction:
                    self.env.debuffs.add_dot(CurseOfAgonyDot, self, cooldown)

            elif spell == Spell.CORRUPTION:
                self.env.debuffs.add_dot(CorruptionDot, self, max(casting_time, self.env.GCD))
            elif spell == Spell.CURSE_OF_AGONY:
                self.env.debuffs.add_dot(CurseOfAgonyDot, self, cooldown)
            elif spell == Spell.SIPHON_LIFE:
                self.env.debuffs.add_dot(SiphonLifeDot, self, cooldown)

        if hit and self.cds.zhc.is_active():
            self.cds.zhc.use_charge()

        # handle gcd
        if cooldown:
            yield self.env.timeout(cooldown)

    def _channel_tick(self,
                      spell: Spell,
                      damage_type: DamageType,
                      min_dmg: int,
                      max_dmg: int,
                      tick_time: float):

        yield self.env.timeout(tick_time)

        description = ""
        if self.env.print:
            description = f"({round(tick_time, 2)} tick)"

            if damage_type == DamageType.SHADOW and self.env.debuffs.improved_shadow_bolt.is_active:
                description += " (ISB)"

        dmg = self.roll_spell_dmg(min_dmg, max_dmg, SPELL_COEFFICIENTS.get(spell, 0), damage_type)
        dmg = self.modify_dmg(dmg, damage_type, is_periodic=False)

        self.print(f"{spell.value} {description} {dmg}")

        if SPELL_TRIGGERS_ON_HIT.get(spell, False):
            self._check_for_procs(
                spell=spell,
                damage_type=damage_type)

        self.env.meter.register_dot_dmg(
            char_name=self.name,
            spell_name=spell.value,
            dmg=dmg,
            cast_time=round(tick_time, 2),
            aoe=spell in SPELL_HITS_MULTIPLE_TARGETS)

    def _shadowbolt(self):
        min_dmg = 482
        max_dmg = 539
        if self.nightfall:
            casting_time = 0
            self.nightfall = False
        else:
            casting_time = 3 - self.tal.bane * 0.1

        crit_modifier = self.tal.devastation

        yield from self._shadow_spell(spell=Spell.SHADOWBOLT,
                                        talent_school=TalentSchool.Destruction,
                                      min_dmg=min_dmg,
                                      max_dmg=max_dmg,
                                      crit_modifier=crit_modifier,
                                      base_cast_time=casting_time)

    def _immolate(self):
        mult = 1 + .04 * self.tal.improved_immolate
        dmg = int(279 * mult)
        casting_time = 2 - self.tal.bane * 0.1
        crit_modifier = self.tal.devastation

        yield from self._fire_spell(spell=Spell.IMMOLATE,
                                    min_dmg=dmg,
                                    max_dmg=dmg,
                                    crit_modifier=crit_modifier,
                                    base_cast_time=casting_time)

    def _soul_fire(self):
        min_dmg = 703
        max_dmg = 881

        casting_time = 6 - self.tal.bane * 0.4
        crit_modifier = self.tal.devastation

        yield from self._fire_spell(spell=Spell.SOUL_FIRE,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    crit_modifier=crit_modifier,
                                    base_cast_time=casting_time)

    def _searing_pain(self):
        min_dmg = 204
        max_dmg = 241
        casting_time = 1.5
        crit_modifier = self.tal.improved_searing_pain * 2 + self.tal.devastation

        yield from self._fire_spell(spell=Spell.SEARING_PAIN,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    crit_modifier=crit_modifier,
                                    base_cast_time=casting_time)

    def _conflagrate(self):
        min_dmg = 447
        max_dmg = 557

        casting_time = 0
        crit_modifier = self.tal.devastation

        if self.env.debuffs.is_dot_active(ImmolateDot, self):
            tick_dmg = self.env.debuffs.immolate_dots[self].get_effective_tick_dmg()

            min_dmg += tick_dmg
            max_dmg += tick_dmg

            self.env.debuffs.immolate_dots[self].ticks_left -= 1

        yield from self._fire_spell(spell=Spell.CONFLAGRATE,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    crit_modifier=crit_modifier,
                                    base_cast_time=casting_time)

    def _corruption(self):
        cast_time = 1.5 - self.tal.improved_corruption * 0.3
        yield from self._shadow_spell(
            spell=Spell.CORRUPTION,
            talent_school=TalentSchool.Affliction,
            min_dmg=137,
            max_dmg=137,
            base_cast_time=cast_time,
            crit_modifier=0,
            on_gcd=True,
        )

    def _curse_of_shadow(self):
        yield from self._shadow_dot(spell=Spell.CURSE_OF_SHADOW, base_cast_time=0)

    def _curse_of_agony(self):
        yield from self._shadow_dot(spell=Spell.CURSE_OF_AGONY, base_cast_time=0)

    def _siphon_life(self):
        yield from self._shadow_dot(spell=Spell.SIPHON_LIFE, base_cast_time=0)

    def _get_soul_siphon_multiplier(self):
        num_affliction_effects = 0

        if self.opts.permanent_curse:
            num_affliction_effects += 1
        else:
            # TODO add per owner tracking
            if self.env.debuffs.is_curse_of_shadows_active():
                num_affliction_effects += 1

        if self.env.debuffs.is_dot_active(CurseOfAgonyDot, self):
            num_affliction_effects += 1

        if self.env.debuffs.is_dot_active(CorruptionDot, self):
            num_affliction_effects += 1

        if self.env.debuffs.is_dot_active(SiphonLifeDot, self):
            num_affliction_effects += 1

        # max out at 4
        num_affliction_effects = min(num_affliction_effects, 4)

        return 1 + (self.tal.soul_siphon * 0.02 * num_affliction_effects)

    def _drain_soul_channel(self, channel_time: float = 6):
        self.env.meter.register_spell_dmg(
            char_name=self.name,
            spell_name=Spell.DRAIN_SOUL.value,
            dmg=0,
            cast_time=0)

        # check for resist
        if not self._roll_hit(self._get_hit_chance(Spell.DRAIN_SOUL_CHANNEL), DamageType.SHADOW):
            self.print(f"{Spell.DRAIN_SOUL_CHANNEL.value} ({round(self.env.GCD, 2)}) gcd RESIST")
            yield self.env.timeout(self.env.GCD)
            return
        else:
            self._check_for_procs(
                spell=Spell.DRAIN_SOUL_CHANNEL,
                damage_type=DamageType.SHADOW)
            self.print(f"{Spell.DRAIN_SOUL_CHANNEL.value}")

        num_ticks = 6

        haste_factor = self.get_haste_factor_for_talent_school(TalentSchool.Affliction, DamageType.SHADOW)
        channel_time /= haste_factor

        time_between_ticks = channel_time / num_ticks

        for i in range(num_ticks):
            if i == 0:
                yield from self._drain_soul_tick(tick_time=time_between_ticks + self.lag)  # initial delay
            else:
                yield from self._drain_soul_tick(tick_time=time_between_ticks)

    def _drain_soul_tick(self, tick_time: float = 3):
        dmg = 198 * 1.2 # mysterious extra dmg in game

        if self.tal.soul_siphon:
            dmg *= self._get_soul_siphon_multiplier()

        if self.tal.improved_drains:
            dmg *= 1 + self.tal.improved_drains * 0.05

        yield from self._channel_tick(
            spell=Spell.DRAIN_SOUL,
            damage_type=DamageType.SHADOW,
            min_dmg=int(dmg),
            max_dmg=int(dmg),
            tick_time=tick_time,
        )

    def _dark_harvest_channel(self, channel_time: float = 8):
        self.env.meter.register_spell_dmg(
            char_name=self.name,
            spell_name=Spell.DARK_HARVEST.value,
            dmg=0,
            cast_time=0)

        self.dark_harvest_cd.activate()

        # check for resist
        if not self._roll_hit(self._get_hit_chance(Spell.DARK_HARVEST_CHANNEL), DamageType.SHADOW):
            self.print(f"{Spell.DARK_HARVEST_CHANNEL.value} ({round(self.env.GCD, 2)}) gcd RESIST")
            yield self.env.timeout(self.env.GCD)
            return
        else:
            self._check_for_procs(
                spell=Spell.DARK_HARVEST_CHANNEL,
                damage_type=DamageType.SHADOW)
            self.print(f"{Spell.DARK_HARVEST_CHANNEL.value}")

        num_ticks = 8

        haste_factor = self.get_haste_factor_for_talent_school(TalentSchool.Affliction, DamageType.SHADOW)
        channel_time /= haste_factor

        time_between_ticks = channel_time / num_ticks

        self.add_talent_school_haste(TalentSchool.Affliction, Spell.DARK_HARVEST.value, 30)

        for i in range(num_ticks):
            if i == 0:
                yield from self._dark_harvest_tick(tick_time=time_between_ticks + self.lag)  # initial delay
            elif i == num_ticks - 1 and self.opts.doomcaller_dh_bonus_25:
                # last tick
                # 5 set bonus - The last tick of your Dark Harvest spell deals 400% damage
                yield from self._dark_harvest_tick(tick_time=time_between_ticks, dmg_multiplier=5)
            else:
                yield from self._dark_harvest_tick(tick_time=time_between_ticks)

        self.remove_talent_school_haste(TalentSchool.Affliction, Spell.DARK_HARVEST.value)

    def _dark_harvest_tick(self, tick_time: float = 3, dmg_multiplier: float = None):
        dmg = 158

        if dmg_multiplier is not None:
            dmg *= dmg_multiplier

        if self.tal.soul_siphon:
            dmg *= self._get_soul_siphon_multiplier()

        yield from self._channel_tick(
            spell=Spell.DARK_HARVEST,
            damage_type=DamageType.SHADOW,
            min_dmg=int(dmg),
            max_dmg=int(dmg),
            tick_time=tick_time,
        )

    def nightfall_proc(self):
        self.nightfall = True
        self.print("Nightfall proc!")

    def _spam_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            yield from self._shadowbolt()

    def _corruption_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
            else:
                yield from self._shadowbolt()

    def _agony_corruption_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if not self.env.debuffs.is_dot_active(CurseOfAgonyDot, self):
                yield from self._curse_of_agony()
            elif not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
            else:
                yield from self._shadowbolt()

    def _corruption_immolate_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
            elif not self.env.debuffs.is_dot_active(ImmolateDot, self):
                yield from self._immolate()
            else:
                yield from self._shadowbolt()

    def _agony_corruption_immolate_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if not self.env.debuffs.is_dot_active(CurseOfAgonyDot, self):
                yield from self._curse_of_agony()
            elif not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
            elif not self.env.debuffs.is_dot_active(ImmolateDot, self):
                yield from self._immolate()
            else:
                yield from self._shadowbolt()

    def _coa_corruption_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if not self.env.debuffs.is_dot_active(CurseOfAgonyDot, self):
                yield from self._curse_of_agony()
            elif not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
            else:
                yield from self._shadowbolt()

    def _coa_corruption_siphon_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if not self.env.debuffs.is_dot_active(CurseOfAgonyDot, self):
                yield from self._curse_of_agony()
            elif not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
            elif not self.env.debuffs.is_dot_active(SiphonLifeDot, self):
                yield from self._siphon_life()
            else:
                yield from self._shadowbolt()

    def _immo_conflag_soulfire_searing(self, cds: CooldownUsages = CooldownUsages(),
                                           delay=2):
        """
        This rotation prioritizes:
        1. Uses Soul Fire on cooldown
        2. Keeps up Corruption and Immolate DoTs
        3. Uses Conflagrate on cooldown when Immolate is active
        4. Fills with Searing Pain

        Args:
            cds: Cooldown usage configuration
            delay: Initial delay before starting rotation
            curse_type: Type of curse to use ("shadow" or "agony")
        """

        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)

            # Use Soul Fire on cooldown
            if not self.soul_fire_cd.on_cooldown:
                yield from self._soul_fire()
                continue

            # If Immolate isn't up, cast it
            if not self.env.debuffs.is_dot_active(ImmolateDot, self):
                yield from self._immolate()
                continue

            # Use Conflagrate when available and Immolate is active
            if not self.conflagrate_cd.on_cooldown and self.env.debuffs.is_dot_active(ImmolateDot, self):
                yield from self._conflagrate()
                continue

            # Keep DoTs up
            if not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
                continue

            # Default to Searing Pain spam
            yield from self._searing_pain()

    def _coa_corruption_siphon_harvest_drain(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        """
        Affliction rotation that prioritizes:
        1. Keeping Curse of Shadow/Agony up
        2. Keeping Corruption up
        3. Keeping Siphon Life up (if use_siphon_life=True)
        4. Using Dark Harvest as a channel
        5. Using Drain Soul as a filler

        Args:
            cds: Cooldown usage configuration
            delay: Initial delay before starting rotation
            use_siphon_life: Whether to use Siphon Life in the rotation
        """
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)

            if self.opts.use_nightfall_as_affliction and self.nightfall:
                yield from self._shadowbolt()
                continue

            if not self.env.debuffs.is_dot_active(CurseOfAgonyDot, self):
                yield from self._curse_of_agony()
                continue

            # Keep Corruption up
            if not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
                continue

            # Keep Siphon Life up if we're using it
            if not self.env.debuffs.is_dot_active(SiphonLifeDot, self):
                yield from self._siphon_life()
                continue

            # Start Dark Harvest channel if all DoTs are up
            if self.dark_harvest_cd.usable:
                yield from self._dark_harvest_channel()
                continue

            # fill with Drain Soul
            yield from self._drain_soul_channel()

    def _coa_corruption_harvest_drain(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        """
        Affliction rotation that prioritizes:
        1. Keeping Curse of Shadow/Agony up
        2. Keeping Corruption up
        4. Using Dark Harvest as a channel
        5. Using Drain Soul as a filler

        Args:
            cds: Cooldown usage configuration
            delay: Initial delay before starting rotation
            use_siphon_life: Whether to use Siphon Life in the rotation
        """
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)

            if not self.env.debuffs.is_dot_active(CurseOfAgonyDot, self):
                yield from self._curse_of_agony()
                continue

            # Keep Corruption up
            if not self.env.debuffs.is_dot_active(CorruptionDot, self):
                yield from self._corruption()
                continue

            # Start Dark Harvest channel if all DoTs are up
            if self.dark_harvest_cd.usable:
                yield from self._dark_harvest_channel()
                continue

            # fill with Drain Soul
            yield from self._drain_soul_channel()

    # affliction
    @simrotation("(Affli) CoA -> Corruption -> Siphon Life -> Harvest -> Drain Soul")
    def coa_corruption_siphon_harvest_drain(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return (partial(self._set_rotation,
                        name="coa_corruption_siphon_harvest_drain")
                (cds=cds, delay=delay))

    @simrotation("(Affli) CoA -> Corruption -> Harvest -> Drain Soul")
    def coa_corruption_harvest_drain(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return (partial(self._set_rotation,
                        name="coa_corruption_harvest_drain")
                (cds=cds, delay=delay))

    # smruin
    @simrotation("(SMRuin) CoA -> Corruption -> Shadowbolt")
    def coa_corruption_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="coa_corruption_shadowbolt")(cds=cds, delay=delay)

    @simrotation("(SMRuin) CoA -> Corruption -> Siphon Life -> Shadowbolt")
    def coa_corruption_siphon_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="coa_corruption_siphon_shadowbolt")(cds=cds, delay=delay)

    # fire
    @simrotation("(Fire) Immolate -> Conflagrate -> Soul Fire -> Searing Pain")
    def immo_conflag_soulfire_searing(self,
                                      cds: CooldownUsages = CooldownUsages(),
                                      delay=2):
        return (partial(self._set_rotation,
                        name="immo_conflag_soulfire_searing")
                (cds=cds, delay=delay))

    @simrotation("Spam Shadowbolt")
    def spam_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        # set rotation to internal _spam_fireballs and use partial to pass args and kwargs to that function
        return partial(self._set_rotation, name="spam_shadowbolt")(cds=cds, delay=delay)

    @simrotation("Corruption -> Shadowbolt")
    def corruption_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="corruption_shadowbolt")(cds=cds, delay=delay)

    @simrotation("Agony -> Corruption -> Shadowbolt")
    def agony_corruption_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="agony_corruption_shadowbolt")(cds=cds, delay=delay)

    @simrotation("Agony -> Corruption -> Immolate -> Shadowbolt")
    def agony_corruption_immolate_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="agony_corruption_immolate_shadowbolt")(cds=cds, delay=delay)

    @simrotation("CoA -> Corruption -> Immolate -> Shadowbolt")
    def coa_corruption_immolate_shadowbolt(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="coa_corruption_immolate_shadowbolt")(cds=cds, delay=delay)
