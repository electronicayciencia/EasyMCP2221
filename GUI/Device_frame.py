import tkinter as tk
from tkinter import ttk

class Device_frame(ttk.Labelframe):
    """Populate device data frame."""

    def __init__(self, root, sts):
        super().__init__(root)

        self["text"] = " Device "

        ttk.Label(self, textvariable=sts["strings"]["description"], font="Helvetica, 14").pack(anchor=tk.W, pady=2, padx=5)
        ttk.Label(self, textvariable=sts["strings"]["serial"]).pack(anchor=tk.W, pady=2, padx=5)
        ttk.Label(self, textvariable=sts["strings"]["manufacturer"]).pack(anchor=tk.W, pady=2, padx=5)
