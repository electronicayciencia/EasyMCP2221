import tkinter as tk
from tkinter import ttk

class Func_GPIO_IN_frame(tk.Frame):

    def __init__(self, root):
        super().__init__(root)

        self.status = tk.Label(self, relief="groove", text="Unknown", bg="yellow", anchor="center")
        self.status.pack(fill=tk.X, ipady=10, pady=10, padx=10)

    def high(self):
        self.status.config(text="HIGH", bg="red", fg="white")

    def low(self):
        self.status.config(text="low", bg="green", fg="white")



class Func_GPIO_OUT_frame(tk.Frame):

    def __init__(self, root, pin):
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

    def __init__(self, root):
        super().__init__(root)

        self.ref = "OFF"

        self.pb = ttk.Progressbar(
            root,
            orient = 'vertical',
            mode = 'determinate',
            length = 300,
        )
        self.pb.pack(pady=10)

        self.label = tk.Label(self, 
            relief="flat", 
            text="-V", 
            fg="red", 
            bg="black", 
            anchor="center",
            font=('Lucida Console', 16),
        )
        
        self.label.pack(fill=tk.X, ipady=5, pady=10, padx=10)

    def update(self, d):
        """Update ADC reading. 
        
        d: reading from 0 to 1023
        """
        
        if self.ref == "1.024V":
            v = d * 1.024 / 1024
            self.pb["value"] = d / 1024 * 100
            self.label["text"] = f'{v:1.3f}V'

        elif self.ref == "2.048V":
            v = d * 2.048 / 1024
            self.pb["value"] = d / 1024 * 100
            self.label["text"] = f'{v:1.3f}V'

        elif self.ref == "4.096V":
            v = d * 4.096 / 1024
            self.pb["value"] = d / 1024 * 100
            self.label["text"] = f'{v:1.2f}V'
        
        elif self.ref == "VDD":
            v = d * 100 / 1024
            self.pb["value"] = v
            self.label["text"] = f'{v:3.2f}%'

        else:
            self.label["text"] = "OFF"
            self.pb["value"] = 0



class Func_DAC_frame(tk.Frame):

    def __init__(self, root):
        super().__init__(root)

        self.ref = "OFF"
        self.dac = tk.StringVar()
        self.last_dac = 0

        self.slider = tk.Scale(
            root,
            from_=31,
            to=0,
            command=self.update_slide,
            length=290,
            variable=self.dac,
            orient='vertical',
        )
        self.slider.pack(pady=10, expand=True, fill=tk.Y)

        self.label = tk.Label(self, 
            relief="flat", 
            text="-V", 
            fg="black", 
            bg="yellow", 
            anchor="center",
            font=('Lucida Console', 16),
        )
        
        self.label.pack(fill=tk.X, ipady=5, pady=10, padx=10)


    def update_slide(self, v):
        """Proxy function to force discrete steps on the slide."""
        v = round(float(v))
        self.dac.set(v)
        if v != self.last_dac:
            self.last_dac = v
            self.update()


    def update(self):
        """Update DAC settings. 
        
        Take DAC value from Slider StringVar.
        """
        
        d = int(float(self.dac.get()))
        
        if self.ref == "1.024V":
            v = d * 1.024 / 32
            self.label["text"] = f'{v:1.3f}V'
            print("Set DAC to", d)

        elif self.ref == "2.048V":
            v = d * 2.048 / 32
            self.label["text"] = f'{v:1.3f}V'
            print("Set DAC to", d)

        elif self.ref == "4.096V":
            v = d * 4.096 / 32
            self.label["text"] = f'{v:1.2f}V'
            print("Set DAC to", d)

        elif self.ref == "VDD":
            v = d * 100 / 32
            self.label["text"] = f'{v:3.2f}%'
            print("Set DAC to", d)

        else:
            self.label["text"] = "OFF"
            print("Set DAC to OFF")


