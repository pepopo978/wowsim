from _example_imports import *

characters = []
num_mages = 3
num_locks = 3

for i in range(num_mages):
    fm = Mage(name=f'mage{i}', sp=1009, crit=33.17, hit=16, tal=FireMageTalents)
    fm.smart_scorch_and_fireblast()
    characters.append(fm)

for i in range(num_locks):
    lock = Warlock(name=f'lock{i}', sp=1005, crit=30.73, hit=10, tal=SMRuin(), opts=WarlockOptions())
    lock.corruption_immolate_shadowbolt()
    characters.append(lock)

sim = Simulation(characters=characters)
sim.run(iterations=1000, duration=60)
sim.extended_report()
