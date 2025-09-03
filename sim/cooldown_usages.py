from dataclasses import dataclass
from typing import Optional, Union, List


@dataclass(kw_only=True)
class CooldownUsages:
    # Mage
    combustion: Optional[Union[float, List[float]]] = None
    arcane_power: Optional[Union[float, List[float]]] = None
    presence_of_mind: Optional[Union[float, List[float]]] = None

    # Consumables
    potion_of_quickness: Optional[Union[float, List[float]]] = None

    # Racials
    berserking15: Optional[Union[float, List[float]]] = None
    berserking10: Optional[Union[float, List[float]]] = None
    blood_fury: Optional[Union[float, List[float]]] = None
    perception: Optional[Union[float, List[float]]] = None

    # Trinkets
    charm_of_magic: Optional[Union[float, List[float]]] = None
    toep: Optional[Union[float, List[float]]] = None
    zhc: Optional[Union[float, List[float]]] = None
    mqg: Optional[Union[float, List[float]]] = None
    reos: Optional[Union[float, List[float]]] = None
