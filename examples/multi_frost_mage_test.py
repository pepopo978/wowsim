from _example_imports import *

mages = []
num_mages = 3

for i in range(num_mages):
    if i == 0:
        fm = Mage(name=f'wc1', sp=1000, crit=40.43, hit=16,
                  tal=MageTalents(
                      piercing_ice=3,
                      frostbite=3,
                      ice_shards=5,
                      shatter=0,
                      winters_chill=4,
                      flash_freeze=2,
                      ice_barrier=True,
                      improved_cone_of_cold=3,
                      frost_nova_cooldown=21  # 2 points in improved frost nova
                  ),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True))
        fm.icicle_frostbolts(cds=CooldownUsages())
        mages.append(fm)
    if i == 1:
        fm = Mage(name=f'wc2', sp=1000, crit=40.43, hit=16,
                  tal=MageTalents(
                      piercing_ice=3,
                      frostbite=3,
                      ice_shards=5,
                      shatter=0,
                      winters_chill=4,
                      flash_freeze=2,
                      ice_barrier=True,
                      improved_cone_of_cold=3,
                      frost_nova_cooldown=21  # 2 points in improved frost nova
                  ),
                  opts=MageOptions(use_frostnova_for_icicles=True,
                                   start_with_ice_barrier=True))
        fm.icicle_frostbolts(cds=CooldownUsages())
        mages.append(fm)

    # if i == 1:
    #     fm = Mage(name=f'arcane explosion', sp=1000, crit=40.43, hit=16,
    #               tal=IcicleMageTalents(),
    #               opts=MageOptions(use_frostnova_for_icicles=True,
    #                                start_with_ice_barrier=True))
    #     fm.spam_arcane_explosion(cds=CooldownUsages())
    #     mages.append(fm)
    # elif i==2:
    #     fm = Mage(name=f'coc', sp=1000, crit=40.43, hit=16,
    #               tal=IcicleMageTalents(),
    #               opts=MageOptions(use_frostnova_for_icicles=True,
    #                                start_with_ice_barrier=True))
    #     fm.icicle_coc_frostbolts(cds=CooldownUsages())
    #     mages.append(fm)

sim = Simulation(characters=mages, num_mobs=1)
sim.run(iterations=5000, duration=120)
sim.detailed_report()
