import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning

from GP_frame import GP_frame
from Device_frame import Device_frame
from Control_frame import Control_frame


class App(tk.Tk):

 
    def __init__(self):
        super().__init__()

        # Global status
        self.sts = {
            "strings" : {
                "description":  tk.StringVar(self, "Not connected"),
                "serial":       tk.StringVar(self, "-"),
                "manufacturer": tk.StringVar(self, "-"),
            },
            "dac_ref": tk.StringVar(self, "OFF"),
            "dac": tk.StringVar(self, 0),
            "pwr": tk.StringVar(),
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
        }
    

        self.title('EasyMCP2221 utility')
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

        self.control_frame = Control_frame(topframe, self.sts)
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

        # Bottom frames
        self.gp_frame = []
        
        # link both DAC frames
        self.global_DAC = tk.StringVar()

        for pin in (0,1,2,3):
            frame = GP_frame(self, pin, self.sts)
            frame.grid(row=1, column=pin, **gridding)
            self.gp_frame.append(frame)



    def initialize_gui_data(self):

        #self.sts["strings"]["description"].set("MCP2221A USB-I2C/UART Combo")
        #self.sts["strings"]["serial"].set("Serial: 01234567")
        #self.sts["strings"]["manufacturer"].set("Microchip Technology Inc.")

        self.sts["func"][0].set("LED_URX")
        self.sts["func"][1].set("LED_UTX")
        self.sts["func"][2].set("USBCFG")
        self.sts["func"][3].set("LED_I2C")

        self.sts["dac_ref"].set("OFF")
        self.sts["dac"].set("16")

        self.sts["pwr"].set("enabled")
        
        self.sts["in"][0].set("1")
        self.sts["in"][1].set("0")
        self.sts["in"][2].set("1")
        self.sts["in"][3].set("0")

        self.sts["adc_ref"].set("OFF")
        self.sts["adc"][0].set("256")
        self.sts["adc"][1].set("512")
        self.sts["adc"][2].set("1023")

        self.sts["clk"]["freq"].set("24MHz")
        self.sts["clk"]["duty"].set("25")



    def quit_click(self):
        self.destroy()

    def reset_click(self):
        print("Reset")

    def i2cscan_click(self):
        print("I2C Scan")



if __name__ == "__main__":

    app = App()
    app.initialize_gui_data()

    try:
        from ctypes import windll
        #root.attributes('-toolwindow', True)
        #windll.shcore.SetProcessDpiAwareness(1)
    finally:
        app.mainloop()