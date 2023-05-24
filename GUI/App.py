import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning

from GP_frame import GP_frame
from Device_frame import Device_frame
from Control_frame import Control_frame


class App(tk.Tk):

    def __init__(self):
        super().__init__()

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

        self.device_frame = Device_frame(topframe)
        self.device_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.control_frame = Control_frame(topframe)
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

        for i in (0,1,2,3):
            frame = GP_frame(self, i)
            frame.grid(row=1, column=i, **gridding)
            self.gp_frame.append(frame)


    def initialize_gui_data(self):

        self.device_frame.data["description"].set("MCP2221 USB-I2C/UART Combo")
        self.device_frame.data["serial"].set("Serial: 01234567")
        self.device_frame.data["manufacturer"].set("Microchip Technology Inc.")

        self.gp_frame[0].func.set("GPIO_IN")
        self.gp_frame[1].func.set("GPIO_IN")
        self.gp_frame[2].func.set("GPIO_IN")
        self.gp_frame[3].func.set("GPIO_IN")

        self.control_frame.adc_vref.set("1.024V")
        self.control_frame.dac_vref.set("OFF")

        self.control_frame.power_mgmnt.set("enabled")


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