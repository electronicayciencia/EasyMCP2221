# One bit DAC (PWM output). 
# GP0 will be the output.
# Naive approach:
#   0-i slots On
#   remaining slots Off
import EasyMCP2221

# Actual frequency depends on USB mode
slots = 100

# Number of ON slots
on = 4


# Connect to the device
mcp = EasyMCP2221.Device()

mcp.set_pin_function(gp0 = "GPIO_OUT")

while True:
    for i in range(slots):
        if i < on:
            mcp.GPIO_write(gp0 = True)
        else:
            mcp.GPIO_write(gp0 = False)

