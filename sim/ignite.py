from typing import Optional

from sim import JUSTIFY
from sim.env import Environment
from sim.mage import Mage, Spell

IGNITE_WINDOW = 6
IGNITE_TICK_TIME = 2
IGNITE_NUM_TICKS = IGNITE_WINDOW / IGNITE_TICK_TIME  # 2 ticks per ignite window
IGNITE_TICK_AMOUNT_PER_TICK_PER_TALENT_POINT = .08 / IGNITE_NUM_TICKS  # 8% per tick per talent point


class Ignite:
    def __init__(self, env):
        self._uptimes = [0, 0, 0, 0, 0]  # each index is number of ignite stacks
        self._num_ticks = [0, 0, 0, 0, 0]

        self.owner: Optional[Mage] = None
        self.env: Environment = env

        self.active = False
        self.num_drops = 0
        self.tick_dmg = 0
        self.last_crit_time = 0
        self.ticks_left = 0
        self.stacks = 0
        self.ticks = []

        self.last_monitor_time = 0

        self.crit_this_window = False
        self.contains_scorch = False
        self.contains_fire_blast = False
        self.contains_partial = False
        self.ignite_id = 0

        self.had_any_ignites = False

    def is_suboptimal(self):
        return self.contains_scorch or self.contains_fire_blast or self.contains_partial

    def record_uptimes(self):
        if self.active:
            for i in range(self.stacks):
                self._uptimes[i] += self.env.now - self.last_monitor_time

        self.last_monitor_time = self.env.now

    def refresh(self, mage: Mage, dmg: int, spell: Spell, partial: bool, ignite_talent_points: int):
        self.check_for_drop()
        self.last_crit_time = self.env.now

        self.record_uptimes()

        if self.active:
            if self.stacks <= 4:
                self.tick_dmg += dmg * (IGNITE_TICK_AMOUNT_PER_TICK_PER_TALENT_POINT * ignite_talent_points)
                self.stacks += 1
                if partial:
                    self.contains_partial = True

                if spell == Spell.SCORCH:
                    self.contains_scorch = True
                elif spell == Spell.FIREBLAST:
                    self.contains_fire_blast = True

            self.ticks_left = IGNITE_NUM_TICKS
        else:  # new ignite
            self.active = True
            self.tick_dmg = dmg * (IGNITE_TICK_AMOUNT_PER_TICK_PER_TALENT_POINT * ignite_talent_points)
            self.stacks = 1
            self.owner = mage
            self.ticks_left = IGNITE_NUM_TICKS

            if partial:
                self.contains_partial = True

            if spell == Spell.SCORCH:
                self.contains_scorch = True
            elif spell == Spell.FIREBLAST:
                self.contains_fire_blast = True

            self.env.meter.register_ignite_dmg(
                char_name=self.owner.name,
                dmg=0,
                aoe=False,
                increment_cast=True)

            # start tick thread
            self.env.process(self.run(self.ignite_id))

    def drop(self):
        self.owner.print(f"Ignite dropped")
        self.active = False
        self.owner = None
        self.tick_dmg = 0
        self.stacks = 0
        self.ticks_left = 0
        self.last_crit_time = 0
        self.contains_scorch = False
        self.contains_fire_blast = False
        self.ignite_id += 1  # increment ignite id
        self.num_drops += 1

    def check_for_drop(self):
        # only check last crit time if ignite is active and down to 0 ticks
        if self.active and self.ticks_left == 0:
            # check if 6 seconds have passed since last crit
            if self.env.now - self.last_crit_time >= IGNITE_WINDOW:
                self.drop()

    def check_for_drop_after(self, delay):
        yield self.env.timeout(delay)
        self.check_for_drop()

    def run(self, ignite_id):
        while self.ignite_id == ignite_id:
            yield self.env.timeout(IGNITE_TICK_TIME)

            if self.ticks_left > 0 and self.ignite_id == ignite_id:
                self.had_any_ignites = True
                self.ticks_left -= 1
                self._do_dmg()

                if self.ticks_left == 0:
                    time_left = self.last_crit_time + IGNITE_WINDOW - self.env.now + .001 # add a small amount to prevent rounding errors
                    self.env.process(self.check_for_drop_after(time_left))
            else:
                self.check_for_drop()

    def _do_dmg(self):
        self.record_uptimes()
        tick_dmg = self.tick_dmg

        if self.env.debuffs.has_coe:
            tick_dmg *= 1.1  # ignite double dips on CoE

        if self.env.debuffs.has_nightfall:
            tick_dmg *= 1.15

        # doesn't snapshot on vmangos
        tick_dmg *= self.owner.dmg_modifier  # includes AP/PI

        tick_dmg *= 1 + self.env.debuffs.fire_vuln_stacks * 0.03  # ignite double dips on imp.scorch

        tick_dmg = int(tick_dmg)
        if self.env.print:
            time_left = self.last_crit_time + IGNITE_WINDOW - self.env.now
            self.env.p(
                f"{self.env.time()} - ({self.owner.name}) ({self.stacks}) ignite tick {tick_dmg} ticks remaining {self.ticks_left} time left {round(time_left, 2)}s")

        self._num_ticks[self.stacks - 1] += 1
        self.ticks.append(tick_dmg)
        self.env.meter.register_ignite_dmg(
            char_name=self.owner.name,
            dmg=tick_dmg,
            aoe=False)

    @property
    def time_remaining(self):
        time_left = (self.last_crit_time + IGNITE_WINDOW) - self.env.now
        return max(time_left, 0)

    @property
    def uptime_gte_1_stack(self):
        return self._uptimes[0] / self.env.now

    @property
    def uptime_gte_2_stacks(self):
        return self._uptimes[1] / self.env.now

    @property
    def uptime_gte_3_stacks(self):
        return self._uptimes[2] / self.env.now

    @property
    def uptime_gte_4_stacks(self):
        return self._uptimes[3] / self.env.now

    @property
    def uptime_5_stacks(self):
        return self._uptimes[4] / self.env.now

    @property
    def avg_tick(self):
        return sum(self.ticks) / len(self.ticks) if self.ticks else 0

    @property
    def max_tick(self):
        return max(self.ticks, default=0)

    @property
    def num_ticks(self):
        return len(self.ticks)

    @property
    def num_1_stack_ticks(self):
        return self._num_ticks[0]

    @property
    def num_2_stack_ticks(self):
        return self._num_ticks[1]

    @property
    def num_3_stack_ticks(self):
        return self._num_ticks[2]

    @property
    def num_4_stack_ticks(self):
        return self._num_ticks[3]

    @property
    def num_5_stack_ticks(self):
        return self._num_ticks[4]

    def _justify(self, string):
        return string.ljust(JUSTIFY, ' ')

    def report(self):
        if not self.had_any_ignites:
            return
        print(f"------ Ignite ------")
        print(f"{self._justify('Ignite uptime')}: {round(self.uptime_gte_1_stack * 100, 2)}%")
        print(f"{self._justify('>=3 stack ignite uptime')}: {round(self.uptime_gte_3_stacks * 100, 2)}%")
        print(f"{self._justify('5 stack ignite uptime')}: {round(self.uptime_5_stacks * 100, 2)}%")
        print(f"{self._justify('Num Ticks')}: {len(self.ticks)}")
        print(f"{self._justify('Average tick')}: {round(self.avg_tick, 2)}")
        print(f"{self._justify('Max Tick')}: {max(self.ticks)}")
