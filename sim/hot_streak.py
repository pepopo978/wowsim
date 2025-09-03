from sim.env import Environment

IGNITE_WINDOW = 4
IGNITE_TICK_TIME = 2


class HotStreak:
    def __init__(self, env, character):
        self.env: Environment = env
        self.character = character

        self.last_crit_time = 0
        self.stacks = 0
        self.num_usages = 0

    def add_stack(self):
        if self.stacks < 5:
            self.stacks += 1
        self.last_crit_time = self.env.now

    def get_stacks(self):
        # reset stacks if more than 30 seconds have passed since last crit
        if self.env.now - self.last_crit_time > 30:
            self.stacks = 0

        return self.stacks

    def use_stacks(self):
        self.stacks = 0
        self.num_usages += 1

    def _justify(self, string):
        return string.ljust(JUSTIFY, ' ')

    def report(self):
        print(f"------ Hot Streak ------")
        print(f"{self._justify('Usages')}: {self.num_usages}")
