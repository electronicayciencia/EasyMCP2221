import tkinter as tk
from tkinter import ttk

class Func_GPIO_IN_frame(tk.Frame):

    def __init__(self, root, pin, sts):
        super().__init__(root)

        self.value = sts["in"][pin]

        self.status = tk.Label(self, relief="ridge", text="Unknown", bg="yellow", anchor="center")
        self.status.pack(fill=tk.X, ipady=10, pady=10, padx=10)

        self.value.trace("w", self.update_label)


    def update_label(self, *args):
        if self.value.get() == "1":
            self.status.config(text="HIGH", bg="red", fg="white")
        else:
            self.status.config(text="low", bg="green", fg="white")



class Func_GPIO_OUT_frame(tk.Frame):

    def __init__(self, root, pin, sts):
        super().__init__(root)

        self.pin = pin
        self.status = 0

        self.button = tk.Button(self, text="Change", command=self.change)
        self.button.pack(fill=tk.X, ipady=10, pady=10, padx=20)


    def change(self):
        self.status ^= 1

        if self.status == 1:
            self.button.configure(relief="sunken", text="HIGH", bg="red", fg="white", activebackground="red")

        else:
            self.button.configure(relief="raised", text="low", bg="green", fg="white", activebackground="green")

        print(f'set gpio {self.pin} to {self.status}')



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
            bg="black",
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

        else:
            v = val / 1024 * 100
            self.label["text"] = f'{v:2.1f}%'




class Func_DAC_frame(tk.Frame):
    """DAC value frame.
    
    Two pins can output DAC. But the DAC is common to both.
    """
    
    def __init__(self, root, sts):
        super().__init__(root)

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
            orient='vertical',
        )

        self.label = tk.Label(self,
            relief="ridge",
            text="-V",
            fg="black",
            bg="yellow",
            anchor="center",
            font=('Lucida Console', 16),
        )

        self.label.pack(fill=tk.X, ipady=5, pady=10, padx=10)
        self.slider.pack(pady=10, expand=True, fill=tk.Y)

        self.dac.trace('w', self.update_label)
        self.ref.trace('w', self.update_label)


    def update_slide(self, v):
        """Proxy function to force discrete steps on the slide."""
        v = round(float(v))
        self.dac.set(v)


    def update_label(self, *args):
        """Update DAC settings.

        Take DAC value from Slider StringVar.
        """

        if self.ref.get() == "OFF":
            self.slider["state"] = "disabled"
        else:
            self.slider["state"] = "active"

        # Skip updates unless something actually changes
        if self.dac.get() == self.last_dac and self.ref.get() == self.last_ref:
            return
        
        self.last_dac = self.dac.get()

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

        elif self.ref.get() == "VDD":
            v = d * 100 / 32
            self.label["text"] = f'{v:3.1f}%'

        else:
            self.label["text"] = "OFF"



class Func_CLK_OUT_frame(tk.Frame):

    def __init__(self, root, sts):
        super().__init__(root)

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
                        command=lambda arg=f: self.freq.set(arg),
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
                        command=lambda arg=d: self.duty.set(arg),
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


    def update_freq_buttons(self, *args):
        # Click the matching button and unclick the others
        f = self.freq.get()
        
        for btn in self.freq_buttons:
            if btn['text'] == f:
                btn['relief'] = "sunken"
                btn['bg'] = "red"
                btn['activebackground'] = "red"
            else:
                btn['relief'] = "raised"
                btn['bg'] = "lightblue"
                btn['activebackground'] = "lightblue"


    def update_duty_buttons(self, *args):
        d = self.duty.get()
        
        for btn in self.duty_buttons:
            if btn['text'] == f'{d}%':
                btn['relief'] = "sunken"
                btn['bg'] = "red"
                btn['activebackground'] = "red"
            else:
                btn['relief'] = "raised"
                btn['bg'] = "lightblue"
                btn['activebackground'] = "lightblue"



class Func_IOC_frame(tk.Frame):

    def __init__(self, root, sts):
        super().__init__(root)

        self.edge = tk.StringVar()

        tk.Label(self, text="Edge detection:").pack(padx=10, pady=10)
        
        r1 = ttk.Radiobutton(self, text='None',    value='none',    variable=self.edge)
        r2 = ttk.Radiobutton(self, text='Rising',  value='rising',  variable=self.edge)
        r3 = ttk.Radiobutton(self, text='Falling', value='falling', variable=self.edge)
        r4 = ttk.Radiobutton(self, text='Both',    value='both',    variable=self.edge)

        package = {
            "padx": 40,
            "pady": 10,
            "anchor": tk.W,
        }
        
        r1.pack(**package)
        r2.pack(**package)
        r3.pack(**package)
        r4.pack(**package)


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

