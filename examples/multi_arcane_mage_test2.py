from _example_imports import *

cds = CooldownUsages()
mages = []
num_mages = 2

haste = 25

for i in range(num_mages):
    fm = None
    if i == 0:
        fm = Mage(name=f'surge', sp=1000, crit=40, hit=16, haste=haste,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(t3_8_set=False, extra_second_arcane_missile=True),
                  equipped_items=EquippedItems(
                      wrath_of_cenarius=True,
                      true_band_of_sulfuras=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=cds)
    elif i == 1:
        fm = Mage(name=f'no surge', sp=1000, crit=40, hit=16, haste=haste,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(t3_8_set=False, extra_second_arcane_missile=True),
                  equipped_items=EquippedItems(
                      wrath_of_cenarius=True,
                      true_band_of_sulfuras=True,
                  ))
        fm.arcane_rupture_missiles(cds=cds)
    if fm:
        mages.append(fm)

sim = Simulation(characters=mages, num_mobs=1)
sim.run(iterations=10000, duration=180, print_casts=False)
sim.detailed_report()
