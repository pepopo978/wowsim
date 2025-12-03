import random

from sim.spell import Spell
from sim.spell_school import DamageType


class ItemProc:
    PERCENT_CHANCE = 0
    COOLDOWN = 0
    PRINT_PROC = False
    PROC_CHANCE_AFFECTED_BY_ENEMIES_HIT = True  # currently most things do
    PROCS_FROM_RESONANCE_CASCADE = True  # it seems like most things do proc from it
    CAN_CRIT = False

    def __init__(self, character, callback):
        self.character = character
        self.callback = callback
        self.last_proc_time = 0

        self.proc_rolls = 0
        self.proc_successes = 0

    @property
    def name(self):
        return type(self).__name__

    def _roll_proc(self, spell: Spell, damage_type: DamageType):
        if random.randint(1, 100) <= self.PERCENT_CHANCE:
            return True

        return False

    def check_for_proc(self, current_time: int, num_mobs: int, spell: Spell, damage_type: DamageType, is_resonance_cascade: bool):
        if self.COOLDOWN and self.last_proc_time + self.COOLDOWN > current_time:
            return

        if is_resonance_cascade and not self.PROCS_FROM_RESONANCE_CASCADE:
            return

        # changed most procs to only roll once when hitting multiple enemies
        if num_mobs > 1 and not self.PROC_CHANCE_AFFECTED_BY_ENEMIES_HIT:
            num_mobs = 1

        self.proc_rolls += num_mobs

        # roll on every eligible mob
        for i in range(num_mobs):
            if self._roll_proc(spell, damage_type):
                self.proc_successes += 1

                self.last_proc_time = current_time
                if self.PRINT_PROC:
                    self.character.print(f"{self.name} triggered")
                self.callback(i)

                if self.COOLDOWN != 0:
                    return  # can't proc again until cooldown is up

class BladeOfEternalDarkness(ItemProc):
    PERCENT_CHANCE = 10
    PROCS_FROM_RESONANCE_CASCADE = True


class OrnateBloodstoneDagger(ItemProc):
    PERCENT_CHANCE = 20
    COOLDOWN = 1
    PROC_CHANCE_AFFECTED_BY_ENEMIES_HIT = False
    PROCS_FROM_RESONANCE_CASCADE = False


class WrathOfCenarius(ItemProc):
    PERCENT_CHANCE = 5

class EndlessGulch(ItemProc):
    PERCENT_CHANCE = 20
    COOLDOWN = 3

class UnceasingFrost(ItemProc):
    PERCENT_CHANCE = 10

class TrueBandOfSulfuras(ItemProc):
    PERCENT_CHANCE = 8
    PERCENT_CHANCE_FIRE = 12

    def _roll_proc(self, spell: Spell, damage_type: DamageType, num_mobs: int = 1):
        chance = self.PERCENT_CHANCE_FIRE if damage_type == DamageType.FIRE else self.PERCENT_CHANCE

        for _ in range(num_mobs):
            if random.randint(1, 100) <= chance:
                return True

        return False

class BindingsOfContainedMagic(ItemProc):
    PERCENT_CHANCE = 10
    COOLDOWN = 18  # 18-second ICD


class SigilOfAncientAccord(ItemProc):
    PERCENT_CHANCE = 8
    COOLDOWN = 2

class SpellwovenNobilityDrape(ItemProc):
    PERCENT_CHANCE = 10


class EmbraceOfTheWindSerpent(ItemProc):
    PERCENT_CHANCE = 15
    CAN_CRIT = True
    PRINT_PROC = True
