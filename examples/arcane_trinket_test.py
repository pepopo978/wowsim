from _example_imports import *

mages = []

base_sp = 1000
base_crit = 40
base_hit = 16
base_haste = 4


def set_rotation(mage: Mage, cds: CooldownUsages):
    mage.arcane_surge_rupture_missiles(cds=cds)


m = Mage(name=f'nothing', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
         ))
set_rotation(m, cds=CooldownUsages(arcane_power=5))
mages.append(m)

m = Mage(name=f'reos', sp=base_sp + 40, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
         ))
set_rotation(m, cds=CooldownUsages(arcane_power=5, reos=5))
mages.append(m)

m = Mage(name=f'charm_of_magic', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
         ))
set_rotation(m, cds=CooldownUsages(arcane_power=5, charm_of_magic=5))
mages.append(m)

m = Mage(name=f'eye of dim', sp=base_sp, crit=base_crit + 3, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
         ))
set_rotation(m, cds=CooldownUsages(arcane_power=5))
mages.append(m)

m = Mage(name=f'gulch', sp=base_sp + 30, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             endless_gulch=True,
         ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5))
mages.append(m)

m = Mage(name=f'tear', sp=base_sp + 44, crit=base_crit, hit=base_hit + 2, haste=base_haste,
          tal=ArcaneMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
          ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5))
mages.append(m)

m = Mage(name=f'toep', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=ArcaneMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
          ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, toep=5))
mages.append(m)

m = Mage(name=f'mqg', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
         ))
set_rotation(m, cds=CooldownUsages(arcane_power=5, mqg=5))
mages.append(m)

m = Mage(name=f'mark of champ', sp=base_sp + 85, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
         ))
set_rotation(m, cds=CooldownUsages(arcane_power=5))
mages.append(m)

m = Mage(name=f'sigil', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             sigil_of_ancient_accord=True,
         ))
set_rotation(m, cds=CooldownUsages(arcane_power=5))
mages.append(m)

m = Mage(name=f'shard of nightmare', sp=base_sp + 36, crit=base_crit, hit=base_hit + 1, haste=base_haste,
          tal=ArcaneMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
          ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5))
mages.append(m)

m = Mage(name=f'zandalarian', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=ArcaneMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
          ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, zhc=5))
mages.append(m)




# aoe test
# sim = Simulation(characters=mages, num_mobs=100, mob_level=60)
# sim.run(iterations=10000, duration=30, print_casts=False, use_multiprocessing=True)

# single target test
sim = Simulation(characters=mages, num_mobs=1, mob_level=63)
sim.run(iterations=10000, duration=120, print_casts=False, use_multiprocessing=True)
sim.detailed_report()
