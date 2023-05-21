import tkinter as tk


root = tk.Tk()

message = tk.Label(root, text="Hello, World!")
message.pack()



try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
finally:
    root.mainloop()
