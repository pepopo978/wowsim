from _example_imports import *

mages = []

haste = 20
m = Mage(name=f'interrupt for s + r', sp=1000, crit=40, hit=16, haste=haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(
             extra_second_arcane_missile=True,
         ),
         equipped_items=EquippedItems(
             ornate_bloodstone_dagger=False,
             wrath_of_cenarius=True,
             endless_gulch=False,
             sigil_of_ancient_accord=True
         ))
m.arcane_surge_rupture_missiles(cds=CooldownUsages())
mages.append(m)

env = Environment(num_mobs=1, mob_level=63)
env.add_characters(mages)
env.run(until=180)
env.meter.detailed_report()
