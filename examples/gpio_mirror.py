# This is to make examples work just by cloning the repo.
import sys
sys.path.append('../')
# ----------------------

# GPIO output and input.
# GP0 and GP1 are inputs, GP2 and GP3 are outputs.
# The state of GP2 and GP3 mirror GP0 and GP1.
# Connect 2 leds to the outputs and 2 buttons to the inputs.
import sys
sys.path.append('../')

import EasyMCP2221
from time import sleep

# Connect to device
mcp = EasyMCP2221.Device()

# GP0 and GP1 are inputs, GP2 and GP3 are outputs.
mcp.set_pin_function(
    gp0 = "GPIO_IN",
    gp1 = "GPIO_IN",
    gp2 = "GPIO_OUT",
    gp3 = "GPIO_OUT")

while True:
    inputs = mcp.GPIO_read()
    mcp.GPIO_write(
        gp2 = inputs[0],
        gp3 = inputs[1])

