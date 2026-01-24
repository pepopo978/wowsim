from _example_imports import *

locks = []
#
lock = Warlock(name=f'affli', sp=1100, crit=10, haste=18, hit=6, creature_type_dmg_mod=2,
               tal=AfflictionLock(),
               opts=WarlockOptions(),
               equipped_items=EquippedItems(
                   wrath_of_cenarius=True,
               )
               )
lock.coa_corruption_siphon_harvest_drain()
locks.append(lock)

# lock = Warlock(name=f'SMRuin', sp=1035, crit=35, hit=13, tal=SMRuin(), opts=WarlockOptions(crit_dmg_bonus_35=True))
# lock.coa_corruption_siphon_shadowbolt()
# locks.append(lock)

# lock = Warlock(name=f'FireLock', sp=1005, crit=40, hit=10, tal=FireLock(), opts=WarlockOptions())
# lock.immo_conflag_soulfire_searing()
# locks.append(lock)

env = Environment(print_dots=True)
env.add_characters(locks)
env.run(until=180)
env.meter.detailed_report()
