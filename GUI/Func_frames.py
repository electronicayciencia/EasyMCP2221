import tkinter as tk
from tkinter import ttk

class Func_GPIO_IN_frame(tk.Frame):

    def __init__(self, root):
        super().__init__(root)

        self.status = tk.Label(self, text="Unknown", bg="yellow", anchor="center")
        self.status.pack(fill=tk.X, ipady=10)

    def high(self):
        self.status.config(text="HIGH", bg="red", fg="white")
    
    def low(self):
        self.status.config(text="low", bg="green", fg="white")


class Func_GPIO_OUT_frame(tk.Frame):

    def __init__(self, root):
        super().__init__(root)

        self.status = tk.Label(self, text="Unknown", bg="yellow")
        self.status.pack()
