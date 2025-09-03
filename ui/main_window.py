import io
import sys
import tkinter as tk
from dataclasses import fields as dataclass_fields
from tkinter import ttk, messagebox
import threading  # Added for running simulation in a separate thread
import inspect  # Added for inspecting function signatures
import copy  # Added for deepcopy

from sim.cooldown_usages import CooldownUsages
from sim.decorators import class_registry, get_options, get_equipped_items
from sim.env import Environment
from sim.equipped_items import EquippedItems
from ui.character_config_window import CharacterConfigWindow
from ui.character_list_view import CharacterListView
from ui.output_view import OutputView
from ui.simulation_controller import SimulationController
from ui.simulation_controls_view import SimulationControlsView

COMBO_WIDTH = 30


# Helper class for redirecting stdout to a Tkinter Text widget
class TextRedirector:
    def __init__(self, widget, root):
        self.widget = widget
        self.root = root  # To use root.after_idle

    def write(self, s):
        # Schedule the UI update to be run in the main Tkinter thread
        if self.widget.winfo_exists():  # Check if widget still exists
            self.root.after_idle(self._write_to_widget, s)

    def _write_to_widget(self, s):
        if self.widget.winfo_exists():  # Double check, as after_idle might run later
            self.widget.insert(tk.END, s)
            self.widget.see(tk.END)  # Auto-scroll

    def flush(self):
        # Tkinter Text widget doesn't really have a flush concept like a file.
        # We can call update_idletasks if immediate processing of pending writes is desired.
        if self.widget.winfo_exists():
            self.root.after_idle(self.widget.update_idletasks)


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Wowsim v1.1.0")
        self.root.geometry("800x750")

        self.characters = []

        # --- Top configuration frame for class selection ---
        config_frame = ttk.Frame(root, padding="10")
        config_frame.pack(fill=tk.X)

        self.class_frame = ttk.LabelFrame(config_frame, text="Class Configuration")
        self.class_frame.pack(fill=tk.X)
        ttk.Label(self.class_frame, text="Select Class:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_var = tk.StringVar()
        class_combo = ttk.Combobox(self.class_frame, textvariable=self.class_var, width=COMBO_WIDTH)
        class_combo['values'] = sorted(list(class_registry.keys()))
        class_combo.grid(row=0, column=1, sticky=tk.W)
        if class_combo['values']:
            class_combo.current(0)
        ttk.Button(self.class_frame, text="Add New Character",
                   command=lambda: self.open_character_config()).grid(row=0, column=2, padx=10)

        # --- Character List View ---
        character_list_container = ttk.Frame(root, padding="10")
        character_list_container.pack(fill=tk.BOTH, expand=True)
        self.character_list_view = CharacterListView(
            character_list_container,
            edit_callback=self._handle_edit_character,
            remove_callback=self._handle_remove_character,
            duplicate_callback=self._handle_duplicate_character  # Added duplicate_callback
        )

        # --- Simulation Controls View ---
        simulation_controls_container = ttk.Frame(root, padding="10")
        simulation_controls_container.pack(fill=tk.X)
        self.simulation_controls_view = SimulationControlsView(
            simulation_controls_container,
            run_simulation_callback=self._handle_run_simulation,
            run_single_simulation_callback=self._handle_run_single_simulation
        )

        # --- Output View ---
        self.output_view = OutputView(self.root)
        # self.output_text is now self.output_view.get_text_widget()

    def get_rotation_names(self, class_name):
        entry = class_registry.get(class_name, {})
        rotations = entry.get("rotations", [])
        return [name for name, _ in rotations]

    def get_rotation_method_names(self, class_name):
        entry = class_registry.get(class_name, {})
        rotations = entry.get("rotations", [])
        return [method for _, method in rotations]

    def get_talent_specs(self, class_name):
        entry = class_registry.get(class_name, {})
        talents = entry.get("talents", {})
        return list(talents.keys())

    def _handle_edit_character(self, character_index):
        if character_index is None or character_index >= len(self.characters):
            messagebox.showwarning("Error", "Invalid character selection for editing.")
            return
        character_data = self.characters[character_index]
        self.open_character_config(
            edit_mode=True,
            edit_index=character_index,
            character_data=character_data
        )

    def _handle_duplicate_character(self, character_index):
        if character_index is None or character_index >= len(self.characters):
            messagebox.showwarning("Error", "Invalid character selection for duplication.")
            return

        original_character_data = self.characters[character_index]
        # Create a deep copy to ensure nested dictionaries/lists are also copied
        duplicated_character_data = copy.deepcopy(original_character_data)

        # Set name to None so CharacterConfigWindow generates a new one
        duplicated_character_data['name'] = None

        # Remove edit_index if it exists, as this is a new character
        if 'edit_index' in duplicated_character_data:
            del duplicated_character_data['edit_index']

        self.open_character_config(
            edit_mode=False,  # It's a new character, not editing an existing one
            character_data=duplicated_character_data  # Pass the copied data
        )

    def open_character_config(self, edit_mode=False, edit_index=None, character_data=None):
        # If character_data is provided (e.g., for duplication), use its class type.
        # Otherwise, use the selected class from the combobox for a brand new character.
        current_class_name = None
        if character_data and 'type' in character_data:
            current_class_name = character_data['type']
        elif edit_mode and character_data:  # Fallback for edit mode if type somehow missing but char_data present
            current_class_name = character_data.get('type', self.class_var.get())
        else:  # For brand new character or if no character_data provided
            current_class_name = self.class_var.get()

        if not current_class_name:
            messagebox.showerror("Error", "Please select a class or ensure character data is valid.")
            return

        rotation_names = self.get_rotation_names(current_class_name)
        rotation_methods = self.get_rotation_method_names(current_class_name)
        rotation_map = dict(zip(rotation_names, rotation_methods))
        talent_specs = self.get_talent_specs(current_class_name)
        options_info = get_options(current_class_name)
        equipped_items_info = get_equipped_items(EquippedItems)
        cooldown_usage_field_names = [field.name for field in dataclass_fields(CooldownUsages)]

        config_data_to_pass = None
        if character_data:  # For both edit mode and duplication (new char with prefill)
            config_data_to_pass = copy.deepcopy(character_data)  # Use a copy
            if edit_mode and edit_index is not None:
                config_data_to_pass['edit_index'] = edit_index
            elif 'edit_index' in config_data_to_pass:  # Ensure no old edit_index for duplicated char
                del config_data_to_pass['edit_index']

        CharacterConfigWindow(
            parent=self.root,
            class_name=current_class_name,
            rotation_names=rotation_names,
            rotation_map=rotation_map,
            talent_specs=talent_specs,
            options_info=options_info,
            equipped_items_info=equipped_items_info,
            cooldown_usage_field_names=cooldown_usage_field_names,
            save_callback=self.add_or_update_character,
            edit_mode=edit_mode,
            character_data_to_edit=config_data_to_pass  # Pass the prepared data
        )

    def add_or_update_character(self, class_type, name, sp, crit, hit, haste, talents, rotation_method_name,
                                options_values, equipped_items_values, cooldown_usages_values,
                                window_to_destroy,
                                edit_mode=False, edit_index=None):
        character = {
            'type': class_type,
            'name': name,
            'sp': sp,
            'crit': crit,
            'hit': hit,
            'haste': haste,
            'talents': talents,
            'rotation': rotation_method_name,
            'options': options_values,
            'equipped_items': equipped_items_values,
            'cooldown_usages': cooldown_usages_values
        }

        equipped_count = sum(1 for v in character['equipped_items'].values() if v)
        char_display = f"{name} ({class_type}) - SP: {sp}, Crit: {crit}%, Hit: {hit}%, Haste: {haste}% - Items: {equipped_count}"

        if edit_mode and edit_index is not None and 0 <= edit_index < len(self.characters):
            self.characters[edit_index] = character
            self.character_list_view.update_item(edit_index, char_display)
        else:  # New character (either from "Add New" or "Duplicate")
            self.characters.append(character)
            self.character_list_view.add_item(char_display)
            # Select the newly added item
            new_index = len(self.characters) - 1
            self.character_list_view.set_selection(new_index)

        window_to_destroy.destroy()

    def _handle_remove_character(self, character_index):
        if character_index is None or not (0 <= character_index < len(self.characters)):
            messagebox.showwarning("Error", "Invalid character selection for removal.")
            return

        # Confirmation dialog
        char_to_remove_name = self.characters[character_index].get('name', 'Unknown Character')
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove '{char_to_remove_name}'?"
        )
        if not confirm:
            return

        self.characters.pop(character_index)
        self.character_list_view.remove_item_at_index(character_index)

        # Optionally, select the previous item or clear selection
        if self.characters:
            new_selection_index = max(0, character_index - 1)
            if new_selection_index < len(self.characters):  # Check if list is not empty after pop
                self.character_list_view.set_selection(new_selection_index)
        # else: list is empty, no selection needed

    def _handle_run_simulation(self, iterations, duration, use_multiprocessing):
        if not self.characters:
            self.output_view.clear()
            self.output_view.append("Error: No characters added to simulation.\n")
            return

        self.output_view.clear()
        # self.output_view.append("Preparing characters for simulation...\n") # Optional

        sim_characters = []
        for char_data in self.characters:
            try:
                class_name = char_data['type']
                registry_entry = class_registry.get(class_name)
                if not registry_entry:
                    self.output_view.append(
                        f"Error: Class '{class_name}' not found in registry for character '{char_data.get('name', 'Unnamed')}'. Skipping.\n")
                    continue

                char_class_info = registry_entry.get('cls')
                if not char_class_info:
                    self.output_view.append(
                        f"Error: Misconfigured registry for class '{class_name}'. Missing 'cls' for character '{char_data.get('name', 'Unnamed')}'. Skipping.\n")
                    continue

                actual_options_cls = registry_entry.get("options_cls")
                options_obj = None
                if actual_options_cls:
                    if hasattr(actual_options_cls, '__dataclass_fields__'):
                        valid_option_keys = {f.name for f in dataclass_fields(actual_options_cls)}
                        user_provided_options = char_data.get('options', {})
                        filtered_options_data = {k: v for k, v in user_provided_options.items() if
                                                 k in valid_option_keys}
                        try:
                            options_obj = actual_options_cls(**filtered_options_data)
                        except TypeError as e:
                            self.output_view.append(
                                f"Error: Could not instantiate options for class '{class_name}' "
                                f"using {actual_options_cls.__name__} with data {filtered_options_data} "
                                f"for character '{char_data.get('name', 'Unnamed')}'. Details: {e}. Skipping character.\n"
                            )
                            continue
                    else:
                        self.output_view.append(
                            f"Warning: Registered options_cls for '{class_name}' ({actual_options_cls.__name__}) is not a dataclass. "
                            f"Options will not be applied for character '{char_data.get('name', 'Unnamed')}'.\n"
                        )
                elif registry_entry.get("cls"):  # Check if class itself exists, even if no options_cls
                    self.output_view.append(
                        f"Info: No options_cls found in registry for class '{class_name}'. "
                        f"Proceeding without class-specific options for character '{char_data.get('name', 'Unnamed')}'.\n"
                    )

                talent_specs_dict = registry_entry.get('talents', {})
                talent_spec_name = char_data.get('talents')
                talent_class_for_spec = talent_specs_dict.get(talent_spec_name) if talent_spec_name else None

                talent_instance = None
                if talent_class_for_spec:
                    try:
                        talent_instance = talent_class_for_spec()
                    except Exception as e:
                        self.output_view.append(
                            f"Error: Could not instantiate talent spec '{talent_spec_name}' "
                            f"for class '{class_name}' using {talent_class_for_spec.__name__} "
                            f"for character '{char_data.get('name', 'Unnamed')}'. Details: {e}. Skipping character.\n"
                        )
                        continue
                elif talent_spec_name:  # Talent name provided but not found
                    self.output_view.append(
                        f"Warning: Talent spec '{talent_spec_name}' not found for class '{class_name}' "
                        f"for character '{char_data.get('name', 'Unnamed')}'. Using no talents.\n")

                equipped_items_obj = EquippedItems()
                for item_name, item_value in char_data.get('equipped_items', {}).items():
                    if hasattr(equipped_items_obj, item_name):
                        setattr(equipped_items_obj, item_name, item_value)
                    else:
                        self.output_view.append(
                            f"Warning: Unknown item '{item_name}' for character '{char_data.get('name', 'Unnamed')}'. Ignoring.\n"
                        )

                cooldown_usages_values = char_data.get('cooldown_usages', {})
                try:
                    cooldown_usages_obj = CooldownUsages(**cooldown_usages_values)
                except TypeError as e:
                    self.output_view.append(
                        f"Error: Could not instantiate CooldownUsages with data {cooldown_usages_values} "
                        f"for character '{char_data.get('name', 'Unnamed')}'. Details: {e}. Using default CooldownUsages. \n"
                    )
                    cooldown_usages_obj = CooldownUsages()

                char_instance = char_class_info(
                    name=char_data['name'],
                    sp=char_data['sp'],
                    crit=char_data['crit'],
                    hit=char_data['hit'],
                    haste=char_data['haste'],
                    tal=talent_instance,
                    opts=options_obj,
                    equipped_items=equipped_items_obj
                )

                rotation_method_name = char_data['rotation']
                if hasattr(char_instance, rotation_method_name):
                    rotation_method = getattr(char_instance, rotation_method_name)
                    sig = inspect.signature(rotation_method)
                    if 'cds' in sig.parameters:
                        rotation_method(cds=cooldown_usages_obj)
                    else:
                        rotation_method()  # Call without cds if not expected
                else:
                    self.output_view.append(
                        f"Error: Rotation method '{rotation_method_name}' not found on character '{char_data['name']}'. Skipping character.\n")
                    continue

                sim_characters.append(char_instance)

            except Exception as e:
                import traceback
                self.output_view.append(
                    f"Critical error setting up character '{char_data.get('name', 'Unnamed')}': {str(e)}\n")
                self.output_view.append(traceback.format_exc() + "\nSkipping character.\n")
                continue

        if not sim_characters:
            self.output_view.append("Error: No characters were successfully configured for the simulation.\n")
            self.root.update_idletasks()
            return

        self.output_view.append(
            f"\nSuccessfully configured {len(sim_characters)} character(s) for simulation.\n"
            f"Starting simulation ({iterations} iterations, {duration}s duration, "
            f"multiprocessing: {'Enabled' if use_multiprocessing else 'Disabled'})...\n"
        )
        self.root.update_idletasks()  # Ensure initial messages are displayed

        # Consider disabling simulation control buttons here to prevent multiple submissions
        # e.g., self.simulation_controls_view.disable_buttons()

        controller = SimulationController(
            output_text_widget=self.output_view.get_text_widget(),
            characters_data=sim_characters,  # Pass list of character instances
            iterations=iterations,
            duration=duration,
            use_multiprocessing=use_multiprocessing
        )

        def simulation_task():
            original_stdout = sys.stdout
            redirector = TextRedirector(self.output_view.get_text_widget(), self.root)
            sys.stdout = redirector

            try:
                controller.execute()
            except Exception as e:
                import traceback
                print(f"\n--- SIMULATION ERROR ---\n")
                print(f"An error occurred during the simulation:\n{str(e)}\n")
                print(traceback.format_exc())
                print(f"--- END SIMULATION ERROR ---\n")
            finally:
                sys.stdout = original_stdout  # Always restore original stdout
                self.root.after_idle(lambda: {
                    self.output_view.append("\nSimulation process finished.\n")
                    # Consider re-enabling simulation control buttons here
                    # e.g., self.simulation_controls_view.enable_buttons()
                })

        sim_thread = threading.Thread(target=simulation_task, daemon=True)
        sim_thread.start()

    def _handle_run_single_simulation(self, duration):
        if not self.characters:
            self.output_view.clear()
            self.output_view.append("Error: No characters added to simulation for a single run.\n")
            return

        self.output_view.clear()

        sim_characters = []
        # This section is now very similar to the setup in _handle_run_simulation
        # For brevity, I'm showing the structure, assuming the detailed logic is mirrored
        # from the updated _handle_run_simulation or refactored into a helper.
        # For this specific request, only _handle_run_simulation was targeted for the deep change.
        # The following is a conceptual placeholder for character setup.

        # --- Begin Character Setup (similar to _handle_run_simulation) ---
        for char_data in self.characters:
            try:
                class_name = char_data['type']
                registry_entry = class_registry.get(class_name)
                if not registry_entry:
                    self.output_view.append(
                        f"Error: Class '{class_name}' not found. Skipping char '{char_data.get('name', 'Unknown')}'.\n")
                    continue
                char_class_info = registry_entry.get('cls')
                if not char_class_info:
                    self.output_view.append(
                        f"Error: Misconfigured registry for '{class_name}'. Skipping char '{char_data.get('name', 'Unknown')}'.\n")
                    continue

                actual_options_cls = registry_entry.get("options_cls")
                options_obj = None
                if actual_options_cls:
                    if hasattr(actual_options_cls, '__dataclass_fields__'):
                        valid_option_keys = {f.name for f in dataclass_fields(actual_options_cls)}
                        user_provided_options = char_data.get('options', {})
                        filtered_options_data = {k: v for k, v in user_provided_options.items() if
                                                 k in valid_option_keys}
                        try:
                            options_obj = actual_options_cls(**filtered_options_data)
                        except TypeError as e:
                            self.output_view.append(
                                f"Error instantiating options for '{class_name}': {e}. Skipping char '{char_data.get('name', 'Unknown')}'.\n")
                            continue
                    # else: warnings about non-dataclass options_cls

                talent_specs_dict = registry_entry.get('talents', {})
                talent_spec_name = char_data.get('talents')
                talent_class_for_spec = talent_specs_dict.get(talent_spec_name) if talent_spec_name else None
                talent_instance = None
                if talent_class_for_spec:
                    try:
                        talent_instance = talent_class_for_spec()
                    except Exception as e:
                        self.output_view.append(
                            f"Error instantiating talent '{talent_spec_name}': {e}. Skipping char '{char_data.get('name', 'Unknown')}'.\n")
                        continue
                # else: warnings about missing talent spec

                equipped_items_obj = EquippedItems()
                for item_name, item_value in char_data.get('equipped_items', {}).items():
                    if hasattr(equipped_items_obj, item_name):
                        setattr(equipped_items_obj, item_name, item_value)

                cooldown_usages_obj = CooldownUsages(**char_data.get('cooldown_usages', {}))

                char_instance = char_class_info(
                    name=char_data['name'], sp=char_data['sp'], crit=char_data['crit'],
                    hit=char_data['hit'], haste=char_data['haste'], tal=talent_instance,
                    opts=options_obj, equipped_items=equipped_items_obj
                )

                rotation_method_name = char_data['rotation']
                if hasattr(char_instance, rotation_method_name):
                    rotation_method = getattr(char_instance, rotation_method_name)
                    sig = inspect.signature(rotation_method)
                    if 'cds' in sig.parameters:
                        rotation_method(cds=cooldown_usages_obj)
                    else:
                        rotation_method()
                else:
                    self.output_view.append(
                        f"Error: Rotation '{rotation_method_name}' not found for char '{char_data.get('name', 'Unknown')}'. Skipping.\n")
                    continue

                sim_characters.append(char_instance)
            except Exception as e:
                import traceback
                self.output_view.append(
                    f"Critical error setting up character '{char_data.get('name', 'Unnamed')} for single run: {str(e)}\n")
                self.output_view.append(traceback.format_exc() + "\nSkipping character.\n")
                continue
        # --- End Character Setup ---

        if not sim_characters:
            self.output_view.append("No characters were successfully configured for the single run.\n")
            self.root.update_idletasks()
            return

        self.output_view.append(
            f"\nSuccessfully configured {len(sim_characters)} character(s).\n"
            f"Starting single simulation run (1 iteration, {duration}s duration)...\n"
        )
        self.root.update_idletasks()

        original_sys_stdout = sys.stdout
        captured_output_buffer = None

        try:
            env = Environment(print_casts=True)
            env.add_characters(sim_characters)  # sim_characters now contains instances

            captured_output_buffer = io.StringIO()
            sys.stdout = captured_output_buffer

            env.run(until=duration)

            if hasattr(env, 'meter') and hasattr(env.meter, 'detailed_report'):
                env.meter.detailed_report()
            else:
                print("Error: Environment meter or detailed_report method not found.")

            sys.stdout = original_sys_stdout
            report_str = captured_output_buffer.getvalue()

            self.output_view.append("\n--- Single Run Report ---\n")
            self.output_view.append(report_str)

        except Exception as e:
            if original_sys_stdout:  # Ensure stdout is restored if an error occurred before it was
                sys.stdout = original_sys_stdout
            self.output_view.append(f"\nAn error occurred during single simulation: {str(e)}\n")
            import traceback
            self.output_view.append(traceback.format_exc())
        finally:
            if original_sys_stdout and sys.stdout != original_sys_stdout:  # Ensure it's always restored
                sys.stdout = original_sys_stdout
            if captured_output_buffer is not None:
                captured_output_buffer.close()
