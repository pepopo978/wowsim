from _example_imports import *

# mages = []
# fm = Mage(name=f'regular r6_r5', sp=1065, crit=47, hit=16, haste=3,
#           tal=FireMageTalents(),
#           opts=MageOptions(
#               zg_5_set=False
#           ),
#           equipped_items=EquippedItems(endless_gulch=False, true_band_of_sulfuras=False, unceasing_frost=False))
# fm.spam_flamestrike_r6_r5(cds=CooldownUsages())
# mages.append(fm)
#
# sim = Simulation(characters=mages, mob_level=62)
# sim.run(iterations=10000, duration=15, print_casts=False)
# sim.extremely_detailed_report()

mages = []
fm = Mage(name=f'zg set r6_r5', sp=956, crit=39, hit=16, haste=5,
          tal=FireMageTalents(),
          opts=MageOptions(
              zg_5_set=True
          ),
          equipped_items=EquippedItems(endless_gulch=False, true_band_of_sulfuras=False, unceasing_frost=False))
fm.spam_flamestrike_r6_r5(cds=CooldownUsages())
mages.append(fm)

sim = Simulation(characters=mages, mob_level=62)
sim.run(iterations=10000, duration=30, print_casts=False)
sim.extremely_detailed_report()

mages = []
fm = Mage(name=f'zg set r6', sp=956, crit=39, hit=16, haste=5,
          tal=FireMageTalents(),
          opts=MageOptions(
              zg_5_set=True
          ),
          equipped_items=EquippedItems(endless_gulch=False, true_band_of_sulfuras=False, unceasing_frost=False))
fm.spam_flamestrike_r6(cds=CooldownUsages())
mages.append(fm)

#
# fm = Mage(name=f'zg set r6_r5 3', sp=956, crit=39, hit=16, haste=5,
#           tal=FireMageTalents(),
#           opts=MageOptions(
#               zg_5_set=True
#           ),
#           equipped_items=EquippedItems(endless_gulch=False, true_band_of_sulfuras=False, unceasing_frost=False))
# fm.spam_flamestrike_r6_r5(cds=CooldownUsages())
# mages.append(fm)
#
# fm = Mage(name=f'zg set r6_r5 4', sp=956, crit=39, hit=16, haste=5,
#           tal=FireMageTalents(),
#           opts=MageOptions(
#               zg_5_set=True
#           ),
#           equipped_items=EquippedItems(endless_gulch=False, true_band_of_sulfuras=False, unceasing_frost=False))
# fm.spam_flamestrike_r6_r5(cds=CooldownUsages())
# mages.append(fm)

sim = Simulation(characters=mages, mob_level=62)
sim.run(iterations=10000, duration=30, print_casts=False)
sim.extremely_detailed_report()
