# Easy to use utility to configure MCP2221
import EasyMCP2221
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning




def i2cscan_click():
    print("i2c scan")

def reset_click():
    print("reset")

def save_click():
    print("save")

def quit_click():
    print("quit")


def gp0_func_changed(func):
    print("New GP0 function is:", func)

def gp1_func_changed(func):
    print("New GP1 function is:", func)

def gp2_func_changed(func):
    print("New GP2 function is:", func)

def gp3_func_changed(func):
    print("New GP3 function is:", func)






root = tk.Tk()
root.title('EasyMCP2221 utility')

#root.option_add("*Font", "arial 15")
#root.rowconfigure(0, weight=1)
#root.rowconfigure(1, weight=4)



#padding = {'padx': 5, 'pady': 5}
padding = {}


#root.tk.call("source", "Azure-ttk-theme/azure.tcl")
#root.tk.call("set_theme", "light")

def create_device_data_frame(root, description, serial, manufacturer):
    device_data_frame = ttk.Labelframe(root, text="Device Info")

    ttk.Label(device_data_frame, text=description).pack(fill=tk.X, **padding)
    ttk.Label(device_data_frame, text="Serial: %s" % serial).pack(fill=tk.X, **padding)
    ttk.Label(device_data_frame, text=manufacturer).pack(fill=tk.X, **padding)

    return device_data_frame



create_device_data_frame(
    root,
    description = "MCP2221 USB-I2C/UART Combo",
    serial = "01234567",
    manufacturer = "Microchip Technology Inc.",
).grid(row=0, column=0, columnspan=2, sticky=tk.NS)





main_buttons_frame = ttk.Frame(root, borderwidth=1, relief="solid")
#main_buttons_frame.rowconfigure(0, weight=3)
#main_buttons_frame.rowconfigure(1, weight=1)

ttk.Button(
    main_buttons_frame,
    text="I2C Scan",
    command=i2cscan_click).grid(row=0, column=0, sticky=tk.NS, **padding)

ttk.Button(
    main_buttons_frame,
    text="Quit",
    command=quit_click).grid(row=0, column=1, sticky=tk.NS, **padding)

ttk.Button(
    main_buttons_frame,
    text="Reset",
    command=reset_click).grid(row=1, column=0, sticky=tk.NS, **padding)

ttk.Button(
    main_buttons_frame,
    text="Save",
    command=save_click).grid(row=1, column=1, sticky=tk.NS, **padding)


main_buttons_frame.grid(row=0, column=2, columnspan=2, sticky=tk.NSEW)

pin_funcs = {
    "gp0": ["GPIO_IN", "GPIO_OUT", "SSPND", "LED_URX"],
    "gp1": ["GPIO_IN", "GPIO_OUT", "CLK_OUT", "ADC", "LED_UTX", "IOC"],
    "gp2": ["GPIO_IN", "GPIO_OUT", "USBCFG", "ADC", "DAC"],
    "gp3": ["GPIO_IN", "GPIO_OUT", "LED_I2C", "ADC", "DAC"]
}
gp0_func_var = tk.StringVar()
gp1_func_var = tk.StringVar()
gp2_func_var = tk.StringVar()
gp3_func_var = tk.StringVar()


gp0_frame = ttk.Labelframe(root, text="GP0")
gp1_frame = ttk.Labelframe(root, text="GP1")
gp2_frame = ttk.Labelframe(root, text="GP2")
gp3_frame = ttk.Labelframe(root, text="GP3")

ttk.OptionMenu(gp0_frame, gp0_func_var, "GP0 func", *pin_funcs["gp0"], command=gp0_func_changed).pack(fill=tk.X)
ttk.OptionMenu(gp1_frame, gp1_func_var, "GP1 func", *pin_funcs["gp1"], command=gp1_func_changed).pack(fill=tk.X)
ttk.OptionMenu(gp2_frame, gp2_func_var, "GP2 func", *pin_funcs["gp2"], command=gp2_func_changed).pack(fill=tk.X)
ttk.OptionMenu(gp3_frame, gp3_func_var, "GP3 func", *pin_funcs["gp3"], command=gp3_func_changed).pack(fill=tk.X)

gp0_frame.grid(row=1, column=0, sticky=tk.NSEW)
gp1_frame.grid(row=1, column=1, sticky=tk.NSEW)
gp2_frame.grid(row=1, column=2, sticky=tk.NSEW)
gp3_frame.grid(row=1, column=3, sticky=tk.NSEW)

gp0_func_frame = ttk.Frame(gp0_frame)
gp1_func_frame = ttk.Frame(gp1_frame)
gp2_func_frame = ttk.Frame(gp2_frame)
gp3_func_frame = ttk.Frame(gp3_frame)



# -------------------






# -------------------

try:
    from ctypes import windll
    #root.attributes('-toolwindow', True)
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()