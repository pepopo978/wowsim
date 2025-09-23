from dataclasses import dataclass
from sim.decorators import simoption

@dataclass(kw_only=True)
class MageOptions:
    fullt2: bool = simoption("Full T2 8-set bonus (10% instant cast chance on main spells)", default=False, spec=None)
    apply_undead_bonus: bool = simoption("Apply Undead Bonus (+2% damage vs undead)", default=False, spec=None)
    t35_3_set: bool = simoption("T3.5 3-set bonus 10% chance for aoe spells to deal 15% more dmg", default=False, spec=None)

    # Fire
    drop_suboptimal_ignites: bool = simoption("Drop suboptimal ignites (cast frostbolt to drop bad ignite)", default=False, spec="Fire")
    remaining_seconds_for_ignite_extend: int = simoption("Seconds remaining for ignite extension", default=3, spec="Fire")
    extend_ignite_with_fire_blast: bool = simoption("Extend ignite with Fire Blast", default=False, spec="Fire")
    extend_ignite_with_scorch: bool = simoption("Extend ignite with Scorch", default=False, spec="Fire")
    pyro_on_t2_proc: bool = simoption("Cast Pyroblast on T2 proc", default=True, spec="Fire")
    pyro_on_max_hot_streak: bool = simoption("Cast Pyroblast on max Hot Streak stacks", default=True, spec="Fire")
    zg_5_set: bool = simoption("ZG 5-set bonus -0.5 sec on Flamestrike", default=False, spec="Fire")

    # Frost
    frostbolt_rank: int = simoption("Frostbolt rank (11, 4, or 3)", default=11, spec="Frost")
    use_icicles_without_flash_freeze: bool = simoption("Use Icicles without Flash Freeze proc", default=False, spec="Frost")
    use_frostnova_for_icicles: bool = simoption("Use Frost Nova to proc Flash Freeze", default=True, spec="Frost")
    keep_ice_barrier_up: bool = simoption("Keep Ice Barrier up", default=True, spec="Frost")
    start_with_ice_barrier: bool = simoption("Start with Ice Barrier active", default=True, spec="Frost")
    starting_ice_barrier_duration: int = simoption("Starting Ice Barrier duration (seconds)", default=55, spec="Frost")
    use_cold_snap_for_nova: bool = simoption("Use Cold Snap to reset Frost Nova", default=True, spec="Frost")

    # Arcane
    use_presence_of_mind_on_cd: bool = simoption("Use Presence of Mind on cooldown", default=True, spec="Arcane")
    extra_second_arcane_missile: bool = simoption("Extra second on Arcane Missiles (effect on some belts)", default=False, spec="Arcane")
    interrupt_arcane_missiles_for_rupture: bool = simoption("Interrupt Arcane Missiles early for Rupture", default=True, spec="Arcane")
    interrupt_arcane_missiles_for_surge: bool = simoption("Interrupt Arcane Missiles early for Surge", default=True, spec="Arcane")
    interrupt_arcane_missiles_for_sulfuras_proc: bool = simoption("Interrupt Arcane Missiles early for Sulfuras haste proc", default=True, spec="Arcane")
    delay_when_interrupting_missiles: float = simoption("Delay when interrupting Arcane Missiles (seconds)", default=0.05, spec="Arcane")
    t3_8_set: bool = simoption("T3 8-set bonus (Arcane)", default=False, spec="Arcane")
    t35_arcane_3_set: bool = simoption("T3.5 3-set bonus 5% more resonance(Arcane)", default=False, spec="Arcane")
