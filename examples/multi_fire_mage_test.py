from _example_imports import *

# mages = []
#
# fm = Mage(name=f'regular', sp=1000, crit=40.43, hit=16, haste=3,
#           tal=FireMageTalents(),
#           opts=MageOptions(extend_ignite_with_scorch=True))
# fm.smart_scorch_and_fireblast(CooldownUsages(combustion=10, mqg=10))
# mages.append(fm)
#
# sim = Simulation(characters=mages)
# sim.run(iterations=10000, duration=120, print_casts=False)
# sim.detailed_report()

mages = []
fm = Mage(name=f'hot streak', sp=1000, crit=40.43, hit=16, haste=3,
          tal=MageTalents(
              ignite=5,
              fire_vuln=3,
              fire_power=5,
              critical_mass=0,  # generally counted in crit already, 2% per point
              hot_streak=2,
              incinerate_crit=0,
              fire_blast_cooldown=6.5,
              fire_blast_gcd=1
          ),
          opts=MageOptions(extend_ignite_with_scorch=False))
fm.smart_scorch_and_fireblast(CooldownUsages(combustion=10, mqg=10))
mages.append(fm)

fm = Mage(name=f'incinerate', sp=1000, crit=40.43, hit=16, haste=3,
          tal=MageTalents(
              ignite=5,
              fire_vuln=3,
              fire_power=5,
              critical_mass=0,  # generally counted in crit already, 2% per point
              hot_streak=0,
              incinerate_crit=4,
              fire_blast_cooldown=6.5,
              fire_blast_gcd=1
          ),
          opts=MageOptions(extend_ignite_with_scorch=False),
          equipped_items=EquippedItems(unceasing_frost=False))
fm.smart_scorch_and_fireblast(CooldownUsages(combustion=10, mqg=10))
mages.append(fm)


sim = Simulation(characters=mages)
sim.run(iterations=10000, duration=120, print_casts=False)
sim.detailed_report()
