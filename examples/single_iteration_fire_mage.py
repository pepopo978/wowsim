from _example_imports import *

base_sp = 1000
base_crit = 40
base_hit = 14
base_haste = 4

duration=120

fm = Mage(name=f'fireblast -> scorch', sp=1050, crit=50, hit=16, haste=5,
          tal=FireMageTalents(),
          opts=MageOptions(
              min_ignite_stacks_to_extend=2,
              scorch_after_fire_blast=True,
          ))
fm.smart_scorch_and_fireblast(CooldownUsages(combustion=10, mqg=10))

# sim = Simulation(characters=[fm])
# sim.run(iterations=20000, duration=duration, print_casts=False)
# sim.detailed_report()

env = Environment()
env.add_characters([fm])
env.run(until=180)
env.meter.detailed_report()
