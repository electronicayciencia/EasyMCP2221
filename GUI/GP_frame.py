import tkinter as tk
from tkinter import ttk

import logging
logger = logging.getLogger(__name__)

from Func_frames import *

class GP_frame(ttk.Labelframe):
    """Create each of the 4 GPIO frames."""

    def __init__(self, root, pin, sts, mcp):
        super().__init__(root)

        self.pin = pin
        self.mcp = mcp
        self["text"] = f' GP{pin} '

        all_pin_funcs = [
            ["GPIO_IN", "GPIO_OUT", "SSPND", "LED_URX"],
            ["GPIO_IN", "GPIO_OUT", "CLK_OUT", "ADC", "LED_UTX", "IOC"],
            ["GPIO_IN", "GPIO_OUT", "USBCFG", "ADC", "DAC"],
            ["GPIO_IN", "GPIO_OUT", "LED_I2C", "ADC", "DAC"]
        ]

        self.pin_funcs = all_pin_funcs[pin]

        # Create and place function selector menus
        self.func = sts["func"][pin]
        self.out = sts["out"][pin]
        
        # Trace var is broken on ttk.OptionMenu
        # See: https://stackoverflow.com/questions/53171384/tkinter-function-repeats-itself-twice-when-ttk-widgets-are-engaged
        tk.OptionMenu(self,
            self.func,
            *self.pin_funcs,
            command=self.select_func,
            ).pack(fill=tk.X, pady=5, padx=10)


        # Inner frame to place all function frames overlapping
        cont = ttk.Frame(self)
        cont.columnconfigure(0, weight=1)
        cont.rowconfigure(0, weight=1)
        cont.pack(expand=True, fill=tk.X, anchor=tk.N)

        self.subframes = {}

        # Create all needed frames
        for f in self.pin_funcs:
            if f == "GPIO_IN":  fr = Func_GPIO_IN_frame(cont, pin, sts)
            if f == "GPIO_OUT": fr = Func_GPIO_OUT_frame(cont, pin, sts, mcp)
            if f == "ADC":      fr = Func_ADC_frame(cont, pin, sts)
            if f == "DAC":      fr = Func_DAC_frame(cont, sts, mcp)
            if f == "CLK_OUT":  fr = Func_CLK_OUT_frame(cont, sts, mcp)
            if f == "IOC":      fr = Func_IOC_frame(cont, sts, mcp)
            if f == "LED_URX":  fr = Func_GENERIC_frame(cont, "LED_URX")
            if f == "LED_UTX":  fr = Func_GENERIC_frame(cont, "LED_UTX")
            if f == "SSPND":    fr = Func_GENERIC_frame(cont, "SSPND")
            if f == "USBCFG":   fr = Func_GENERIC_frame(cont, "USBCFG")
            if f == "LED_I2C":  fr = Func_GENERIC_frame(cont, "LED_I2C")

            self.subframes[f] = fr

            fr.grid(row=0, column=0, sticky=tk.NSEW)

        self.func.trace("w", self.update_view)

    def select_func(self, *args):
        func = self.func.get()
        out = int(self.out.get())
        logger.info(f'New GP{self.pin} function is {func} (gpio out {out}).')
        if self.pin == 0: self.mcp.set_pin_function(gp0 = func, out0 = out)
        if self.pin == 1: self.mcp.set_pin_function(gp1 = func, out1 = out)
        if self.pin == 2: self.mcp.set_pin_function(gp2 = func, out2 = out)
        if self.pin == 3: self.mcp.set_pin_function(gp3 = func, out3 = out)

    def update_view(self, *args):
        self.subframes[self.func.get()].tkraise()

