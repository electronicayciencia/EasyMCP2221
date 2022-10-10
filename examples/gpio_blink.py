# How to blink a LED connected to GP0
import EasyMCP2221
from time import sleep

# Connect to device
mcp = EasyMCP2221.Device()

# Reclaim GP0 for General Purpose Input Output, as an Output.
# Default output is logical level 0.
mcp.set_pin_function(gp2 = "GPIO_OUT")

while True:
    mcp.GPIO_write(gp2 = True)
    sleep(0.5)
    mcp.GPIO_write(gp2 = False)
    sleep(0.5)

