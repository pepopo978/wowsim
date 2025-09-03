from _example_imports import *
from sim.druid import Druid
from sim.druid_options import DruidOptions
from sim.druid_talents import BalanceDruidTalents

druids = []
num_druids = 5

control_sp = 1111
control_crit = 35
control_hit = 15
control_haste = 7

options = DruidOptions(ignore_arcane_eclipse=True, ignore_nature_eclipse=True, starfire_on_balance_of_all_things_proc=True,
                       set_bonus_3_5_boat=True, extra_dot_ticks=1)

for i in range(num_druids):
    d = None
    if i == 0:
        d = Druid(name=f'control', sp=control_sp, crit=control_crit, hit=control_hit, haste=control_haste,
                  tal=BalanceDruidTalents(),
                  opts=options,
                  equipped_items=EquippedItems())
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
        d.set_arcane_eclipse_subrotation(d.moonfire_insect_swarm_starfire_subrotation)
        d.set_nature_eclipse_subrotation(d.insect_swarm_moonfire_wrath_subrotation)
    elif i == 1:
        d = Druid(name=f'1 hit', sp=control_sp, crit=control_crit, hit=control_hit + 1, haste=control_haste,
                 tal=BalanceDruidTalents(),
                 opts=options,
                 equipped_items=EquippedItems())
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
        d.set_arcane_eclipse_subrotation(d.moonfire_insect_swarm_starfire_subrotation)
        d.set_nature_eclipse_subrotation(d.insect_swarm_moonfire_wrath_subrotation)
    elif i == 2:
        d = Druid(name=f'1 crit', sp=control_sp, crit=control_crit + 1, hit=control_hit, haste=control_haste,
                 tal=BalanceDruidTalents(),
                 opts=options,
                 equipped_items=EquippedItems())
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
        d.set_arcane_eclipse_subrotation(d.moonfire_insect_swarm_starfire_subrotation)
        d.set_nature_eclipse_subrotation(d.insect_swarm_moonfire_wrath_subrotation)
    elif i == 3:
        d = Druid(name=f'1 haste', sp=control_sp, crit=control_crit, hit=control_hit, haste=control_haste + 1,
                 tal=BalanceDruidTalents(),
                 opts=options,
                 equipped_items=EquippedItems())
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
        d.set_arcane_eclipse_subrotation(d.moonfire_insect_swarm_starfire_subrotation)
        d.set_nature_eclipse_subrotation(d.insect_swarm_moonfire_wrath_subrotation)
    elif i == 4:
        d = Druid(name=f'20sp', sp=control_sp + 20, crit=control_crit, hit=control_hit, haste=control_haste,
                 tal=BalanceDruidTalents(),
                 opts=options,
                 equipped_items=EquippedItems())
        d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
        d.set_arcane_eclipse_subrotation(d.moonfire_insect_swarm_starfire_subrotation)
        d.set_nature_eclipse_subrotation(d.insect_swarm_moonfire_wrath_subrotation)

    if d:
        druids.append(d)

sim = Simulation(characters=druids)
sim.run(iterations=50000, duration=180, print_casts=False)
sim.detailed_report()
