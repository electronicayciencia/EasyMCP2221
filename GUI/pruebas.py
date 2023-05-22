import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror, showwarning

root = tk.Tk()
root.title('Grid Demo')
root.geometry("600x600")

gridding = {
    'sticky': tk.NSEW,
}


top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X)

frame1 = ttk.Labelframe(top_frame, text=" Box 1 ")
label2 = tk.Label(top_frame, text='Box 2', bg="green", fg="white")

frame1.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
label2.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)


bot_frame = tk.Frame(root)
bot_frame.pack(expand=True, fill=tk.BOTH)

bot_frame.columnconfigure(0, weight=1, uniform="gpio")
bot_frame.columnconfigure(1, weight=1, uniform="gpio")
bot_frame.columnconfigure(2, weight=1, uniform="gpio")
bot_frame.columnconfigure(3, weight=1, uniform="gpio")

label3 = tk.Label(bot_frame, text='Box 3', bg="blue", fg="white")
label4 = tk.Label(bot_frame, text='Box 4', bg="cyan", fg="black")
label5 = tk.Label(bot_frame, text='Box 5', bg="magenta", fg="black")
label6 = tk.Label(bot_frame, text='Box 6', bg="yellow", fg="black")

label3.grid(row=0, column=0, sticky=tk.NS)
label4.grid(row=0, column=1, **gridding)
label5.grid(row=0, column=2, **gridding)
label6.grid(row=0, column=3, **gridding)

label7 = tk.Label(frame1, text='Box 7444444444444444444444444444444', bg="green", fg="white")
label7.pack()


try:
    from ctypes import windll
    #root.attributes('-toolwindow', True)
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
