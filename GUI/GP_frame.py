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
        ttk.OptionMenu(self, self.func, None, *self.pin_funcs, command=self.gp_func_updated).pack(fill=tk.X, pady=5, padx=2)

        ttk.Separator(self, orient='horizontal').pack(fill=tk.X,  pady=10, padx=20, anchor=tk.N)

        if pin == 0:
            f = Func_GPIO_IN_frame(self)
        elif pin == 1:
            f = Func_ADC_frame(self)
            f.ref = "1.024V"
            f.update(512)
        elif pin == 2:
            f = Func_DAC_frame(self)
            f.ref = "1.024V"
        else:
            f = Func_GENERIC_frame(self, "SSPND")
            #f = Func_IOC_frame(self)
            #f = Func_CLK_OUT_frame(self)
            #f = Func_GPIO_OUT_frame(self, pin)

        f.pack(expand=True, fill=tk.X, anchor=tk.N)



    def gp_func_updated(self, func):
        print("New GP%s function is %s." % (self.pin, func))

