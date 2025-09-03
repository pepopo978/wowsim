from _example_imports import *

mages = []
num_mages = 1

for i in range(num_mages):
    fm = Mage(name=f'test', sp=1000, crit=35, hit=16,
              tal=FireMageTalents(),
              opts=MageOptions(
                  extend_ignite_with_scorch=True
              ),
              equipped_items=EquippedItems(endless_gulch=False, true_band_of_sulfuras=True, unceasing_frost=True))
    fm.smart_scorch_and_fireblast(cds=CooldownUsages(combustion=10, mqg=10))
    mages.append(fm)

env = Environment()
env.add_characters(mages)
env.run(until=180)
env.meter.detailed_report()
