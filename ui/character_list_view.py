import tkinter as tk
from tkinter import ttk, messagebox

class CharacterListView:
    def __init__(self, parent_container, edit_callback, remove_callback, duplicate_callback):
        self.edit_callback = edit_callback
        self.remove_callback = remove_callback
        self.duplicate_callback = duplicate_callback # Added duplicate_callback

        # Main frame for this view, which includes the listbox and buttons
        self.view_frame = ttk.Frame(parent_container)
        self.view_frame.pack(fill=tk.BOTH, expand=True)

        # LabelFrame for the listbox
        self.listbox_labelframe = ttk.LabelFrame(self.view_frame, text="Characters")
        self.listbox_labelframe.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.listbox = tk.Listbox(self.listbox_labelframe)
        self.listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        scrollbar = ttk.Scrollbar(self.listbox_labelframe, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Frame for buttons, placed within the main view_frame, below the listbox_labelframe
        button_frame = ttk.Frame(self.view_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Edit Selected",
                   command=self._on_edit_pressed).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Duplicate Selected", # Added Duplicate button
                   command=self._on_duplicate_pressed).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Selected",
                   command=self._on_remove_pressed).pack(side=tk.LEFT, padx=5)

    def _on_edit_pressed(self):
        selected_index = self.get_selected_index()
        if selected_index is None:
            messagebox.showwarning("No Selection", "Please select a character to edit.")
            return
        if self.edit_callback:
            self.edit_callback(selected_index)

    def _on_duplicate_pressed(self): # Added handler for duplicate button
        selected_index = self.get_selected_index()
        if selected_index is None:
            messagebox.showwarning("No Selection", "Please select a character to duplicate.")
            return
        if self.duplicate_callback:
            self.duplicate_callback(selected_index)

    def _on_remove_pressed(self):
        selected_index = self.get_selected_index()
        if selected_index is None:
            messagebox.showwarning("No Selection", "Please select a character to remove.")
            return
        if self.remove_callback:
            self.remove_callback(selected_index)

    def add_item(self, display_text):
        self.listbox.insert(tk.END, display_text)

    def update_item(self, index, display_text):
        self.listbox.delete(index)
        self.listbox.insert(index, display_text)
        self.listbox.selection_set(index)
        self.listbox.see(index)

    def remove_item_at_index(self, index):
        self.listbox.delete(index)

    def get_selected_index(self):
        selected = self.listbox.curselection()
        return selected[0] if selected else None

    def set_selection(self, index):
        self.listbox.selection_set(index)
        self.listbox.see(index)

    def clear_list(self):
        self.listbox.delete(0, tk.END)
