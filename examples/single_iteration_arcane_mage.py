from _example_imports import *

mages = []


base_sp = 1000
base_crit = 30
base_hit = 16

cooldowns = CooldownUsages()

m = Mage(name=f'test', sp=base_sp, crit=base_crit, hit=base_hit, haste=11,
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
         ))
m.arcane_rupture_missiles(cds=cooldowns)
mages.append(m)

env = Environment(num_mobs=1, mob_level=63)
env.add_characters(mages)
env.run(until=180)
env.meter.detailed_report()
