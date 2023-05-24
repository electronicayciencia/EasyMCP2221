import tkinter as tk
from tkinter import ttk

from Func_frames import *

class GP_frame(ttk.Labelframe):
    """Create each of the 4 GPIO frames."""

    def __init__(self, root, pin):
        super().__init__(root)

        self.pin = pin
        self["text"] = f' GP{pin} '

        all_pin_funcs = [
            ["GPIO_IN", "GPIO_OUT", "SSPND", "LED_URX"],
            ["GPIO_IN", "GPIO_OUT", "CLK_OUT", "ADC", "LED_UTX", "IOC"],
            ["GPIO_IN", "GPIO_OUT", "USBCFG", "ADC", "DAC"],
            ["GPIO_IN", "GPIO_OUT", "LED_I2C", "ADC", "DAC"]
        ]

        self.pin_funcs = all_pin_funcs[pin]

        # Create and place function selector menus
        self.func = tk.StringVar()
        ttk.OptionMenu(self, self.func, None, *self.pin_funcs, command=self.gp_func_updated).pack(fill=tk.X, pady=10, padx=2)

        f = Func_GPIO_IN_frame(self)
        f.pack(expand=True, fill=tk.X)
        f.low()


    def gp_func_updated(self, func):
        print("New GP%s function is %s." % (self.pin, func))

