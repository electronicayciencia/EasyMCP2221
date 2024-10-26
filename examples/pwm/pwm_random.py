# One bit DAC (PWM output). 
# GP0 will be the output.
# Random approach:
#   Probability of an slot to be on is equal to on/slots
import EasyMCP2221
import random

# Actual frequency depends on USB mode
slots = 100

# Number of ON slots
on = 4


# Connect to the device
mcp = EasyMCP2221.Device()

mcp.set_pin_function(gp0 = "GPIO_OUT")

while True:
    i = random.randint(0, slots-1)

    if i < on:
        mcp.GPIO_write(gp0 = True)
    else:
        mcp.GPIO_write(gp0 = False)
    
