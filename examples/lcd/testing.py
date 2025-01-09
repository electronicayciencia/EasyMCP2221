# Drive a 16x02 LCD with an I2C interface via PCF8574.
# Using a custom driver.

from EasyMCP2221 import SMBus
from lcd_driver import LCD

bus = SMBus()
lcd = LCD(bus, addr=0x27)

bus.mcp.set_pin_function(
    gp0 = "GPIO_IN",  # unused
    gp1 = "GPIO_IN",  # unused
    gp2 = "GPIO_IN",  # unused
    gp3 = "LED_I2C")  # i2c traffic indicator


lcd.clear()

lcd.display_string("Electronica", 1)
lcd.display_string(" y ciencia   EyC", 2)

lcd.clear()

#                   1234567890123456
lcd.display_string(" Blog EyC  2023 ", 1)
lcd.display_string("                ", 2)

exit()

i = 1
while True:
    #lcd.display_string("Counter... %4d" % (i), 1)
    #lcd.display_string("Counter... %4d" % (i), 1)
    i = i + 1
