import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning

root = tk.Tk()
root.title('EasyMCP2221 utility')
root.geometry("800x600")



#-------------------------------
# Callbacks

def gp_func_updated(gp, func):
    print("New GP%s function is %s." % (gp, func))
    gp_func[1].set("GPIO_IN")

def adc_vref_updated(value):
    print("New ADC vref is", value)

def dac_vref_updated(value):
    print("New DAC vref is", value)

def power_mgmnt_updated():
    print("New power management is:", power_mgmnt.get())

def save_click():
    print("Save")

def quit_click():
    print("Quit!")

def reset_click():
    print("Reset")

def i2cscan_click():
    print("I2C Scan")



#-------------------------------
# Create 2x4 layout and frames

gridding = {
    'sticky': "nsew",
    'padx': 10,
    'pady': 10,
}

#root.rowconfigure(0, weight=1, uniform="ala")
#root.rowconfigure(1, weight=3, uniform="ala")

root.columnconfigure(0, weight=1, uniform="gpio")
root.columnconfigure(1, weight=1, uniform="gpio")
root.columnconfigure(2, weight=1, uniform="gpio")
root.columnconfigure(3, weight=1, uniform="gpio")

# Top frames

topframe=tk.Frame(root)
topframe.grid(row=0, column=0, columnspan=4, **gridding)

device_frame = ttk.Labelframe(topframe, text=" Device ")
device_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

control_frame = ttk.Labelframe(topframe, text=" Options ")
control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

buttons_frame = ttk.Frame(topframe)
buttons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

# Bottom frames

gp_frame = []
gp_frame.append(ttk.Labelframe(root, text=' GP0 '))
gp_frame.append(ttk.Labelframe(root, text=' GP1 '))
gp_frame.append(ttk.Labelframe(root, text=' GP2 '))
gp_frame.append(ttk.Labelframe(root, text=' GP3 '))


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

gp_func = []
gp_func.append(tk.StringVar())
gp_func.append(tk.StringVar())
gp_func.append(tk.StringVar())
gp_func.append(tk.StringVar())

ttk.OptionMenu(gp_frame[0], gp_func[0], "GP0 func", *pin_funcs[0], command=lambda f: gp_func_updated(0, f)).pack(fill=tk.X, pady=10, padx=2)
ttk.OptionMenu(gp_frame[1], gp_func[1], "GP1 func", *pin_funcs[1], command=lambda f: gp_func_updated(1, f)).pack(fill=tk.X, pady=10, padx=2)
ttk.OptionMenu(gp_frame[2], gp_func[2], "GP2 func", *pin_funcs[2], command=lambda f: gp_func_updated(2, f)).pack(fill=tk.X, pady=10, padx=2)
ttk.OptionMenu(gp_frame[3], gp_func[3], "GP3 func", *pin_funcs[3], command=lambda f: gp_func_updated(3, f)).pack(fill=tk.X, pady=10, padx=2)

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
# Populate control frame
adc_vref = tk.StringVar()
dac_vref = tk.StringVar()
power_mgmnt = tk.StringVar()

vref_values = ("OFF", "1.024V", "2.048V", "4.096V", "VDD")


ttk.Label(control_frame, 
          text="ADC reference:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
          
ttk.Label(control_frame, 
          text="DAC reference:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)

ttk.OptionMenu(control_frame, 
               adc_vref, 
               "adc vref", 
               *vref_values, 
               command=adc_vref_updated).grid(row=0, column=1, sticky=tk.E)

ttk.OptionMenu(control_frame, 
               dac_vref, 
               "dac vref", 
               *vref_values,
               command=dac_vref_updated).grid(row=1, column=1, sticky=tk.E)

ttk.Checkbutton(control_frame,
                text='Enable Power Management',
                command=power_mgmnt_updated,
                variable=power_mgmnt,
                onvalue='enabled',
                offvalue='disabled').grid(row=2, column=0, columnspan=2, pady=5, padx=10)

tk.Button(control_frame, 
          text="Save current configuration", 
          command=save_click).grid(row=3, column=0, columnspan=2, pady=5, padx=10, sticky=tk.EW)


#-------------------------------
# Populate buttons frame

options = {
    "padx": 5,
    "pady": 5,
    "ipadx": 5,
    "ipady": 5,
    "expand": True,
    "fill": tk.X,
}

tk.Button(buttons_frame, text="Quit",     command=quit_click).pack(**options)
tk.Button(buttons_frame, text="Reset",    command=reset_click).pack(**options)
tk.Button(buttons_frame, text="I2C Scan", command=i2cscan_click).pack(**options)


#-------------------------------
# Create auxiliary frames for any GPIO



def click(gp):
    print("Click on GP", gp)

def slider_changed(a,b):  
    print(a,b)

def create_gpio_in(root, gp):
    tk.Button(root, text="Click me", command=lambda: click(gp)).pack() 
    
    current_value=tk.StringVar()
    
    slider = ttk.Scale(
        root,
        from_=0,
        to=100,
        orient='vertical',
        variable=current_value,
        command=lambda x: slider_changed(gp, x),
    ).pack()

    

create_gpio_in(gp_frame[0], 0)
create_gpio_in(gp_frame[1], 1)
create_gpio_in(gp_frame[2], 2)
create_gpio_in(gp_frame[3], 3)



#-------------------------------


def initialize_gui_data():

    device_data["description"].set("MCP2221 USB-I2C/UART Combo")
    device_data["serial"].set("Serial: 01234567")
    device_data["manufacturer"].set("Microchip Technology Inc.")
    
    gp_func[0].set("GPIO_IN")
    gp_func[1].set("GPIO_IN")
    gp_func[2].set("GPIO_IN")
    gp_func[3].set("GPIO_IN")
    
    adc_vref.set("OFF")
    dac_vref.set("OFF")
    
    power_mgmnt.set("enabled")


initialize_gui_data()

try:
    from ctypes import windll
    #root.attributes('-toolwindow', True)
    #windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
