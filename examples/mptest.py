from _example_imports import *
import multiprocessing

mage1 = Mage(
    name='multiprocessing', 
    sp=0, 
    crit=0, 
    hit=0, 
    haste=0,
    opts=MageOptions(
        ),
    tal=IcicleMageTalents(),
    equipped_items=EquippedItems(
        )
)

mage1.icicle_frostbolts(
    cds=CooldownUsages(
        )
)

if __name__ == '__main__':
    sim = Simulation(
        characters=[mage1],
        permanent_coe=True,
        permanent_cos=True,
    )
    # Set num_processes='Auto' for CPU count, or specify a number like num_processes=8
    # chunk_size determines the iteration count in each chunk
    sim.run(
        iterations=500000,
        duration=120,
        num_processes='Auto',
        chunk_size=200
)
    sim.extremely_detailed_report()
