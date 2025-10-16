import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Tuple, Any, Optional  # For type hinting
from collections import defaultdict

# This can be adjusted or passed as an argument if needed
CONFIG_WINDOW_COMBO_WIDTH = 58  # Adjusted slightly from main window for internal layout
COOLDOWN_ENTRY_WIDTH = 25


class CharacterConfigWindow(tk.Toplevel):
    _default_name_counters = defaultdict(int)

    def __init__(self, parent, class_name, rotation_names, rotation_map, talent_specs,
                 options_info: List[Tuple[str, str, Any, Optional[str]]],  # options_info now includes spec
                 equipped_items_info, cooldown_usage_field_names: List[str],
                 save_callback,
                 edit_mode=False, character_data_to_edit=None):
        super().__init__(parent)
        self.transient(parent)  # Make it a dialog behavior
        self.grab_set()  # Modal behavior

        self.class_name = class_name
        self.rotation_names = rotation_names
        self.rotation_map = rotation_map  # Map of display name -> method name
        self.rotation_name_from_method = {v: k for k, v in rotation_map.items()}
        self.talent_specs = talent_specs
        self.options_info = options_info  # List of (name, desc, default, spec)
        self.equipped_items_info = equipped_items_info
        self.cooldown_usage_field_names = cooldown_usage_field_names
        self.save_callback = save_callback
        self.edit_mode = edit_mode
        self.character_data = character_data_to_edit if character_data_to_edit else {}
        self.edit_index = self.character_data.get('edit_index') if self.edit_mode else None

        title_prefix = "Edit" if self.edit_mode else "Configure"
        self.title(f"{title_prefix} {self.class_name}")
        self.geometry("600x750")  # Adjusted height for potentially more tabs

        # Common stats frame
        stats_frame = ttk.LabelFrame(self, text="Character Stats")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(stats_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        default_base_name = f"{self.class_name.lower()}"
        initial_name_value = self.character_data.get('name')

        if initial_name_value is None:
            if not self.edit_mode:
                CharacterConfigWindow._default_name_counters[self.class_name] += 1
                count = CharacterConfigWindow._default_name_counters[self.class_name]
                initial_name_value = f"{default_base_name}{count}"
            else:
                initial_name_value = default_base_name

        self.name_var = tk.StringVar(value=initial_name_value)
        ttk.Entry(stats_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(stats_frame, text="Spell Power:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sp_var = tk.IntVar(value=self.character_data.get('sp', 1000))
        ttk.Spinbox(stats_frame, textvariable=self.sp_var, from_=0, to=10000, increment=10, width=8).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(stats_frame, text="Crit:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.crit_var = tk.DoubleVar(value=self.character_data.get('crit', 35))
        ttk.Spinbox(stats_frame, textvariable=self.crit_var, from_=0, to=100, increment=1, width=8).grid(
            row=1, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(stats_frame, text="Hit:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.hit_var = tk.IntVar(value=self.character_data.get('hit', 10))
        ttk.Spinbox(stats_frame, textvariable=self.hit_var, from_=0, to=100, increment=1, width=8).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(stats_frame, text="Haste:").grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.haste_var = tk.DoubleVar(value=self.character_data.get('haste', 5))
        ttk.Spinbox(stats_frame, textvariable=self.haste_var, from_=0, to=100, increment=1, width=8).grid(
            row=2, column=3, sticky=tk.W, padx=5, pady=5)

        main_notebook = ttk.Notebook(self)
        main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        general_config_frame = ttk.Frame(main_notebook)
        main_notebook.add(general_config_frame, text="General Config")

        self.talents_var = tk.StringVar()
        self.rotation_var = tk.StringVar()
        self.options_vars = {}
        self.equipped_items_vars = {}
        self.cooldown_usages_vars = {}

        ttk.Label(general_config_frame, text="Talents:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        talents_combo = ttk.Combobox(general_config_frame, textvariable=self.talents_var,
                                     width=CONFIG_WINDOW_COMBO_WIDTH)
        talents_combo['values'] = self.talent_specs
        talents_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        initial_talent = self.character_data.get('talents')
        if initial_talent and initial_talent in self.talent_specs:
            self.talents_var.set(initial_talent)
        elif self.talent_specs:
            talents_combo.current(0)

        ttk.Label(general_config_frame, text="Rotation:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        rotation_combo = ttk.Combobox(general_config_frame, textvariable=self.rotation_var,
                                      width=CONFIG_WINDOW_COMBO_WIDTH)
        rotation_combo['values'] = self.rotation_names
        rotation_combo.grid(row=1, column=1, sticky=tk.W, columnspan=3, padx=5, pady=5)

        initial_rotation_method = self.character_data.get('rotation')
        if initial_rotation_method and initial_rotation_method in self.rotation_map.values():
            display_name = self.rotation_name_from_method.get(initial_rotation_method,
                                                              self.rotation_names[0] if self.rotation_names else "")
            self.rotation_var.set(display_name)
        elif self.rotation_names:
            rotation_combo.current(0)

        options_notebook = ttk.Notebook(main_notebook)
        main_notebook.add(options_notebook, text="Class Options")

        options_by_spec: Dict[str, List[Tuple[str, str, Any, Optional[str]]]] = defaultdict(list)
        for option_name, option_desc, default_value, spec_name in self.options_info:
            tab_name = spec_name if spec_name else "General"
            options_by_spec[tab_name].append((option_name, option_desc, default_value, spec_name))

        for spec_tab_name, spec_options in sorted(options_by_spec.items()):
            spec_frame = ttk.Frame(options_notebook)
            options_notebook.add(spec_frame, text=spec_tab_name)
            row_index = 0
            for option_name, option_desc, default_value, _ in spec_options:
                # Use character_data value if present, otherwise default_value
                option_value = self.character_data.get('options', {}).get(option_name, default_value)

                if isinstance(default_value, bool):
                    self.options_vars[option_name] = tk.BooleanVar(value=option_value)
                    ttk.Checkbutton(spec_frame, text=option_desc, variable=self.options_vars[option_name]).grid(
                        row=row_index, column=0, sticky=tk.W, columnspan=2, padx=5, pady=5)
                elif isinstance(default_value, int):
                    self.options_vars[option_name] = tk.IntVar(value=option_value)
                    ttk.Label(spec_frame, text=option_desc).grid(row=row_index, column=0, sticky=tk.W, padx=5, pady=5)
                    ttk.Spinbox(spec_frame, textvariable=self.options_vars[option_name], from_=-1000, to=1000,
                                increment=1, width=8).grid(
                        row=row_index, column=1, sticky=tk.W, padx=5, pady=5)
                elif isinstance(default_value, float):
                    self.options_vars[option_name] = tk.DoubleVar(value=option_value)
                    ttk.Label(spec_frame, text=option_desc).grid(row=row_index, column=0, sticky=tk.W, padx=5, pady=5)
                    ttk.Spinbox(spec_frame, textvariable=self.options_vars[option_name], from_=-1000.0, to=1000.0,
                                increment=0.1, width=8).grid(
                        row=row_index, column=1, sticky=tk.W, padx=5, pady=5)
                elif isinstance(default_value, str):
                    self.options_vars[option_name] = tk.StringVar(value=option_value)
                    ttk.Label(spec_frame, text=option_desc).grid(row=row_index, column=0, sticky=tk.W, padx=5, pady=5)
                    ttk.Entry(spec_frame, textvariable=self.options_vars[option_name], width=30).grid(
                        row=row_index, column=1, sticky=tk.W, columnspan=2, padx=5, pady=5)
                row_index += 1

        items_frame = ttk.Frame(main_notebook)
        main_notebook.add(items_frame, text="Equipped Items")
        for i, (item_name, item_desc, default_value) in enumerate(self.equipped_items_info):
            # Use character_data value if present, otherwise default_value
            item_value = self.character_data.get('equipped_items', {}).get(item_name, default_value)
            self.equipped_items_vars[item_name] = tk.BooleanVar(value=item_value)
            ttk.Checkbutton(items_frame, text=item_desc, variable=self.equipped_items_vars[item_name]).grid(
                row=i, column=0, sticky=tk.W, columnspan=2, padx=5, pady=5)

        cooldowns_frame = ttk.Frame(main_notebook)
        main_notebook.add(cooldowns_frame, text="Cooldown Usages")
        cooldown_row_index = 0

        # Always try to get cooldowns from character_data for pre-filling
        saved_cooldowns = self.character_data.get('cooldown_usages', {})
        for field_name in self.cooldown_usage_field_names:
            label_text = field_name.replace('_', ' ').title() + ":"
            ttk.Label(cooldowns_frame, text=label_text).grid(row=cooldown_row_index, column=0, sticky=tk.W, padx=5,
                                                             pady=2)
            initial_value_str = ""
            raw_val = saved_cooldowns.get(field_name)
            if raw_val is not None:
                if isinstance(raw_val, list):
                    initial_value_str = ", ".join(map(str, raw_val))
                else:
                    initial_value_str = str(raw_val)

            var = tk.StringVar(value=initial_value_str)
            self.cooldown_usages_vars[field_name] = var
            ttk.Entry(cooldowns_frame, textvariable=var, width=COOLDOWN_ENTRY_WIDTH).grid(row=cooldown_row_index,
                                                                                          column=1, sticky=tk.W, padx=5,
                                                                                          pady=2)
            cooldown_row_index += 1
        ttk.Label(cooldowns_frame,
                  text="Enter time(s) in seconds. For multiple uses, separate with commas (e.g., 5, 65.5).").grid(
            row=cooldown_row_index, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)

        button_text = "Update Character" if self.edit_mode else "Add Character"
        ttk.Button(self, text=button_text, command=self._on_save).pack(pady=10, padx=10, side=tk.BOTTOM, fill=tk.X)

    def _on_save(self):
        name = self.name_var.get()
        sp = self.sp_var.get()
        crit = self.crit_var.get()
        hit = self.hit_var.get()
        haste = self.haste_var.get()
        talents = self.talents_var.get()
        selected_rotation_display_name = self.rotation_var.get()
        rotation_method_name = self.rotation_map.get(selected_rotation_display_name, "")

        options_values = {k: v.get() for k, v in self.options_vars.items()}
        equipped_items_values = {k: v.get() for k, v in self.equipped_items_vars.items()}

        raw_cooldown_usages_values = {k: v.get() for k, v in self.cooldown_usages_vars.items()}
        cooldown_usages_values = {}
        for cd_name, val_str in raw_cooldown_usages_values.items():
            val_str_stripped = val_str.strip()
            if not val_str_stripped:
                cooldown_usages_values[cd_name] = None
                continue

            try:
                if ',' in val_str_stripped:
                    cooldown_usages_values[cd_name] = [float(x.strip()) for x in val_str_stripped.split(',')]
                else:
                    cooldown_usages_values[cd_name] = float(val_str_stripped)
            except ValueError:
                messagebox.showerror("Invalid Input",
                                     f"Invalid format for cooldown '{cd_name.replace('_', ' ').title()}': '{val_str}'. Please use numbers or comma-separated numbers.")
                return

        self.save_callback(
            self.class_name, name, sp, crit, hit, haste, talents, rotation_method_name,
            options_values, equipped_items_values, cooldown_usages_values,
            self,
            self.edit_mode,
            self.edit_index
        )
