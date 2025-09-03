from _example_imports import *

mages = []
num_mages = 5

for i in range(num_mages):
    fm = Mage(name=f'mage{i}', sp=1004, crit=92, hit=16, opts=MageOptions(drop_suboptimal_ignites=True),
              tal=FireMageTalents)
    fm.smart_scorch(cds=CooldownUsages(combustion=10, reos=5))
    mages.append(fm)

# Single run
# env = Environment()
# env.add_characters(mages)
# env.run(until=222)
# env.meter.report()

# multi run
sim = Simulation(characters=mages, permanent_coe=True, permanent_nightfall=True)
sim.run(iterations=1000, duration=222)
sim.report()
