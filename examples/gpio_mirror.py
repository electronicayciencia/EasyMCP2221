# GPIO output and input.
# GP0 is an output, but GP3 will be an input.
# The state of GP3 will mirror GP0.
import EasyMCP2221
from time import sleep

# Connect to device
mcp = EasyMCP2221.Device()

# GP0 and GP1 are inputs, GP2 and GP3 are outputs.
mcp.set_pin_function(
    gp0 = "GPIO_OUT",
    gp3 = "GPIO_IN")

while True:
    inputs = mcp.GPIO_read()
    mcp.GPIO_write(
        gp0 = inputs[3])

