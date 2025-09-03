from sim.dot import Dot
from sim.mage import Spell as MageSpell
from sim.spell_school import DamageType


class MoonfireDot(Dot):
    def __init__(self, owner, env, cast_time: float):
        super().__init__(MageSpell.MOONFIRE.value, owner, env, DamageType.ARCANE, cast_time, register_casts=False)

        self.coefficient = .1302
        self.base_time_between_ticks = 3
        self.ticks_left = 6 + self.owner.opts.extra_dot_ticks
        self.starting_ticks = 6 + self.owner.opts.extra_dot_ticks
        self.base_tick_dmg = 96

    def _get_effective_tick_dmg(self):
        dmg = self.base_tick_dmg + self.sp * self.coefficient
        if self.owner.opts.set_bonus_3_dot_dmg:
            # 15% more dot dmg
            dmg *= 1.15

        return int(self.owner.modify_dmg(dmg, self.damage_type, is_periodic=True))
