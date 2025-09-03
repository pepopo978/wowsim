from sim.character import Character
from sim.cooldowns import WrathOfCenariusBuff, EndlessGulchBuff, TrueBandOfSulfurasBuff, BindingsOfContainedMagicBuff
from sim.env import Environment
from sim.equipped_items import EquippedItems
from sim.item_procs import *
from sim.spell import Spell, SPELL_COEFFICIENTS
from sim.spell_school import DamageType


class ItemProcHandler:
    def __init__(self, character: Character, env: Environment, equipped_items: EquippedItems):
        self.character = character
        self.env = env

        self.procs = []

        self.wrath_of_cenarius_buff = None
        self.endless_gulch_buff = None
        self.true_band_of_sulfuras_buff = None
        self.bindings_buff = None

        self.wisdom_of_the_makaru_stacks = 0

        if equipped_items:
            if equipped_items.blade_of_eternal_darkness:
                self.procs.append(BladeOfEternalDarkness(character, self._blade_of_eternal_darkness_proc))
            if equipped_items.ornate_bloodstone_dagger:
                self.procs.append(OrnateBloodstoneDagger(character, self._ornate_bloodstone_dagger_proc))
            if equipped_items.wrath_of_cenarius:
                self.wrath_of_cenarius_buff = WrathOfCenariusBuff(character)
                self.procs.append(WrathOfCenarius(character, self._wrath_of_cenarius_proc))
            if equipped_items.true_band_of_sulfuras:
                self.true_band_of_sulfuras_buff = TrueBandOfSulfurasBuff(character)
                self.procs.append(TrueBandOfSulfuras(character, self._true_band_of_sulfuras_proc))    
            if equipped_items.endless_gulch:
                self.endless_gulch_buff = EndlessGulchBuff(character)
                self.procs.append(EndlessGulch(character, self._endless_gulch_proc))
            if equipped_items.unceasing_frost:
                self.procs.append(UnceasingFrost(character, self._unceasing_frost_proc))
            if equipped_items.bindings_of_contained_magic:
                self.bindings_buff = BindingsOfContainedMagicBuff(character)
                self.procs.append(BindingsOfContainedMagic(character, self._bindings_proc))
            if equipped_items.sigil_of_ancient_accord:
                self.procs.append(SigilOfAncientAccord(character, self._sigil_of_ancient_accord_proc))                   


    def check_for_procs(self, current_time, spell: Spell, damage_type: DamageType):
        for proc in self.procs:
            proc.check_for_proc(current_time, self.env.num_mobs, spell, damage_type)

    def _tigger_proc_dmg(self, spell, min_dmg, max_dmg, damage_type):
        dmg = self.character.roll_spell_dmg(min_dmg, max_dmg, SPELL_COEFFICIENTS.get(spell, 0), damage_type)
        dmg = self.character.modify_dmg(dmg, damage_type, is_periodic=False)

        partial_amount = self.character.roll_partial(is_dot=False, is_binary=False)
        if partial_amount < 1:
            dmg = int(dmg * partial_amount)

        self.env.meter.register_proc_dmg(
            char_name=self.character.name,
            spell_name=spell.value,
            dmg=dmg,
            aoe=False)

    def _blade_of_eternal_darkness_proc(self):
        self._tigger_proc_dmg(Spell.ENGULFING_SHADOWS, 100, 100, DamageType.SHADOW)

    def _ornate_bloodstone_dagger_proc(self):
        self._tigger_proc_dmg(Spell.BURNING_HATRED, 250, 250, DamageType.FIRE)

    def _wrath_of_cenarius_proc(self):
        if self.wrath_of_cenarius_buff:
            self.wrath_of_cenarius_buff.activate()

    def _endless_gulch_proc(self):
        self.wisdom_of_the_makaru_stacks += 1
        self.character.print(f"Wisdom of the Makaru proc {self.wisdom_of_the_makaru_stacks}")
        if self.wisdom_of_the_makaru_stacks >= 10:
            self.wisdom_of_the_makaru_stacks = 0
            if self.endless_gulch_buff:
                self.endless_gulch_buff.activate()
                
    def _true_band_of_sulfuras_proc(self):
        if self.true_band_of_sulfuras_buff:
            self.true_band_of_sulfuras_buff.activate()                

    def _unceasing_frost_proc(self):
        self.env.debuffs.add_freezing_cold()

    def _bindings_proc(self):
        if self.bindings_buff:
            self.bindings_buff.activate()

    def _sigil_of_ancient_accord_proc(self):
        dmg = self.character.roll_spell_dmg(400, 400, SPELL_COEFFICIENTS.get(Spell.ANCIENT_ACCORD, 0),  DamageType.ARCANE)
        dmg = self.character.modify_dmg(dmg, DamageType.ARCANE, is_periodic=False)

        # roll crit
        if self.character._roll_crit(self.character.crit, DamageType.ARCANE):
            dmg *= 1.5

        partial_amount = self.character.roll_partial(is_dot=False, is_binary=False)
        if partial_amount < 1:
            dmg = int(dmg * partial_amount)

        self.env.meter.register_proc_dmg(
            char_name=self.character.name,
            spell_name=Spell.ANCIENT_ACCORD.value,
            dmg=dmg,
            aoe=False)

        additional_mobs = self.env.num_mobs - 1
        if additional_mobs > 0:
            extra_dmg = 100 * additional_mobs
            dmg = self.character.roll_spell_dmg(extra_dmg, extra_dmg, SPELL_COEFFICIENTS.get(Spell.ANCIENT_ACCORD_SPLASH, 0),
                                                DamageType.ARCANE)
            dmg = self.character.modify_dmg(dmg, DamageType.ARCANE, is_periodic=False)
            # roll crit
            if self.character._roll_crit(self.character.crit, DamageType.ARCANE):
                dmg *= 1.5

            partial_amount = self.character.roll_partial(is_dot=False, is_binary=False)
            if partial_amount < 1:
                dmg = int(dmg * partial_amount)

            self.env.meter.register_proc_dmg(
                char_name=self.character.name,
                spell_name=Spell.ANCIENT_ACCORD_SPLASH.value,
                dmg=dmg,
                aoe=False)
