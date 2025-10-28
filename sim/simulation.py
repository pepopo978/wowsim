import os
import time
import traceback
from collections import defaultdict
from concurrent.futures import TimeoutError
from copy import deepcopy
from typing import List, Union

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from loky import ProcessPoolExecutor
from tqdm import trange

from sim import JUSTIFY
from sim.character import Character
from sim.env import Environment
from sim.utils import mean, mean_percentage

# Multiprocessing worker initialization
worker_characters = None


def init_worker(characters):
    global worker_characters
    worker_characters = [deepcopy(c) for c in characters]


def run_simulation(args, chunk_range):
    try:
        characters = worker_characters
        chunk_results = {
            'dps': defaultdict(list),
            'casts': defaultdict(list),
            'per_spell_data': defaultdict(list),
            'buff_uptime': defaultdict(list),
            'debuff_uptime': defaultdict(float),
            'partial_resists': defaultdict(list),
            'resists': defaultdict(list),
            'missile_count': defaultdict(list),
            'rupture_missile_count': defaultdict(list),
            'total_spell_dmg': [],
            'total_dot_dmg': [],
            'total_ignite_dmg': [],
            'total_dmg': [],
            'avg_dps': [],
            'max_single_dps': [],
            'had_any_ignite': False,
            'had_any_isbs': False,
            '>=1 stack uptime': [],
            '>=2 stack uptime': [],
            '>=3 stack uptime': [],
            '>=4 stack uptime': [],
            '5 stack uptime': [],
            '1 stack ticks': [],
            '2 stack ticks': [],
            '3 stack ticks': [],
            '4 stack ticks': [],
            '5 stack ticks': [],
            'avg_tick': [],
            'num_ticks': [],
            'max_tick': [],
            'num_drops': [],
            'ISB uptime': [],
            'Total added dot dmg': [],
            'Total added spell dmg': [],
        }

        for i in chunk_range:
            env = Environment(
                print_casts=False,
                print_dots=False,
                permanent_coe=args['permanent_coe'],
                permanent_cos=args['permanent_cos'],
                permanent_shadow_weaving=args['permanent_shadow_weaving'],
                permanent_nightfall=args['permanent_nightfall'],
                permanent_isb=args['permanent_isb'],
                num_mobs=args['num_mobs'],
                mob_level=args['mob_level']
            )

            for character in characters:
                character.reset()

            env.add_characters(characters)
            env.run(until=args['duration'])

            dps_results = env.meter.dps()

            for character, mdps in dps_results.items():
                chunk_results['dps'][character].append(mdps)
                chunk_results['casts'][character].append(env.meter.total_casts(character))

            for character in characters:
                char_name = character.name
                chunk_results['partial_resists'][char_name].append(character.num_partials)
                chunk_results['resists'][char_name].append(character.num_resists)

                # Track missile counts if character has them
                if hasattr(character, 'missile_count'):
                    chunk_results['missile_count'][char_name].append(character.missile_count)
                    chunk_results['rupture_missile_count'][char_name].append(character.rupture_missile_count)

                if char_name not in chunk_results['per_spell_data']:
                    chunk_results['per_spell_data'][char_name] = env.meter.per_spell_data(char_name)
                else:
                    for spell_name, data in env.meter.per_spell_data(char_name).items():
                        if spell_name in chunk_results['per_spell_data'][char_name]:
                            for key, value in data.items():
                                chunk_results['per_spell_data'][char_name][spell_name][key] += value
                        else:
                            chunk_results['per_spell_data'][char_name][spell_name] = data

                if char_name not in chunk_results['buff_uptime']:
                    chunk_results['buff_uptime'][char_name] = character.buff_uptimes
                else:
                    for buff_name, buff_uptime in character.buff_uptimes.items():
                        if buff_name in chunk_results['buff_uptime'][char_name]:
                            chunk_results['buff_uptime'][char_name][buff_name] += buff_uptime
                        else:
                            chunk_results['buff_uptime'][char_name][buff_name] = buff_uptime

            for debuff_name, debuff_uptime in env.debuffs.debuff_uptimes.items():
                if debuff_name not in chunk_results['debuff_uptime']:
                    chunk_results['debuff_uptime'][debuff_name] = 0
                chunk_results['debuff_uptime'][debuff_name] += debuff_uptime

            chunk_results['total_spell_dmg'].append(env.meter.total_spell_dmg)
            chunk_results['total_dot_dmg'].append(env.meter.total_dot_dmg)
            chunk_results['total_ignite_dmg'].append(env.meter.total_ignite_dmg)
            chunk_results['total_dmg'].append(env.meter.get_total_dmg())
            chunk_results['avg_dps'].append(env.meter.raid_dmg())
            chunk_results['max_single_dps'].append(max(dps_results.values()))

            ignite = env.debuffs.ignite
            chunk_results['>=1 stack uptime'].append(ignite.uptime_gte_1_stack)
            chunk_results['>=2 stack uptime'].append(ignite.uptime_gte_2_stacks)
            chunk_results['>=3 stack uptime'].append(ignite.uptime_gte_3_stacks)
            chunk_results['>=4 stack uptime'].append(ignite.uptime_gte_4_stacks)
            chunk_results['5 stack uptime'].append(ignite.uptime_5_stacks)
            chunk_results['1 stack ticks'].append(ignite.num_1_stack_ticks)
            chunk_results['2 stack ticks'].append(ignite.num_2_stack_ticks)
            chunk_results['3 stack ticks'].append(ignite.num_3_stack_ticks)
            chunk_results['4 stack ticks'].append(ignite.num_4_stack_ticks)
            chunk_results['5 stack ticks'].append(ignite.num_5_stack_ticks)
            chunk_results['num_ticks'].append(ignite.num_ticks)
            chunk_results['avg_tick'].append(ignite.avg_tick)
            chunk_results['max_tick'].append(ignite.max_tick)
            chunk_results['num_drops'].append(ignite.num_drops)

            isb = env.debuffs.improved_shadow_bolt
            chunk_results['ISB uptime'].append(isb.uptime_percent)
            chunk_results['Total added dot dmg'].append(isb.total_added_dot_dmg)
            chunk_results['Total added spell dmg'].append(isb.total_added_spell_dmg)

            if ignite.had_any_ignites:
                chunk_results['had_any_ignite'] = True
            if isb.had_any_isbs:
                chunk_results['had_any_isbs'] = True

        return chunk_results
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc(), "chunk": chunk_range}


