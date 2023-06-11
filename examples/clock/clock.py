# Digital clock with a DS1307 and LCD display with PCF8574 I2C adapter.
from EasyMCP2221 import SMBus
from lcd_driver import LCD
from DS1307 import DS1307
from time import sleep

bus = SMBus()
#lcd = LCD(bus, addr=0x3F)
ds = DS1307(bus, addr=0x68)


#lcd.clear()
#lcd.display_string("hola", 1)

#print(ds.read_datetime())

#if ds.halted():
#    ds.write_now()
    
#print(ds.read_datetime())

#minutes = ds._read_minutes()
#print(f'minutes {minutes:02d}')
#
#ds.write_all(minutes = 23)
#minutes = ds._read_minutes()
#print(f'minutes {minutes:02d}')

ds._read(0x00)
ds._write(0x00,0x00)
while True:
    ds._read(0x00)
    sleep(0.1)


