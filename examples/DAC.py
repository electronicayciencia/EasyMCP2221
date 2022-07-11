# DAC output
# MCP2221 have only 1 DAC, connected to GP2 and/or GP3.
import sys
sys.path.append('../')
# ----------------------

import EasyMCP2221
from time import sleep

# Connect to device
mcp = EasyMCP2221.Device()

# Use GP2 and GP3 as DAC output.
mcp.set_pin_function(gp2 = "DAC", gp3 = "DAC")

# Configure DAC reference (max. output)
# Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.
mcp.ADC_config(ref="VDD")

while True:
    for v in range(0,32):
        mcp.DAC_write(v)
        sleep(0.01)
    
    for v in range(31,0,-1):
        mcp.DAC_write(v)
        sleep(0.01)

