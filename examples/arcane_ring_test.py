from _example_imports import *

mages = []
num_mobs = 1

base_sp = 1036
base_crit = 37.7
base_hit = 16
base_haste = 5

opts = MageOptions(use_presence_of_mind_on_cd=False)

cooldowns = CooldownUsages(arcane_power=0, mqg=0)

m = Mage(name=f'arcane crab', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
         tal=ArcaneMageTalents(),
         opts=opts,
         equipped_items=EquippedItems(
             wrath_of_cenarius=True,
             unceasing_frost=True,
         ))
m.arcane_rupture_missiles(cds=cooldowns)
mages.append(m)

# m = Mage(name=f'fire crab', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
#          tal=FireMageTalents(),
#          opts=opts,
#          equipped_items=EquippedItems(
#              unceasing_frost=True,
#              true_band_of_sulfuras=True,
#          ))
# m.smart_scorch_and_fireblast(cds=cooldowns)
# mages.append(m)

# m = Mage(name=f't3 ring', sp=base_sp + 30, crit=base_crit + 1, hit=base_hit, haste=base_haste,
#          tal=ArcaneMageTalents(),
#          opts=opts,
#          equipped_items=EquippedItems())
#
# m.arcane_surge_rupture_missiles(cds=cooldowns)
# mages.append(m)
#
# m = Mage(name=f't3 ring arcane (ignoring hit)', sp=base_sp + 36, crit=base_crit, hit=base_hit, haste=base_haste,
#          tal=ArcaneMageTalents(),
#          opts=opts,
#          equipped_items=EquippedItems())
#
# m.arcane_surge_rupture_missiles(cds=cooldowns)
# mages.append(m)


sim = Simulation(characters=mages, num_mobs=num_mobs)
sim.run(iterations=10000, duration=30, print_casts=False)
sim.detailed_report()
