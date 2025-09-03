from _example_imports import *

mages = []
num_mages = 3

for i in range(num_mages):
    fm = Mage(name=f'mage{i}', sp=1057, crit=46.43, hit=16, tal=FireMageTalents(), opts=MageOptions(drop_suboptimal_ignites=True))
    fm.smart_scorch_and_fireblast(cds=CooldownUsages())
    mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=2000, duration=120)
sim.extended_report()
