from _example_imports import *

mages = []

fm = Mage(name=f'fireblast', sp=1000 + 30, crit=40.43 + 1, hit=16, haste=3,
          tal=FireMageTalents(),
          opts=MageOptions(
              min_ignite_stacks_to_extend=3,
              extend_ignite_with_scorch=True,
              distance_from_mob=5
          ))
fm.smart_scorch_and_fireblast(CooldownUsages(combustion=10, mqg=10))
mages.append(fm)
#
sim = Simulation(characters=mages)
sim.run(iterations=5000, duration=300, print_casts=False)
sim.detailed_report()

# env = Environment()
# env.add_characters(mages)
# env.run(until=180)
# env.meter.detailed_report()
