# GPIO input
import EasyMCP2221
from time import sleep

# Connect to device
mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp0 = "GPIO_OUT", out0 = True,
    gp1 = "GPIO_OUT", out1 = True,
    gp2 = "DAC", 
    gp3 = "DAC")

mcp.DAC_config(ref = "VDD")
mcp.DAC_write(16)

