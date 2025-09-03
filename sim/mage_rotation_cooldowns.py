from sim.character import Character
from sim.cooldowns import Cooldown
from sim.spell_school import DamageType


class ConeOfColdCooldown(Cooldown):
    PRINTS_ACTIVATION = False

    @property
    def cooldown(self):
        return 10


class FireBlastCooldown(Cooldown):
    PRINTS_ACTIVATION = False

    def __init__(self, character: Character, cooldown: float):
        super().__init__(character)
        self._cd = cooldown

    @property
    def cooldown(self):
        return self._cd

class FrostNovaCooldown(Cooldown):
    PRINTS_ACTIVATION = False

    def __init__(self, character: Character, cooldown: float):
        super().__init__(character)
        self._cd = cooldown
        self._cast_number = 0

    @property
    def cooldown(self):
        return self._cd

    # need special handling for when cooldown ends due to possibility of cooldown reset
    def activate(self):
        if self.usable:
            self._active = True

            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} activated")

            cooldown = self.cooldown
            if self.STARTS_CD_ON_ACTIVATION and cooldown:
                self._on_cooldown = True

                def callback(self, cooldown, cast_number):
                    yield self.env.timeout(cooldown)
                    # if cooldown got reset already, do nothing
                    if cast_number == self._cast_number:
                        if self.PRINTS_ACTIVATION:
                            self.character.print(f"{self.name} cooldown ended after {cooldown} seconds")

                        self._on_cooldown = False
                        self._cast_number += 1

                self.character.env.process(callback(self, cooldown, self._cast_number))

            if self.duration:
                def callback(self):
                    yield self.character.env.timeout(self.duration)
                    self.deactivate()

                self.character.env.process(callback(self))
            else:
                self.deactivate()

    def reset_cooldown(self):
        if self.PRINTS_ACTIVATION:
            self.character.print(f"{self.name} cooldown reset")
        self._cast_number += 1
        self._on_cooldown = False


class ColdSnapCooldown(Cooldown):
    PRINTS_ACTIVATION = True

    @property
    def cooldown(self):
        return 600

    def activate(self):
        if self.usable:
            super().activate()
            # reset all frost cooldowns (only frost nova for now)
            if hasattr(self.character, 'frost_nova_cd'):
                self.character.frost_nova_cd.reset_cooldown()


class IciclesCooldown(Cooldown):
    PRINTS_ACTIVATION = False

    @property
    def cooldown(self):
        return 30

    @property
    def usable(self):
        return not self._active and not self._on_cooldown

    def deactivate(self):
        self._active = False
        if self.PRINTS_ACTIVATION:
            self.character.print(f"{self.name} deactivated")

        if self.cooldown:
            self._on_cooldown = True

            self._time_off_cooldown = self.env.now + self.cooldown

            def callback(self):
                yield self.env.timeout(self.cooldown)

                # flash freeze can proc and restart the cooldown,
                # need to check the latest _time_off_cooldown for this thread
                if self._time_off_cooldown <= self.env.now:
                    self._on_cooldown = False

            self.character.env.process(callback(self))


class ArcaneSurgeCooldown(Cooldown):
    # requires partial resist as well
    PRINTS_ACTIVATION = False

    def __init__(self, character: Character, apply_cd_haste: bool):
        super().__init__(character)
        self._base_cd = 8
        self._resist_time = None
        self._apply_cd_haste = apply_cd_haste

    @property
    def cooldown(self):
        return self._base_cd / self.character.get_haste_factor_for_damage_type(
            DamageType.ARCANE) if self._apply_cd_haste else self._base_cd

    def enable_due_to_resist(self):
        self._resist_time = self.character.env.now

    @property
    def usable(self):
        if not self._active and not self._on_cooldown and self._resist_time:
            if self.character.env.now - self._resist_time < 4:
                return True
            else:
                self._resist_time = None

        return False

    def time_left(self):
        if self._resist_time:
            return self._resist_time + 3 - self.character.env.now
        return 0

    def activate(self):
        super().activate()
        self._resist_time = None


class ArcaneRuptureCooldown(Cooldown):
    PRINTS_ACTIVATION = False
    TRACK_UPTIME = True

    def __init__(self, character: Character, apply_cd_haste: bool):
        super().__init__(character)
        self._base_cd = 15
        self._apply_cd_haste = apply_cd_haste
        self._cast_number = 0

    @property
    def usable(self):
        return not self._on_cooldown

    @property
    def duration(self):
        return 7.6 # account for .4s missile travel time

    @property
    def cooldown(self):
        return self._base_cd / self.character.get_haste_factor_for_damage_type(
            DamageType.ARCANE) if self._apply_cd_haste else self._base_cd

    # need special handling for when cooldown ends due to possibility of cooldown reset
    def activate(self):
        if self.usable:
            self._active = True

            self.track_buff_start_time()

            if self.PRINTS_ACTIVATION:
                self.character.print(f"{self.name} activated")

            cooldown = self.cooldown
            if self.STARTS_CD_ON_ACTIVATION and cooldown:
                self._on_cooldown = True

                def callback(self, cooldown, cast_number):
                    yield self.env.timeout(cooldown)
                    # if cooldown got reset already, do nothing
                    if cast_number == self._cast_number:
                        if self.PRINTS_ACTIVATION:
                            self.character.print(f"{self.name} cooldown ended after {cooldown} seconds")

                        self._on_cooldown = False
                        self._cast_number += 1

                self.character.env.process(callback(self, cooldown, self._cast_number))

            if self.duration:
                def callback(self):
                    yield self.character.env.timeout(self.duration)
                    self.deactivate()

                self.character.env.process(callback(self))
            else:
                self.deactivate()

    def reset_cooldown(self):
        if self.PRINTS_ACTIVATION:
            self.character.print(f"{self.name} cooldown reset")
        self._cast_number += 1
        self._on_cooldown = False


class TemporalConvergenceCooldown(Cooldown):
    PRINTS_ACTIVATION = False

    @property
    def cooldown(self):
        return 15
