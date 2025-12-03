from _example_imports import *

mages = []
num_mobs = 1

base_sp = 1036
base_crit = 37.7
base_hit = 16
base_haste = 15

opts = MageOptions(use_presence_of_mind_on_cd=False)

cooldowns = CooldownUsages()

fm = Mage(name=f'contained', sp=base_sp + 18, crit=base_crit + 1, hit=base_hit, haste=base_haste,
          tal=ArcaneMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
              bindings_of_contained_magic=True,
          ))
fm.arcane_surge_rupture_missiles(cds=CooldownUsages())
mages.append(fm)

fm = Mage(name=f'soul harvestor', sp=base_sp+26, crit=base_crit+1, hit=base_hit, haste=base_haste,
          tal=ArcaneMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
          ))
fm.arcane_surge_rupture_missiles(cds=CooldownUsages())
mages.append(fm)

sim = Simulation(characters=mages, num_mobs=num_mobs)
sim.run(iterations=10000, duration=180, print_casts=False)
sim.detailed_report()
