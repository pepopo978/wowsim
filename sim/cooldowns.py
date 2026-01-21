from sim.character import Character
from sim.spell_school import DamageType


class Cooldown:
    STARTS_CD_ON_ACTIVATION = True
    PRINTS_ACTIVATION = True
    TRACK_UPTIME = False

    def __init__(self, character: Character):
        self.character = character
        self._on_cooldown = False
        self._active = False

    @property
    def duration(self):
        return 0

    @property
    def cooldown(self):
        return 0

    @property
    def env(self):
        return self.character.env

    @property
    def usable(self):
        return not self._active and not self._on_cooldown

    @property
    def on_cooldown(self):
        return self._on_cooldown

    def is_active(self):
        return self._active

    @property
    def name(self):
        return type(self).__name__

    def track_buff_start_time(self):
        if self.name not in self.character.buff_start_times:
            self.character.buff_start_times[self.name] = self.character.env.now

    def track_buff_uptime(self):
        if self.name not in self.character.buff_uptimes:
            self.character.buff_uptimes[self.name] = 0
        self.character.buff_uptimes[self.name] += self.character.env.now - self.character.buff_start_times[self.name]

        del self.character.buff_start_times[self.name]

    def activate(self):
        if self.usable:
            self._active = True

            if self.TRACK_UPTIME:
                self.track_buff_start_time()

            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} activated")

            cooldown = self.cooldown
            if self.STARTS_CD_ON_ACTIVATION and cooldown:
                self._on_cooldown = True

                def callback(self, cooldown):
                    yield self.env.timeout(cooldown)
                    if self.PRINTS_ACTIVATION:
                        self.character.print(f"{self.name} cooldown ended after {cooldown} seconds")

                    self._on_cooldown = False

                self.character.env.process(callback(self, cooldown))

            if self.duration:
                def callback(self):
                    yield self.character.env.timeout(self.duration)
                    self.deactivate()

                self.character.env.process(callback(self))
            else:
                self.deactivate()

    def deactivate(self):
        if self._active and self.TRACK_UPTIME:
            # add to uptime
            self.track_buff_uptime()

        self._active = False

        if self.PRINTS_ACTIVATION:
            self.character.print(f"{self.name} deactivated")

        cooldown = self.cooldown
        if not self.STARTS_CD_ON_ACTIVATION and cooldown:
            self._on_cooldown = True

            def callback(self, cooldown):
                yield self.env.timeout(cooldown)
                if self.PRINTS_ACTIVATION:
                    self.character.print(f"{self.name} cooldown ended after {cooldown} seconds")

                self._on_cooldown = False

            self.character.env.process(callback(self, cooldown))


class MQG(Cooldown):
    # Mind Quickening Gem
    @property
    def duration(self):
        return 20

    @property
    def cooldown(self):
        return 300

    def activate(self):
        super().activate()
        self.character.add_trinket_haste(self.name, 33)

    def deactivate(self):
        super().deactivate()
        self.character.remove_trinket_haste(self.name)


class Berserking(Cooldown):
    @property
    def duration(self):
        return 10

    @property
    def cooldown(self):
        return 180

    def __init__(self, character: Character, haste: float):
        super().__init__(character)
        self.haste = haste

    def activate(self):
        super().activate()
        self.character.add_trinket_haste(self.name, self.haste)

    def deactivate(self):
        super().deactivate()
        self.character.remove_trinket_haste(self.name)


class BloodFury(Cooldown):
    @property
    def duration(self):
        return 15

    @property
    def cooldown(self):
        return 120

    def activate(self):
        super().activate()
        self.character.add_sp_bonus(60)

    def deactivate(self):
        super().deactivate()
        self.character.remove_sp_bonus(60)


class Perception(Cooldown):
    @property
    def duration(self):
        return 20

    @property
    def cooldown(self):
        return 180

    def activate(self):
        super().activate()
        self.character.add_crit_bonus(2)

    def deactivate(self):
        super().deactivate()
        self.character.remove_crit_bonus(2)


class TOEP(Cooldown):
    # Talisman of Ephemeral Power
    DMG_BONUS = 175

    @property
    def duration(self):
        return 15

    @property
    def cooldown(self):
        return 90

    def activate(self):
        super().activate()
        self.character.add_sp_bonus(self.DMG_BONUS)

    def deactivate(self):
        super().deactivate()
        self.character.remove_sp_bonus(self.DMG_BONUS)


class ZandalarianHeroCharm(Cooldown):
    def __init__(self, character: Character):
        super().__init__(character)
        self._initial_sp_bonus = 204
        self._current_sp_bonus = 0

    @property
    def cooldown(self):
        return 120

    @property
    def duration(self):
        return 20

    def use_charge(self):
        if self._current_sp_bonus > 0:
            deduction = min(17, self._current_sp_bonus)
            self._current_sp_bonus -= deduction

            # deduct from character
            self.character.remove_sp_bonus(deduction)

    def activate(self):
        super().activate()
        self._current_sp_bonus = self._initial_sp_bonus
        self.character.add_sp_bonus(self._current_sp_bonus)

    def deactivate(self):
        super().deactivate()
        self.character.remove_sp_bonus(self._current_sp_bonus)
        self._current_sp_bonus = 0


