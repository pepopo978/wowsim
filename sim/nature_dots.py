import random

from sim.dot import Dot
from sim.mage import Spell as MageSpell
from sim.spell_school import DamageType


class InsectSwarmDot(Dot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__(MageSpell.INSECT_SWARM.value, owner, env, DamageType.NATURE, cast_time)

        self.coefficient = .158
        self.base_time_between_ticks = 2
        self.ticks_left = 9 + self.owner.opts.extra_dot_ticks
        self.starting_ticks = 9 + self.owner.opts.extra_dot_ticks
        self.base_tick_dmg = 54

        self.balance_of_all_things = self.owner.tal.balance_of_all_things

    def _get_effective_tick_dmg(self):
        dmg = self.base_tick_dmg + self.sp * self.coefficient
        if self.owner.opts.set_bonus_3_dot_dmg:
            # 15% more dot dmg
            dmg *= 1.15

        return int(self.owner.modify_dmg(dmg, self.damage_type, is_periodic=True))

    def _do_dmg(self):
        super()._do_dmg()
        if self.balance_of_all_things and self.owner.balance_of_all_things_stacks < 3:
            if random.randint(1, 100) <= 6 * self.balance_of_all_things:
                self.env.p(f"{self.env.time()} - ({self.owner.name}) Balance of All Things proc")
                self.owner.balance_of_all_things_stacks += 1
