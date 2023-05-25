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

        # Inner frame to place all function frames overlapping
        cont = ttk.Frame(self)
        cont.columnconfigure(0, weight=1)
        cont.rowconfigure(0, weight=1)
        cont.pack(expand=True, fill=tk.X, anchor=tk.N)

        self.subframes = {}
        
        # Create all needed frames
        for func in self.pin_funcs:
            if func == "GPIO_IN":  f = Func_GPIO_IN_frame(cont)
            if func == "GPIO_OUT": f = Func_GPIO_OUT_frame(cont, pin)
            if func == "ADC":      f = Func_ADC_frame(cont)
            if func == "DAC":      f = Func_DAC_frame(cont)
            if func == "CLK_OUT":  f = Func_CLK_OUT_frame(cont)
            if func == "IOC":      f = Func_IOC_frame(cont)
            if func == "LED_URX":  f = Func_GENERIC_frame(cont, "LED_URX")
            if func == "LED_UTX":  f = Func_GENERIC_frame(cont, "LED_UTX")
            if func == "SSPND":    f = Func_GENERIC_frame(cont, "SSPND")
            if func == "USBCFG":   f = Func_GENERIC_frame(cont, "USBCFG")
            if func == "LED_I2C":  f = Func_GENERIC_frame(cont, "LED_I2C")
                
            self.subframes[func] = f
        
            #f.pack(expand=True, fill=tk.X, anchor=tk.N)
            f.grid(row=0, column=0, sticky=tk.NSEW)



    def gp_func_updated(self, func):
        print("New GP%s function is %s." % (self.pin, func))
        self.subframes[func].tkraise()
