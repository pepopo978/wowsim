from typing import Dict

from sim import JUSTIFY
from sim.env import Environment
from sim.warlock import Character

ISB_DURATION = 10


class ImprovedShadowBolt:
    def __init__(self, env, permanent_isb=False):
        self._uptime = 0
        self._added_dot_dmg: Dict[Character, int] = {}
        self._added_spell_dmg: Dict[Character, int] = {}

        self.permanent_isb = permanent_isb

        self.env: Environment = env

        self.activation_time = None
        self.last_monitor_time = 0

        self.had_any_isbs = False
        self.total_activations = 0
        self.activations: Dict[Character, int] = {}

    @property
    def is_active(self):
        if self.permanent_isb:
            return True

        if self.activation_time is None:
            return False

        return self.env.now - self.activation_time <= ISB_DURATION

    def record_uptimes(self):
        if self.is_active:
            self._uptime += self.env.now - self.last_monitor_time

        self.last_monitor_time = self.env.now

    def apply_to_dot(self, warlock: Character, dmg: int):
        if self.is_active:
            self.record_uptimes()

            added_dmg = int(dmg * 0.2)
            self._added_dot_dmg[warlock] = self._added_dot_dmg.get(warlock, 0) + added_dmg
            return dmg + added_dmg
        else:
            return dmg

    def apply_to_spell(self, warlock: Character, dmg: int):
        if self.is_active:
            self.record_uptimes()

            added_dmg = int(dmg * 0.2)
            self._added_spell_dmg[warlock] = self._added_spell_dmg.get(warlock, 0) + added_dmg
            return dmg + added_dmg
        else:
            return dmg

    def refresh(self, warlock: Character):
        self.record_uptimes()

        self.had_any_isbs = True
        self.activation_time = self.env.now
        self.total_activations += 1
        self.activations[warlock] = self.activations.get(warlock, 0) + 1

    @property
    def uptime(self):
        return self._uptime

    @property
    def uptime_percent(self):
        return round(self.uptime / self.env.now * 100, 2)

    @property
    def total_added_dot_dmg(self):
        return sum(self._added_dot_dmg.values())

    @property
    def total_added_spell_dmg(self):
        return sum(self._added_spell_dmg.values())

    def _justify(self, string):
        return string.ljust(JUSTIFY, ' ')

    def report(self):
        if not self.had_any_isbs:
            return

        print(f"------ ISB ------")
        for lock, activations in self.activations.items():
            label = f"{lock.name} ISB Procs"
            activations_percent = round(activations / self.total_activations * 100, 2)
            print(f"{self._justify(label)}: {activations} ({activations_percent}%)")

        for lock, added_dmg in self._added_dot_dmg.items():
            label = f"{lock.name} ISB Dot Dmg | Spell Dmg"
            dot_dmg = self._added_dot_dmg.get(lock, 0)
            spell_dmg = self._added_spell_dmg.get(lock, 0)
            print(f"{self._justify(label)}: {dot_dmg} | {spell_dmg}")

        print(f"{self._justify('ISB uptime')}: {self.uptime_percent}%")
        print(f"{self._justify('Total added dot dmg')}: {self.total_added_dot_dmg}")
        print(f"{self._justify('Total added spell dmg')}: {self.total_added_spell_dmg}")
