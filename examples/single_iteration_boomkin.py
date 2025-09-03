from _example_imports import *
from sim.druid import Druid
from sim.druid_options import DruidOptions
from sim.druid_talents import BalanceDruidTalents

boomkins = []
num_boomkins = 1

options = DruidOptions(ignore_arcane_eclipse=False,
                       ignore_nature_eclipse=False,
                       extra_dot_ticks=1,
                       starfire_on_balance_of_all_things_proc=True,
                       set_bonus_3_dot_dmg=True,
                       set_bonus_3_5_boat=True,
                       ebb_and_flow_idol=True)

for i in range(num_boomkins):
    d = Druid(name=f'test', sp=1000, crit=40, hit=16, haste=0,
              tal=BalanceDruidTalents(),
              opts=options,
              equipped_items=EquippedItems())
    d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
    d.set_arcane_eclipse_subrotation(d.moonfire_starfire_subrotation)
    d.set_nature_eclipse_subrotation(d.insect_swarm_wrath_subrotation)
    boomkins.append(d)

env = Environment(print_dots=True)
env.add_characters(boomkins)
env.run(until=120)
env.meter.detailed_report()
