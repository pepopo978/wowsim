from _example_imports import *

mages = []
num_trinkets = 9

base_sp = 1000
base_crit = 40
base_hit = 14
base_haste = 4

duration=120

fm = Mage(name=f'nothing', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages())
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'scythe', sp=base_sp + 40, crit=base_crit + 2, hit=base_hit + 2, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages())
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'reos', sp=base_sp + 40, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages(reos=12))
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'eye of dim', sp=base_sp, crit=base_crit + 3, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages())
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'gulch', sp=base_sp + 30, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems(endless_gulch=True))
fm.smart_scorch_and_fireblast(cds=CooldownUsages())
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'tear', sp=base_sp + 44, crit=base_crit, hit=base_hit + 2, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages())
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'toep', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages(toep=12))
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'mqg', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages(mqg=12))
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'mark of champ', sp=base_sp + 85, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages())
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'shard of nightmare', sp=base_sp + 36, crit=base_crit, hit=base_hit+1, haste=base_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages())
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'zandalarian', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
            tal=FireMageTalents(),
            opts=MageOptions(),
            equipped_items=EquippedItems())
fm.smart_scorch_and_fireblast(cds=CooldownUsages(zhc=12))
sim = Simulation(characters=[fm])
sim.run(iterations=20000, duration=duration, print_casts=False)
sim.detailed_report()
