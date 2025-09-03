from _example_imports import *

mages = []
num_rings = 2
num_mobs = 1

base_sp = 1000
base_crit = 40
base_hit = 16
base_haste = 5

cooldowns = CooldownUsages(mqg=5, arcane_power=5)

m = Mage(name=f'contained magic', sp=base_sp + 18, crit=base_crit + 1, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             bindings_of_contained_magic=True,
         ))
m.arcane_surge_rupture_missiles(cds=cooldowns)
mages.append(m)

m = Mage(name=f'soul harvestor', sp=base_sp + 26, crit=base_crit + 1, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
         ))
m.arcane_surge_rupture_missiles(cds=cooldowns)
mages.append(m)

sim = Simulation(characters=mages, num_mobs=num_mobs)
sim.run(iterations=10000, duration=120, print_casts=False)
sim.detailed_report()
