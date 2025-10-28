from _example_imports import *

mages = []

haste = 10
m = Mage(name=f'normal', sp=1000, crit=40, hit=16, haste=haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(
             extra_second_arcane_missile=True,
             distance_from_mob=30,
         ),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             true_band_of_sulfuras=True,
             endless_gulch=False,
         ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, mqg=5))
mages.append(m)
#
# m = Mage(name=f'interrupt for r', sp=1000, crit=40, hit=16, haste=haste,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(
#              extra_second_arcane_missile=True,
#              interrupt_arcane_missiles_for_surge=False,
#          ),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages())
# mages.append(m)
#
# m = Mage(name=f'no interrupt', sp=1000, crit=40, hit=16, haste=haste,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(
#              extra_second_arcane_missile=True,
#              interrupt_arcane_missiles_for_surge=False,
#              interrupt_arcane_missiles_for_rupture=False,
#          ),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages())
# mages.append(m)

# m = Mage(name=f'eyestalk', sp=1000+41, crit=40+1, hit=16, haste=5,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(),
#          equipped_items=EquippedItems(
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages())
# mages.append(m)
#
# m = Mage(name=f'frostfire', sp=1000+23, crit=40 + .16, hit=16, haste=5+1,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(extra_second_arcane_missile=True),
#          equipped_items=EquippedItems(
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages())
# mages.append(m)
#
# m = Mage(name=f'boed', sp=905, crit=39, hit=16, haste=9,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(interrupt_arcane_missiles=False),
#          equipped_items=EquippedItems(
#              blade_of_eternal_darkness=True,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.spam_arcane_explosion(cds=CooldownUsages(arcane_power=5, mqg=5))
# mages.append(m)
#
# m = Mage(name=f'ornate', sp=905, crit=39, hit=16, haste=9,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(interrupt_arcane_missiles=False),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=True,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.spam_arcane_explosion(cds=CooldownUsages(arcane_power=5, mqg=5))
# mages.append(m)
#
# m = Mage(name=f'woc', sp=1000, crit=40, hit=16, haste=5,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, mqg=5))
# mages.append(m)
#
# m = Mage(name=f'sulfuras', sp=1020, crit=40, hit=16, haste=6,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=False,
#              endless_gulch=False,
#              true_band_of_sulfuras=True,
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, mqg=5))
# mages.append(m)
#
# m = Mage(name=f'felforged', sp=1029, crit=42, hit=16, haste=5,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=False,
#              endless_gulch=False,
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, mqg=5))
# mages.append(m)
#
# m = Mage(name=f'3 set arcane', sp=1000, crit=40, hit=16, haste=5,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(t35_arcane_3_set=True),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.spam_arcane_explosion(cds=CooldownUsages())
# mages.append(m)
#
# m = Mage(name=f'3 set regular', sp=1000, crit=40, hit=16, haste=5,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(t35_3_set=True),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#              unceasing_frost=True
#          ))
# m.spam_arcane_explosion(cds=CooldownUsages())
# mages.append(m)

# m = Mage(name=f'reos', sp=1000, crit=40, hit=16, haste=5,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(interrupt_arcane_missiles=False),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages(reos=20))
# mages.append(m)
#
# m = Mage(name=f'reos', sp=1000, crit=40, hit=16, haste=0,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(interrupt_arcane_missiles=False),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.arcane_missiles(cds=CooldownUsages())
# mages.append(m)
#
# m = Mage(name=f'double reos', sp=1040, crit=40, hit=16, haste=8,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(interrupt_arcane_missiles=True),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              endless_gulch=False,
#          ))
# m.arcane_surge_rupture_missiles(cds=CooldownUsages(arcane_power=5, reos=[5, 150]))
# mages.append(m)

sim = Simulation(characters=mages, num_mobs=1, mob_level=63)
sim.run(iterations=5000, duration=120, print_casts=False, use_multiprocessing=True)
sim.detailed_report()
