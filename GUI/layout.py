import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning



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



class Device_frame(ttk.Labelframe):
    """Populate device data frame."""

    def __init__(self, root):
        super().__init__(root)

        self["text"] = " Device "
    
        self.data = {
            "description"  : tk.StringVar(),
            "serial"       : tk.StringVar(),
            "manufacturer" : tk.StringVar(),
        }
    
        ttk.Label(self, textvariable=self.data["description"], font="Helvetica, 14").pack(anchor=tk.W, pady=2, padx=5)
        ttk.Label(self, textvariable=self.data["serial"]).pack(anchor=tk.W, pady=2, padx=5)
        ttk.Label(self, textvariable=self.data["manufacturer"]).pack(anchor=tk.W, pady=2, padx=5)



class GP_frame(ttk.Labelframe):
    """Create each of the 4 GPIO frames."""

    def __init__(self, root, pin):
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
        self.func = tk.StringVar()
        ttk.OptionMenu(self, self.func, None, *self.pin_funcs, command=self.gp_func_updated).pack(fill=tk.X, pady=10, padx=2)

        f = GPIO_IN_frame(self)
        f.pack()


    def gp_func_updated(self, func):
        print("New GP%s function is %s." % (self.pin, func))
        
    


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        
        self.title('EasyMCP2221 utility')
        #root.geometry("800x600")

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
            "ipadx": 5,
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
        print("Quit!")
    
    def reset_click(self):
        print("Reset")
    
    def i2cscan_click(self):
        print("I2C Scan")



class GPIO_IN_frame(tk.Frame):

    def __init__(self, root):
        super().__init__(root)
        
        self.status = tk.Label(self, text="Unknown", bg="yellow")
        
        self.status.pack()




#-------------------------------
#
#-------------------------------

#-------------------------------
# Create auxiliary frames for any GPIO



#def click(gp):
#    print("Click on GP", gp)
#
#def slider_changed(a,b):  
#    print(a,b)
#
#def create_gpio_in(root, gp):
#    tk.Button(root, text="Click me", command=lambda: click(gp)).pack() 
#    
#    current_value=tk.StringVar()
#    
#    slider = ttk.Scale(
#        root,
#        from_=0,
#        to=100,
#        orient='vertical',
#        variable=current_value,
#        command=lambda x: slider_changed(gp, x),
#    ).pack()
#
#    
#
#create_gpio_in(gp_frame[0], 0)
#create_gpio_in(gp_frame[1], 1)
#create_gpio_in(gp_frame[2], 2)
#create_gpio_in(gp_frame[3], 3)
#


#-------------------------------



    
app = App()
app.initialize_gui_data()

try:
    from ctypes import windll
    #root.attributes('-toolwindow', True)
    #windll.shcore.SetProcessDpiAwareness(1)
finally:
    app.mainloop()