class REOS(Cooldown):
    # Restrained Essence of Sapphiron
    DMG_BONUS = 130

    @property
    def duration(self):
        return 20

    @property
    def cooldown(self):
        return 120

    def activate(self):
        super().activate()
        self.character.add_sp_bonus(self.DMG_BONUS)

    def deactivate(self):
        super().deactivate()
        self.character.remove_sp_bonus(self.DMG_BONUS)


class Combustion(Cooldown):
    STARTS_CD_ON_ACTIVATION = False

    def __init__(self, character: Character):
        super().__init__(character)
        self._charges = 0
        self._crit_bonus = 0

    @property
    def cooldown(self):
        return 180

    @property
    def crit_bonus(self):
        return self._crit_bonus

    def use_charge(self):
        if self._charges:
            self._charges -= 1
            if self._charges == 0:
                self.deactivate()

    def cast_fire_spell(self):
        if self._charges:
            self._crit_bonus += 10

    def activate(self):
        super().activate()
        self._charges = 3
        self._crit_bonus = 10


class PresenceOfMind(Cooldown):
    STARTS_CD_ON_ACTIVATION = False

    def __init__(self, character: Character, apply_cd_haste: bool):
        super().__init__(character)
        self._base_cd = 180
        self._apply_cd_haste = apply_cd_haste

    @property
    def cooldown(self):
        return self._base_cd / self.character.get_haste_factor_for_damage_type(
            DamageType.ARCANE) if self._apply_cd_haste else self._base_cd

    @property
    def duration(self):
        return 9999


class ArcanePower(Cooldown):
    def __init__(self, character: Character, apply_cd_haste: bool):
        super().__init__(character)
        self._base_cd = 180
        self._apply_cd_haste = apply_cd_haste

    @property
    def cooldown(self):
        return self._base_cd / self.character.get_haste_factor_for_damage_type(
            DamageType.ARCANE) if self._apply_cd_haste else self._base_cd

    @property
    def duration(self):
        return 20

    def activate(self):
        super().activate()
        self.character.add_cooldown_haste(self.name, 30)

    def deactivate(self):
        super().deactivate()
        self.character.remove_cooldown_haste(self.name)


class PotionOfQuickness(Cooldown):
    @property
    def cooldown(self):
        return 120

    @property
    def duration(self):
        return 30

    def activate(self):
        super().activate()
        self.character.add_consume_haste(self.name, 5)

    def deactivate(self):
        super().deactivate()
        self.character.remove_consume_haste(self.name)


class JuJuFlurry(Cooldown):
    @property
    def cooldown(self):
        return 60

    @property
    def duration(self):
        return 20

    def activate(self):
        super().activate()
        self.character.add_consume_haste(self.name, 3)

    def deactivate(self):
        super().deactivate()
        self.character.remove_consume_haste(self.name)


class WrathOfCenariusBuff(Cooldown):
    DMG_BONUS = 132
    PRINTS_ACTIVATION = True
    TRACK_UPTIME = True

    def __init__(self, character: Character):
        super().__init__(character)
        self._buff_end_time = -1

    @property
    def usable(self):
        return not self._active

    @property
    def duration(self):
        return 10

    # need special handling for when cooldown ends due to possibility of cooldown reset
    def activate(self):
        if self.usable:
            self.character.add_sp_bonus(self.DMG_BONUS)

            if self.TRACK_UPTIME:
                self.track_buff_start_time()

            self._buff_end_time = self.character.env.now + self.duration

            self._active = True
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} activated")

            def callback(self):
                while True:
                    remaining_time = self._buff_end_time - self.character.env.now
                    yield self.character.env.timeout(remaining_time)

                    if self.character.env.now >= self._buff_end_time:
                        self.deactivate()
                        break

            self.character.env.process(callback(self))
        else:
            # refresh buff end time
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} refreshed")
            self._buff_end_time = self.character.env.now + self.duration

    def deactivate(self):
        super().deactivate()
        self.character.remove_sp_bonus(self.DMG_BONUS)


class EndlessGulchBuff(Cooldown):
    PRINTS_ACTIVATION = True
    TRACK_UPTIME = True

    def __init__(self, character: Character):
        super().__init__(character)
        self._buff_end_time = -1

    @property
    def duration(self):
        return 15

    # need special handling for when cooldown ends due to possibility of refresh
    def activate(self):
        if self.usable:
            self.character.add_trinket_haste(self.name, 20)

            if self.TRACK_UPTIME:
                self.track_buff_start_time()

            self._buff_end_time = self.character.env.now + self.duration

            self._active = True
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} activated")

            def callback(self):
                while True:
                    remaining_time = self._buff_end_time - self.character.env.now
                    yield self.character.env.timeout(remaining_time)

                    if self.character.env.now >= self._buff_end_time:
                        self.deactivate()
                        break

            self.character.env.process(callback(self))
        else:
            # refresh buff end time
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} refreshed")
            self._buff_end_time = self.character.env.now + self.duration

    def deactivate(self):
        super().deactivate()
        self.character.remove_trinket_haste(self.name)


