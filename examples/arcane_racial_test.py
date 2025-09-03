from _example_imports import *

mages = []
num_mages = 6

base_sp = 1000
base_crit = 40
base_hit = 14

for i in range(num_mages):
    if i == 0:
        fm = Mage(name=f'gnome', sp=base_sp, crit=base_crit+0.4, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=0, mqg=0))
    elif i == 1:
        fm = Mage(name=f'undead', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(apply_undead_bonus=True),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=0, mqg=0))
    elif i == 2:
        fm = Mage(name=f'troll', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=0, mqg=0, berserking10=0))
    elif i == 3:
        fm = Mage(name=f'orc', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=0, mqg=0, blood_fury=0))
    elif i == 4:
        fm = Mage(name=f'human', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=0, mqg=0, perception=0))
    else:
        fm = Mage(name=f'no racial', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=ArcaneMageTalents(),
                  opts=MageOptions(),
                  equipped_items=EquippedItems(
                      ornate_bloodstone_dagger=False,
                      wrath_of_cenarius=True,
                  ))
        fm.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=10, mqg=10))

    mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=10000, duration=120, print_casts=False)
sim.detailed_report()
