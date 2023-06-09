# Digital clock with a DS1307 and LCD dysplay
from EasyMCP2221 import SMBus
from lcd_driver import LCD

bus = SMBus(1)
lcd = LCD(bus)

lcd.clear()
lcd.display_string("hola", 1)

