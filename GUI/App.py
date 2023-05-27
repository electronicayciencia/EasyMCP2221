import sys
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning

from GP_frame import GP_frame
from Device_frame import Device_frame
from Control_frame import Control_frame

import EasyMCP2221

class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.reading_period = 100

        self.connect()

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
            "ioc": tk.StringVar(),
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

        self.main_window()
        self.load_flash()
        self.mcp.reset()

        # Read/update main loop
        self.read_io_and_adc_loop()


    def main_window(self):
        self.title("EasyMCP2221 utility")
        #self.geometry("680x600")

        # Create 2x4 layout and frames
        self.columnconfigure(0, weight=1, uniform="gpio")
        self.columnconfigure(1, weight=1, uniform="gpio")
        self.columnconfigure(2, weight=1, uniform="gpio")
        self.columnconfigure(3, weight=1, uniform="gpio")

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


    def read_io_and_adc_loop(self, *args):
        try:
            io_read = self.mcp.GPIO_read()
            adc_read = self.mcp.ADC_read()
        except Exception as e:
            print("Read error:", str(e))
            showerror("Error", "Error reading MCP2221.")
            self.destroy()
            return

        self.sts["in"][0].set(io_read[0])
        self.sts["in"][1].set(io_read[1])
        self.sts["in"][2].set(io_read[2])
        self.sts["in"][3].set(io_read[3])

        self.sts["adc"][0].set(adc_read[0])
        self.sts["adc"][1].set(adc_read[1])
        self.sts["adc"][2].set(adc_read[2])

        self.after(self.reading_period, self.read_io_and_adc_loop)


    def connect(self):
        try:
            self.mcp = EasyMCP2221.Device()
        except Exception as e:
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
        try:
            self.mcp.reset()
        except:
            showerror('Reset error', str(e))
            self.destroy()
            return

        self.load_flash()


    def i2cscan_click(self):
        print("I2C Scan")



if __name__ == "__main__":

    app = App()


    try:
        from ctypes import windll
        #root.attributes('-toolwindow', True)
        #windll.shcore.SetProcessDpiAwareness(1)
    finally:
        app.mainloop()