import tkinter as tk
from tkinter import ttk

import logging
logger = logging.getLogger(__name__)

class Func_GPIO_IN_frame(tk.Frame):

    def __init__(self, root, pin, sts):
        super().__init__(root)

        self.value = sts["in"][pin]

        self.status = tk.Label(self, relief="ridge", text="Unknown", bg="yellow2", anchor="center")
        self.status.pack(fill=tk.X, ipady=10, pady=10, padx=10)

        self.value.trace("w", self.update_label)


    def update_label(self, *args):
        if self.value.get() == "1":
            self.status.config(text="HIGH", bg="red2", fg="white")
        else:
            self.status.config(text="low", bg="green", fg="white")



class Func_GPIO_OUT_frame(tk.Frame):

    def __init__(self, root, pin, sts, mcp):
        super().__init__(root)

        self.pin = pin
        self.mcp = mcp
        self.status = sts["out"][pin]

        self.button = tk.Button(self, text="Change", command=self.toogle)
        self.button.pack(fill=tk.X, ipady=10, pady=10, padx=20)

        self.status.trace("w", self.update_button)

    def toogle(self):
        l = int(self.status.get())
        l ^= 1
        self.status.set(l)

        if self.pin == 0: self.mcp.GPIO_write(gp0 = l)
        if self.pin == 1: self.mcp.GPIO_write(gp1 = l)
        if self.pin == 2: self.mcp.GPIO_write(gp2 = l)
        if self.pin == 3: self.mcp.GPIO_write(gp3 = l)
        logger.info(f'Set pin {self.pin} to {l}')

    def update_button(self, *args):
        if self.status.get() == "1":
            self.button.configure(relief="sunken", text="HIGH", bg="red2", fg="white", activebackground="red2")
        else:
            self.button.configure(relief="raised", text="low", bg="green", fg="white", activebackground="green")



class Func_ADC_frame(tk.Frame):

    def __init__(self, root, pin, sts):
        super().__init__(root)

        self.ref = sts["adc_ref"]
        self.val = sts["adc"][pin-1] # ADC0 in GP1

        self.pb = ttk.Progressbar(
            self,
            orient = 'vertical',
            mode = 'determinate',
            length = 300,
        )

        self.label = tk.Label(self,
            relief="ridge",
            text="-V",
            fg="red",
            bg="gray10",
            anchor="center",
            font=('Lucida Console', 16),
        )

        self.label.pack(fill=tk.X, ipady=5, pady=10, padx=10)
        self.pb.pack(pady=10)

        self.val.trace("w", self.update_view)
        self.ref.trace("w", self.update_view)


    def update_view(self, *args):
        """Update ADC label and bar."""
        val = int(self.val.get())
        ref = self.ref.get()

        if ref == "OFF":
            self.label["text"] = "OFF"
            self.pb["value"] = 0
            return

        self.pb["value"] = val / 1024 * 100

        if ref == "1.024V":
            v = val * 1.024 / 1024
            self.label["text"] = f'{v:1.3f}V'

        elif ref == "2.048V":
            v = val * 2.048 / 1024
            self.label["text"] = f'{v:1.3f}V'

        elif ref == "4.096V":
            v = val * 4.096 / 1024
            self.label["text"] = f'{v:1.3f}V'

        elif ref == "VDD (3.3V)":
            v = val * 3.3 / 1024
            self.label["text"] = f'{v:1.3f}V'

        elif ref == "VDD (5V)":
            v = val * 5 / 1024
            self.label["text"] = f'{v:1.3f}V'

        else:
            v = val * 100 / 1024
            self.label["text"] = f'{v:2.1f}%'




