from _example_imports import *

mages = []

base_sp = 1000
base_crit = 30
base_hit = 16
haste = 15

m = Mage(name=f'combined cd', sp=base_sp, crit=base_crit, hit=base_hit, haste=haste,
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
m.arcane_rupture_missiles(cds=CooldownUsages(mqg=5, arcane_power=5))
mages.append(m)

m = Mage(name=f'separate cd', sp=base_sp, crit=base_crit, hit=base_hit, haste=haste,
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
m.arcane_rupture_missiles(cds=CooldownUsages(mqg=5, arcane_power=25))
mages.append(m)

sim = Simulation(characters=mages, num_mobs=1, mob_level=63)
sim.run(iterations=10000, duration=180, print_casts=False, use_multiprocessing=True)
sim.detailed_report()
