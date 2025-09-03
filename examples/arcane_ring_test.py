from _example_imports import *

mages = []
num_mobs = 1

base_sp = 1000
base_crit = 40
base_hit = 16
base_haste = 5

cooldowns = CooldownUsages(mqg=5, arcane_power=5)

m = Mage(name=f'wrath_of_cenarius', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems(
             wrath_of_cenarius=True,
         ))
m.arcane_surge_rupture_missiles(cds=cooldowns)
mages.append(m)

m = Mage(name=f'meph ring', sp=base_sp + 29, crit=base_crit + 2, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems())
m.arcane_surge_rupture_missiles(cds=cooldowns)
mages.append(m)

m = Mage(name=f't3 ring', sp=base_sp + 30, crit=base_crit + 1, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems())

m.arcane_surge_rupture_missiles(cds=cooldowns)
mages.append(m)

m = Mage(name=f't3 ring arcane (ignoring hit)', sp=base_sp + 36, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=MageOptions(),
         equipped_items=EquippedItems())

m.arcane_surge_rupture_missiles(cds=cooldowns)
mages.append(m)


sim = Simulation(characters=mages, num_mobs=num_mobs)
sim.run(iterations=10000, duration=180, print_casts=False)
sim.detailed_report()
