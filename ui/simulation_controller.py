import tkinter as tk
from sim.simulation import Simulation
import sys
from io import StringIO
import traceback


class SimulationController:
    def __init__(self, output_text_widget: tk.Text, characters_data: list,
                 iterations: int, duration: int, use_multiprocessing: bool):
        """
        Initializes the SimulationController.
        Args:
            output_text_widget: The Tkinter Text widget for logging.
            characters_data: A list of pre-instantiated character objects.
            iterations: Number of simulation iterations.
            duration: Duration of each simulation iteration.
            use_multiprocessing: Boolean flag to use multiprocessing.
        """
        self.output_text = output_text_widget
        # characters_data is now expected to be a list of character *instances*
        self.characters_data_input = characters_data
        self.iterations = iterations
        self.duration = duration
        self.use_multiprocessing = use_multiprocessing
        self.char_instances = []  # This will be populated by _initialize_simulation_characters

    def _log(self, message: str):
        if self.output_text and self.output_text.winfo_exists():
            self.output_text.insert(tk.END, message + "\n")
            self.output_text.see(tk.END)

    def _initialize_simulation_characters(self):
        """
        Initializes self.char_instances from the pre-configured character objects
        passed in self.characters_data_input.
        """
        self._log("SimulationController: Initializing with pre-configured character instances...")

        if not isinstance(self.characters_data_input, list):
            self._log(
                f"  Error: Expected a list of character instances, but received {type(self.characters_data_input)}.")
            self.char_instances = []
            return

        if not self.characters_data_input:
            self._log("  Warning: No character instances were provided by the main window.")
            self.char_instances = []
            return

        # Directly use the provided instances, assuming they are valid character objects
        self.char_instances = self.characters_data_input
        self._log(f"  Successfully initialized with {len(self.char_instances)} character instance(s).")

    def execute(self):
        if self.output_text and self.output_text.winfo_exists():
            self.output_text.delete(1.0, tk.END)  # Clear previous output

        self._log("SimulationController: Execution started.")

        # This method now assigns the pre-built instances to self.char_instances
        self._initialize_simulation_characters()

        if not self.char_instances:  # Check if char_instances got populated
            self._log("Error: No character instances available for simulation. Aborting execution.")
            return

        self._log(f"Starting simulation with {len(self.char_instances)} character(s)...")
        self._log(
            f"Parameters: Iterations={self.iterations}, Duration={self.duration}s, Multiprocessing={self.use_multiprocessing}")

        # The Simulation class expects a list of character instances.
        sim = Simulation(characters=self.char_instances)

        original_stdout = sys.stdout
        simulation_output_buffer = StringIO()

        try:
            # Redirect stdout to capture the report from sim.detailed_report()
            sys.stdout = simulation_output_buffer

            # Run the simulation
            sim.run(iterations=self.iterations, duration=self.duration,
                    use_multiprocessing=self.use_multiprocessing, print_casts=False)

            self._log("Simulation finished. Generating report...")
            sim.detailed_report()  # This will print to simulation_output_buffer

        except Exception as e:
            # Ensure stdout is restored if an error occurred
            sys.stdout = original_stdout
            self._log(f"--- ERROR DURING SIMULATION ---")
            self._log(f"Error: {str(e)}")
            self._log(traceback.format_exc())
            # Also print to actual stderr for developer visibility if UI log fails or is part of the issue
            print(f"SIMULATION_CONTROLLER_ERROR: {traceback.format_exc()}", file=sys.__stderr__)
        finally:
            # Crucial: always restore original stdout
            sys.stdout = original_stdout

            report_content = simulation_output_buffer.getvalue()
            simulation_output_buffer.close()

            if report_content.strip():  # Check if there's actual content in the report
                self._log("\n--- Simulation Report ---")
                # Insert report content into the Tkinter text widget
                if self.output_text and self.output_text.winfo_exists():
                    self.output_text.insert(tk.END, report_content)
                    self.output_text.see(tk.END)
            else:
                # This message is useful if sim.detailed_report() produces no output
                # or if something went wrong with capturing.
                self._log("No report content generated or captured from simulation (or report was empty).")

            self._log("SimulationController: Execution completed.")
