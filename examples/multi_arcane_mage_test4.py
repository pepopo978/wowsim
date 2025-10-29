from _example_imports import *

mages = []

base_sp = 1000
base_crit = 40
base_hit = 16
base_haste = 0

cooldowns = CooldownUsages()

m = Mage(name=f'0 haste', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(
             extra_second_arcane_missile=True,
             distance_from_mob=5,
         ),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             true_band_of_sulfuras=True,
             endless_gulch=False,
         ))
m.arcane_missiles(cds=cooldowns)
mages.append(m)


sim = Simulation(characters=mages, num_mobs=1, mob_level=63)
sim.run(iterations=10000, duration=180, print_casts=False, use_multiprocessing=True)
sim.detailed_report()
