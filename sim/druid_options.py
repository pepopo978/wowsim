from dataclasses import dataclass
from sim.decorators import simoption

@dataclass(kw_only=True)
class DruidOptions:
    ignore_arcane_eclipse: bool = simoption("Ignore Arcane Eclipse", default=False)
    ignore_nature_eclipse: bool = simoption("Ignore Nature Eclipse", default=False)

    distance_from_mob: int = simoption("Distance From Mob", default=25, spec=None)

    starfire_on_balance_of_all_things_proc: bool = simoption("Cast Starfire on Balance of All Things proc", default=False)
    set_bonus_3_dot_dmg: bool = simoption("3pc Set Bonus: +15% DoT damage", default=False)
    set_bonus_3_5_boat: bool = simoption("3.5pc Set Bonus: -0.25s Starfire cast time from Balance of All Things", default=False)

    extra_dot_ticks: int = simoption("Extra DoT ticks", default=0)
    ebb_and_flow_idol: bool = simoption("Ebb and Flow Idol equipped", default=False)
