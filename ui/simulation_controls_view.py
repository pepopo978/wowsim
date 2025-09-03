import tkinter as tk
from tkinter import ttk

class SimulationControlsView:
    def __init__(self, parent_container, run_simulation_callback, run_single_simulation_callback):
        self.run_simulation_callback = run_simulation_callback
        self.run_single_simulation_callback = run_single_simulation_callback

        self.view_frame = ttk.Frame(parent_container)
        self.view_frame.pack(fill=tk.X)

        sim_settings = ttk.LabelFrame(self.view_frame, text="Simulation Settings")
        sim_settings.pack(fill=tk.X, pady=10)

        ttk.Label(sim_settings, text="Iterations:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.iterations_var = tk.IntVar(value=5000)
        ttk.Entry(sim_settings, textvariable=self.iterations_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(sim_settings, text="Duration (sec):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.duration_var = tk.IntVar(value=180)
        ttk.Entry(sim_settings, textvariable=self.duration_var, width=10).grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        self.multiprocessing_var = tk.BooleanVar(value=False) # doesn't work in pyinstaller
        ttk.Checkbutton(sim_settings, text="Use Multiprocessing (doesn't work when using exe)", variable=self.multiprocessing_var).grid(
            row=0, column=4, sticky=tk.W, padx=5, pady=5)

        sim_action_buttons_frame = ttk.Frame(self.view_frame)
        sim_action_buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(sim_action_buttons_frame, text="Run Simulation (Multiple Iterations)",
                   command=self._on_run_simulation).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        ttk.Button(sim_action_buttons_frame, text="Run Single Iteration",
                   command=self._on_run_single_simulation).pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

    def _on_run_simulation(self):
        if self.run_simulation_callback:
            self.run_simulation_callback(
                iterations=self.iterations_var.get(),
                duration=self.duration_var.get(),
                use_multiprocessing=self.multiprocessing_var.get()
            )

    def _on_run_single_simulation(self):
        if self.run_single_simulation_callback:
            self.run_single_simulation_callback(
                duration=self.duration_var.get()
            )

    def get_duration(self):
        return self.duration_var.get()
