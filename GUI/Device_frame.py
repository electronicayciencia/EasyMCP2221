import tkinter as tk
from tkinter import ttk

class Device_frame(ttk.Labelframe):
    """Populate device data frame."""

    def __init__(self, root, sts):
        super().__init__(root)

        self["text"] = " Device "

        package = {
            "anchor": tk.W, 
            "pady": 5,
            "padx": 10
        }

        ttk.Label(self, 
            font="Helvetica, 14",
            wraplength=350,
            textvariable=sts["strings"]["description"]).pack(**package)
        
        ttk.Label(self, 
            font="Helvetica, 12",
            textvariable=sts["strings"]["serial"]).pack(**package)
        
        ttk.Label(self, 
            font="Helvetica, 12",
            textvariable=sts["strings"]["manufacturer"]).pack(**package)
