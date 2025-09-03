import tkinter as tk
import simpy
from ui.main_window import MainWindow # Corrected class name

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root) # Corrected class name
    root.mainloop()
