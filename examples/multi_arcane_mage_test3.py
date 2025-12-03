from _example_imports import *

mages = []

base_sp = 1000
base_crit = 40
base_hit = 16
haste = 5

m = Mage(name=f'drape', sp=base_sp + 11, crit=base_crit, hit=base_hit, haste=haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(
             extra_second_arcane_missile=True,
         ),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             true_band_of_sulfuras=True,
             endless_gulch=False,
             spellwoven_nobility_drape=True,
         ))
m.spam_arcane_explosion(cds=CooldownUsages())
mages.append(m)

m = Mage(name=f'no drape', sp=base_sp + 26, crit=base_crit + 1, hit=base_hit, haste=haste,
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
m.spam_arcane_explosion(cds=CooldownUsages())
mages.append(m)

sim = Simulation(characters=mages, num_mobs=3, mob_level=63)
sim.run(iterations=10000, duration=180, print_casts=False, use_multiprocessing=False)
sim.detailed_report()