class Simulation:
    def __init__(self,
                 characters: List[Character] = None,
                 permanent_coe: bool = True,
                 permanent_cos: bool = True,
                 permanent_shadow_weaving: bool = True,
                 permanent_nightfall: bool = False,
                 permanent_isb: bool = False,
                 num_mobs: int = 1,
                 mob_level: int = 63):
        self.characters = characters or []
        self.permanent_coe = permanent_coe
        self.permanent_cos = permanent_cos
        self.permanent_shadow_weaving = permanent_shadow_weaving
        self.permanent_nightfall = permanent_nightfall
        self.permanent_isb = permanent_isb
        self.num_mobs = num_mobs
        self.mob_level = mob_level
        self.duration = 0
        self.results = None

    def run(self,
            iterations: int,
            duration: int,
            print_casts: bool = False,
            print_dots: bool = False,
            use_multiprocessing: bool = True,
            num_processes: Union[int, str] = 'Auto',
            chunk_size: int = 128):

        self.duration = duration

        if use_multiprocessing:
            if print_casts or print_dots:
                print("Warning: print_casts and print_dots are disabled when using multiprocessing.")
                print_casts = False
                print_dots = False

            start_time = time.time()

            if num_processes == 'Auto':
                num_cpu = os.cpu_count() or 1
                num_processes = max(1, num_cpu - 1)
            else:
                num_processes = max(1, num_processes)

            if num_processes > 8:
                print("Limiting number of processes to 8.")
                num_processes = 8

            chunks = []
            for start in range(0, iterations, chunk_size):
                end = min(start + chunk_size, iterations)
                chunks.append(range(start, end))

            total_chunks = len(chunks)
            print(f"Total chunks to process: {total_chunks} (using {num_processes} workers)")

            args = {
                'permanent_coe': self.permanent_coe,
                'permanent_cos': self.permanent_cos,
                'permanent_shadow_weaving': self.permanent_shadow_weaving,
                'permanent_nightfall': self.permanent_nightfall,
                'permanent_isb': self.permanent_isb,
                'num_mobs': self.num_mobs,
                'mob_level': self.mob_level,
                'duration': duration
            }

            completed = 0
            results = []
            with ProcessPoolExecutor(
                    max_workers=num_processes,
                    initializer=init_worker,
                    initargs=(self.characters,)
            ) as executor:
                try:
                    print("Starting simulation...")
                    futures = [executor.submit(run_simulation, args, chunk) for chunk in chunks]

                    for idx, future in enumerate(futures):
                        try:
                            result = future.result(timeout=10)
                            results.append(result)
                            completed += 1

                            if completed % 10 == 0 or completed == total_chunks:
                                print(f"Processed {completed}/{total_chunks} chunks", flush=True)

                        except TimeoutError:
                            print(f"\nTimeout on chunk {idx}! Terminating.")
                            for f in futures[idx + 1:]:
                                f.cancel()
                            raise RuntimeError(f"Chunk {idx} timed out after 10 seconds")
                        except Exception as e:
                            print(f"\nError in chunk {idx}: {str(e)}")
                            for f in futures[idx + 1:]:
                                f.cancel()
                            raise

                    print("\nAll chunks completed!")

                except Exception as e:
                    print(f"\nFatal error during processing: {str(e)}")
                    raise

            error_chunks = [r for r in results if 'error' in r]
            if error_chunks:
                error_msg = "\n".join(f"Chunk {ec['chunk']}: {ec['error']}\nStacktrace:\n{ec.get('traceback', 'No traceback available')}" for ec in error_chunks[:3])
                raise RuntimeError(f"Errors in chunks:\n{error_msg}")

            if len(results) != total_chunks:
                missing = total_chunks - len(results)
                raise RuntimeError(f"Missing {missing} chunks in results")

            self._merge_results(results)
            self.results['iterations'] = iterations

            end_time = time.time()
            total_time = end_time - start_time
            iterations_per_sec = iterations / total_time
            print(f"Total processing time: {total_time:.2f} seconds")
            print(f"Iterations per second: {iterations_per_sec:.2f}")

        else:
            self.results = {
                'iterations': iterations,
                'dps': defaultdict(list),
                'casts': defaultdict(list),
                'per_spell_data': defaultdict(list),
                'buff_uptime': defaultdict(list),
                'debuff_uptime': defaultdict(list),
                'partial_resists': defaultdict(list),
                'resists': defaultdict(list),
                'missile_count': defaultdict(list),
                'rupture_missile_count': defaultdict(list),
                'total_spell_dmg': [None] * iterations,
                'total_dot_dmg': [None] * iterations,
                'total_ignite_dmg': [None] * iterations,
                'total_dmg': [None] * iterations,
                'avg_dps': [None] * iterations,
                'max_single_dps': [None] * iterations,
                'had_any_ignite': False,
                'had_any_isbs': False,
                '>=1 stack uptime': [None] * iterations,
                '>=2 stack uptime': [None] * iterations,
                '>=3 stack uptime': [None] * iterations,
                '>=4 stack uptime': [None] * iterations,
                '5 stack uptime': [None] * iterations,
                '1 stack ticks': [None] * iterations,
                '2 stack ticks': [None] * iterations,
                '3 stack ticks': [None] * iterations,
                '4 stack ticks': [None] * iterations,
                '5 stack ticks': [None] * iterations,
                'avg_tick': [None] * iterations,
                'num_ticks': [None] * iterations,
                'max_tick': [None] * iterations,
                'num_drops': [None] * iterations,
                'ISB uptime': [None] * iterations,
                'Total added dot dmg': [None] * iterations,
                'Total added spell dmg': [None] * iterations,
            }

            for i in trange(iterations, ascii=True):
                env = Environment(print_casts=print_casts,
                                  print_dots=print_dots,
                                  permanent_coe=self.permanent_coe,
                                  permanent_cos=self.permanent_cos,
                                  permanent_shadow_weaving=self.permanent_shadow_weaving,
                                  permanent_nightfall=self.permanent_nightfall,
                                  permanent_isb=self.permanent_isb,
                                  num_mobs=self.num_mobs,
                                  mob_level=self.mob_level)

                for character in self.characters:
                    character.reset()

                env.add_characters(self.characters)

                env.run(until=duration)
                dps_results = env.meter.dps()
                for character, mdps in dps_results.items():
                    self.results['dps'][character].append(mdps)
                    self.results['casts'][character].append(env.meter.total_casts(character))

                for character in self.characters:
                    char_name = character.name
                    self.results['partial_resists'][char_name].append(character.num_partials)
                    self.results['resists'][char_name].append(character.num_resists)

                    # Track missile counts if character has them
                    if hasattr(character, 'missile_count'):
                        self.results['missile_count'][char_name].append(character.missile_count)
                        self.results['rupture_missile_count'][char_name].append(character.rupture_missile_count)

                    if char_name not in self.results['per_spell_data']:
                        self.results['per_spell_data'][char_name] = env.meter.per_spell_data(char_name)
                    else:
                        for spell_name, data in env.meter.per_spell_data(char_name).items():
                            if spell_name in self.results['per_spell_data'][char_name]:
                                for key, value in data.items():
                                    self.results['per_spell_data'][char_name][spell_name][key] += value
                            else:
                                self.results['per_spell_data'][char_name][spell_name] = data

                    if char_name not in self.results['buff_uptime']:
                        self.results['buff_uptime'][char_name] = character.buff_uptimes
                    else:
                        for buff_name, buff_uptime in character.buff_uptimes.items():
                            if buff_name in self.results['buff_uptime'][char_name]:
                                self.results['buff_uptime'][char_name][buff_name] += buff_uptime
                            else:
                                self.results['buff_uptime'][char_name][buff_name] = buff_uptime

                for debuff_name, debuff_uptime in env.debuffs.debuff_uptimes.items():
                    if debuff_name not in self.results['debuff_uptime']:
                        self.results['debuff_uptime'][debuff_name] = 0
                    self.results['debuff_uptime'][debuff_name] += debuff_uptime

                self.results['total_spell_dmg'][i] = env.meter.total_spell_dmg
                self.results['total_dot_dmg'][i] = env.meter.total_dot_dmg
                self.results['total_ignite_dmg'][i] = env.meter.total_ignite_dmg

                self.results['total_dmg'][i] = env.meter.get_total_dmg()
                self.results['avg_dps'][i] = env.meter.raid_dmg()
                self.results['max_single_dps'][i] = max(dps_results.values())

                ignite = env.debuffs.ignite
                self.results['>=1 stack uptime'][i] = ignite.uptime_gte_1_stack
                self.results['>=2 stack uptime'][i] = ignite.uptime_gte_2_stacks
                self.results['>=3 stack uptime'][i] = ignite.uptime_gte_3_stacks
                self.results['>=4 stack uptime'][i] = ignite.uptime_gte_4_stacks
                self.results['5 stack uptime'][i] = ignite.uptime_5_stacks
                self.results['1 stack ticks'][i] = ignite.num_1_stack_ticks
                self.results['2 stack ticks'][i] = ignite.num_2_stack_ticks
                self.results['3 stack ticks'][i] = ignite.num_3_stack_ticks
                self.results['4 stack ticks'][i] = ignite.num_4_stack_ticks
                self.results['5 stack ticks'][i] = ignite.num_5_stack_ticks
                self.results['num_ticks'][i] = ignite.num_ticks
                self.results['avg_tick'][i] = ignite.avg_tick
                self.results['max_tick'][i] = ignite.max_tick
                self.results['num_drops'][i] = ignite.num_drops

                isb = env.debuffs.improved_shadow_bolt
                self.results['ISB uptime'][i] = isb.uptime_percent
                self.results['Total added dot dmg'][i] = isb.total_added_dot_dmg
                self.results['Total added spell dmg'][i] = isb.total_added_spell_dmg

                if ignite.had_any_ignites:
                    self.results['had_any_ignite'] = True
                if isb.had_any_isbs:
                    self.results['had_any_isbs'] = True

    def _merge_results(self, results):
        merged = {
            'dps': defaultdict(list),
            'casts': defaultdict(list),
            'per_spell_data': defaultdict(lambda: defaultdict(lambda: defaultdict(int))),
            'buff_uptime': defaultdict(lambda: defaultdict(float)),
            'partial_resists': defaultdict(list),
            'resists': defaultdict(list),
            'missile_count': defaultdict(list),
            'rupture_missile_count': defaultdict(list),
            'total_spell_dmg': [],
            'total_dot_dmg': [],
            'total_ignite_dmg': [],
            'total_dmg': [],
            'avg_dps': [],
            'max_single_dps': [],
            'had_any_ignite': False,
            'had_any_isbs': False,
            '>=1 stack uptime': [],
            '>=2 stack uptime': [],
            '>=3 stack uptime': [],
            '>=4 stack uptime': [],
            '5 stack uptime': [],
            '1 stack ticks': [],
            '2 stack ticks': [],
            '3 stack ticks': [],
            '4 stack ticks': [],
            '5 stack ticks': [],
            'avg_tick': [],
            'num_ticks': [],
            'max_tick': [],
            'num_drops': [],
            'ISB uptime': [],
            'Total added dot dmg': [],
            'Total added spell dmg': [],
            'debuff_uptime': defaultdict(float),
        }

        for chunk in results:
            if 'error' in chunk:
                continue

            for key in [
                'total_spell_dmg', 'total_dot_dmg', 'total_ignite_dmg',
                'total_dmg', 'avg_dps', 'max_single_dps',
                '>=1 stack uptime', '>=2 stack uptime', '>=3 stack uptime',
                '>=4 stack uptime', '5 stack uptime', '1 stack ticks',
                '2 stack ticks', '3 stack ticks', '4 stack ticks', '5 stack ticks',
                'avg_tick', 'num_ticks', 'max_tick', 'num_drops', 'ISB uptime',
                'Total added dot dmg', 'Total added spell dmg'
            ]:
                if key in chunk:
                    merged[key].extend(chunk[key])

            merged['had_any_ignite'] |= chunk.get('had_any_ignite', False)
            merged['had_any_isbs'] |= chunk.get('had_any_isbs', False)

            for char in chunk['dps']:
                merged['dps'][char].extend(chunk['dps'][char])
                merged['casts'][char].extend(chunk['casts'][char])
                merged['partial_resists'][char].extend(chunk['partial_resists'][char])
                merged['resists'][char].extend(chunk['resists'][char])

                # Merge missile counts if they exist
                if char in chunk['missile_count']:
                    merged['missile_count'][char].extend(chunk['missile_count'][char])
                    merged['rupture_missile_count'][char].extend(chunk['rupture_missile_count'][char])

                if char in chunk['per_spell_data']:
                    for spell, data in chunk['per_spell_data'][char].items():
                        for metric, value in data.items():
                            merged['per_spell_data'][char][spell][metric] += value

                if char in chunk['buff_uptime']:
                    for buff, uptime in chunk['buff_uptime'][char].items():
                        merged['buff_uptime'][char][buff] += uptime

            # Merge debuff_uptime
            if 'debuff_uptime' in chunk:
                for debuff, uptime in chunk['debuff_uptime'].items():
                    merged['debuff_uptime'][debuff] += uptime

        self.results = merged

    def _justify(self, string):
        return string.ljust(JUSTIFY, ' ')

    def report(self, verbosity=1):
        chars_to_dps = {}

        if verbosity > 1:
            messages_to_dps = {}
            for char in self.results['dps']:
                mean_dps = mean(self.results['dps'][char])
                mean_casts = mean(self.results['casts'][char])
                label = f"{char} DPS Mean"
                msg = f"{self._justify(label)}: {mean_dps} in {mean_casts} casts"
                messages_to_dps[msg] = mean_dps
                chars_to_dps[char] = mean_dps

            sorted_by_dps = dict(sorted(messages_to_dps.items(), key=lambda item: item[1], reverse=True))
            for msg, dps in sorted_by_dps.items():
                print(msg)

        print(f"{self._justify('Total spell dmg')}: {mean(self.results['total_spell_dmg'])}")
        print(f"{self._justify('Total dot dmg')}: {mean(self.results['total_dot_dmg'])}")
        if self.results['had_any_ignite']:
            print(f"{self._justify('Total ignite dmg')}: {mean(self.results['total_ignite_dmg'])}")
        print(f"{self._justify('Total dmg')}: {mean(self.results['total_dmg'])}")

        print(f"{self._justify('Average char dps')}: {mean(self.results['avg_dps'])}")
        print(f"{self._justify('Highest single char dps')}: {max(self.results['max_single_dps'])}")

        if verbosity > 1:
            if self.results['had_any_ignite']:
                print(f"------ Ignite ------")
                if verbosity > 2:
                    print(
                        f"{self._justify('Average >=1 stack ignite uptime')}: {mean_percentage(self.results['>=1 stack uptime'])}%")
                    print(
                        f"{self._justify('Average >=2 stack ignite uptime')}: {mean_percentage(self.results['>=2 stack uptime'])}%")
                    print(
                        f"{self._justify('Average >=3 stack ignite uptime')}: {mean_percentage(self.results['>=3 stack uptime'])}%")
                    print(
                        f"{self._justify('Average >=4 stack ignite uptime')}: {mean_percentage(self.results['>=4 stack uptime'])}%")
                print(
                    f"{self._justify('Average   5 stack ignite uptime')}: {mean_percentage(self.results['5 stack uptime'])}%")
                if verbosity > 2:
                    print(f"{self._justify('Average   1 stack ticks')}: {mean(self.results['1 stack ticks'])}")
                    print(f"{self._justify('Average   2 stack ticks')}: {mean(self.results['2 stack ticks'])}")
                    print(f"{self._justify('Average   3 stack ticks')}: {mean(self.results['3 stack ticks'])}")
                    print(f"{self._justify('Average   4 stack ticks')}: {mean(self.results['4 stack ticks'])}")
                print(f"{self._justify('Average   5 stack ticks')}: {mean(self.results['5 stack ticks'])}")
                print(f"{self._justify('Average ignite tick')}: {mean(self.results['avg_tick'])}")
                print(f"{self._justify('Average num tick')}: {mean(self.results['num_ticks'])}")
                print(f"{self._justify('Average max tick')}: {mean(self.results['max_tick'])}")
                print(f"{self._justify('Average num drops')}: {mean(self.results['num_drops'])}")

        if verbosity > 1:
            if self.results['had_any_isbs']:
                print(f"------ ISB ------")
                print(f"{self._justify('ISB uptime')}: {mean(self.results['ISB uptime'])}%")
                print(f"{self._justify('Total added dot dmg')}: {mean(self.results['Total added dot dmg'])}")
                print(f"{self._justify('Total added spell dmg')}: {mean(self.results['Total added spell dmg'])}")

        if verbosity > 2:
            print(f"------ Per Spell Data ------")
            chars_sorted = sorted(self.results['dps'].keys(), key=lambda x: mean(self.results['dps'][x]), reverse=True)
            for char in chars_sorted:
                iterations = self.results['iterations']
                print(f"{char}:")
                for spell_name, data in self.results['per_spell_data'][char].items():
                    num_casts = round(data['num_casts'] / iterations, 1)
                    num_ticks = round(data['num_ticks'] / iterations, 1)
                    total_dmg = round(data['total_dmg'] / iterations)
                    percent_dmg = round(data['percent_dmg'] / iterations, 1)
                    avg_dmg = round(data['avg_dmg'] / iterations)
                    avg_cast_time = round(data['avg_cast_time'] / iterations, 2)
                    avg_dps = round(data['avg_dps'] / iterations)

                    if num_ticks > 0:
                        stats = f"{num_casts} casts ({num_ticks} ticks)"
                    else:
                        stats = f"{num_casts} casts"

                    if total_dmg:
                        stats += f", {total_dmg} dmg ({percent_dmg}%), {avg_dmg} avg dmg"
                    if avg_cast_time:
                        stats += f", {avg_cast_time} avg cast time"
                    if avg_dps:
                        stats += f", {avg_dps} dps"

                    print(f"    {spell_name.ljust(JUSTIFY, ' ')}: {stats}")

            print(f"------ Resists ------")
            for char in self.results['partial_resists']:
                label = f"{char} Partial Resists"
                print(f"{self._justify(label)}: {mean(self.results['partial_resists'][char])}")

            for char in self.results['resists']:
                label = f"{char} Resists"
                print(f"{self._justify(label)}: {mean(self.results['resists'][char])}")

            # Print missile statistics if any character has missile_count
            if self.results['missile_count']:
                print(f"------ Rupture Missile Statistics ------")
                for char in self.results['missile_count']:
                    total_missiles = sum(self.results['missile_count'][char])
                    total_rupture_missiles = sum(self.results['rupture_missile_count'][char])
                    avg_missiles = mean(self.results['missile_count'][char])
                    avg_rupture_missiles = mean(self.results['rupture_missile_count'][char])

                    if total_missiles > 0:
                        rupture_pct = round(100 * total_rupture_missiles / total_missiles, 1)
                        label = f"{char} % Missiles with Rupture"
                        print(f"{self._justify(label)}: {rupture_pct}%")

        if verbosity > 2:
            print(f"------ Buff Uptime ------")
            chars_sorted = sorted(self.results['dps'].keys(), key=lambda x: mean(self.results['dps'][x]), reverse=True)
            for char in chars_sorted:
                iterations = self.results['iterations']
                print(f"{char}:")
                for buff_name, total_uptime in self.results['buff_uptime'][char].items():
                    avg_uptime = round(total_uptime / iterations, 1)
                    avg_uptime_percent = round(100 * avg_uptime / self.duration, 1)
                    print(f"    {buff_name.ljust(JUSTIFY, ' ')}: {avg_uptime} sec ({avg_uptime_percent}%)")

            print(f"------ Debuff Uptime ------")
            for debuff_name, total_uptime in self.results['debuff_uptime'].items():
                avg_uptime = round(total_uptime / self.results['iterations'], 1)
                avg_uptime_percent = round(100 * avg_uptime / self.duration, 1)
                print(f"    {debuff_name.value.ljust(JUSTIFY, ' ')}: {avg_uptime} sec ({avg_uptime_percent}%)")

        if verbosity > 3:
            print(f"------ Advanced Stats ------")
            for char in self.results['dps']:
                label = f"{char} DPS standard deviation"
                print(f"{self._justify(label)}: {round(np.std(self.results['dps'][char]), 2)}")
                label = f"{char} DPS min"
                print(f"{self._justify(label)}: {np.min(self.results['dps'][char])}")
                label = f"{char} DPS 25th percentile"
                print(f"{self._justify(label)}: {np.percentile(self.results['dps'][char], 25)}")
                label = f"{char} DPS 50th percentile"
                print(f"{self._justify(label)}: {np.percentile(self.results['dps'][char], 50)}")
                label = f"{char} DPS 75th percentile"
                print(f"{self._justify(label)}: {np.percentile(self.results['dps'][char], 75)}")
                label = f"{char} DPS max"
                print(f"{self._justify(label)}: {np.max(self.results['dps'][char])}")

    def extended_report(self):
        self.report(verbosity=2)

    def detailed_report(self):
        self.report(verbosity=3)

    def extremely_detailed_report(self):
        self.report(verbosity=4)

    def histogram_report_individual(self):
        for char in self.results['dps']:
            fig = px.histogram(x=self.results['dps'][char], histnorm='probability density')
            fig.update_layout(title=f"DPS of {char}")
            fig.show()

    def histogram_report_overlay(self):
        fig = go.Figure()
        for char in self.results['dps']:
            fig.add_trace(go.Histogram(x=self.results['dps'][char], name=char))

        fig.update_layout(title=f"DPS Distributions", barmode='overlay')
        fig.update_traces(opacity=0.50)
        fig.show()
