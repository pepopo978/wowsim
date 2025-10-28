from typing import Dict

from sim import JUSTIFY


def _round(num):
    if num > 100:
        return round(num)
    elif num > 10:
        return round(num, 1)
    else:
        return round(num, 2)


def mean(sequence):
    if not sequence:
        return 0
    return _round(sum(sequence) / len(sequence))


def mean_percentage(sequence):
    if not sequence:
        return 0
    return _round(100 * sum(sequence) / len(sequence))


class DamageMeter:
    def __init__(self, env, num_mobs):
        self.env = env
        self.num_mobs = num_mobs

        self.character_dmg: Dict[str, int] = {}
        self.character_num_casts: Dict[str, Dict[str, int]] = {}
        self.character_num_ticks: Dict[str, Dict[str, int]] = {}
        self.character_spell_dmg: Dict[str, Dict[str, int]] = {}
        self.character_spell_cast_time: Dict[str, Dict[str, int]] = {}

        self.total_spell_dmg = 0
        self.total_dot_dmg = 0
        self.total_ignite_dmg = 0
        self.total_proc_dmg = 0

    def _register(self, char_name: str, spell_name: str, dmg: int, cast_time: float, aoe=False,
                  increment_cast=True, increment_tick=False):
        if aoe:
            dmg *= self.num_mobs

        if not char_name in self.character_dmg:
            self.character_dmg[char_name] = 0
        self.character_dmg[char_name] += dmg

        if not char_name in self.character_spell_dmg:
            self.character_spell_dmg[char_name] = {}
        if not spell_name in self.character_spell_dmg[char_name]:
            self.character_spell_dmg[char_name][spell_name] = 0
        self.character_spell_dmg[char_name][spell_name] += dmg

        if increment_cast:
            if not char_name in self.character_num_casts:
                self.character_num_casts[char_name] = {}
            if not spell_name in self.character_num_casts[char_name]:
                self.character_num_casts[char_name][spell_name] = 0
            self.character_num_casts[char_name][spell_name] += 1

        if increment_tick:
            if not char_name in self.character_num_ticks:
                self.character_num_ticks[char_name] = {}
            if not spell_name in self.character_num_ticks[char_name]:
                self.character_num_ticks[char_name][spell_name] = 0
            self.character_num_ticks[char_name][spell_name] += 1

        if cast_time:
            if not char_name in self.character_spell_cast_time:
                self.character_spell_cast_time[char_name] = {}
            if not spell_name in self.character_spell_cast_time[char_name]:
                self.character_spell_cast_time[char_name][spell_name] = 0
            self.character_spell_cast_time[char_name][spell_name] += cast_time

        return dmg

    def register_spell_dmg(self, char_name: str, spell_name: str, dmg: int,
                           cast_time: float, aoe=False, increment_cast=True):
        final_dmg = self._register(char_name, spell_name, dmg, cast_time, aoe, increment_cast)
        self.total_spell_dmg += final_dmg

    def register_proc_dmg(self, char_name: str, spell_name: str, dmg: int, aoe=False):
        final_dmg = self._register(char_name, spell_name, dmg, 0, aoe)
        self.total_proc_dmg += final_dmg

    def register_dot_cast(self, char_name: str, spell_name: str, cast_time: float):
        self._register(char_name, spell_name, 0, cast_time, aoe=False, increment_cast=True)

    def register_dot_dmg(self, char_name: str, spell_name: str, dmg: int, aoe=False, cast_time=0):
        final_dmg = self._register(char_name, spell_name, dmg, cast_time, aoe, increment_cast=False, increment_tick=True)
        self.total_dot_dmg += final_dmg

    def register_ignite_dmg(self, char_name: str, dmg: int, aoe=False, increment_cast=False):
        final_dmg = self._register(char_name, "ignite", dmg, 0, aoe, increment_cast=increment_cast)
        self.total_ignite_dmg += final_dmg

    def get_total_dmg(self):
        return self.total_spell_dmg + self.total_dot_dmg + self.total_ignite_dmg

    def raid_dmg(self):
        total_raid_dmg = sum(self.character_dmg.values())
        total_time = self.env.now
        return round(total_raid_dmg / total_time / len(self.character_dmg.keys()), 1)

    def report(self):
        total_time = self.env.now
        casts = {}
        for character in self.env.characters:
            casts[character.name] = sum(self.character_num_casts[character.name].values())

        for name, dps in self.dps().items():
            print(f"{name.ljust(JUSTIFY, ' ')}: {dps} dps in {casts[name]} casts")

        total_raid_dmg = sum(self.character_dmg.values())
        print(
            f"{'Average DPS'.ljust(JUSTIFY, ' ')}: {round(total_raid_dmg / total_time / len(self.character_dmg.keys()), 1)}")

        # Print rupture missile percentage for characters with missile_count > 0
        for character in self.env.characters:
            if hasattr(character, 'missile_count') and character.missile_count > 0:
                rupture_pct = round(100 * character.rupture_missile_count / character.missile_count, 1)
                print(f"{character.name.ljust(JUSTIFY, ' ')}: {rupture_pct}% missiles with rupture ({character.rupture_missile_count}/{character.missile_count})")

        self.env.debuffs.ignite.report()
        self.env.debuffs.improved_shadow_bolt.report()

    def detailed_report(self):
        self.report()
        print("**** Detailed report ****")
        # give detailed per spell report of number of casts, total damage, average damage, average cast time
        for char_name in self.character_dmg.keys():
            print(f"{char_name}:")
            total_char_dmg = self.character_dmg[char_name]
            for spell_name, num_casts in self.character_num_casts[char_name].items():
                total_dmg = 0
                percent_dmg = 0
                avg_dmg = 0
                avg_cast_time = 0
                avg_dps = 0

                if char_name in self.character_spell_dmg and spell_name in self.character_spell_dmg[char_name]:
                    total_dmg = round(self.character_spell_dmg[char_name][spell_name])
                    percent_dmg = round(100 * total_dmg / total_char_dmg, 1)
                    avg_dmg = mean([total_dmg / num_casts])

                if char_name in self.character_spell_cast_time and spell_name in self.character_spell_cast_time[
                    char_name]:
                    avg_cast_time = mean([self.character_spell_cast_time[char_name][spell_name] / num_casts])
                    avg_dps = _round(avg_dmg / avg_cast_time)

                if char_name in self.character_num_ticks and spell_name in self.character_num_ticks[char_name]:
                    num_ticks = self.character_num_ticks[char_name][spell_name]
                    stats = f"{num_casts} casts ({num_ticks} ticks)"
                else:
                    stats = f"{num_casts} casts"

                if total_dmg:
                    stats += f", {total_dmg} dmg ({percent_dmg}%), {avg_dmg} avg dmg"

                if avg_cast_time:
                    stats += f", {avg_cast_time} avg cast time"

                if avg_dps:
                    stats += f", {avg_dps} dps"

                print(
                    f"{spell_name.ljust(JUSTIFY, ' ')}: {stats}")

    def per_spell_data(self, char_name):
        per_spell_data = {}

        total_char_dmg = self.character_dmg[char_name]
        for spell_name, num_casts in self.character_num_casts[char_name].items():
            total_dmg = 0
            percent_dmg = 0
            avg_dmg = 0
            avg_cast_time = 0
            avg_dps = 0

            if char_name in self.character_spell_dmg and spell_name in self.character_spell_dmg[char_name]:
                total_dmg = round(self.character_spell_dmg[char_name][spell_name])
                percent_dmg = round(100 * total_dmg / total_char_dmg, 1)
                avg_dmg = mean([total_dmg / num_casts])

            if char_name in self.character_spell_cast_time and spell_name in self.character_spell_cast_time[char_name]:
                avg_cast_time = mean([self.character_spell_cast_time[char_name][spell_name] / num_casts])
                avg_dps = _round(avg_dmg / avg_cast_time)

            num_ticks = 0
            if char_name in self.character_num_ticks and spell_name in self.character_num_ticks[char_name]:
                num_ticks = self.character_num_ticks[char_name][spell_name]

            per_spell_data[spell_name] = {
                "num_casts": num_casts,
                "num_ticks": num_ticks,
                "total_dmg": total_dmg,
                "percent_dmg": percent_dmg,
                "avg_dmg": avg_dmg,
                "avg_cast_time": avg_cast_time,
                "avg_dps": avg_dps
            }

        return per_spell_data

    def dps(self):
        total_time = self.env.now
        dps = {}
        for name, dmg in self.character_dmg.items():
            dps[name] = round(dmg / total_time, 1)
        return dps

    def total_casts(self, char_name):
        return sum(self.character_num_casts[char_name].values())
