import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning

root = tk.Tk()
root.title('EasyMCP2221 utility')
root.geometry("600x600")

#-------------------------------
# Create 2x4 layout and frames

root.rowconfigure(0, weight=1, uniform="ala")
root.rowconfigure(1, weight=4, uniform="ala")

root.columnconfigure(0, weight=1, uniform="gpio")
root.columnconfigure(1, weight=1, uniform="gpio")
root.columnconfigure(2, weight=1, uniform="gpio")
root.columnconfigure(3, weight=1, uniform="gpio")

device_frame = ttk.Labelframe(root, text=" Device ")
control_frame = ttk.Frame(root)

gp_frame = []
gp_frame.append(ttk.Labelframe(root, text=' GP0 '))
gp_frame.append(ttk.Labelframe(root, text=' GP1 '))
gp_frame.append(ttk.Labelframe(root, text=' GP2 '))
gp_frame.append(ttk.Labelframe(root, text=' GP3 '))

gridding = {
    'sticky': "nsew",
    'padx': 10,
    'pady': 10,
}

device_frame.grid(row=0, column=0, columnspan=2, **gridding)
control_frame.grid(row=0, column=2, columnspan=2, **gridding)

gp_frame[0].grid(row=1, column=0, **gridding)
gp_frame[1].grid(row=1, column=1, **gridding)
gp_frame[2].grid(row=1, column=2, **gridding)
gp_frame[3].grid(row=1, column=3, **gridding)

#-------------------------------
# Create and place function selector menus

pin_funcs = [
    ["GPIO_IN", "GPIO_OUT", "SSPND", "LED_URX"],
    ["GPIO_IN", "GPIO_OUT", "CLK_OUT", "ADC", "LED_UTX", "IOC"],
    ["GPIO_IN", "GPIO_OUT", "USBCFG", "ADC", "DAC"],
    ["GPIO_IN", "GPIO_OUT", "LED_I2C", "ADC", "DAC"]
]

def gp0_func_updated(f): gp_func_updated(0, f)
def gp1_func_updated(f): gp_func_updated(1, f)
def gp2_func_updated(f): gp_func_updated(2, f)
def gp3_func_updated(f): gp_func_updated(3, f)

gp_func = []
gp_func.append(tk.StringVar())
gp_func.append(tk.StringVar())
gp_func.append(tk.StringVar())
gp_func.append(tk.StringVar())

ttk.OptionMenu(gp_frame[0], gp_func[0], "GP0 func", *pin_funcs[0], command=gp0_func_updated).pack(fill=tk.X, pady=10, padx=2)
ttk.OptionMenu(gp_frame[1], gp_func[1], "GP1 func", *pin_funcs[1], command=gp1_func_updated).pack(fill=tk.X, pady=10, padx=2)
ttk.OptionMenu(gp_frame[2], gp_func[2], "GP2 func", *pin_funcs[2], command=gp2_func_updated).pack(fill=tk.X, pady=10, padx=2)
ttk.OptionMenu(gp_frame[3], gp_func[3], "GP3 func", *pin_funcs[3], command=gp3_func_updated).pack(fill=tk.X, pady=10, padx=2)

#-------------------------------
# Populate device data frame

device_data = {}
device_data["description"]  = tk.StringVar()
device_data["serial"]       = tk.StringVar()
device_data["manufacturer"] = tk.StringVar()

ttk.Label(device_frame, textvariable=device_data["description"], font="Helvetica, 14").pack(anchor=tk.W, pady=2, padx=5)
ttk.Label(device_frame, textvariable=device_data["serial"]).pack(anchor=tk.W, pady=2, padx=5)
ttk.Label(device_frame, textvariable=device_data["manufacturer"]).pack(anchor=tk.W, pady=2, padx=5)


#-------------------------------
# Layout ends



def gp_func_updated(gp, func):
    print("New GP%s function is %s." % (gp, func))
    gp_func[1].set("GPIO_IN")




device_data["description"].set("MCP2221 USB-I2C/UART Combo")
device_data["serial"].set("Serial: 01234567")
device_data["manufacturer"].set("Microchip Technology Inc.")







try:
    from ctypes import windll
    #root.attributes('-toolwindow', True)
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
