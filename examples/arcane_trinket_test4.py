from _example_imports import *

mages = []
num_mobs = 1

base_sp = 1036
base_crit = 40
base_hit = 16
base_haste = 9

opts = MageOptions(use_presence_of_mind_on_cd=False)

cooldowns = CooldownUsages()

fm = Mage(name=f'3/3 temporal_convergence', sp=base_sp, crit=base_crit, hit=base_hit, haste=base_haste,
          tal=MageTalents(
              arcane_focus=3,  # not looked at currently
              arcane_impact=3,
              arcane_rupture=True,
              temporal_convergence=3,
              arcane_instability=3,
              presence_of_mind=True,
              accelerated_arcana=True,
              arcane_potency=2,
              resonance_cascade=5,
              arcane_power=True,
              fire_blast_gcd=1.0,
              fire_blast_cooldown=6.5,
              ignite=True,
          ),
          opts=MageOptions(),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
              bindings_of_contained_magic=False,
          ))
fm.arcane_surge_rupture_missiles(cds=CooldownUsages())
mages.append(fm)
#
# fm = Mage(name=f'soul harvestor', sp=base_sp+26, crit=base_crit+1, hit=base_hit, haste=base_haste,
#           tal=ArcaneMageTalents(),
#           opts=MageOptions(),
#           equipped_items=EquippedItems(
#               ornate_bloodstone_dagger=False,
#               wrath_of_cenarius=True,
#           ))
# fm.arcane_surge_rupture_missiles(cds=CooldownUsages())
# mages.append(fm)

sim = Simulation(characters=mages, num_mobs=num_mobs)
sim.run(iterations=20000, duration=180, print_casts=False)
sim.detailed_report()
