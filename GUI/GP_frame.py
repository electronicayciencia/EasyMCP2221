import tkinter as tk
from tkinter import ttk

from Func_frames import *

class GP_frame(ttk.Labelframe):
    """Create each of the 4 GPIO frames."""

    def __init__(self, root, pin, sts):
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
        self.func = sts["func"][pin]
        
        # Trace var is broken on ttk.OptionMenu
        # See: https://stackoverflow.com/questions/53171384/tkinter-function-repeats-itself-twice-when-ttk-widgets-are-engaged
        tk.OptionMenu(self,
            self.func, 
            *self.pin_funcs,
            #command=self.gp_func_updated,
            ).pack(fill=tk.X, pady=5, padx=10)

        #ttk.Separator(self, orient='horizontal').pack(fill=tk.X,  pady=10, padx=20, anchor=tk.N)
        self.func.trace("w", self.gp_func_updated)
        
        # Inner frame to place all function frames overlapping
        cont = ttk.Frame(self)
        cont.columnconfigure(0, weight=1)
        cont.rowconfigure(0, weight=1)
        cont.pack(expand=True, fill=tk.X, anchor=tk.N)

        self.subframes = {}
        
        # Create all needed frames
        for f in self.pin_funcs:
            if f == "GPIO_IN":  fr = Func_GPIO_IN_frame(cont, pin, sts)
            if f == "GPIO_OUT": fr = Func_GPIO_OUT_frame(cont, pin, sts)
            if f == "ADC":      fr = Func_ADC_frame(cont, pin, sts)
            if f == "DAC":      fr = Func_DAC_frame(cont, sts)
            if f == "CLK_OUT":  fr = Func_CLK_OUT_frame(cont, sts)
            if f == "IOC":      fr = Func_IOC_frame(cont, sts)
            if f == "LED_URX":  fr = Func_GENERIC_frame(cont, "LED_URX")
            if f == "LED_UTX":  fr = Func_GENERIC_frame(cont, "LED_UTX")
            if f == "SSPND":    fr = Func_GENERIC_frame(cont, "SSPND")
            if f == "USBCFG":   fr = Func_GENERIC_frame(cont, "USBCFG")
            if f == "LED_I2C":  fr = Func_GENERIC_frame(cont, "LED_I2C")
                
            self.subframes[f] = fr
        
            fr.grid(row=0, column=0, sticky=tk.NSEW)


    def gp_func_updated(self, *args):
        print("New GP%s function is %s." % (self.pin, self.func.get()))
        self.subframes[self.func.get()].tkraise()


