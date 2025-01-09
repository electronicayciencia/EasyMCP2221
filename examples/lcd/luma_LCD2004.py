# Drive a 16x02 LCD with an I2C interface via PCF8574.
# Using the Luma library.

from EasyMCP2221 import SMBus
from luma.core.interface.serial import pcf8574
from luma.lcd.device import hd44780

bus = SMBus()

interface = pcf8574(bus=bus, address=0x27, backlight_enabled=True)
device = hd44780(interface, width=16, height=2)

i = 0
while True:
    device.text = "Counting... %d" % i
    i = i + 1
