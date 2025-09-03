from _example_imports import *

mages = []
num_trinkets = 11

base_sp = 1000
base_crit = 40
base_hit = 14

for i in range(num_trinkets):
    fm = None
    if i == 0:
        fm = Mage(name=f'nothing', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())
        fm.icicle_frostbolts(cds=CooldownUsages())
    elif i == 1:
        fm = Mage(name=f'reos', sp=base_sp + 40, crit=base_crit, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages(reos=5))
    elif i == 2:
        fm = Mage(name=f'charm_of_magic', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages(charm_of_magic=5))
    elif i == 3:
        fm = Mage(name=f'eye of dim', sp=base_sp, crit=base_crit + 3, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages())
    elif i == 4:
        fm = Mage(name=f'gulch', sp=base_sp + 30, crit=base_crit, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems(endless_gulch=True))

        fm.icicle_frostbolts(cds=CooldownUsages())
    elif i == 5:
        fm = Mage(name=f'tear', sp=base_sp + 44, crit=base_crit, hit=base_hit + 2,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages())
    elif i == 6:
        fm = Mage(name=f'toep', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages(toep=5))
    elif i == 7:
        fm = Mage(name=f'mqg', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages(mqg=5))
    elif i == 8:
        fm = Mage(name=f'mark of champ', sp=base_sp + 85, crit=base_crit, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages())
    elif i == 9:
        fm = Mage(name=f'shard of nightmare', sp=base_sp + 36, crit=base_crit, hit=base_hit+1,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages())
    elif i == 10:
        fm = Mage(name=f'zandalarian hero charm', sp=base_sp, crit=base_crit, hit=base_hit,
                  tal=IcicleMageTalents(),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True),
                  equipped_items=EquippedItems())

        fm.icicle_frostbolts(cds=CooldownUsages(zhc=5))

    if fm:
        mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=10000, duration=120, print_casts=False)
sim.detailed_report()
