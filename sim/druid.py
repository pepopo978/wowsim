import random
from functools import partial

from sim.arcane_dots import MoonfireDot
from sim.character import CooldownUsages
from sim.decorators import simrotation, simclass
from sim.druid_options import DruidOptions
from sim.druid_rotation_cooldowns import ArcaneEclipseCooldown, NatureEclipseCooldown
from sim.druid_talents import DruidTalents
from sim.env import Environment
from sim.equipped_items import EquippedItems
from sim.mage_rotation_cooldowns import *
from sim.nature_dots import InsectSwarmDot
from sim.spell import Spell, SPELL_COEFFICIENTS, SPELL_TRIGGERS_ON_HIT, SPELL_HITS_MULTIPLE_TARGETS, \
    SPELL_HAS_TRAVEL_TIME
from sim.spell_school import DamageType
from sim.talent_school import TalentSchool


@simclass(DruidTalents, DruidOptions)
class Druid(Character):
    def __init__(self,
                 tal: DruidTalents,
                 opts: DruidOptions = DruidOptions(),
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

        self.nature_eclipse_rotation = None
        self.arcane_eclipse_rotation = None

    def get_class(self):
        return self.__class__.__name__

    def reset(self):
        super().reset()

    def _setup_cds(self):
        self.arcane_eclipse = ArcaneEclipseCooldown(self)
        self.nature_eclipse = NatureEclipseCooldown(self)

        self.natures_grace_active = False
        self.balance_of_all_things_stacks = 0

    def attach_env(self, env: Environment):
        super().attach_env(env)

        self._setup_cds()

    def _get_cast_time(self, base_cast_time: float, damage_type: DamageType):
        # check for nature's grace
        if base_cast_time > 0 and self.natures_grace_active:
            base_cast_time -= 0.5
            self.natures_grace_active = False

        return super()._get_cast_time(base_cast_time, damage_type)

    def _get_talent_school(self, spell: Spell):
        if spell in [Spell.CORRUPTION, Spell.CURSE_OF_AGONY, Spell.CURSE_OF_SHADOW]:
            return TalentSchool.Affliction
        elif spell in [Spell.SHADOWBOLT, Spell.IMMOLATE, Spell.SEARING_PAIN, Spell.CONFLAGRATE]:
            return TalentSchool.Destruction
        else:
            raise ValueError(f"Unknown spell {spell}")

    def _get_hit_chance(self, spell: Spell, is_binary=False):
        if self.env.mob_level == 63:
            return min(83 + self.hit, 99)
        elif self.env.mob_level == 62:
            return min(94 + self.hit, 99)
        elif self.env.mob_level == 61:
            return min(95 + self.hit, 99)
        else:
            return min(96 + self.hit, 99)

    def _get_crit_multiplier(self, talent_school: TalentSchool, damage_type: DamageType):
        mult = super()._get_crit_multiplier(talent_school, damage_type)
        if self.tal.vengeance:
            mult += 0.1 * self.tal.vengeance
        return mult

    def _get_crit_chance(self, damage_type: DamageType):
        return self.crit + self._crit_bonus + self.damage_type_crit[damage_type]

    def modify_dmg(self, dmg: int, damage_type: DamageType, is_periodic: bool):
        dmg = super().modify_dmg(dmg, damage_type, is_periodic)

        if self.nature_eclipse.is_active() and damage_type == DamageType.NATURE:
            dmg *= (1.1 + 0.6 * self._get_crit_chance(damage_type) / 100)
        elif self.arcane_eclipse.is_active() and damage_type == DamageType.ARCANE:
            dmg *= (1.1 + 0.6 * self._get_crit_chance(damage_type) / 100)

        if self.tal.moonfury == 1:
            dmg *= 1.03
        elif self.tal.moonfury == 2:
            dmg *= 1.06
        elif self.tal.moonfury == 3:
            dmg *= 1.1

        return int(dmg)

    # caller must handle any gcd cooldown
    def _spell(self,
               spell: Spell,
               damage_type: DamageType,
               talent_school: TalentSchool,
               min_dmg: int,
               max_dmg: int,
               base_cast_time: float,
               crit_modifier: float,
               cooldown: float,
               on_gcd: bool,
               calculate_cast_time: bool = True):
        had_natures_grace = self.natures_grace_active

        casting_time = self._get_cast_time(base_cast_time, damage_type) if calculate_cast_time else base_cast_time

        # account for gcd
        gcd = self.env.GCD
        if spell == Spell.WRATH:
            gcd -= 0.1 * self.tal.imp_wrath
        if on_gcd and casting_time < gcd and cooldown == 0:
            cooldown = gcd - casting_time if casting_time > self.lag else gcd

        hit = self._roll_hit(self._get_hit_chance(spell), damage_type)
        crit = False
        dmg = 0
        if hit:
            crit = self._roll_crit(self.crit + crit_modifier, damage_type)
            dmg = self.roll_spell_dmg(min_dmg, max_dmg, SPELL_COEFFICIENTS.get(spell, 0), damage_type)
            dmg = self.modify_dmg(dmg, damage_type, is_periodic=False)
        else:
            self.num_resists += 1

        is_binary_spell = spell in {}

        partial_amount = self.roll_partial(is_dot=False, is_binary=is_binary_spell)
        partial_desc = ""
        if partial_amount < 1:
            dmg = int(dmg * partial_amount)
            partial_desc = f"({int(partial_amount * 100)}% partial)"

        if casting_time:
            yield self.env.timeout(casting_time)

        description = ""
        if self.env.print:
            description = f"({round(casting_time, 2)} cast)"
            if cooldown:
                description += f" ({round(cooldown, 2)} gcd)"

            if had_natures_grace:
                description += " (NG)"
        if not hit:
            self.print(f"{spell.value} {description} RESIST")
        elif not crit:
            self.print(f"{spell.value} {description} {partial_desc} {dmg}")
        else:
            mult = self._get_crit_multiplier(talent_school, damage_type)
            dmg = int(dmg * mult)

            if self.tal.natures_grace:
                self.natures_grace_active = True

            self.print(f"{spell.value} {description} {partial_desc} **{dmg}**")

        if hit:
            if spell == Spell.STARFIRE and not self.arcane_eclipse.is_active():
                # 50% chance to enter arcane eclipse on starfire hit
                if self._roll_proc(50):
                    self.nature_eclipse.activate()
            elif spell == Spell.WRATH and not self.nature_eclipse.is_active():
                # 30% chance to enter nature eclipse on wrath hit
                if self._roll_proc(30):
                    self.arcane_eclipse.activate()

        if hit and self.cds.zhc.is_active():
            self.cds.zhc.use_charge()

        if hit and spell == Spell.MOONFIRE:
            self.env.debuffs.add_dot(MoonfireDot, self, 0)

        if hit and SPELL_TRIGGERS_ON_HIT.get(spell, False):
            self.env.process(self._check_for_procs(
                spell=spell,
                damage_type=damage_type,
                delay=spell in SPELL_HAS_TRAVEL_TIME))

            self.env.meter.register_spell_dmg(
                char_name=self.name,
                spell_name=spell.value,
                dmg=dmg,
                cast_time=round(casting_time + cooldown, 2),
                aoe=spell in SPELL_HITS_MULTIPLE_TARGETS)

        return hit, crit, dmg, cooldown, partial_amount

    def _arcane_spell(self,
                      spell: Spell,
                      min_dmg: int,
                      max_dmg: int,
                      base_cast_time: float,
                      crit_modifier: float,
                      cooldown: float = 0.0,
                      on_gcd: bool = True,
                      calculate_cast_time: bool = True):

        hit, crit, dmg, cooldown, partial_amount = yield from self._spell(spell=spell,
                                                                          damage_type=DamageType.ARCANE,
                                                                          talent_school=TalentSchool.Balance,
                                                                          min_dmg=min_dmg,
                                                                          max_dmg=max_dmg,
                                                                          base_cast_time=base_cast_time,
                                                                          crit_modifier=crit_modifier,
                                                                          cooldown=cooldown,
                                                                          on_gcd=on_gcd,
                                                                          calculate_cast_time=calculate_cast_time)

        # handle gcd
        if cooldown:
            yield self.env.timeout(cooldown)

    def _starfire(self):
        # use rank 2 to get full spell coefficient
        min_dmg = 496
        max_dmg = 585
        casting_time = 3.5
        crit_modifier = 0

        if self.tal.imp_starfire == 1:
            casting_time -= 0.17
        elif self.tal.imp_starfire == 2:
            casting_time -= 0.34
        elif self.tal.imp_starfire == 3:
            casting_time -= 0.5

        if self.balance_of_all_things_stacks > 0:
            casting_time -= 1 if self.opts.set_bonus_3_5_boat else .5
            if self.opts.ebb_and_flow_idol:
                casting_time -= 0.2

            self.balance_of_all_things_stacks -= 1

        yield from self._nature_spell(spell=Spell.STARFIRE,
                                      min_dmg=min_dmg,
                                      max_dmg=max_dmg,
                                      base_cast_time=casting_time,
                                      crit_modifier=crit_modifier)

    def _nature_spell(self,
                      spell: Spell,
                      min_dmg: int,
                      max_dmg: int,
                      base_cast_time: float,
                      crit_modifier: float,
                      cooldown: float = 0.0,
                      on_gcd: bool = True,
                      calculate_cast_time: bool = True):

        hit, crit, dmg, cooldown, partial_amount = yield from self._spell(spell=spell,
                                                                          damage_type=DamageType.NATURE,
                                                                          talent_school=TalentSchool.Balance,
                                                                          min_dmg=min_dmg,
                                                                          max_dmg=max_dmg,
                                                                          base_cast_time=base_cast_time,
                                                                          crit_modifier=crit_modifier,
                                                                          cooldown=cooldown,
                                                                          on_gcd=on_gcd,
                                                                          calculate_cast_time=calculate_cast_time)

        # handle gcd
        if cooldown:
            yield self.env.timeout(cooldown)

    def _wrath(self):
        # use rank 2 to get full spell coefficient
        min_dmg = 278
        max_dmg = 313
        casting_time = 2.0 - 0.1 * self.tal.imp_wrath
        crit_modifier = 0

        yield from self._nature_spell(spell=Spell.WRATH,
                                      min_dmg=min_dmg,
                                      max_dmg=max_dmg,
                                      base_cast_time=casting_time,
                                      crit_modifier=crit_modifier)

    def _moonfire(self):
        # use rank 2 to get full spell coefficient
        min_dmg = 189
        max_dmg = 222
        casting_time = 0
        crit_modifier = 0

        if self.tal.imp_moonfire > 0:
            min_dmg *= 1 + 0.05 * self.tal.imp_moonfire
            min_dmg = int(min_dmg)
            max_dmg *= 1 + 0.05 * self.tal.imp_moonfire
            max_dmg = int(max_dmg)
            crit_modifier = 5 * self.tal.imp_moonfire

        yield from self._nature_spell(spell=Spell.MOONFIRE,
                                      min_dmg=min_dmg,
                                      max_dmg=max_dmg,
                                      base_cast_time=casting_time,
                                      crit_modifier=crit_modifier)

    def _nature_dot(self,
                    spell: Spell,
                    base_cast_time: float,
                    cooldown: float = 0.0):

        casting_time = self._get_cast_time(base_cast_time, DamageType.NATURE)

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
        else:
            if hit and SPELL_TRIGGERS_ON_HIT.get(spell, False):
                self.env.process(self._check_for_procs(
                    spell=spell,
                    damage_type=DamageType.SHADOW,
                    delay=spell in SPELL_HAS_TRAVEL_TIME))

            self.print(f"{spell.value} {description}")
            if spell == Spell.INSECT_SWARM:
                self.env.debuffs.add_dot(InsectSwarmDot, self, round(casting_time + cooldown, 2))

        if hit and self.cds.zhc.is_active():
            self.cds.zhc.use_charge()

        # handle gcd
        if cooldown:
            yield self.env.timeout(cooldown)

    def _insect_swarm(self):
        # use rank 2 to get full spell coefficient
        min_dmg = 278
        max_dmg = 313
        casting_time = 0
        crit_modifier = 0

        yield from self._nature_dot(spell=Spell.INSECT_SWARM,
                                    base_cast_time=casting_time)

    # subrotations for different eclipse states
    def insect_swarm_wrath_subrotation(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        if not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
            yield from self._insect_swarm()
        else:
            yield from self._wrath()

    def insect_swarm_moonfire_wrath_subrotation(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        if not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
            yield from self._insect_swarm()
        elif not self.env.debuffs.is_dot_active(MoonfireDot, self) and self.env.remaining_time() > 20:
            yield from self._moonfire()
        else:
            yield from self._wrath()

    def moonfire_starfire_subrotation(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        if not self.env.debuffs.is_dot_active(MoonfireDot, self) and self.env.remaining_time() > 20:
            yield from self._moonfire()
        else:
            yield from self._starfire()

    def moonfire_insect_swarm_starfire_subrotation(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        if not self.env.debuffs.is_dot_active(MoonfireDot, self) and self.env.remaining_time() > 20:
            yield from self._moonfire()
        elif not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
            yield from self._insect_swarm()
        else:
            yield from self._starfire()

    def set_nature_eclipse_subrotation(self, rotation):
        self.nature_eclipse_rotation = rotation

    def set_arcane_eclipse_subrotation(self, rotation):
        self.arcane_eclipse_rotation = rotation

    def _base_rotation(self, cds: CooldownUsages = CooldownUsages(), delay=2, rotation_callback=None):
        self._use_cds(cds)
        yield from self._random_delay(delay)

        while True:
            self._use_cds(cds)
            if self.opts.starfire_on_balance_of_all_things_proc and self.balance_of_all_things_stacks > 0 and self.arcane_eclipse.is_active():
                yield from self._starfire()
            elif self.opts.starfire_on_balance_of_all_things_proc and self.balance_of_all_things_stacks > 2:
                yield from self._starfire()
            elif self.nature_eclipse.is_active() and self.nature_eclipse_rotation and not self.opts.ignore_nature_eclipse:
                yield from self.nature_eclipse_rotation(self)
            elif self.arcane_eclipse.is_active() and self.arcane_eclipse_rotation and not self.opts.ignore_arcane_eclipse:
                yield from self.arcane_eclipse_rotation(self)
            elif rotation_callback:
                yield from rotation_callback()

    def _spam_starfire(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            yield from self._starfire()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _insect_swarm_spam_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            if not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
                yield from self._insect_swarm()
            else:
                yield from self._wrath()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _spam_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            yield from self._wrath()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _moonfire_starfire(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            if not self.env.debuffs.is_dot_active(MoonfireDot, self) and self.env.remaining_time() > 20:
                yield from self._moonfire()
            else:
                yield from self._starfire()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _insect_swarm_starfire(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            if not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
                yield from self._insect_swarm()
            else:
                yield from self._starfire()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _insect_swarm_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            if not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
                yield from self._insect_swarm()
            else:
                yield from self._wrath()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _moonfire_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            if not self.env.debuffs.is_dot_active(MoonfireDot, self) and self.env.remaining_time() > 20:
                yield from self._moonfire()
            else:
                yield from self._wrath()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _moonfire_insect_swarm_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            if not self.env.debuffs.is_dot_active(MoonfireDot, self) and self.env.remaining_time() > 20:
                yield from self._moonfire()
            elif not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
                yield from self._insect_swarm()
            else:
                yield from self._wrath()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _moonfire_insect_swarm_starfire(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            if not self.env.debuffs.is_dot_active(MoonfireDot, self) and self.env.remaining_time() > 20:
                yield from self._moonfire()
            elif not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
                yield from self._insect_swarm()
            else:
                yield from self._starfire()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    def _maximize_eclipse(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        def _rotation_callback():
            if not self.env.debuffs.is_dot_active(MoonfireDot, self) and self.env.remaining_time() > 20:
                yield from self._moonfire()
            elif not self.env.debuffs.is_dot_active(InsectSwarmDot, self) and self.env.remaining_time() > 20:
                yield from self._insect_swarm()
            elif self.nature_eclipse.usable:
                yield from self._starfire()
            elif self.arcane_eclipse.usable:
                yield from self._wrath()
            else:
                yield from self._starfire()

        return self._base_rotation(cds=cds, delay=delay, rotation_callback=_rotation_callback)

    @simrotation("Maximize Eclipse")
    def maximize_eclipse(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="maximize_eclipse")(cds=cds, delay=delay)

    @simrotation("Moonfire -> Insect Swarm -> Wrath")
    def moonfire_insect_swarm_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="moonfire_insect_swarm_wrath")(cds=cds, delay=delay)

    @simrotation("Moonfire -> Insect Swarm -> Starfire")
    def moonfire_insect_swarm_starfire(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="moonfire_insect_swarm_starfire")(cds=cds, delay=delay)

    # Regular rotations when not in eclipse
    @simrotation("Starfire (Spam)")
    def spam_starfire(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_starfire")(cds=cds, delay=delay)

    @simrotation("Insect Swarm -> Wrath (Spam)")
    def insect_swarm_spam_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="insect_swarm_spam_wrath")(cds=cds, delay=delay)

    @simrotation("Wrath (Spam)")
    def spam_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="spam_wrath")(cds=cds, delay=delay)

    @simrotation("Moonfire -> Starfire")
    def moonfire_starfire(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="moonfire_starfire")(cds=cds, delay=delay)

    @simrotation("Insect Swarm -> Starfire")
    def insect_swarm_starfire(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="insect_swarm_starfire")(cds=cds, delay=delay)

    @simrotation("Insect Swarm -> Wrath")
    def insect_swarm_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="insect_swarm_wrath")(cds=cds, delay=delay)

    @simrotation("Moonfire -> Wrath")
    def moonfire_wrath(self, cds: CooldownUsages = CooldownUsages(), delay=2):
        return partial(self._set_rotation, name="moonfire_wrath")(cds=cds, delay=delay)
