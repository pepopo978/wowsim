from _example_imports import *

mages = []
num_mages = 1

for i in range(num_mages):
    fm = Mage(name=f'test', sp=1065, crit=47, hit=16, haste=0,
              tal=FireMageTalents(),
              opts=MageOptions(
                  zg_5_set=True
              ),
              equipped_items=EquippedItems(endless_gulch=False, true_band_of_sulfuras=False, unceasing_frost=False))
    fm.spam_flamestrike_r6_r5_r4(cds=CooldownUsages())
    mages.append(fm)

env = Environment(print_dots=True)
env.add_characters(mages)
env.run(until=180)
env.meter.detailed_report()
