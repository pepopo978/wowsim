from dataclasses import dataclass

from sim.decorators import simtalent


@dataclass
class DruidTalents:
    imp_wrath: int = 0
    imp_moonfire: int = 0
    moonfury: int = 0
    vengeance: int = 0
    natures_grace: bool = 0
    imp_starfire: int = 0
    balance_of_all_things: float = 0
    eclipse: bool = 0


@simtalent("Balance (Default)")
class BalanceDruidTalents(DruidTalents):
    def __init__(self):
        super().__init__(
            imp_wrath=5,
            imp_moonfire=2,
            moonfury=3,
            vengeance=5,
            natures_grace=True,
            imp_starfire=3,
            balance_of_all_things=5,
            eclipse=True
        )
