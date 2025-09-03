import tkinter as tk
from tkinter import ttk

class OutputView:
    def __init__(self, parent_container):
        self.frame = ttk.LabelFrame(parent_container, text="Output")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.text_widget = tk.Text(self.frame, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=scrollbar.set)

    def get_text_widget(self):
        return self.text_widget

    def clear(self):
        self.text_widget.delete(1.0, tk.END)

    def append(self, text_content):
        self.text_widget.insert(tk.END, text_content)
        self.text_widget.see(tk.END)
