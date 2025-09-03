from _example_imports import *

mages = []
num_mages = 2

for i in range(num_mages):
    if i == 0:
        fm = Mage(name=f'reg', sp=1000 + 30, crit=40 + 1, hit=16, haste=0,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())
        fm.icicle_frostbolts(cds=CooldownUsages())
        mages.append(fm)
    if i == 1:
        fm = Mage(name=f'sulfuras ring', sp=1000 + 20, crit=40, hit=16, haste=1,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems(true_band_of_sulfuras=True))
        fm.icicle_frostbolts(cds=CooldownUsages())
        mages.append(fm)

sim = Simulation(characters=mages, num_mobs=1)
sim.run(iterations=10000, duration=120)
sim.detailed_report()
