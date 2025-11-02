from _example_imports import *


base_sp = 1000
base_crit = 40
base_hit = 16
base_haste = 0

cooldowns = CooldownUsages()

mages = []
for i in range(7, 9, 1):
    m = Mage(name=f'{i} haste', sp=base_sp, crit=base_crit, hit=base_hit, haste=i,
             tal=ArcaneMageTalents(),
             opts=MageOptions(
                 extra_second_arcane_missile=True,
             ),
             equipped_items=EquippedItems(
                 ornate_bloodstone_dagger=False,
                 wrath_of_cenarius=True,
                 true_band_of_sulfuras=True,
                 endless_gulch=False,
             ))
    m.arcane_rupture_missiles(cds=cooldowns)
    mages.append(m)


sim = Simulation(characters=mages, num_mobs=1, mob_level=63)
sim.run(iterations=10000, duration=180, print_casts=False, use_multiprocessing=False)
sim.detailed_report()
