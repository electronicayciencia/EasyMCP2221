# Digital clock with a DS1307 and LCD display with PCF8574 I2C adapter.
from EasyMCP2221 import SMBus
from lcd_driver import LCD
from DS1307 import DS1307


bus = SMBus(1)
lcd = LCD(bus)
ds = DS1307(bus)


lcd.clear()
#lcd.display_string("hola", 1)

print(ds.read_datetime())

if ds.halted():
    ds.write_now()
    
print(ds.read_datetime())

