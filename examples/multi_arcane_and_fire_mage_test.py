from _example_imports import *

mages = [
]

arcane_extend_ignite_with_fire_blast=True

am = Mage(name=f'arcane 1', sp=1000, crit=40, hit=16, haste=0,
          tal=ArcaneMageTalents(),
          opts=MageOptions(t3_8_set=False, extra_second_arcane_missile=False, extend_ignite_with_fire_blast=arcane_extend_ignite_with_fire_blast),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
              endless_gulch=False,
          ))
am.damage_type_hit[DamageType.FIRE] = -6
am.arcane_surge_rupture_missiles(cds=CooldownUsages(mqg=5, arcane_power=5))
mages.append(am)

am = Mage(name=f'arcane 2', sp=1000, crit=40, hit=16, haste=0,
          tal=ArcaneMageTalents(),
          opts=MageOptions(t3_8_set=False, extra_second_arcane_missile=False, extend_ignite_with_fire_blast=arcane_extend_ignite_with_fire_blast),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
              endless_gulch=False,
          ))
am.damage_type_hit[DamageType.FIRE] = -6
am.arcane_surge_rupture_missiles(cds=CooldownUsages(mqg=5, arcane_power=5))
mages.append(am)

am = Mage(name=f'arcane 3', sp=1000, crit=40, hit=16, haste=0,
          tal=ArcaneMageTalents(),
          opts=MageOptions(t3_8_set=False, extra_second_arcane_missile=False, extend_ignite_with_fire_blast=arcane_extend_ignite_with_fire_blast),
          equipped_items=EquippedItems(
              ornate_bloodstone_dagger=False,
              wrath_of_cenarius=True,
              endless_gulch=False,
          ))
am.damage_type_hit[DamageType.FIRE] = -6
am.arcane_surge_rupture_missiles(cds=CooldownUsages(mqg=5, arcane_power=5))
mages.append(am)

fm = Mage(name=f'fire 1', sp=1000, crit=40, hit=16, haste=0,
          tal=FireMageTalents(),
            opts=MageOptions(t3_8_set=False, extra_second_arcane_missile=False),
          )
fm.smart_scorch(cds=CooldownUsages(mqg=5,combustion=5))
mages.append(fm)

sim = Simulation(characters=mages)
sim.run(iterations=10000, duration=120, print_casts=False)
sim.detailed_report()
