from _example_imports import *
from sim.druid import Druid
from sim.druid_options import DruidOptions
from sim.druid_talents import BalanceDruidTalents

Druids = []
num_trinkets = 9

base_sp = 924
base_crit = 35
base_hit = 10
base_haste = 0

options = DruidOptions(ignore_arcane_eclipse=True, ignore_nature_eclipse=True,
                       starfire_on_balance_of_all_things_proc=True)

for i in range(num_trinkets):
    d = None
    if i == 0:
        d = Druid(name=f'nothing', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
                  tal=BalanceDruidTalents(),
                  opts=options)
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
    elif i == 1:
        d = Druid(name=f'reos', sp=base_sp + 40, crit=base_crit, hit=base_hit, haste=base_haste,
                  tal=BalanceDruidTalents(),
                  opts=options)
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages(reos=5))
    elif i == 2:
        pass
    elif i == 3:
        d = Druid(name=f'eye of dim', sp=base_sp, crit=base_crit + 3, hit=base_hit, haste=base_haste,
                  tal=BalanceDruidTalents(),
                  opts=options)
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
    elif i == 4:
        d = Druid(name=f'gulch', sp=base_sp + 30, crit=base_crit, hit=base_hit, haste=base_haste,
                  tal=BalanceDruidTalents(),
                  opts=options,
                  equipped_items=EquippedItems(endless_gulch=True))
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
    elif i == 5:
        d = Druid(name=f'tear', sp=base_sp + 44, crit=base_crit, hit=base_hit + 2, haste=base_haste,
                  tal=BalanceDruidTalents(),
                  opts=options)
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
    elif i == 6:
        d = Druid(name=f'toep', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
                  tal=BalanceDruidTalents(),
                  opts=options)
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages(toep=5))
    elif i == 7:
        pass
    elif i == 8:
        d = Druid(name=f'mark of champ', sp=base_sp + 85, crit=base_crit, hit=base_hit, haste=base_haste,
                  tal=BalanceDruidTalents(),
                  opts=options)
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())

    if d:
        d.set_arcane_eclipse_subrotation(d.moonfire_insect_swarm_starfire_subrotation)
        d.set_nature_eclipse_subrotation(d.insect_swarm_moonfire_wrath_subrotation)

        Druids.append(d)

sim = Simulation(characters=Druids)
sim.run(iterations=10000, duration=60, print_casts=False)
sim.detailed_report()