class Func_DAC_frame(tk.Frame):
    """DAC value frame.

    Two pins can output DAC. But the DAC is common to both.
    """

    def __init__(self, root, sts, mcp):
        super().__init__(root)

        self.mcp = mcp

        self.ref = sts["dac_ref"]
        self.dac = sts["dac"]
        self.last_dac = 0
        self.last_ref = 0

        self.slider = tk.Scale(
            self,
            from_=31,
            to=0,
            length=290,
            variable=self.dac,
            command=self.updated_slide,
            orient='vertical',
        )

        self.label = tk.Label(self,
            relief="ridge",
            text="-V",
            fg="black",
            bg="yellow2",
            anchor="center",
            font=('Lucida Console', 16),
        )

        self.label.pack(fill=tk.X, ipady=5, pady=10, padx=10)
        self.slider.pack(pady=10, expand=True, fill=tk.Y)

        self.dac.trace('w', self.update_label)
        self.ref.trace('w', self.update_label)


    def updated_slide(self, v):
        """Proxy function to force discrete steps on the slide."""

        v = round(float(v))
        self.dac.set(v)

        # Skip updates unless something actually changes
        if self.dac.get() == self.last_dac and self.ref.get() == self.last_ref:
            return

        self.last_dac = self.dac.get()

        logger.info(f'Set dac to {v}')
        self.mcp.DAC_write(v)


    def update_label(self, *args):
        """Update DAC settings.

        Take DAC value from Slider StringVar.
        """

        if self.ref.get() == "OFF":
            self.slider["state"] = "disabled"
        else:
            self.slider["state"] = "active"


        d = int(float(self.dac.get()))

        if self.ref.get() == "1.024V":
            v = d * 1.024 / 32
            self.label["text"] = f'{v:1.3f}V'

        elif self.ref.get() == "2.048V":
            v = d * 2.048 / 32
            self.label["text"] = f'{v:1.3f}V'

        elif self.ref.get() == "4.096V":
            v = d * 4.096 / 32
            self.label["text"] = f'{v:1.2f}V'

        elif self.ref.get() == "VDD (5V)":
            v = d * 5 / 32
            self.label["text"] = f'{v:1.2f}V'
            
        elif self.ref.get() == "VDD (3.3V)":
            v = d * 3.3 / 32
            self.label["text"] = f'{v:1.3f}V'

        elif self.ref.get() == "VDD":
            v = d * 100 / 32
            self.label["text"] = f'{v:3.1f}%'
        else:
            self.label["text"] = "OFF"



class Func_CLK_OUT_frame(tk.Frame):

    def __init__(self, root, sts, mcp):
        super().__init__(root)

        self.mcp = mcp

        self.freq = sts["clk"]["freq"]
        self.duty = sts["clk"]["duty"]

        freq_frame = tk.Frame(self)
        duty_frame = tk.Frame(self)

        freq_frame.pack(pady=10)
        duty_frame.pack(pady=10)


        freqs = ("375kHz", "750kHz", "1.5MHz", "3MHz", "6MHz", "12MHz", "24MHz")
        duties = (0, 25, 50, 75)

        self.freq_buttons = []
        self.duty_buttons = []

        for f in freqs:
            button = tk.Button(freq_frame,
                        text=f,
                        command=lambda arg=f: self.set_freq(arg),
                        anchor=tk.E,
                        bg = "lightblue",
                        activebackground="lightblue",
                        padx=5,
                    )

            button.pack(pady=1, fill=tk.X)
            self.freq_buttons.append(button)


        for d in duties:
            button = tk.Button(duty_frame,
                        text=f'{d}%',
                        command=lambda arg=d: self.set_duty(arg),
                        anchor=tk.E,
                        bg = "lightblue",
                        activebackground="lightblue",
                        padx=5,
                    )

            self.duty_buttons.append(button)
            button.pack(pady=1, fill=tk.X)

        # Update buttons when some parameter changes
        self.freq.trace("w", self.update_freq_buttons)
        self.duty.trace("w", self.update_duty_buttons)


    def set_freq(self, freq):
        self.freq.set(freq)
        self.reconfig_clk()

    def set_duty(self, duty):
        self.duty.set(duty)
        self.reconfig_clk()

    def reconfig_clk(self):
        duty = int(self.duty.get())
        freq = self.freq.get()
        self.mcp.clock_config(duty, freq)
        logger.info(f'Reconfigure clock: Duty {duty}, frequency {freq}.')

    def update_freq_buttons(self, *args):
        # Click the matching button and unclick the others
        f = self.freq.get()

        for btn in self.freq_buttons:
            if btn['text'] == f:
                btn['relief'] = "sunken"
                btn['bg'] = "turquoise1"
                btn['activebackground'] = "turquoise1"
            else:
                btn['relief'] = "raised"
                btn['bg'] = "lightblue"
                btn['activebackground'] = "lightblue"


    def update_duty_buttons(self, *args):
        d = self.duty.get()

        for btn in self.duty_buttons:
            if btn['text'] == f'{d}%':
                btn['relief'] = "sunken"
                btn['bg'] = "turquoise1"
                btn['activebackground'] = "turquoise1"
            else:
                btn['relief'] = "raised"
                btn['bg'] = "lightblue"
                btn['activebackground'] = "lightblue"



