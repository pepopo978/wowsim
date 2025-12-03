from enum import Enum

from sim.arcane_dots import MoonfireDot
from sim.character import Character
from sim.fire_dots import PyroblastDot, FireballDot, ImmolateDot
from sim.ignite import Ignite
from sim.improved_shadow_bolt import ImprovedShadowBolt
from sim.item_procs import EmbraceOfTheWindSerpent
from sim.nature_dots import InsectSwarmDot
from sim.shadow_dots import CorruptionDot, CurseOfAgonyDot, SiphonLifeDot, FeastOfHakkarDot
from sim.spell_school import DamageType


class SharedDebuffNames(Enum):
    WINTERS_CHILL = "5 stack Winter's Chill"
    FIRE_VULNERABILITY = "5 stack Fire Vulnerability"
    FREEZING_COLD = "Freezing Cold"

class Debuffs:
    def __init__(self, env,
                 permanent_coe=True,
                 permanent_cos=True,
                 permanent_shadow_weaving=True,
                 permanent_isb=False,
                 permanent_nightfall=False,
                 ):
        self.env = env
        self.fire_vuln_stacks = 0
        self.fire_vuln_timer = 0
        self.permanent_coe = permanent_coe
        self.permanent_cos = permanent_cos
        self.permanent_nightfall = permanent_nightfall
        self.permanent_shadow_weaving = permanent_shadow_weaving
        self.permanent_isb = permanent_isb
        self.ticks = 0

        self.ignite = Ignite(env)
        self.improved_shadow_bolt = ImprovedShadowBolt(env, permanent_isb)

        self.wc_stacks = 0
        self.wc_timer = 0
        self.coe_timer = 0
        self.cos_timer = 0
        self.shadow_weaving_stacks = 0

        self.freezing_cold_timer = 0

        self.debuff_start_times = {}  # debuff_name -> start_time
        self.debuff_uptimes = {}  # debuff_name -> total_uptime

        # Dynamic dot storage - dot_class -> {(owner, target_index) -> Dot instance}
        self.dots = {}

        # Decaying Flesh tracking - (owner, target_index) -> stack_count
        self.decaying_flesh_stacks = {}

    def track_debuff_start(self, debuff_name):
        """Track when a debuff starts"""
        if debuff_name not in self.debuff_start_times:
            self.debuff_start_times[debuff_name] = self.env.now

    def track_debuff_end(self, debuff_name):
        """Track when a debuff ends and add to total uptime"""
        if debuff_name in self.debuff_start_times:
            if debuff_name not in self.debuff_uptimes:
                self.debuff_uptimes[debuff_name] = 0

            self.debuff_uptimes[debuff_name] += self.env.now - self.debuff_start_times[debuff_name]
            del self.debuff_start_times[debuff_name]

    def add_remaining_debuff_uptime(self):
        for debuff_name, start_time in self.debuff_start_times.items():
            if debuff_name not in self.debuff_uptimes:
                self.debuff_uptimes[debuff_name] = 0

            self.debuff_uptimes[debuff_name] += self.env.now - start_time

    @property
    def has_coe(self):
        return self.permanent_coe or self.coe_timer > 0

    @property
    def has_cos(self):
        return self.permanent_cos or self.cos_timer > 0

    @property
    def has_nightfall(self):
        return self.permanent_nightfall

    @property
    def has_freezing_cold(self):
        return self.freezing_cold_timer > 0

    def modify_dmg(self, character: Character, dmg: int, damage_type: DamageType, is_periodic: bool):
        debuffs = self.env.debuffs
        if debuffs.has_cos and damage_type in (DamageType.SHADOW, DamageType.ARCANE):
            dmg *= 1.1
        elif debuffs.has_coe and damage_type in (DamageType.FIRE, DamageType.FROST):
            dmg *= 1.1

        if damage_type == DamageType.FIRE:
            if self.fire_vuln_stacks:
                dmg *= 1 + self.fire_vuln_stacks * 0.03
            if self.freezing_cold_timer > 0:
                dmg *= 1.05

        if debuffs.has_nightfall:
            dmg *= 1.10

        if damage_type == DamageType.SHADOW:
            if self.shadow_weaving_stacks > 0:
                dmg *= 1 + self.shadow_weaving_stacks * 0.03

            if is_periodic:
                dmg = self.env.debuffs.improved_shadow_bolt.apply_to_dot(warlock=character, dmg=dmg)
            else:
                dmg = self.env.debuffs.improved_shadow_bolt.apply_to_spell(warlock=character, dmg=dmg)

        return dmg

    def add_fire_vuln(self):
        if self.fire_vuln_stacks == 4:
            self.track_debuff_start(SharedDebuffNames.FIRE_VULNERABILITY)

        self.fire_vuln_stacks = min(self.fire_vuln_stacks + 1, 5)
        self.fire_vuln_timer = 30

    def add_freezing_cold(self):
        if self.freezing_cold_timer <= 0:
            self.track_debuff_start(SharedDebuffNames.FREEZING_COLD)

        self.freezing_cold_timer = 10

    def add_winters_chill_stack(self):
        if self.wc_stacks == 4:
            self.track_debuff_start(SharedDebuffNames.WINTERS_CHILL)

        if self.wc_stacks < 5:
            self.env.p(f"{self.env.time()} - {SharedDebuffNames.WINTERS_CHILL} stack {self.wc_stacks + 1} added")

        self.wc_stacks = min(self.wc_stacks + 1, 5)
        self.wc_timer = 15

    def is_dot_active(self, dot_class, owner, target_index=0):
        """Generic method to check if a dot is active for a given owner and target"""
        if dot_class not in self.dots:
            return False
        key = (owner, target_index)
        return key in self.dots[dot_class] and self.dots[dot_class][key].is_active()

    def add_dot(self, dot_class, owner, cast_time=0, target_index=0):
        """Generic method to add a dot of any class"""
        if dot_class not in self.dots:
            self.dots[dot_class] = {}

        key = (owner, target_index)
        if key in self.dots[dot_class] and self.dots[dot_class][key].is_active():
            # refresh existing dot
            self.dots[dot_class][key].refresh(cast_time)
        else:
            # create new dot
            self.dots[dot_class][key] = dot_class(owner, self.env, cast_time)
            # start dot thread
            self.env.process(self.dots[dot_class][key].run())

    def get_dot_time_left(self, dot_class, owner, target_index=0):
        """Get remaining time on a dot in seconds"""
        if not self.is_dot_active(dot_class, owner, target_index):
            return 0

        key = (owner, target_index)
        dot = self.dots[dot_class][key]

        # Calculate time until next tick
        time_since_last_tick = self.env.now - dot.last_tick_time
        time_until_next_tick = dot.time_between_ticks - time_since_last_tick

        # Total time = time until next tick + time for remaining ticks after that
        remaining_ticks_after_next = max(0, dot.ticks_left - 1)
        total_time_left = time_until_next_tick + (remaining_ticks_after_next * dot.time_between_ticks)

        return max(0, total_time_left)

    def get_dot_ticks_left(self, dot_class, owner, target_index=0):
        """Get remaining ticks on a dot"""
        if not self.is_dot_active(dot_class, owner, target_index):
            return 0

        key = (owner, target_index)
        dot = self.dots[dot_class][key]
        return dot.ticks_left

    def add_decaying_flesh_stack(self, owner, target_index=0):
        """Add a stack of Decaying Flesh for a specific owner and target.
        When reaching 3 stacks, triggers Feast of Hakkar DoT and resets stacks."""
        key = (owner, target_index)

        # Get current stacks (default to 0)
        current_stacks = self.decaying_flesh_stacks.get(key, 0)

        # Increment stacks
        current_stacks += 1

        if EmbraceOfTheWindSerpent.PRINT_PROC:
            owner.print(f"Decaying Flesh stack {current_stacks} added on target {target_index}")

        if current_stacks >= 3:
            # Trigger Feast of Hakkar DoT
            if EmbraceOfTheWindSerpent.PRINT_PROC:
                owner.print(f"Triggering Feast of Hakkar on target {target_index}")

            # Clear Feast of Hakkar for all other players on this target
            self._clear_feast_of_hakkar_for_other_players(owner, target_index)

            # Add/refresh Feast of Hakkar for current player
            self.add_dot(FeastOfHakkarDot, owner, cast_time=0, target_index=target_index)

            # Reset stacks
            self.decaying_flesh_stacks[key] = 0
        else:
            # Update stacks
            self.decaying_flesh_stacks[key] = current_stacks

    def _clear_feast_of_hakkar_for_other_players(self, owner, target_index):
        """Clear Feast of Hakkar DoT for all players except the specified owner on the given target."""
        if FeastOfHakkarDot not in self.dots:
            return

        # Find all keys for this target_index with different owners
        keys_to_remove = []
        for key in self.dots[FeastOfHakkarDot].keys():
            key_owner, key_target_index = key
            if key_target_index == target_index and key_owner != owner:
                # Mark this DoT as expired by setting ticks to 0
                self.dots[FeastOfHakkarDot][key].ticks_left = 0
                keys_to_remove.append(key)
                if self.env.print_dots:
                    self.env.p(f"{self.env.time()} - ({key_owner.name}) Feast of Hakkar cleared from target {target_index}")

        # Clean up the cleared DoTs
        for key in keys_to_remove:
            del self.dots[FeastOfHakkarDot][key]

    def get_decaying_flesh_stacks(self, owner, target_index=0):
        """Get the current number of Decaying Flesh stacks for a specific owner and target."""
        key = (owner, target_index)
        return self.decaying_flesh_stacks.get(key, 0)

    def clear_decaying_flesh_stacks(self, owner, target_index=0):
        """Clear Decaying Flesh stacks for a specific owner and target."""
        key = (owner, target_index)
        if key in self.decaying_flesh_stacks:
            del self.decaying_flesh_stacks[key]

    # special case due to shared debuff
    def is_curse_of_shadows_active(self):
        return self.cos_timer > 0

    def add_curse_of_shadow_dot(self):
        self.cos_timer = 300

    def run(self):
        while True:
            yield self.env.timeout(1)

            self.ticks += 1

            if self.fire_vuln_stacks > 0:
                self.fire_vuln_timer = max(self.fire_vuln_timer - 1, 0)
                if self.fire_vuln_timer <= 0:
                    self.fire_vuln_stacks = 0
                    self.track_debuff_end(SharedDebuffNames.FIRE_VULNERABILITY)

            if self.wc_stacks > 0:
                self.wc_timer = max(self.wc_timer - 1, 0)
                if self.wc_timer <= 0:
                    self.wc_stacks = 0
                    self.track_debuff_end(SharedDebuffNames.WINTERS_CHILL)

            if self.freezing_cold_timer > 0:
                self.freezing_cold_timer = max(self.freezing_cold_timer - 1, 0)
                if self.freezing_cold_timer <= 0:
                    self.freezing_cold_timer = 0
                    self.env.debuffs.track_debuff_end(SharedDebuffNames.FREEZING_COLD)

            if self.permanent_shadow_weaving and self.shadow_weaving_stacks < 5:
                self.shadow_weaving_stacks = int(self.ticks / 3)

