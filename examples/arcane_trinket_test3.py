from _example_imports import *

mages = []
num_mobs = 1

base_sp = 1036
base_crit = 37.7
base_hit = 16
base_haste = 31.8

opts = MageOptions(use_presence_of_mind_on_cd=False)

cooldowns = CooldownUsages(arcane_power=[5, 120])

m = Mage(name=f'base', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=opts,
         equipped_items=EquippedItems(
             wrath_of_cenarius=True,
         ))
m.arcane_rupture_missiles(cds=cooldowns)
mages.append(m)

m = Mage(name=f'1 crit', sp=base_sp, crit=base_crit + 1, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=opts,
         equipped_items=EquippedItems(
             wrath_of_cenarius=True,
         ))
m.arcane_rupture_missiles(cds=cooldowns)
mages.append(m)

m = Mage(name=f'1 haste', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste + 1,
         tal=ArcaneMageTalents(),
         opts=opts,
         equipped_items=EquippedItems(
             wrath_of_cenarius=True,
         ))
m.arcane_rupture_missiles(cds=cooldowns)
mages.append(m)

m = Mage(name=f'20 sp', sp=base_sp + 20, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=opts,
         equipped_items=EquippedItems(
             wrath_of_cenarius=True,
         ))
m.arcane_rupture_missiles(cds=cooldowns)
mages.append(m)

sim = Simulation(characters=mages, num_mobs=num_mobs)
sim.run(iterations=10000, duration=180, print_casts=False)
sim.detailed_report()
