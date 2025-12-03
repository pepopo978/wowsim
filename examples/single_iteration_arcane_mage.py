from _example_imports import *

mages = []


base_sp = 1000
base_crit = 30
base_hit = 16

cooldowns = CooldownUsages()

m = Mage(name=f'test', sp=base_sp, crit=base_crit, hit=base_hit, haste=9,
         tal=ArcaneMageTalents(),
         opts=MageOptions(
             extra_second_arcane_missile=True,
             distance_from_mob=30,
         ),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=False,
             true_band_of_sulfuras=False,
             endless_gulch=False,
             spellwoven_nobility_drape=True,
             embrace_of_the_wind_serpent=True,
         ))
m.spam_arcane_explosion(cds=cooldowns)
mages.append(m)

env = Environment(num_mobs=3, mob_level=63, print_dots=True, permanent_isb=True)
env.add_characters(mages)
env.run(until=180)
env.meter.detailed_report()
