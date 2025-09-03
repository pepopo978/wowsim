from _example_imports import *

cds = CooldownUsages()
mages = []
num_mages = 2
for i in range(num_mages):
    fm = None
    if i == 0:
        fm = Mage(name=f'normal', sp=1000, crit=40, hit=16, haste=4,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(t3_8_set=False, extra_second_arcane_missile=False),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=False,
                      endless_gulch=False,
                  ))
        fm.arcane_surge_rupture_missiles(cds=cds)
    elif i == 1:
        fm = Mage(name=f'ornate', sp=1000-95, crit=40-1, hit=16, haste=4,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(t3_8_set=False, extra_second_arcane_missile=False),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=True,
                      wrath_of_cenarius=False,
                      endless_gulch=False,
                  ))
        fm.arcane_surge_rupture_missiles(cds=cds)
    if fm:
        mages.append(fm)

sim = Simulation(characters=mages, num_mobs=1)
sim.run(iterations=5000, duration=120, print_casts=False)
sim.detailed_report()
