from _example_imports import *

mages = []

base_sp = 1050
base_crit = 50
base_hit = 16
base_haste = 4


def sim(mages):
    for mage in mages:
        mage.smart_scorch_and_fireblast(CooldownUsages(combustion=10))
    sim = Simulation(characters=mages)
    sim.run(iterations=10000, duration=180, print_casts=False, use_multiprocessing=False)
    sim.detailed_report()

#
fm = Mage(name=f'frostfire', sp=base_sp + 30, crit=base_crit + 1.2, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(
          ))

m2 = Mage(name=f'mage2', sp=base_sp + 30, crit=base_crit + 1.2, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(
          ))
m3 = Mage(name=f'mage3', sp=base_sp + 30, crit=base_crit + 1.2, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(
          ))
sim([fm])

fm = Mage(name=f'crab ring', sp=base_sp + 15, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          equipped_items=EquippedItems(unceasing_frost=True),
          opts=MageOptions(
          ))
m2 = Mage(name=f'mage2', sp=base_sp + 30, crit=base_crit + 1.2, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(
          ))
m3 = Mage(name=f'mage3', sp=base_sp + 30, crit=base_crit + 1.2, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(
          ))
sim([fm])

# env = Environment()
# env.add_characters(mages)
# env.run(until=180)
# env.meter.detailed_report()
