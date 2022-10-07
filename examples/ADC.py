# ADC input
# MCP2221 have one 10bit ADC with three channels connected to GP1, GP2 and GP3.
# The ADC is always running.
import EasyMCP2221
from time import sleep

# Connect to device
mcp = EasyMCP2221.Device()

# Use GP1, GP2 and GP3 as analog input.
mcp.set_pin_function(gp1 = "ADC", gp2 = "ADC", gp3 = "ADC")

# Configure ADC reference
# Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.
mcp.ADC_config(ref="VDD")

# Read ADC values
# (adc values are always available regardless of pin function, even if output)
while True:
    values = mcp.ADC_read()

    print("ADC0: %4.1f%%    ADC1: %4.1f%%    ADC2: %4.1f%%" %
        (
        values[0] / 1024 * 100,
        values[1] / 1024 * 100,
        values[2] / 1024 * 100,
        ))

    sleep(0.1)
