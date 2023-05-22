import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning


root = tk.Tk()
root.title('Grid Demo')
root.geometry("600x600")

gridding = {
    'sticky': "nsew", 
    'padx': 10, 
    'pady': 10, 
}


root.rowconfigure(0, weight=1, uniform="row")
root.rowconfigure(1, weight=3, uniform="row")

root.columnconfigure(0, weight=1, uniform="gpio")
root.columnconfigure(1, weight=1, uniform="gpio")
root.columnconfigure(2, weight=1, uniform="gpio")
root.columnconfigure(3, weight=1, uniform="gpio")

topframe=tk.Frame(root, bg="white")
topframe.grid(row=0, column=0, columnspan=4, **gridding)

label1 = tk.Label(topframe, text="Box 11111111111111", bg="red", fg="white")
label2 = tk.Label(topframe, text='Box 222222222222222222', bg="green", fg="white")
label3 = tk.Label(root, text='Box 333333333333', bg="blue", fg="white")
label4 = tk.Label(root, text='Box 4', bg="cyan", fg="black")
label5 = tk.Label(root, text='Box 5', bg="magenta", fg="black")
label6 = tk.Label(root, text='Box 6', bg="yellow", fg="black")

label1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
label2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
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
