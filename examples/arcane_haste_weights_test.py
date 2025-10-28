from _example_imports import *

mages = []
num_mages = 5

control_sp = 1050
control_crit = 35
control_hit = 15
control_haste = 25

equipped_items = EquippedItems(
    ornate_bloodstone_dagger=False,
    wrath_of_cenarius=True,
    true_band_of_sulfuras=True,
)
options = MageOptions(
    t35_arcane_3_set=True,
)
for i in range(num_mages):
    fm = None
    if i == 0:
        fm = Mage(name=f'control', sp=control_sp, crit=control_crit, hit=control_hit, haste=control_haste,
                  tal=ArcaneMageTalents(),
                  opts=options,
                  equipped_items=equipped_items)
    elif i == 1:
        fm = Mage(name=f'1 hit', sp=control_sp, crit=control_crit, hit=control_hit + 1, haste=control_haste,
                  tal=ArcaneMageTalents(),
                  opts=options,
                  equipped_items=equipped_items)
    elif i == 2:
        fm = Mage(name=f'1 crit', sp=control_sp, crit=control_crit + 1, hit=control_hit, haste=control_haste,
                  tal=ArcaneMageTalents(),
                  opts=options,
                  equipped_items=equipped_items)
    elif i == 3:
        fm = Mage(name=f'1 haste', sp=control_sp, crit=control_crit, hit=control_hit, haste=control_haste + 1,
                  tal=ArcaneMageTalents(),
                  opts=options,
                  equipped_items=equipped_items)
    elif i == 4:
        fm = Mage(name=f'20sp', sp=control_sp + 20, crit=control_crit, hit=control_hit, haste=control_haste,
                  tal=ArcaneMageTalents(),
                  opts=options,
                  equipped_items=equipped_items)

    if fm:
        fm.arcane_rupture_missiles(cds=CooldownUsages())
        mages.append(fm)

sim = Simulation(characters=mages, num_mobs=1, mob_level=63)
sim.run(iterations=20000, duration=180, print_casts=False)
sim.detailed_report()
