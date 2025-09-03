from sim.dot import Dot
from sim.spell import Spell
from sim.spell_school import DamageType


class FireballDot(Dot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__(Spell.FIREBALL.value, owner, env, DamageType.FIRE, cast_time, register_casts=False)

        self.coefficient = 0
        self.base_time_between_ticks = 2
        self.ticks_left = 4
        self.starting_ticks = 4
        self.base_tick_dmg = 19

    def _do_dmg(self):
        super()._do_dmg()


class PyroblastDot(Dot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__(Spell.PYROBLAST.value, owner, env, DamageType.FIRE, cast_time, register_casts=False)

        self.coefficient = 0.15
        self.base_time_between_ticks = 3
        self.ticks_left = 4
        self.starting_ticks = 4
        self.base_tick_dmg = 67


class ImmolateDot(Dot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__(Spell.IMMOLATE.value, owner, env, DamageType.FIRE, cast_time, register_casts=False)

        self.coefficient = 0.15
        self.base_time_between_ticks = 3
        self.ticks_left = 4
        self.starting_ticks = 4
        self.base_tick_dmg = 102 * (1 + owner.tal.aftermath * 0.02)


    def get_effective_tick_dmg(self):
        return self._get_effective_tick_dmg()
