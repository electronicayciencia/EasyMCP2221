import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning

root = tk.Tk()
root.title('Pack Demo')
root.geometry("300x200")

package = {
    'padx': 10, 
    'pady': 10, 
    'expand': True, 
    'fill': tk.BOTH, 
    'side': tk.LEFT,
}

top_frame = tk.Frame(root)
top_frame.pack(expand=False, fill=tk.BOTH, side=tk.TOP)

bottom_frame = tk.Frame(root)
bottom_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)


label1 = tk.Label(top_frame, text="Box 1\nline\nline", bg="red", fg="white")
label2 = tk.Label(top_frame, text='Box 2', bg="green", fg="white")
label3 = tk.Label(bottom_frame, text='Box 33333333', bg="blue", fg="white")
label4 = tk.Label(bottom_frame, text='Box 4', bg="cyan", fg="black")
label5 = tk.Label(bottom_frame, text='Box 5', bg="magenta", fg="black")
label6 = tk.Label(bottom_frame, text='Box 6', bg="yellow", fg="black")

label1.pack(**package)
label2.pack(**package)
label3.pack(**package)
label4.pack(**package)
label5.pack(**package)
label6.pack(**package)

try:
    from ctypes import windll
    #root.attributes('-toolwindow', True)
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
