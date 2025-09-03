from _example_imports import *

mages = []
num_mages = 4

base_sp = 1000
base_crit = 40
base_hit = 16

for i in range(num_mages):
    if i == 0:
        fm = Mage(name=f'mqg nothing', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, mqg=5))
    elif i == 1:
        fm = Mage(name=f'mqg 40 sp', sp=base_sp+40, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, mqg=5))
    elif i == 2:
        fm = Mage(name=f'mqg charm_of_magic', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, mqg=5, charm_of_magic=25))
    elif i == 3:
        fm = Mage(name=f'mqg toep', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, mqg=5, toep=25))


    mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=10000, duration=120, print_casts=False)
sim.detailed_report()
