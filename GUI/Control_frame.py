import tkinter as tk
from tkinter import ttk

class Control_frame(ttk.Labelframe):
    """Populate control frame."""

    def __init__(self, root):
        super().__init__(root)

        self["text"] = " Options "

        self.adc_vref = tk.StringVar()
        self.dac_vref = tk.StringVar()
        self.power_mgmnt = tk.StringVar()

        vref_values = ("OFF", "1.024V", "2.048V", "4.096V", "VDD")


        ttk.Label(self,
                  text="ADC reference:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)

        ttk.Label(self,
                  text="DAC reference:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)

        ttk.OptionMenu(self,
                       self.adc_vref,
                       None,
                       *vref_values,
                       command=self.adc_vref_updated).grid(row=0, column=1, sticky=tk.E)

        ttk.OptionMenu(self,
                       self.dac_vref,
                       None,
                       *vref_values,
                       command=self.dac_vref_updated).grid(row=1, column=1, sticky=tk.E)

        ttk.Checkbutton(self,
                        text='Enable Power Management',
                        command=self.power_mgmnt_updated,
                        variable=self.power_mgmnt,
                        onvalue='enabled',
                        offvalue='disabled').grid(row=2, column=0, columnspan=2, pady=5, padx=10)

        tk.Button(self,
                  text="Save current configuration",
                  command=self.save_click).grid(row=3, column=0, columnspan=2, pady=5, padx=10, sticky=tk.EW)


    def adc_vref_updated(self, value):
        print("New ADC vref is", value)

    def dac_vref_updated(self, value):
        print("New DAC vref is", value)

    def power_mgmnt_updated(self):
        print("New power management is:", self.power_mgmnt.get())

    def save_click(self):
        print("Save")