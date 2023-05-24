import tkinter as tk
from tkinter import ttk

class Device_frame(ttk.Labelframe):
    """Populate device data frame."""

    def __init__(self, root):
        super().__init__(root)

        self["text"] = " Device "

        self.data = {
            "description"  : tk.StringVar(),
            "serial"       : tk.StringVar(),
            "manufacturer" : tk.StringVar(),
        }

        ttk.Label(self, textvariable=self.data["description"], font="Helvetica, 14").pack(anchor=tk.W, pady=2, padx=5)
        ttk.Label(self, textvariable=self.data["serial"]).pack(anchor=tk.W, pady=2, padx=5)
        ttk.Label(self, textvariable=self.data["manufacturer"]).pack(anchor=tk.W, pady=2, padx=5)

