from _example_imports import *

mages = []

fm = Mage(name=f'reg', sp=1000 + 30, crit=40.43 + 1, hit=16, haste=3,
          tal=FireMageTalents(),
          opts=MageOptions())
fm.smart_scorch_and_fireblast(CooldownUsages(combustion=10, mqg=10))
mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=10000, duration=120, print_casts=False)
sim.detailed_report()

mages = []
fm = Mage(name=f'sulfuras', sp=1000 + 20, crit=40.43, hit=16, haste=3 + 1,
          tal=FireMageTalents(),
          opts=MageOptions(extend_ignite_with_scorch=False),
          equipped_items=EquippedItems(true_band_of_sulfuras=True))
fm.smart_scorch_and_fireblast(CooldownUsages(combustion=10, mqg=10))
mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=10000, duration=120, print_casts=False)
sim.detailed_report()
