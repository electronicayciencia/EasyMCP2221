import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning, askyesno

import logging
logger = logging.getLogger(__name__)

from GP_frame import GP_frame
from Device_frame import Device_frame
from Control_frame import Control_frame
from I2Cscan_window import I2Cscan_window

import EasyMCP2221


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.mcp = None
        self.reading_period = 100
        self.i2c_scanning = False # ADC, GPIO and INT reading interferes with the I2C scan.

        # Global status
        self.sts = {
            "strings" : {
                "description": tk.StringVar(self, "Not connected"),
                "serial":      tk.StringVar(self, "-"),
                "vendor":      tk.StringVar(self, "-"),
            },
            "dac_ref": tk.StringVar(self, "OFF"),
            "dac": tk.StringVar(self, 0),
            "pwr": tk.StringVar(),
            # Interrupt on change
            "ioc": tk.StringVar(),
            "int": tk.StringVar(),
            "clk": {
                "freq": tk.StringVar(self, "12MHz"),
                "duty": tk.StringVar(self, 0),
            },

            #Function of each pin
            "func": [
                tk.StringVar(self, "-"),
                tk.StringVar(self, "-"),
                tk.StringVar(self, "-"),
                tk.StringVar(self, "-"),
            ],

            #ADC input of each pin
            "adc_ref": tk.StringVar(self, "OFF"),
            "adc": [
                tk.StringVar(self, 0),
                tk.StringVar(self, 0),
                tk.StringVar(self, 0),
            ],

            #Logic input of each pin
            "in": [
                tk.StringVar(self, 0),
                tk.StringVar(self, 0),
                tk.StringVar(self, 0),
                tk.StringVar(self, 0),
            ],

            #Logic output of each pin
            "out": [
                tk.StringVar(self, 0),
                tk.StringVar(self, 0),
                tk.StringVar(self, 0),
                tk.StringVar(self, 0),
            ],
        }

        self.iconbitmap(default=self.resource_path("icon-dvd.ico"))

        self.connect()

        self.main_window()
        self.load_flash()
        self.mcp.reset()

        # Read/update main loop
        self.read_mcp_loop()

        logger.debug("Starting APP")


    def main_window(self):
        self.title("EasyMCP2221 utility v1.0 - Electronica y ciencia")
        #self.geometry("680x600")

        # Create 2x4 layout and frames
        for i in (0,1,2,3):
            self.columnconfigure(i, weight=1, uniform="gpio")

        gridding = {
            'sticky': "nsew",
            'padx': 10,
            'pady': 10,
        }

        # Top frame and subframes
        topframe=tk.Frame(self)
        topframe.grid(row=0, column=0, columnspan=4, **gridding)

        self.device_frame = Device_frame(topframe, self.sts)
        self.device_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.control_frame = Control_frame(topframe, self.sts, self.mcp)
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        buttons_frame = ttk.Frame(topframe)
        buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Populate buttons frame
        options = {
            "padx": 5,
            "pady": 5,
            "ipadx": 20,
            "ipady": 5,
            "expand": True,
            "fill": tk.X,
        }

        tk.Button(buttons_frame, text="Quit",     command=self.quit_click).pack(**options)
        tk.Button(buttons_frame, text="Reset",    command=self.reset_click).pack(**options)
        tk.Button(buttons_frame, text="I2C Scan", command=self.i2cscan_click).pack(**options)

        # GPIO frames
        self.gp_frame = []

        for pin in (0,1,2,3):
            frame = GP_frame(self, pin, self.sts, self.mcp)
            frame.grid(row=1, column=pin, **gridding)
            self.gp_frame.append(frame)


    def read_mcp_loop(self, *args):
        if self.i2c_scanning:
            self.after(self.reading_period, self.read_mcp_loop)
            return

        try:
            io_read  = self.mcp.GPIO_read()
            adc_read = self.mcp.ADC_read()
            int_read = self.mcp.IOC_read()
        except Exception as e:
            logger.critical("Read error: " + str(e))
            showerror("Error", "Error reading MCP2221.")
            self.destroy()
            return

        for i in (0,1,2,3):
            self.sts["in"][i].set(io_read[i])

        for i in (0,1,2):
            self.sts["adc"][i].set(adc_read[i])

        self.sts["int"].set(int_read)

        self.after(self.reading_period, self.read_mcp_loop)


    def connect(self):
        try:
            self.mcp = EasyMCP2221.Device()
        except Exception as e:
            logger.critical('Device not found: ' + str(e))
            showerror('Device not found', str(e))
            sys.exit()


    def quit_click(self):
        self.destroy()


    def load_flash(self):
        # For testing purposes:
        #self.sts["strings"]["description"].set("MCP2221A USB-I2C/UART Combo")
        #self.sts["strings"]["serial"].set("Serial: 01234567")
        #self.sts["strings"]["manufacturer"].set("Microchip Technology Inc.")
        #
        #self.sts["func"][0].set("LED_URX")
        #self.sts["func"][1].set("LED_UTX")
        #self.sts["func"][2].set("USBCFG")
        #self.sts["func"][3].set("LED_I2C")
        #
        #self.sts["dac_ref"].set("OFF")
        #self.sts["dac"].set("16")
        #
        #self.sts["pwr"].set("enabled")
        #
        #self.sts["in"][0].set("0")
        #self.sts["in"][1].set("1")
        #self.sts["in"][2].set("0")
        #self.sts["in"][3].set("1")
        #
        #self.sts["out"][0].set("1")
        #self.sts["out"][1].set("0")
        #self.sts["out"][2].set("1")
        #self.sts["out"][3].set("0")
        #
        #self.sts["adc_ref"].set("OFF")
        #self.sts["adc"][0].set("256")
        #self.sts["adc"][1].set("512")
        #self.sts["adc"][2].set("1023")
        #
        #self.sts["clk"]["freq"].set("24MHz")
        #self.sts["clk"]["duty"].set("25")


        device_flash = self.mcp.read_flash_info()

        self.sts["strings"]["description"].set(device_flash["USB_PRODUCT"])
        self.sts["strings"]["serial"].set("Serial: %s" % device_flash["USB_SERIAL"])
        self.sts["strings"]["vendor"].set(device_flash["USB_VENDOR"])

        self.sts["func"][0].set(device_flash["GP_SETTINGS"]["GP0"]["func"])
        self.sts["func"][1].set(device_flash["GP_SETTINGS"]["GP1"]["func"])
        self.sts["func"][2].set(device_flash["GP_SETTINGS"]["GP2"]["func"])
        self.sts["func"][3].set(device_flash["GP_SETTINGS"]["GP3"]["func"])

        self.sts["adc_ref"].set(device_flash["CHIP_SETTINGS"]["adc_ref"])
        self.sts["dac_ref"].set(device_flash["CHIP_SETTINGS"]["dac_ref"])
        self.sts["dac"].set(device_flash["CHIP_SETTINGS"]["dac_val"])

        self.sts["pwr"].set(device_flash["CHIP_SETTINGS"]["pwr"])
        self.sts["ioc"].set(device_flash["CHIP_SETTINGS"]["ioc"])

        self.sts["out"][0].set(device_flash["GP_SETTINGS"]["GP0"]["outval"])
        self.sts["out"][1].set(device_flash["GP_SETTINGS"]["GP1"]["outval"])
        self.sts["out"][2].set(device_flash["GP_SETTINGS"]["GP2"]["outval"])
        self.sts["out"][3].set(device_flash["GP_SETTINGS"]["GP3"]["outval"])

        self.sts["clk"]["freq"].set(device_flash["CHIP_SETTINGS"]["clk_freq"])
        self.sts["clk"]["duty"].set(device_flash["CHIP_SETTINGS"]["clk_duty"])


    def reset_click(self):
        logger.info("Reset")
        try:
            self.mcp.reset()
        except:
            showerror('Reset error', str(e))
            self.destroy()
            return

        self.load_flash()


    def i2cscan_click(self):
        logger.info("I2C Scan")

        # ADC, GPIO and INT reading interferes with the I2C scan.
        self.i2c_scanning = True
        i2cscan = I2Cscan_window(self, self.mcp)
        self.wait_window(i2cscan)
        self.i2c_scanning = False


    def resource_path(self, relative_path):
        """ Resource path inside a pyinstaller exe """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
