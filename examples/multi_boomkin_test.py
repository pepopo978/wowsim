from _example_imports import *
from sim.druid import Druid
from sim.druid_options import DruidOptions
from sim.druid_talents import BalanceDruidTalents

boomkins = []
options = DruidOptions(ignore_arcane_eclipse=False,
                       ignore_nature_eclipse=False,
                       extra_dot_ticks=1,
                       starfire_on_balance_of_all_things_proc=True,
                       set_bonus_3_dot_dmg=True,
                       set_bonus_3_5_boat=True,
                       ebb_and_flow_idol=True)

base_sp = 1111
base_crit = 39.84
base_hit = 16
base_haste = 7

def setEclipseRotation(d:Druid):
    d.set_arcane_eclipse_subrotation(d.moonfire_insect_swarm_starfire_subrotation)
    d.set_nature_eclipse_subrotation(d.insect_swarm_moonfire_wrath_subrotation)

d = Druid(name=f'spam_starfire', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.spam_starfire(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)

d = Druid(name=f'spam_wrath', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.spam_wrath(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)

d = Druid(name=f'moonfire_starfire', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.moonfire_starfire(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)

d = Druid(name=f'insect_swarm_starfire', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.insect_swarm_starfire(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)
d = Druid(name=f'insect_swarm_wrath', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.insect_swarm_wrath(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)

d = Druid(name=f'moonfire_wrath', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.moonfire_wrath(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)

d = Druid(name=f'moonfire_insect_swarm_wrath', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.moonfire_insect_swarm_wrath(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)

d = Druid(name=f'moonfire_insect_swarm_starfire', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.moonfire_insect_swarm_starfire(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)

d = Druid(name=f'maximize_eclipse', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=BalanceDruidTalents(),
          opts=options,
          equipped_items=EquippedItems())
d.maximize_eclipse(cds=CooldownUsages())
setEclipseRotation(d)
boomkins.append(d)

sim = Simulation(characters=boomkins)
sim.run(iterations=10000, duration=300, use_multiprocessing=True)
sim.detailed_report()
