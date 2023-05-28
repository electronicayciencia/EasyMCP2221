import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno

import logging
logger = logging.getLogger(__name__)

class Control_frame(ttk.Labelframe):
    """Populate control frame."""

    def __init__(self, root, sts, mcp):
        super().__init__(root)

        self["text"] = " Chip settings "
        self.mcp = mcp

        self.adc_vref = sts["adc_ref"]
        self.dac_vref = sts["dac_ref"]
        self.power_mgmnt = sts["pwr"]

        vref_values = ("OFF", "1.024V", "2.048V", "4.096V", "VDD", "VDD (5V)", "VDD (3.3V)")

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
                        text='USB remote wake-up',
                        command=self.power_mgmnt_updated,
                        variable=self.power_mgmnt,
                        onvalue='enabled',
                        offvalue='disabled').grid(row=2, column=0, sticky=tk.W, columnspan=2, pady=5, padx=10, ipadx=20)

        tk.Button(self,
                  text="Save current configuration",
                  command=self.save_click).grid(row=3, column=0, columnspan=2, pady=5, padx=10, sticky=tk.EW)


    def adc_vref_updated(self, value):
        logger.info(f'New ADC vref is {value}')
        if "VDD" in value:
            self.mcp.ADC_config(ref = "VDD")
        else:
            self.mcp.ADC_config(ref = value)

    def dac_vref_updated(self, value):
        logger.info(f'New DAC vref is {value}')
        if "VDD" in value:
            self.mcp.DAC_config(ref = "VDD")
        else:
            self.mcp.DAC_config(ref = value)

    def power_mgmnt_updated(self):
        pwr = self.power_mgmnt.get()
        if pwr == "enabled":
            logger.info("Enable power management")
            self.mcp.enable_power_management(True)
        else:
            logger.info("Disable power management")
            self.mcp.enable_power_management(False)


    def save_click(self):
        ans = askyesno(
            title="Save",
            message="Do you want to save this configuration as default?\nYou can modify it at any time.")

        if ans:
            logger.info("Save")
            self.mcp.save_config()
