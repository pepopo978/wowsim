from _example_imports import *

control_sp = 300
control_crit = 18
control_hit = 13
control_haste = 3

cooldown_usages = CooldownUsages()

fm = Mage(name=f'control', sp=control_sp, crit=control_crit, hit=control_hit, haste=control_haste,
                  tal=FireMageTalents(),
                  opts=MageOptions(),
                  )
fm.smart_scorch_and_fireblast(cds=cooldown_usages)

sim = Simulation(characters=[fm])
sim.run(iterations=50000, duration=120, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'1 hit', sp=control_sp, crit=control_crit, hit=control_hit + 1, haste=control_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          )
fm.smart_scorch_and_fireblast(cds=cooldown_usages)

sim = Simulation(characters=[fm])
sim.run(iterations=50000, duration=120, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'1 crit', sp=control_sp, crit=control_crit + 1, hit=control_hit, haste=control_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          )
fm.smart_scorch_and_fireblast(cds=cooldown_usages)

sim = Simulation(characters=[fm])
sim.run(iterations=50000, duration=120, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'1 haste', sp=control_sp, crit=control_crit, hit=control_hit, haste=control_haste + 1,
          tal=FireMageTalents(),
          opts=MageOptions(),
          )
fm.smart_scorch_and_fireblast(cds=cooldown_usages)

sim = Simulation(characters=[fm])
sim.run(iterations=50000, duration=120, print_casts=False)
sim.detailed_report()

fm = Mage(name=f'20sp', sp=control_sp + 20, crit=control_crit, hit=control_hit, haste=control_haste,
          tal=FireMageTalents(),
          opts=MageOptions(),
          )
fm.smart_scorch_and_fireblast(cds=cooldown_usages)

sim = Simulation(characters=[fm])
sim.run(iterations=50000, duration=120, print_casts=False)
sim.detailed_report()