class CharmOfMagic(Cooldown):
    #  Use: Increases the critical hit chance of your Arcane spells by 5%, and increases the critical hit damage of your Arcane spells by 50% for 20 sec.
    @property
    def cooldown(self):
        return 180

    @property
    def duration(self):
        return 20

    def activate(self):
        super().activate()
        self.character.damage_type_crit[DamageType.ARCANE] += 5
        self.character.damage_type_crit_mult[DamageType.ARCANE] += 0.25

    def deactivate(self):
        super().deactivate()
        self.character.damage_type_crit[DamageType.ARCANE] -= 5
        self.character.damage_type_crit_mult[DamageType.ARCANE] -= 0.25
        
        
class TrueBandOfSulfurasBuff(Cooldown):
    PRINTS_ACTIVATION = True
    TRACK_UPTIME = True

    def __init__(self, character: Character):
        super().__init__(character)
        self._buff_end_time = -1

    @property
    def duration(self):
        return 6

    # need special handling for when cooldown ends due to possibility of refresh
    def activate(self):
        if self.usable:
            self.character.add_trinket_haste(self.name, 5)

            if self.TRACK_UPTIME:
                self.track_buff_start_time()

            self._buff_end_time = self.character.env.now + self.duration

            self._active = True
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} activated")

            def callback(self):
                while True:
                    remaining_time = self._buff_end_time - self.character.env.now
                    yield self.character.env.timeout(remaining_time)

                    if self.character.env.now >= self._buff_end_time:
                        self.deactivate()
                        break

            self.character.env.process(callback(self))
        else:
            # refresh buff end time
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} refreshed")
            self._buff_end_time = self.character.env.now + self.duration

    def deactivate(self):
        super().deactivate()
        self.character.remove_trinket_haste(self.name)        

class BindingsOfContainedMagicBuff(Cooldown):
    DMG_BONUS = 100
    PRINTS_ACTIVATION = True
    TRACK_UPTIME = True

    def __init__(self, character: Character):
        super().__init__(character)
        self._buff_end_time = -1

    @property
    def usable(self):
        return not self._active

    @property
    def duration(self):
        return 6

    def activate(self):
        if self.usable:
            self.character.add_sp_bonus(self.DMG_BONUS)

            if self.TRACK_UPTIME:
                self.track_buff_start_time()

            self._buff_end_time = self.character.env.now + self.duration

            self._active = True
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} activated")

            def callback(self):
                while True:
                    remaining_time = self._buff_end_time - self.character.env.now
                    yield self.character.env.timeout(remaining_time)

                    if self.character.env.now >= self._buff_end_time:
                        self.deactivate()
                        break

            self.character.env.process(callback(self))
        # else:
            # if self.PRINTS_ACTIVATION:
                # self.character.print(f"{self.name} refreshed")
            # self._buff_end_time = self.character.env.now + self.duration

    def deactivate(self):
        super().deactivate()
        self.character.remove_sp_bonus(self.DMG_BONUS)

class SpellwovenNobilityDrapeBuff(Cooldown):
    INTELLECT_BONUS = 150
    CRIT_BONUS = INTELLECT_BONUS / 53.77
    PRINTS_ACTIVATION = True
    TRACK_UPTIME = True

    def __init__(self, character: Character):
        super().__init__(character)
        self._buff_end_time = -1

    @property
    def usable(self):
        return not self._active

    @property
    def duration(self):
        return 6

    def activate(self):
        if self.usable:
            self.character.add_crit_bonus(self.CRIT_BONUS)

            if self.TRACK_UPTIME:
                self.track_buff_start_time()

            self._buff_end_time = self.character.env.now + self.duration

            self._active = True
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} activated")

            def callback(self):
                while True:
                    remaining_time = self._buff_end_time - self.character.env.now
                    yield self.character.env.timeout(remaining_time)

                    if self.character.env.now >= self._buff_end_time:
                        self.deactivate()
                        break

            self.character.env.process(callback(self))
        else:
            # refresh buff end time
            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} refreshed")
            self._buff_end_time = self.character.env.now + self.duration

    def deactivate(self):
        super().deactivate()
        self.character.remove_crit_bonus(self.CRIT_BONUS)

class Cooldowns:
    def __init__(self, character):
        # mage cds
        has_accelerated_arcana = False
        if hasattr(character.tal, "accelerated_arcana"):
            has_accelerated_arcana = character.tal.accelerated_arcana

        self.combustion = Combustion(character)
        self.arcane_power = ArcanePower(character, has_accelerated_arcana)
        self.presence_of_mind = PresenceOfMind(character, has_accelerated_arcana)

        self.potion_of_quickness = PotionOfQuickness(character)

        self.charm_of_magic = CharmOfMagic(character)
        self.toep = TOEP(character)
        self.reos = REOS(character)
        self.mqg = MQG(character)
        self.zhc = ZandalarianHeroCharm(character)

        # racials
        self.berserking15 = Berserking(character, 15)
        self.berserking10 = Berserking(character, 10)
        self.blood_fury = BloodFury(character)
        self.perception = Perception(character)
