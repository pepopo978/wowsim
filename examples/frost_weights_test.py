from _example_imports import *

mages = []
num_mages = 5

control_sp = 300
control_crit = 18
control_hit = 13
control_haste = 0

for i in range(num_mages):
    fm = None
    if i == 0:
        fm = Mage(name=f'control', sp=control_sp, crit=control_crit, hit=control_hit, haste=control_haste,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=False,
                  ))
        fm.icicle_frostbolts()
    elif i == 1:
        fm = Mage(name=f'1 hit',  sp=control_sp, crit=control_crit, hit=control_hit+1, haste=control_haste,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=False,
                  ))
        fm.icicle_frostbolts()
    elif i == 2:
        fm = Mage(name=f'1 crit',  sp=control_sp, crit=control_crit+1, hit=control_hit, haste=control_haste,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=False,
                  ))
        fm.icicle_frostbolts()
    elif i == 3:
        fm = Mage(name=f'1 haste',  sp=control_sp, crit=control_crit, hit=control_hit, haste=control_haste+1,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=False,
                  ))
        fm.icicle_frostbolts()
    elif i == 4:
        fm = Mage(name=f'20sp',  sp=control_sp + 20, crit=control_crit, hit=control_hit, haste=control_haste,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=False,
                  ))
        fm.icicle_frostbolts()

    if fm:
        mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=50000, duration=110, print_casts=False)
sim.detailed_report()
