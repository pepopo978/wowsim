from _example_imports import *

mages = []
num_mages = 1

for i in range(num_mages):
    fm = Mage(name=f'mage{i}', sp=1051, crit=33.17, hit=16,
              tal=IcicleMageTalents(),
              opts=MageOptions(
                  use_frostnova_for_icicles=True,
                  use_cold_snap_for_nova=True,
                  start_with_ice_barrier=True))
    fm.icicle_frostbolts()
    mages.append(fm)

env = Environment()
env.add_characters(mages)
env.run(until=180)
env.meter.report()
