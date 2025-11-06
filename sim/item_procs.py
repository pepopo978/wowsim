import random

from sim.spell import Spell
from sim.spell_school import DamageType


class ItemProc:
    PERCENT_CHANCE = 0
    COOLDOWN = 0
    PRINT_PROC = False
    PROC_CHANCE_AFFECTED_BY_ENEMIES_HIT = False

    def __init__(self, character, callback):
        self.character = character
        self.callback = callback
        self.last_proc_time = 0

        self.proc_rolls = 0
        self.proc_successes = 0

    @property
    def name(self):
        return type(self).__name__

    def _roll_proc(self, spell: Spell, damage_type: DamageType, num_mobs: int = 1):
        for _ in range(num_mobs):
            if random.randint(1, 100) <= self.PERCENT_CHANCE:
                return True

        return False

    def check_for_proc(self, current_time: int, num_mobs: int, spell: Spell, damage_type: DamageType):
        if self.COOLDOWN and self.last_proc_time + self.COOLDOWN > current_time:
            return

        # changed most procs to only roll once when hitting multiple enemies
        if num_mobs > 1 and not self.PROC_CHANCE_AFFECTED_BY_ENEMIES_HIT:
            num_mobs = 1

        self.proc_rolls += num_mobs

        if self.COOLDOWN == 0:
            # roll on every mob
            for _ in range(num_mobs):
                if self._roll_proc(spell, damage_type, 1):
                    self.proc_successes += 1

                    self.last_proc_time = current_time
                    if self.PRINT_PROC:
                        self.character.print(f"{self.name} triggered")
                    self.callback()
        else:
            # only can proc once per spell due to cooldown
            if self._roll_proc(spell, damage_type, num_mobs):
                self.proc_successes += 1

                self.last_proc_time = current_time
                if self.PRINT_PROC:
                    self.character.print(f"{self.name} triggered")
                self.callback()


class BladeOfEternalDarkness(ItemProc):
    PERCENT_CHANCE = 10
    PROC_CHANCE_AFFECTED_BY_ENEMIES_HIT = True


class OrnateBloodstoneDagger(ItemProc):
    PERCENT_CHANCE = 20
    COOLDOWN = 1
    PRINT_PROC = False


class WrathOfCenarius(ItemProc):
    PERCENT_CHANCE = 5
    PROC_CHANCE_AFFECTED_BY_ENEMIES_HIT = True

class EndlessGulch(ItemProc):
    PERCENT_CHANCE = 20
    COOLDOWN = 3

class UnceasingFrost(ItemProc):
    PERCENT_CHANCE = 10
    PRINT_PROC = True

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
    PRINT_PROC = True

class SpellwovenNobilityDrape(ItemProc):
    PERCENT_CHANCE = 10
    PROC_CHANCE_AFFECTED_BY_ENEMIES_HIT = True
    PRINT_PROC = True
