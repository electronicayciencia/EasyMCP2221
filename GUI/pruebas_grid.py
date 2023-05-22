import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning

root = tk.Tk()
root.title('Grid Demo')
root.geometry("600x600")


root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=3)

root.columnconfigure(0, weight=1, uniform="gpio")
root.columnconfigure(1, weight=1, uniform="gpio")
root.columnconfigure(2, weight=1, uniform="gpio")
root.columnconfigure(3, weight=1, uniform="gpio")


label1 = tk.Label(root, text="Box 1", bg="red", fg="white")
label2 = tk.Label(root, text='Box 2', bg="green", fg="white")
label3 = tk.Label(root, text='Box 3', bg="blue", fg="white")
label4 = tk.Label(root, text='Box 4', bg="cyan", fg="black")
label5 = tk.Label(root, text='Box 5', bg="magenta", fg="black")
label6 = tk.Label(root, text='Box 6', bg="yellow", fg="black")

gridding = {
    'sticky': "nsew", 
    'padx': 10, 
    'pady': 10, 
}

label1.grid(row=0, column=0, columnspan=2, **gridding)
label2.grid(row=0, column=2, columnspan=2, **gridding)
label3.grid(row=1, column=0, **gridding)
label4.grid(row=1, column=1, **gridding)
label5.grid(row=1, column=2, **gridding)
label6.grid(row=1, column=3, **gridding)





try:
    from ctypes import windll
    #root.attributes('-toolwindow', True)
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
