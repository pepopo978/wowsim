from dataclasses import dataclass
from sim.decorators import simequipped


@dataclass(kw_only=True)
class EquippedItems:
    blade_of_eternal_darkness: bool = simequipped("Blade of Eternal Darkness (10% chance for 100 dmg and mana)", default=False)
    ornate_bloodstone_dagger: bool = simequipped("Ornate Bloodstone Dagger (20% chance to do 250 fire dmg to target and self)", default=False)
    wrath_of_cenarius: bool = simequipped("Wrath of Cenarius (5% chance for 132 sp for 10s)", default=False)
    endless_gulch: bool = simequipped("Endless Gulch (20% chance to get stacks, at 8 stacks increase cast speed 20% for 10s)", default=False)
    true_band_of_sulfuras: bool = simequipped("True Band of Sulfuras (5% haste proc)", default=False)
    unceasing_frost: bool = simequipped("Unceasing Frost (+5% fire damage)", default=False)
    bindings_of_contained_magic: bool = simequipped("Bindings of Contained Magic (10% chance of 100sp for 6s)", default=False)
    sigil_of_ancient_accord: bool = simequipped("Sigil of Ancient Accord (8% chance for 400 arcane damage)", default=False)
    spellwoven_nobility_drape: bool = simequipped("Spellwoven Nobility Drape (10% chance for 150 intellect for 6s)", default=False)
