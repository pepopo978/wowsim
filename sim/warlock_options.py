from dataclasses import dataclass
from sim.decorators import simoption

@dataclass(kw_only=True)
class WarlockOptions:
    distance_from_mob: int = simoption("Distance From Mob", default=25, spec=None)

    permanent_curse: bool = simoption("Assume curse is always up", default=True)
    firestone: bool = simoption("2% fire crit chance", default=False)
    crit_dmg_bonus_35: bool = simoption("10% crit damage bonus", default=False)
    doomcaller_coa_bonus_25: bool = simoption("5% more Curse of Agony dmg", default=False)
    doomcaller_dh_bonus_25: bool = simoption("The last tick of your Dark Harvest spell deals 400% damage", default=False)
    siphon_life_bonus_35: bool = simoption("50% more siphon", default=False)
    use_nightfall_as_affliction: bool = simoption("Use nightfall on shadow bolt as affliction", default=False)
    use_nightfall_as_fire: bool = simoption("Use nightfall on fire", default=False)
    eye_of_dormant_corruption: bool = simoption("Eye of Dormant Corruption - increases corruption duration by 3 sec", default=False)
