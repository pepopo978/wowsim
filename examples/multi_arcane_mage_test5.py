from _example_imports import *

mages = []

base_sp = 1000
base_crit = 40
base_hit = 16
haste = 5

# m = Mage(name=f'embrace', sp=base_sp, crit=base_crit, hit=base_hit, haste=haste,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(
#              extra_second_arcane_missile=True,
#          ),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              true_band_of_sulfuras=True,
#              endless_gulch=False,
#              spellwoven_nobility_drape=False,
#              embrace_of_the_wind_serpent=True,
#          ))
# m.spam_arcane_explosion(cds=CooldownUsages())
# mages.append(m)
#
# m = Mage(name=f'no embrace', sp=base_sp + 47, crit=base_crit + 1, hit=base_hit, haste=haste,
#          tal=ArcaneMageTalents(),
#          opts=MageOptions(
#              extra_second_arcane_missile=True,
#          ),
#          equipped_items=EquippedItems(
#              ornate_bloodstone_dagger=False,
#              wrath_of_cenarius=True,
#              true_band_of_sulfuras=True,
#              endless_gulch=False,
#          ))
# m.spam_arcane_explosion(cds=CooldownUsages())
# mages.append(m)

m = Mage(name=f'sigil', sp=base_sp, crit=base_crit, hit=base_hit, haste=haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(
             extra_second_arcane_missile=True,
         ),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             true_band_of_sulfuras=False,
             endless_gulch=False,
             spellwoven_nobility_drape=False,
             embrace_of_the_wind_serpent=False,
             sigil_of_ancient_accord=True,
         ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages())
mages.append(m)

m = Mage(name=f'80 sp', sp=base_sp + 80, crit=base_crit, hit=base_hit, haste=haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(
             extra_second_arcane_missile=True,
         ),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             true_band_of_sulfuras=False,
             endless_gulch=False,
             spellwoven_nobility_drape=False,
             embrace_of_the_wind_serpent=False,
         ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages())
mages.append(m)

sim = Simulation(characters=mages, num_mobs=1, mob_level=63, permanent_cos=False, permanent_isb=False, permanent_shadow_weaving=False)
sim.run(iterations=10000, duration=180, print_casts=False, use_multiprocessing=True)
sim.detailed_report()
