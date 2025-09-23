import random
from functools import partial

from sim.character import CooldownUsages
from sim.decorators import simrotation, simclass
from sim.env import Environment
from sim.equipped_items import EquippedItems
from sim.fire_dots import FireballDot, PyroblastDot, Flamestriker4Dot, Flamestriker5Dot, Flamestriker6Dot
from sim.hot_streak import HotStreak
from sim.mage_options import MageOptions
from sim.mage_rotation_cooldowns import *
from sim.mage_talents import MageTalents
from sim.spell import Spell, SPELL_COEFFICIENTS, SPELL_TRIGGERS_ON_HIT, SPELL_HITS_MULTIPLE_TARGETS, \
    SPELL_HAS_TRAVEL_TIME
from sim.spell_school import DamageType
from sim.talent_school import TalentSchool


@simclass(MageTalents, MageOptions)
class Mage(Character):
    def __init__(self,
                 tal: MageTalents,
                 opts: MageOptions = MageOptions(),
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

        self._t2_8set_proc: bool = False
        self._t3_arcane_8set_proc_time: bool = False

        self._flash_freeze_proc: bool = False

        self.hot_streak = None

        if self.tal:
            if self.tal.critical_mass:
                self.damage_type_crit[DamageType.FIRE] += 6

            if self.tal.ice_shards > 0:
                self.damage_type_crit_mult[DamageType.FROST] += self.tal.ice_shards * 0.1

            if self.tal.arcane_potency:
                self.damage_type_crit_mult[DamageType.ARCANE] += self.tal.arcane_potency * 0.25

        self._ice_barrier_expiration = 0

    def get_class(self):
        return self.__class__.__name__

    def reset(self):
        super().reset()

        self._t2_8set_proc = False
        self._flash_freeze_proc = False
        self._t3_arcane_8set_proc_time = False

    def _setup_cds(self):
        self.fire_blast_cd = FireBlastCooldown(self, self.tal.fire_blast_cooldown)
        self.frost_nova_cd = FrostNovaCooldown(self, self.tal.frost_nova_cooldown)
        self.cold_snap_cd = ColdSnapCooldown(self)
        self.cone_of_cold_cd = ConeOfColdCooldown(self)
        self.icicles_cd = IciclesCooldown(self)
        self.arcane_rupture_cd = ArcaneRuptureCooldown(self, self.tal.accelerated_arcana)
        self.arcane_surge_cd = ArcaneSurgeCooldown(self, self.tal.accelerated_arcana)
        self.temporal_convergence_cd = TemporalConvergenceCooldown(self)

    def attach_env(self, env: Environment):
        super().attach_env(env)

        self._setup_cds()

        if self.tal.hot_streak:
            self.hot_streak = HotStreak(env, self)

        if self.opts.start_with_ice_barrier:
            self._ice_barrier_expiration = self.opts.starting_ice_barrier_duration

    def _ice_barrier_active(self):
        return self._ice_barrier_expiration >= self.env.now

    def _arcane_rupture_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)

            if self.arcane_rupture_cd.usable:
                # if pom available, use it on rupture
                if self.opts.use_presence_of_mind_on_cd and self.cds.presence_of_mind.usable:
                    self.cds.presence_of_mind.activate()
                yield from self._arcane_rupture()
            else:
                yield from self._arcane_missiles_channel(interrupt_for_rupture=self.opts.interrupt_arcane_missiles_for_rupture)

    def _arcane_surge_rupture_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)

            if self.arcane_surge_cd.usable and not self.has_trinket_or_cooldown_haste():
                yield from self._arcane_surge()
            elif self.arcane_rupture_cd.usable:
                # if pom available, use it on rupture
                if self.opts.use_presence_of_mind_on_cd and self.cds.presence_of_mind.usable:
                    self.cds.presence_of_mind.activate()
                yield from self._arcane_rupture()
            else:
                yield from self._arcane_missiles_channel(interrupt_for_surge=self.opts.interrupt_arcane_missiles_for_surge,
                                                         interrupt_for_rupture=self.opts.interrupt_arcane_missiles_for_rupture)

    def _arcane_surge_fireblast_rupture_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)

            if self.arcane_surge_cd.usable and not self.has_trinket_or_cooldown_haste():
                yield from self._arcane_surge()
            elif self.arcane_rupture_cd.usable:
                # if pom available, use it on rupture
                if self.opts.use_presence_of_mind_on_cd and self.cds.presence_of_mind.usable:
                    self.cds.presence_of_mind.activate()
                yield from self._arcane_rupture()
            elif self.fire_blast_cd.usable and not self.has_trinket_or_cooldown_haste():
                yield from self._fire_blast()
            else:
                yield from self._arcane_missiles_channel(
                    interrupt_for_surge=self.opts.interrupt_arcane_missiles_for_surge,
                    interrupt_for_rupture=self.opts.interrupt_arcane_missiles_for_rupture)

    def _arcane_rupture_surge_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if self.arcane_rupture_cd.usable:
                # if pom available, use it on rupture
                if self.opts.use_presence_of_mind_on_cd and self.cds.presence_of_mind.usable:
                    self.cds.presence_of_mind.activate()
                yield from self._arcane_rupture()
            elif self.arcane_surge_cd.usable and not self.has_trinket_or_cooldown_haste():
                yield from self._arcane_surge()
            else:
                yield from self._arcane_missiles_channel(
                    interrupt_for_surge=self.opts.interrupt_arcane_missiles_for_surge,
                    interrupt_for_rupture=self.opts.interrupt_arcane_missiles_for_rupture)

    def _arcane_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            yield from self._arcane_missiles_channel()

    def _spam_arcane_explosion(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            yield from self._arcane_explosion()

    def _spam_fireballs(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            yield from self._fireball()

    def _spam_pyroblast(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            yield from self._pyroblast()

    def _spam_flamestrike_r6_r5_r4(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        rank_cycle = 0  # 0=R6, 1=R5, 2=R4
        while True:
            self._use_cds(cds)
            if rank_cycle == 0:
                yield from self._flamestrike_r6()
            elif rank_cycle == 1:
                yield from self._flamestrike_r5()
            else:  # rank_cycle == 2
                yield from self._flamestrike_r4()
            rank_cycle = (rank_cycle + 1) % 3  # Cycle through 0, 1, 2

    def _spam_flamestrike_r6_r5(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        use_r6 = True  # Start with R6
        while True:
            self._use_cds(cds)
            if use_r6:
                yield from self._flamestrike_r6()
            else:
                yield from self._flamestrike_r5()
            use_r6 = not use_r6  # Alternate for next cast

    def _spam_flamestrike_r6(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            yield from self._flamestrike_r6()

    def _spam_frostbolts(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if self.tal.ice_barrier and not self._ice_barrier_active():
                yield from self._ice_barrier()
            else:
                yield from self._frostbolt()

    def _icicle_frostbolts(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if self.tal.ice_barrier and not self._ice_barrier_active():
                yield from self._ice_barrier()
            elif self._flash_freeze_proc:
                self._flash_freeze_proc = False
                yield from self._icicles_channel(channel_time=1.0)
            elif self.opts.use_frostnova_for_icicles and self.frost_nova_cd.usable:
                yield from self._frost_nova()
            elif self.opts.use_frostnova_for_icicles and self.opts.use_cold_snap_for_nova and self.cold_snap_cd.usable:
                self.cold_snap_cd.activate()
                yield from self._frost_nova()
            elif self.opts.use_icicles_without_flash_freeze and self.icicles_cd.usable:
                yield from self._icicles_channel()
            else:
                yield from self._frostbolt()

    def _icicle_coc_frostbolts(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if self.tal.ice_barrier and not self._ice_barrier_active():
                yield from self._ice_barrier()
            elif self._flash_freeze_proc:
                self._flash_freeze_proc = False
                yield from self._icicles_channel(channel_time=1.0)
            elif self.opts.use_frostnova_for_icicles and self.frost_nova_cd.usable:
                yield from self._frost_nova()
            elif self.opts.use_frostnova_for_icicles and self.opts.use_cold_snap_for_nova and self.cold_snap_cd.usable:
                self.cold_snap_cd.activate()
                yield from self._frost_nova()
            elif self.opts.use_icicles_without_flash_freeze and self.icicles_cd.usable:
                yield from self._icicles_channel()
            elif self.cone_of_cold_cd.usable:
                yield from self._cone_of_cold()
            else:
                yield from self._frostbolt()

    def _spam_scorch(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            yield from self._scorch()

    def _spam_scorch_unless_mqg(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if self.cds.mqg.is_active():
                yield from self._fireball()
            else:
                yield from self._scorch()

    def _one_scorch_then_fireballs(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        """1 scorch then 9 fireballs rotation"""
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            yield from self._scorch()
            for _ in range(9):
                self._use_cds(cds)
                yield from self._fireball()

    def _smart_scorch(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        """ Cast scorch if less than 5 imp scorch stacks or if 5 stack ignite
        and extend_ignite_with_scorch else cast fireball"""
        self._use_cds(cds)
        yield from self._random_delay(delay)
        while True:
            self._use_cds(cds)

            if self.env.debuffs.fire_vuln_stacks < 5 or self.env.debuffs.fire_vuln_timer <= 4.5:
                yield from self._scorch()
            else:
                yield from self._fireball()

    def _smart_scorch_and_fireblast(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        """Same as above except fireblast on cd"""
        self._use_cds(cds)
        yield from self._random_delay(delay)
        while True:
            self._use_cds(cds)
            if self.env.debuffs.fire_vuln_stacks < 5 or self.env.debuffs.fire_vuln_timer <= 4.5:
                yield from self._scorch()
            elif self.fire_blast_cd.usable:
                yield from self._fire_blast()
            else:
                yield from self._fireball()

    def _smart_scorch_and_fireblast_and_surge(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        """Same as above except fireblast on cd"""
        self._use_cds(cds)
        yield from self._random_delay(delay)
        while True:
            self._use_cds(cds)
            if self.env.debuffs.fire_vuln_stacks < 5 or self.env.debuffs.fire_vuln_timer <= 4.5:
                yield from self._scorch()
            elif self.fire_blast_cd.usable:
                yield from self._fire_blast()
            elif self.arcane_surge_cd.usable and not self.has_trinket_or_cooldown_haste():
                yield from self._arcane_surge()
            else:
                yield from self._fireball()

    def _one_scorch_one_pyro_then_fb(self, cds: CooldownUsages = CooldownUsages(), delay=1):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        self._use_cds(cds)
        yield from self._scorch()
        self._use_cds(cds)
        yield from self._pyroblast()
        for _ in range(7):
            self._use_cds(cds)
            yield from self._fireball()

        yield from self._one_scorch_then_fireballs(cds, delay=0)

    def _one_scorch_one_frostbolt_then_fb(self, cds: CooldownUsages = CooldownUsages(), delay=1):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        self._use_cds(cds)
        yield from self._scorch()
        self._use_cds(cds)
        yield from self._frostbolt()
        for _ in range(8):
            self._use_cds(cds)
            yield from self._fireball()

        yield from self._one_scorch_then_fireballs(cds, delay=0)

    def _get_cast_time(self, base_cast_time: float, damage_type: DamageType):
        # check for pom
        if base_cast_time > 0 and self.cds.presence_of_mind.is_active():
            self.cds.presence_of_mind.deactivate()
            return self.lag

        return super()._get_cast_time(base_cast_time, damage_type)

    def _get_talent_school(self, spell: Spell):
        if spell in [Spell.CORRUPTION, Spell.CURSE_OF_AGONY, Spell.CURSE_OF_SHADOW]:
            return TalentSchool.Affliction
        elif spell in [Spell.SHADOWBOLT, Spell.IMMOLATE, Spell.SEARING_PAIN, Spell.CONFLAGRATE]:
            return TalentSchool.Destruction
        else:
            raise ValueError(f"Unknown spell {spell}")

    def _get_hit_chance(self, spell: Spell, is_binary=False):
        # elemental precision assumed to be included in hit already
        if self.env.mob_level == 63:
            return min(83 + self.hit, 99)
        elif self.env.mob_level == 62:
            return min(94 + self.hit, 99)
        elif self.env.mob_level == 61:
            return min(95 + self.hit, 99)
        else:
            return min(96 + self.hit, 99)

    def modify_dmg(self, dmg: int, damage_type: DamageType, is_periodic: bool):
        dmg = super().modify_dmg(dmg, damage_type, is_periodic)

        if damage_type == DamageType.FIRE and self.tal.fire_power:
            dmg *= 1.1 if self.tal.fire_power == 5 else 1 + 0.02 * self.tal.fire_power

        if self.tal.piercing_ice and damage_type == DamageType.FROST:
            dmg *= 1.06

        if self.tal.ice_barrier and damage_type == DamageType.FROST and self._ice_barrier_active():
            dmg *= 1.15

        if self.opts.apply_undead_bonus:
            dmg *= 1.02

        return int(dmg)

    def check_for_ignite_extend(self, spell: Spell):
        has_5_stack_scorch = self.env.debuffs.fire_vuln_stacks == 5
        has_5_stack_ignite = self.env.debuffs.ignite and self.env.debuffs.ignite.stacks == 5

        has_ignite_extend_option = self.opts.extend_ignite_with_fire_blast or self.opts.extend_ignite_with_scorch

        return (has_5_stack_scorch and
                has_5_stack_ignite and
                has_ignite_extend_option and
                spell not in (
                    Spell.FIREBLAST,
                    Spell.SCORCH))  # if already casting fireblast or scorch, don't use extend ignite logic

    def extend_ignite(self):
        # check that spell is not already fireblast or scorch
        ignite_time_remaining = self.env.debuffs.ignite.time_remaining
        if ignite_time_remaining <= self.opts.remaining_seconds_for_ignite_extend:
            if self.opts.extend_ignite_with_fire_blast and self.fire_blast_cd.usable:
                yield from self._fire_blast()
                return True

            scorch_cast_time = self._get_cast_time(1.5, DamageType.FIRE) + self.lag
            if self.opts.extend_ignite_with_scorch and ignite_time_remaining > scorch_cast_time:
                yield from self._scorch()
                return True

        return False

    # caller must handle any gcd cooldown
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
               calculate_cast_time: bool = True):

        casting_time = self._get_cast_time(base_cast_time, damage_type) if calculate_cast_time else base_cast_time
        if self._t2_8set_proc and calculate_cast_time:
            casting_time = self.lag
            self._t2_8set_proc = False
            self.print("T2 proc used")

        gcd = custom_gcd if custom_gcd is not None else self.env.GCD
        gcd_wait_time = 0

        # account for gcd
        if on_gcd and casting_time < gcd:
            gcd_wait_time = gcd - casting_time if casting_time > self.lag else gcd

        hit = self._roll_hit(self._get_hit_chance(spell),
                             damage_type) if spell != Spell.ARCANE_SURGE else True  # arcane surge always hits
        crit = False
        dmg = 0
        arcane_instability_hit = False
        arcane_rupture_applied = False
        if hit:
            crit = self._roll_crit(self.crit + crit_modifier, damage_type)
            dmg = self.roll_spell_dmg(min_dmg, max_dmg, SPELL_COEFFICIENTS.get(spell, 0), damage_type)
            dmg = self.modify_dmg(dmg, damage_type, is_periodic=False)

            if (self._t3_arcane_8set_proc_time and
                    (spell != Spell.ARCANE_MISSILE and spell != Spell.ICICLE)):
                if self._t3_arcane_8set_proc_time + 6 > self.env.now:
                    dmg *= 1.1
                self._t3_arcane_8set_proc_time = False

            if self.tal.arcane_instability and damage_type == DamageType.ARCANE:
                hit_chance = {1: 8, 2: 16, 3: 25}.get(self.tal.arcane_instability, 0)

                arcane_instability_hit = self._roll_proc(hit_chance)
                if arcane_instability_hit:
                    dmg *= 1.25

            if self.arcane_rupture_cd.is_active() and spell == Spell.ARCANE_MISSILE:
                dmg *= 1.20
                arcane_rupture_applied = True

            if self.opts.t35_3_set and spell in {Spell.FLAMESTRIKER6, Spell.CONE_OF_COLD, Spell.FROST_NOVA, Spell.BLASTWAVE, Spell.ARCANE_EXPLOSION}:
                if self._roll_proc(10):
                    dmg *= 1.15
                    self.print(f"{spell.value} T3 3-set proc")
        else:
            self.arcane_surge_cd.enable_due_to_resist()
            self.num_resists += 1

        is_binary_spell = spell in {Spell.FROSTBOLT, Spell.FROSTBOLTRK4, Spell.FROSTBOLTRK3, Spell.FROST_NOVA,
                                    Spell.CONE_OF_COLD, Spell.ARCANE_SURGE}

        partial_amount = self.roll_partial(is_dot=False, is_binary=is_binary_spell)
        partial_desc = ""
        if partial_amount < 1:
            dmg = int(dmg * partial_amount)
            partial_desc = f"({int(partial_amount * 100)}% partial)"
            self.arcane_surge_cd.enable_due_to_resist()

            if self.opts.t3_8_set:
                self._t3_arcane_8set_proc_time = self.env.now

        if casting_time:
            yield self.env.timeout(casting_time)

        description = ""
        if self.env.print:
            description = f"({round(casting_time, 2)} cast)"
            if gcd_wait_time:
                description += f" ({round(gcd_wait_time, 2)} gcd)"
            if arcane_instability_hit:
                description += " (AI)"
            if arcane_rupture_applied:
                description += " (AR)"
        if not hit:
            self.print(f"{spell.value} {description} RESIST")
        elif not crit:
            self.print(f"{spell.value} {description} {partial_desc} {dmg}")
        else:
            mult = self._get_crit_multiplier(talent_school, damage_type)
            dmg = int(dmg * mult)
            self.print(f"{spell.value} {description} {partial_desc} **{dmg}**")

        if hit and SPELL_TRIGGERS_ON_HIT.get(spell, False):
            self.env.process(self._check_for_procs(
                spell=spell,
                damage_type=damage_type,
                delay=spell in SPELL_HAS_TRAVEL_TIME))

        if (hit and
                self.opts.fullt2 and
                spell in (Spell.FIREBALL,
                          Spell.FROSTBOLT,
                          Spell.FROSTBOLTRK4,
                          Spell.FROSTBOLTRK3,
                          Spell.ARCANE_MISSILE)):
            if random.randint(1, 100) <= 10:
                self._t2_8set_proc = True
                self.print("T2 proc")

        if hit and self.cds.zhc.is_active():
            self.cds.zhc.use_charge()

        self.env.meter.register_spell_dmg(
            char_name=self.name,
            spell_name=spell.value,
            dmg=dmg,
            cast_time=round(casting_time + gcd_wait_time, 2),
            aoe=spell in SPELL_HITS_MULTIPLE_TARGETS)

        return hit, crit, dmg, gcd_wait_time, partial_amount

    def _arcane_spell(self,
                      spell: Spell,
                      min_dmg: int,
                      max_dmg: int,
                      base_cast_time: float,
                      crit_modifier: float,
                      custom_gcd: float = None,
                      on_gcd: bool = True,
                      calculate_cast_time: bool = True):

        # check if we need to extend ignite instead of casting intended spell
        if self.check_for_ignite_extend(spell):
            cast_spell = yield from self.extend_ignite()
            if cast_spell:
                return

        crit_modifier += self.tal.arcane_impact * 2

        hit, crit, dmg, effective_gcd, partial_amount = yield from self._spell(spell=spell,
                                                                            damage_type=DamageType.ARCANE,
                                                                            talent_school=TalentSchool.Arcane,
                                                                            min_dmg=min_dmg,
                                                                            max_dmg=max_dmg,
                                                                            base_cast_time=base_cast_time,
                                                                            crit_modifier=crit_modifier,
                                                                            custom_gcd=custom_gcd,
                                                                            on_gcd=on_gcd,
                                                                            calculate_cast_time=calculate_cast_time)

        if self.tal.resonance_cascade and hit:
            num_duplicates = 0

            resonance_chance = 4 * self.tal.resonance_cascade
            if self.opts.t35_arcane_3_set:
                resonance_chance += 5

            while num_duplicates < 5:
                if self._roll_proc(resonance_chance):
                    num_duplicates += 1
                    dmg /= 2
                    self.print(f"{spell.value} duplicated for {dmg}")
                    self.env.meter.register_spell_dmg(
                        char_name=self.name,
                        spell_name=spell.value,
                        dmg=dmg,
                        cast_time=0,
                        aoe=spell in SPELL_HITS_MULTIPLE_TARGETS,
                        increment_cast=False)
                else:
                    break

        if spell == Spell.ARCANE_MISSILE and self.tal.temporal_convergence:
            if self.temporal_convergence_cd.usable:
                temporal_convergence_hit = self._roll_proc(5 * self.tal.temporal_convergence)
                if temporal_convergence_hit:
                    self.temporal_convergence_cd.activate()
                    # reset cd on rupture
                    self.arcane_rupture_cd.reset_cooldown()

        if spell == Spell.ARCANE_SURGE:
            self.arcane_surge_cd.activate()
        elif spell == Spell.ARCANE_RUPTURE:
            self.arcane_rupture_cd.activate()

        # handle gcd
        if effective_gcd:
            yield self.env.timeout(effective_gcd)

    def _arcane_missile(self, casting_time: float = 1):
        dmg = 230

        yield from self._arcane_spell(spell=Spell.ARCANE_MISSILE,
                                      min_dmg=dmg,
                                      max_dmg=dmg,
                                      base_cast_time=casting_time,
                                      crit_modifier=0,
                                      on_gcd=False,
                                      calculate_cast_time=False)

    def _arcane_missiles_channel(self, channel_time: float = 5,
                                 interrupt_for_surge: bool = False,
                                 interrupt_for_rupture: bool = False):
        num_missiles = 5

        if self.opts.extra_second_arcane_missile:
            num_missiles += 1
            channel_time += 1

        if self.tal.accelerated_arcana:
            channel_time = channel_time * .95
            channel_time /= self.get_haste_factor_for_damage_type(DamageType.ARCANE)

        time_between_missiles = channel_time / num_missiles

        had_sulfuras_proc = self.equipped_items.true_band_of_sulfuras and self.item_proc_handler.true_band_of_sulfuras_buff.is_active()

        for i in range(num_missiles):
            # check for interrupts
            # don't surge during haste cds as it has gcd that is not reduced by haste
            # don't interrupt rupture missiles either
            if interrupt_for_surge and \
                    self.arcane_surge_cd.usable and \
                    not self.has_trinket_or_cooldown_haste() \
                    and not self.arcane_rupture_cd.is_active():
                # if rupture not active, use surge immediately
                if not self.arcane_rupture_cd.is_active():
                    yield self.env.timeout(self.opts.delay_when_interrupting_missiles)
                    yield from self._arcane_surge()
                    return
                # otherwise wait until it is about to expire
                if self.arcane_surge_cd.time_left() < time_between_missiles:
                    yield self.env.timeout(self.opts.delay_when_interrupting_missiles)
                    yield from self._arcane_surge()
                    return
            if interrupt_for_rupture and self.arcane_rupture_cd.usable and not self.arcane_rupture_cd.is_active():
                yield self.env.timeout(self.opts.delay_when_interrupting_missiles)
                yield from self._arcane_rupture()
                return

            if i == 0:
                yield from self._arcane_missile(casting_time=time_between_missiles + self.lag)  # initial delay
            else:
                yield from self._arcane_missile(casting_time=time_between_missiles)
                if not had_sulfuras_proc and \
                        self.opts.interrupt_arcane_missiles_for_sulfuras_proc and \
                        self.equipped_items.true_band_of_sulfuras and \
                        self.item_proc_handler.true_band_of_sulfuras_buff.is_active():
                    # interrupt channel to restart it with haste
                    self.print(f"Interrupting arcane missiles for haste proc")
                    yield self.env.timeout(self.opts.delay_when_interrupting_missiles)
                    break

        if channel_time < self.env.GCD:
            self.print(f"Post arcane missiles {round(self.env.GCD - channel_time, 2)} gcd")

    def _arcane_surge(self):
        min_dmg = 517
        max_dmg = 612
        casting_time = 0
        crit_modifier = 0

        yield from self._arcane_spell(spell=Spell.ARCANE_SURGE,
                                      min_dmg=min_dmg,
                                      max_dmg=max_dmg,
                                      base_cast_time=casting_time,
                                      crit_modifier=crit_modifier)

    def _arcane_rupture(self):
        min_dmg = 703
        max_dmg = 766
        casting_time = 2.5
        crit_modifier = 0

        if self.tal.accelerated_arcana:
            casting_time *= 0.95

        yield from self._arcane_spell(spell=Spell.ARCANE_RUPTURE,
                                      min_dmg=min_dmg,
                                      max_dmg=max_dmg,
                                      base_cast_time=casting_time,
                                      crit_modifier=crit_modifier)

    def _arcane_explosion(self):
        min_dmg = 243
        max_dmg = 264
        casting_time = 0
        crit_modifier = 0

        yield from self._arcane_spell(spell=Spell.ARCANE_EXPLOSION,
                                      min_dmg=min_dmg,
                                      max_dmg=max_dmg,
                                      base_cast_time=casting_time,
                                      crit_modifier=crit_modifier)

    def _fire_spell(self,
                    spell: Spell,
                    min_dmg: int,
                    max_dmg: int,
                    base_cast_time: float,
                    crit_modifier: float,
                    custom_gcd: float | None = None,
                    on_gcd: bool = True):
        # check if we need to extend ignite instead of casting intended spell
        if self.check_for_ignite_extend(spell):
            cast_spell = yield from self.extend_ignite()
            if cast_spell:
                return

        # check for ignite conditions
        has_5_stack_ignite = self.env.debuffs.ignite and self.env.debuffs.ignite.stacks == 5
        has_bad_ignite = has_5_stack_ignite and self.env.debuffs.ignite.is_suboptimal()

        # check for scorch ignite drop
        if self.opts.drop_suboptimal_ignites and has_bad_ignite:
            yield from self._frostbolt()  # have to use frostbolt with 6s ignite window
            return

        # check for hot streak pyroblast
        if self.hot_streak and self.hot_streak.get_stacks() == 5 and self.opts.pyro_on_max_hot_streak:
            self.print("Hot Streak Pyroblast")
            self.hot_streak.use_stacks()
            yield from self._pyroblast(casting_time=1)
            return

        hit, crit, dmg, effective_gcd, partial_amount = yield from self._spell(spell=spell,
                                                                            damage_type=DamageType.FIRE,
                                                                            talent_school=TalentSchool.Fire,
                                                                            min_dmg=min_dmg,
                                                                            max_dmg=max_dmg,
                                                                            base_cast_time=base_cast_time,
                                                                            crit_modifier=crit_modifier,
                                                                            custom_gcd=custom_gcd,
                                                                            on_gcd=on_gcd)

        if hit:
            self.cds.combustion.cast_fire_spell()  # only happens on hit

            if spell == Spell.FIREBALL:
                self.env.debuffs.add_dot(FireballDot, self, 0)
            elif spell == Spell.PYROBLAST:
                self.env.debuffs.add_dot(PyroblastDot, self, 0)
            elif spell == Spell.FLAMESTRIKER4:
                self.env.debuffs.add_dot(Flamestriker4Dot, self, 0)
            elif spell == Spell.FLAMESTRIKER5:
                self.env.debuffs.add_dot(Flamestriker5Dot, self, 0)
            elif spell == Spell.FLAMESTRIKER6:
                self.env.debuffs.add_dot(Flamestriker6Dot, self, 0)
            elif (spell == Spell.SCORCH or spell == Spell.FIREBLAST) and self.tal.fire_vuln:
                fire_vuln_chance = 100
                if self.tal.fire_vuln < 3:
                    fire_vuln_chance = 33 * self.tal.fire_vuln
                # roll for whether debuff hits
                fire_vuln_hit = self._roll_hit(self._get_hit_chance(spell), DamageType.FIRE)
                if fire_vuln_hit:
                    if fire_vuln_chance == 100 or self._roll_proc(fire_vuln_chance):
                        self.env.debuffs.add_fire_vuln()

        if crit:
            if self.tal.ignite:
                self.env.debuffs.ignite.refresh(self, dmg, spell, partial_amount < 1, self.tal.ignite)

            # check for hot streak
            if self.hot_streak and (spell == Spell.FIREBALL or spell == Spell.FIREBLAST):
                hot_streak_hit = True
                if self.tal.hot_streak == 1:
                    hot_streak_hit = self._roll_proc(50)

                if hot_streak_hit:
                    self.hot_streak.add_stack()

            self.cds.combustion.use_charge()  # only used on crit

        if spell == Spell.FIREBLAST:
            self.fire_blast_cd.activate()

        # handle gcd
        if effective_gcd:
            yield self.env.timeout(effective_gcd)

    def _scorch(self):
        min_dmg = 237
        max_dmg = 280
        casting_time = 1.5
        crit_modifier = 0

        crit_modifier += self.tal.incinerate_crit  # incinerate added crit (2 or 4%)

        yield from self._fire_spell(spell=Spell.SCORCH,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    base_cast_time=casting_time,
                                    crit_modifier=crit_modifier)

    def _fireball(self):
        min_dmg = 596
        max_dmg = 760
        casting_time = 3.5 - self.tal.improved_fireball * .1
        crit_modifier = 0

        if self.opts.pyro_on_t2_proc and self._t2_8set_proc:
            yield from self._pyroblast()
        else:
            yield from self._fire_spell(spell=Spell.FIREBALL,
                                        min_dmg=min_dmg,
                                        max_dmg=max_dmg,
                                        base_cast_time=casting_time,
                                        crit_modifier=crit_modifier)

    def _fire_blast(self):
        min_dmg = 431
        max_dmg = 510
        casting_time = 0
        crit_modifier = 0

        crit_modifier += self.tal.incinerate_crit  # incinerate added crit (2 or 4%)

        yield from self._fire_spell(spell=Spell.FIREBLAST,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    base_cast_time=casting_time,
                                    crit_modifier=crit_modifier,
                                    custom_gcd=self.tal.fire_blast_gcd)

    def _pyroblast(self, casting_time=6.0):
        min_dmg = 716
        max_dmg = 890
        crit_modifier = 0

        yield from self._fire_spell(spell=Spell.PYROBLAST,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    base_cast_time=casting_time,
                                    custom_gcd=1.0,
                                    crit_modifier=crit_modifier)

    def _flamestrike_r4(self):
        min_dmg = 220
        max_dmg = 273
        casting_time = 2.5
        crit_modifier = 0

        crit_modifier += self.tal.improved_flamestrike * 5  # 5% crit per rank

        if self.opts.zg_5_set:
            casting_time -= 0.5  # ZG 5-set bonus

        yield from self._fire_spell(spell=Spell.FLAMESTRIKER4,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    base_cast_time=casting_time,
                                    crit_modifier=crit_modifier)

    def _flamestrike_r5(self):
        min_dmg = 291
        max_dmg = 360
        casting_time = 2.5
        crit_modifier = 0

        crit_modifier += self.tal.improved_flamestrike * 5  # 5% crit per rank

        if self.opts.zg_5_set:
            casting_time -= 0.5  # ZG 5-set bonus

        yield from self._fire_spell(spell=Spell.FLAMESTRIKER5,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    base_cast_time=casting_time,
                                    crit_modifier=crit_modifier)

    def _flamestrike_r6(self):
        min_dmg = 375
        max_dmg = 460
        casting_time = 2.5
        crit_modifier = 0

        crit_modifier += self.tal.improved_flamestrike * 5  # 5% crit per rank

        if self.opts.zg_5_set:
            casting_time -= 0.5  # ZG 5-set bonus

        yield from self._fire_spell(spell=Spell.FLAMESTRIKER6,
                                    min_dmg=min_dmg,
                                    max_dmg=max_dmg,
                                    base_cast_time=casting_time,
                                    crit_modifier=crit_modifier)

    def _frost_spell(self,
                     spell: Spell,
                     min_dmg: int,
                     max_dmg: int,
                     base_cast_time: float,
                     crit_modifier: float,
                     custom_gcd: float | None = None,
                     on_gcd: bool = True,
                     calculate_cast_time: bool = True):
        # check if we need to extend ignite instead of casting intended spell
        if self.check_for_ignite_extend(spell):
            cast_spell = yield from self.extend_ignite()
            if cast_spell:
                return

        crit_modifier += self.env.debuffs.wc_stacks * 2  # winters chill added crit (2% per stack)

        hit, crit, dmg, effective_gcd, partial_amount = yield from self._spell(spell=spell,
                                                                            damage_type=DamageType.FROST,
                                                                            talent_school=TalentSchool.Frost,
                                                                            min_dmg=min_dmg,
                                                                            max_dmg=max_dmg,
                                                                            base_cast_time=base_cast_time,
                                                                            crit_modifier=crit_modifier,
                                                                            custom_gcd=custom_gcd,
                                                                            on_gcd=on_gcd,
                                                                            calculate_cast_time=calculate_cast_time)

        if hit:
            if self.tal.winters_chill and spell != Spell.FROST_NOVA:
                # roll for whether debuff hits
                winters_chill_hit = self._roll_hit(self._get_hit_chance(spell), DamageType.FROST)
                if winters_chill_hit:
                    winters_chill_proc = self.tal.winters_chill * 20
                    if winters_chill_proc == 100 or self._roll_proc(winters_chill_proc):
                        self.env.debuffs.add_winters_chill_stack()

            if self.tal.flash_freeze:
                flash_freeze_hit = False
                if (spell == Spell.FROSTBOLT or
                        spell == Spell.FROSTBOLTRK4 or
                        spell == Spell.FROSTBOLTRK3 or
                        spell == Spell.CONE_OF_COLD):
                    flash_freeze_hit = self._roll_hit(5 * self.tal.frostbite, DamageType.FROST)
                    if flash_freeze_hit and self.tal.flash_freeze < 2:
                        flash_freeze_hit = self._roll_proc(50 * self.tal.flash_freeze)

                if flash_freeze_hit:
                    self._flash_freeze_proc = True
                    self.print("Flash Freeze proc")

        # nova flash freeze doesn't require dmg hitting
        if self.tal.flash_freeze and spell == Spell.FROST_NOVA:
            flash_freeze_hit = True
            if flash_freeze_hit and self.tal.flash_freeze < 2:
                flash_freeze_hit = self._roll_proc(50 * self.tal.flash_freeze)

            if flash_freeze_hit:
                self._flash_freeze_proc = True
                self.print("Flash Freeze proc")

        if spell == Spell.FROST_NOVA:
            self.frost_nova_cd.activate()
        elif spell == Spell.CONE_OF_COLD:
            self.cone_of_cold_cd.activate()

        # handle gcd
        if effective_gcd:
            yield self.env.timeout(effective_gcd)

    def _frostbolt(self):
        min_dmg = 515
        max_dmg = 556
        casting_time = 2.5
        crit_modifier = 0
        spell = Spell.FROSTBOLT

        # check for downrank option
        if self.opts.frostbolt_rank == 4:
            min_dmg = 74
            max_dmg = 83
            casting_time = 2.1
            spell = Spell.FROSTBOLTRK4
        elif self.opts.frostbolt_rank == 3:
            min_dmg = 51
            max_dmg = 58
            casting_time = 1.7
            spell = Spell.FROSTBOLTRK3

        yield from self._frost_spell(spell=spell,
                                     min_dmg=min_dmg,
                                     max_dmg=max_dmg,
                                     base_cast_time=casting_time,
                                     crit_modifier=crit_modifier)

    def _cone_of_cold(self):
        min_dmg = 335
        max_dmg = 366
        casting_time = 0
        crit_modifier = 0

        mult = 1
        if self.tal.improved_cone_of_cold == 1:
            mult = 1.15
        elif self.tal.improved_cone_of_cold == 2:
            mult = 1.25
        else:
            mult = 1.35

        min_dmg = int(min_dmg * mult)
        max_dmg = int(max_dmg * mult)

        yield from self._frost_spell(spell=Spell.CONE_OF_COLD,
                                     min_dmg=min_dmg,
                                     max_dmg=max_dmg,
                                     base_cast_time=casting_time,
                                     crit_modifier=crit_modifier)

    def _frost_nova(self):
        # use rank 2 to get full spell coefficient
        # min_dmg = 33
        # max_dmg = 38
        min_dmg = 0
        max_dmg = 0  # assume target is immune and takes no dmg
        casting_time = 0
        crit_modifier = 0

        yield from self._frost_spell(spell=Spell.FROST_NOVA,
                                     min_dmg=min_dmg,
                                     max_dmg=max_dmg,
                                     base_cast_time=casting_time,
                                     crit_modifier=crit_modifier)

    def _ice_barrier(self):
        self._ice_barrier_expiration = self.env.now + 60

        if self.env.print:
            description = f"({round(self.lag, 2)} cast)"
            description += f" ({self.env.GCD} gcd)"
            self.print(f"Ice Barrier {description}")
        yield self.env.timeout(self.env.GCD)

    def _icicle(self, casting_time: float = 1):
        min_dmg = 272
        max_dmg = 272

        yield from self._frost_spell(spell=Spell.ICICLE,
                                     min_dmg=min_dmg,
                                     max_dmg=max_dmg,
                                     base_cast_time=casting_time,
                                     crit_modifier=0,
                                     on_gcd=False,
                                     calculate_cast_time=False)

    def _icicles_channel(self, channel_time: float = 5):
        self.icicles_cd.deactivate()

        num_icicles = 5
        time_between_icicles = channel_time / num_icicles

        for i in range(num_icicles):
            if i == 0:
                yield from self._icicle(casting_time=time_between_icicles + self.lag)  # initial delay
            else:
                yield from self._icicle(casting_time=time_between_icicles)

    @simrotation("(Arcane) Arcane Surge -> Arcane Rupture -> Arcane Missiles")
    def arcane_surge_rupture_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="arcane_surge_rupture_missiles")(cds=cds, delay=delay)

    @simrotation("(Fire) Smart Scorch -> Fireblast -> Fireball")
    def smart_scorch_and_fireblast(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="smart_scorch_and_fireblast")(cds=cds, delay=delay)

    @simrotation("(Frost) Icicle -> Frostbolt (Spam)")
    def icicle_frostbolts(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="icicle_frostbolts")(cds=cds, delay=delay)

    @simrotation("(Frost) Icicle -> Cone of Cold -> Frostbolt (Spam)")
    def icicle_coc_frostbolts(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="icicle_coc_frostbolts")(cds=cds, delay=delay)

    @simrotation("(Arcane) Arcane Rupture -> Arcane Missiles")
    def arcane_rupture_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="arcane_rupture_missiles")(cds=cds, delay=delay)

    @simrotation("(Arcane) Arcane Surge -> Fireblast -> Arcane Rupture -> Arcane Missiles")
    def arcane_surge_fireblast_rupture_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="arcane_surge_fireblast_rupture_missiles")(cds=cds, delay=delay)

    @simrotation("(Arcane) Arcane Rupture -> Arcane Surge -> Arcane Missiles")
    def arcane_rupture_surge_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="arcane_rupture_surge_missiles")(cds=cds, delay=delay)

    @simrotation("(Arcane) Arcane Missiles")
    def arcane_missiles(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="arcane_missiles")(cds=cds, delay=delay)

    @simrotation("(Arcane) Arcane Explosion (Spam)")
    def spam_arcane_explosion(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_arcane_explosion")(cds=cds, delay=delay)

    @simrotation("(Fire) Fireball (Spam)")
    def spam_fireballs(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        # set rotation to internal _spam_fireballs and use partial to pass args and kwargs to that function
        return partial(self._set_rotation, name="spam_fireballs")(cds=cds, delay=delay)

    @simrotation("(Fire) Pyroblast (Spam)")
    def spam_pyroblast(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_pyroblast")(cds=cds, delay=delay)

    @simrotation("(Fire) Flamestrike R6/R5/R4 (Alternating)")
    def spam_flamestrike_r6_r5_r4(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_flamestrike_r6_r5_r4")(cds=cds, delay=delay)

    @simrotation("(Fire) Flamestrike R6/R5 (Alternating)")
    def spam_flamestrike_r6_r5(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_flamestrike_r6_r5")(cds=cds, delay=delay)

    @simrotation("(Fire) Flamestrike R6 (Spam)")
    def spam_flamestrike_r6(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_flamestrike_r6")(cds=cds, delay=delay)

    @simrotation("(Fire) Scorch (Spam)")
    def spam_scorch(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_scorch")(cds=cds, delay=delay)

    @simrotation("(Fire) Scorch (Spam, unless MQG)")
    def spam_scorch_unless_mqg(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_scorch_unless_mqg")(cds=cds, delay=delay)

    @simrotation("(Fire) Smart Scorch")
    def smart_scorch(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="smart_scorch")(cds=cds, delay=delay)

    @simrotation("(Fire) Smart Scorch -> Fireblast -> Arcane Surge -> Fireball")
    def smart_scorch_and_fireblast_and_surge(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="smart_scorch_and_fireblast_and_surge")(cds=cds, delay=delay)

    @simrotation("(Frost) Frostbolt (Spam)")
    def spam_frostbolts(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_frostbolts")(cds=cds, delay=delay)
