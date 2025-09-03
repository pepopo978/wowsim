from dataclasses import dataclass
from sim.decorators import simtalent

@dataclass(kw_only=True)
class WarlockTalents:
    # affliction
    suppression: int = 0  # 2% hit per point
    improved_corruption: int = 0  # -.3s cast time per point
    improved_curse_of_agony: int = 0  # 3/6/10% damage per point
    improved_drains: int = 0  # 5/10% increase on drain soul
    malediction: bool = False # curse applies agony at the same time
    nightfall: int = 0  # 2/4% chance per point
    rapid_deterioration: bool = False  # 6% affliction haste, haste reduces dot tick time and channel time.  not implementing 50% chance version
    soul_siphon: int = 0  # 2/4/6% drain soul/dark harvest dmg increase per effect on target
    shadow_mastery: int = 0  # 2/4/6/8/10% shadow damage

    # demonology
    improved_imp: int = 0  # 10% imp damage per point
    soul_entrapment: int = 0  # 2/4/6% increased dmg if no demon
    unholy_power: int = 0 # 5/10/15% demon dmg
    demonic_precision: int = 0  # 33/66/100% shared spell hit/crit with demon

    imp_sacrifice: bool = False  # 4% spell dmg
    succubus_sacrifice: bool = False  # 6% shadow dmg

    # TODO - implement these
    imp_master_demonologist: int = 0  # 3/6/9/12/15% reduced spell costs.
    voidwalker_master_demonologist: int = 0 # 2/4/6/8/10% reduced physical damage taken.
    succubus_master_demonologist: int = 0 # 2/4/6/8/10% increased all damage done.
    felhunter_master_demonologist: int = 0 # 0.2/0.4/0.6/0.8/1 increased all resistances per level.
    greater_demons_master_demonologist: int = 0 # 2/4/6/8/10% increased spell critical chance and 8/16/24/32/40% reduced healing taken.

    soul_link: int = 0 # 5% damage for you and demon

    # destruction
    improved_shadow_bolt: int = 0  # 4% shadow damage per point.  20% chance per point to apply on crit.  2% chance per point to apply on regular hit
    demonic_swiftness: int = 0  # reduce imp cast time by .3/.5 sec
    bane: int = 0  # -.1 sec shadowbolt/immolate and -.4 sec soul fire per point
    aftermath: int = 0  # 2/4/6 % immolate damage
    devastation: int = 0  # 1% destruction crit per point
    improved_searing_pain: int = 0  # 2% crit per point
    improved_soul_fire: int = 0  # 10% fire damage for 30 sec after soul fire
    improved_immolate: int = 0 # 4% immolate damage per point
    ruin: int = 0  # .5x crit mult
    emberstorm: int = 0  # 2% fire damage per point

@simtalent("Warlock - Affliction")
class AfflictionLock(WarlockTalents):
    def __init__(self):
        super().__init__(
            suppression=5,
            improved_corruption=5,
            improved_drains=2,
            improved_curse_of_agony=3,
            nightfall=2,
            rapid_deterioration=True,
            soul_siphon=3,
            shadow_mastery=5,
            malediction=True,
            soul_entrapment=3,
            succubus_sacrifice=True,
            improved_shadow_bolt=5,
        )

@simtalent("Warlock - SM/Ruin")
class SMRuin(WarlockTalents):
    def __init__(self):
        super().__init__(
            suppression=5,
            improved_corruption=5,
            improved_curse_of_agony=3,
            nightfall=2,
            rapid_deterioration=True,
            shadow_mastery=5,
            malediction=True,
            improved_shadow_bolt=5,
            bane=5,
            devastation=5,
            ruin=1,
            improved_searing_pain=2,
        )

@simtalent("Warlock - Fire")
class FireLock(WarlockTalents):
    def __init__(self):
        super().__init__(
            soul_entrapment=3,
            imp_sacrifice=True,
            improved_shadow_bolt=5,
            bane=5,
            aftermath=3,
            devastation=5,
            improved_searing_pain=5,
            improved_soul_fire=2,
            improved_immolate=5,
            ruin=1,
            emberstorm=5,
        )
