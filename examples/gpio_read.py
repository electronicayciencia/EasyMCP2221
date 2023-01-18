# GPIO input
import EasyMCP2221
from time import sleep

# Connect to device
mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp0 = "GPIO_IN",
    gp1 = "GPIO_IN",
    gp2 = "GPIO_IN",
    gp3 = "GPIO_IN")

while True:
    print(mcp.GPIO_read())
    sleep(0.1)

