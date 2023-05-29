import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror

from EasyMCP2221.exceptions import NotAckError, TimeoutError, LowSCLError, LowSDAError
from threading import Thread

import logging
logger = logging.getLogger(__name__)


class I2Cscan_window(tk.Toplevel):

    def __init__(self, root, mcp):
        super().__init__(root)
        self.title("I2C Scan")

        x = root.winfo_x() + root.winfo_width() // 2 - 300 // 2
        y = root.winfo_y() + root.winfo_height() // 3 - 50 // 2
        self.geometry(f"+{x}+{y}")

        self.mcp = mcp

        self.devices_msg = []

        self.addr = tk.IntVar()

        # Scan status:
        # -1 : in progress
        #  0 : done, success
        #  1 : done, error
        self.scan_status = tk.IntVar()


        self.transient(root)
        self.grab_set()

        self.pb = ttk.Progressbar(self, orient="horizontal", length=250, mode="determinate")
        self.pb.pack(padx=5, pady=5)

        self.launch_scan()

        self.addr.trace("w", self.update_pb)
        self.scan_status.trace("w", self.show_devices)


    def update_pb(self, *args):
        self.pb["value"] = self.addr.get() / 0x80 * 100


    def launch_scan(self):
        self.scan_status.set(-1)
        t = Thread(target=self.scan)
        t.start()


    def show_devices(self, *args):
        if self.scan_status.get() == -1: # still in progress
            return

        if self.scan_status.get() == 0: # finished successfully
            if len(self.devices_msg) == 0:
                showinfo("I2C Scan result","No devices found.")
            else:
                showinfo("I2C Scan result","\n".join(self.devices_msg))

        self.destroy()


    def scan(self):
        for i in range(0, 0x80):
            self.addr.set(i)
            try:
                self.mcp.I2C_read(i)
                logger.info("I2C slave found at address 0x%02X" % (i))
                self.devices_msg.append("I2C slave found at address 0x%02X" % (i))
            except NotAckError:
                pass
            except (TimeoutError, LowSCLError, LowSDAError) as e:
                logger.warning("Error reading I2C bus." + str(e))
                showerror(title="I2C error", message=str(e))
                self.scan_status.set(1)
                return
            except RuntimeError as e:
                logger.warning("Error reading I2C bus." + str(e))
                showerror(title="I2C error", message="Error reading I2C bus.")
                self.scan_status.set(1)
                return

        self.scan_status.set(0)

