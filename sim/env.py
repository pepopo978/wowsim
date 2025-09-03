import random

import simpy


class Environment(simpy.Environment):
    def __init__(self,
                 print_casts=True,
                 print_dots=False,
                 permanent_coe=True,
                 permanent_cos=True,
                 permanent_shadow_weaving=True,
                 permanent_nightfall=False,
                 permanent_isb=False,
                 num_mobs=1,
                 mob_level=63,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        from sim.debuffs import Debuffs
        from sim.utils import DamageMeter

        self.characters = []
        self.num_mobs = num_mobs
        self.mob_level = mob_level

        self.print = print_casts
        self.print_dots = print_dots
        self.debuffs = Debuffs(self,
                               permanent_coe=permanent_coe,
                               permanent_cos=permanent_cos,
                               permanent_shadow_weaving=permanent_shadow_weaving,
                               permanent_nightfall=permanent_nightfall,
                               permanent_isb=permanent_isb,
                               )
        self.meter = DamageMeter(self, num_mobs)
        self.process(self.debuffs.run())

        self.GCD = 1.57
        self.duration = 0

    def time(self):
        dt = str(round(self.now, 2))
        return '[' + str(dt) + ']'

    def remaining_time(self):
        return self.duration - self.now

    def p(self, msg):
        if self.print:
            print(msg)

    def add_character(self, character):
        self.characters.append(character)
        character.attach_env(self)

    def add_characters(self, characters):
        for char in characters:
            self.add_character(char)

    def run(self, *args, **kwargs):
        self.duration = kwargs.get('until', 0)

        random.shuffle(self.characters)
        for char in self.characters:
            self.process(char.rotation(char))
        super().run(*args, **kwargs)

        for char in self.characters:
            char.add_remaining_buff_uptime()

        self.debuffs.add_remaining_debuff_uptime()