class Func_IOC_frame(tk.Frame):

    def __init__(self, root, sts, mcp):
        super().__init__(root)

        self.mcp = mcp
        self.edge = sts["ioc"]
        self.int  = sts["int"]

        edge_frame = tk.Frame(self)
        int_frame  = tk.Frame(self)

        edge_frame.pack(padx=10, pady=10, fill=tk.X)
        int_frame.pack(padx=10, pady=10, fill=tk.X)

        # Edge select frame
        self.pos_button = tk.Button(edge_frame,
                    text="Rising edge",
                    command=self.toogle_pos_edge,
                    bg = "lightblue",
                    activebackground="lightblue",
                    padx=5,
                )
        
        self.neg_button = tk.Button(edge_frame,
                    text="Falling edge",
                    command=self.toogle_neg_edge,
                    bg = "lightblue",
                    activebackground="lightblue",
                    padx=5,
                )

        self.pos_button.pack(fill=tk.X, padx=10, pady=2)
        self.neg_button.pack(fill=tk.X, padx=10, pady=2)

        self.edge.trace("w", self.update_edge_buttons)

        # Interrupt detector frame
        self.status = tk.Label(int_frame, relief="ridge", text="Unknown", bg="yellow2", anchor="center")
        self.status.pack(fill=tk.X, ipady=10, pady=10, padx=10)

        tk.Button(int_frame,
                    text="Clear",
                    command=self.IOC_clear,
                    padx=5).pack(fill=tk.X, padx=10, pady=2)

        self.int.trace("w", self.update_label)


    def update_label(self, *args):
        if self.int.get() == "1":
            self.status.config(text="FIRED!", bg="red2", fg="white")
        else:
            self.status.config(text="waiting...", bg="lightgrey", fg="black")


    def toogle_neg_edge(self):
        edge = self.edge.get()
        if   edge == "none"   : edge = "falling"
        elif edge == "rising" : edge = "both" 
        elif edge == "falling": edge = "none" 
        elif edge == "both"   : edge = "rising" 
        self.edge.set(edge)
        self.IOC_config()

    def toogle_pos_edge(self):
        edge = self.edge.get()
        if   edge == "none"   : edge = "rising"
        elif edge == "rising" : edge = "none" 
        elif edge == "falling": edge = "both" 
        elif edge == "both"   : edge = "falling" 
        self.edge.set(edge)
        self.IOC_config()


    def update_edge_buttons(self, *args):
        edge = self.edge.get()

        if edge in ("rising", "both"):
            self.pos_button['relief'] = "sunken"
            self.pos_button['bg'] = "turquoise1"
            self.pos_button['activebackground'] = "turquoise1"
        else:
            self.pos_button['relief'] = "raised"
            self.pos_button['bg'] = "lightblue"
            self.pos_button['activebackground'] = "lightblue"
        
        if edge in ("falling", "both"):
            self.neg_button['relief'] = "sunken"
            self.neg_button['bg'] = "turquoise1"
            self.neg_button['activebackground'] = "turquoise1"
        else:    
            self.neg_button['relief'] = "raised"
            self.neg_button['bg'] = "lightblue"
            self.neg_button['activebackground'] = "lightblue"


    def IOC_config(self):
        edge = self.edge.get()
        self.mcp.IOC_config(edge)
        logger.info(f'Set IOC to {edge}')

    def IOC_clear(self):
        edge = self.edge.get()
        self.mcp.IOC_clear()
        logger.info("Clear IOC flag")



class Func_GENERIC_frame(tk.Frame):

    def __init__(self, root, kind):
        super().__init__(root)

        description = {
            "SSPND"   : "Signals when the host has entered in Suspend mode.",
            "LED_URX" : "UART Rx LED activity output.",
            "LED_UTX" : "UART Tx LED activity output.",
            "USBCFG"  : "USB device configured status.",
            "LED_I2C" : "USB/I2C traffic indicator.",
        }

        l = tk.Label(self, text=description[kind], wraplength=100)
        l.pack(padx=10, pady=10, expand=True, anchor=tk.N, fill=tk.X)

