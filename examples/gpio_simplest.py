# This is to make examples work just by cloning the repo.
import sys
sys.path.append('../')
# ----------------------

# Simple example to show how to initialize class,
# set pin function and change value.
import EasyMCP2221

# Connect to device
mcp = EasyMCP2221.Device()

# Reclaim GP0 for General Purpose Input Output, as an Output.
# Default output is logical level 0.
mcp.set_pin_function(gp0 = "GPIO_OUT")

# Change it to logical 1
mcp.GPIO_write(gp0 = True)

