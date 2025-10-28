from _example_imports import *

base_sp = 1000
base_crit = 40
base_hit = 14
base_haste = 4

duration=120

fm = Mage(name=f'mqg', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.spam_arcane_explosion(cds=CooldownUsages(mqg=12))

# sim = Simulation(characters=[fm])
# sim.run(iterations=20000, duration=duration, print_casts=False)
# sim.detailed_report()

env = Environment()
env.add_characters([fm])
env.run(until=180)
env.meter.detailed_report()
