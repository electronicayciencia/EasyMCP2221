# Digital clock with two I2C chips:
# - DS1307 as RTC
# - LCD display based on with PCF8574 I2C adapter.

from EasyMCP2221 import SMBus
from lcd_driver import LCD
from DS1307 import DS1307

# Create SMBus and instances
bus = SMBus()
lcd = LCD(bus, addr=0x3F)
ds = DS1307(bus, addr=0x68)

# Do not create a new MCP Device to use other MCP2221 features in addition to I2C bus.
# It will interfere with existing bus resulting in unpredictable behavior.
# Always re-use bus.mcp object.
bus.mcp.I2C_speed(100_000) # DS1307 only supports 100kHz

bus.mcp.set_pin_function(
    gp0 = "GPIO_IN",  # unused
    gp1 = "IOC",      # trigger update LCD each second
    gp2 = "DAC",      # simulate backup battery
    gp3 = "LED_I2C")  # i2c traffic indicator

bus.mcp.DAC_write(21) # about 3.28V with 5V Vcc
bus.mcp.IOC_config(edge = "rising")

# Initialization after a complete power loss
if ds.halted():
    ds.write_now()
    ds._write(0x07, 0b0001_0000) # sqwe 1Hz
    print("RTC initialized with current timestamp")
else:
    print("RTC was already initialized")

lcd.clear()

# Update only when GP1 changes using Interrupt On Change
while True:
    if bus.mcp.IOC_read():
        bus.mcp.IOC_clear()
        (year, month, day, dow, hours, minutes, seconds) = ds.read_all()

        lcd.display_string("%02d/%02d/20%02d" % (day, month, year), 1)
        lcd.display_string("%02d:%02d:%02d" % (hours, minutes, seconds), 2)
