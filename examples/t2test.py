from _example_imports import *

mages = []
num_t2_mages = 1
num_mages = 1

for i in range(num_t2_mages):
    fm = Mage(name=f't2 mage{i}', sp=1009, crit=33.17, hit=16,
              opts=MageOptions(fullt2=True), tal=FireMageTalents)
    fm.smart_scorch()
    mages.append(fm)

for i in range(num_mages):
    fm = Mage(name=f'mage{i}', sp=1009, crit=33.17, hit=16, tal=FireMageTalents)
    fm.smart_scorch()
    mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=1000, duration=100)
sim.extended_report()
