import EasyMCP2221
import EasyMCP2221
from EasyMCP2221 import SMBus
from time import sleep

bus = SMBus()

mcp = EasyMCP2221.Device()
mcp.set_pin_function(gp0 = "GPIO_OUT", out0 = 1)
mcp.GPIO_write(gp0 = False)
sleep(0.1)
mcp.GPIO_write(gp0 = True)
sleep(1)


mcp = EasyMCP2221.Device()
ds = mcp.I2C_Slave(0x68)

ds.write_register(0x00, 0)
