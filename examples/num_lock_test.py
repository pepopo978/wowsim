from _example_imports import *

locks = []
#
# lock = Warlock(name=f'affli', sp=1005, crit=35, hit=10, tal=AfflictionLock(), opts=WarlockOptions())
# lock.coa_corruption_siphon_harvest_drain()
# locks.append(lock)

# lock = Warlock(name=f'affli 3 set nightfall', sp=1005, crit=35, hit=10,
#                tal=AfflictionLock(),
#                opts=WarlockOptions(siphon_life_bonus_35=True, use_nightfall_as_affliction=True))
# lock.coa_corruption_siphon_harvest_drain()
# locks.append(lock)

lock = Warlock(name=f'affli control', sp=1005, crit=35, hit=10,
               tal=AfflictionLock(),
               opts=WarlockOptions(siphon_life_bonus_35=False),
               equipped_items=EquippedItems(
                   wrath_of_cenarius=True,
               ))
lock.coa_corruption_siphon_harvest_drain()
locks.append(lock)

# lock = Warlock(name=f'SMRuin no siphon', sp=1005, crit=35, hit=10,
#                tal=SMRuin(),
#                opts=WarlockOptions())
# lock.coa_corruption_shadowbolt()
# locks.append(lock)
#
# lock = Warlock(name=f'SMRuin with siphon', sp=1005, crit=35, hit=10, tal=SMRuin(), opts=WarlockOptions())
# lock.coa_corruption_siphon_shadowbolt()
# locks.append(lock)

#
# lock = Warlock(name=f'FireLock', sp=1005, crit=40, hit=10, tal=FireLock(), opts=WarlockOptions())
# lock.immo_conflag_soulfire_searing()
# locks.append(lock)

sim = Simulation(characters=locks)
sim.run(iterations=10000, duration=180, use_multiprocessing=True)
sim.detailed_report()
