# Test DAC output speed
import EasyMCP2221
from time import perf_counter

# Connect to device
mcp = EasyMCP2221.Device()

# Use GP2 and GP3 as DAC output.
mcp.set_pin_function(gp2 = "DAC", gp3 = "DAC")

# Configure DAC reference (max. output)
# Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.
mcp.DAC_config(ref="VDD")

n = 0
a = perf_counter()

while True:
    mcp.DAC_write(n % 32)
    n = n + 1

    t = perf_counter() - a

    if t >= 1:
        print("sps: %.1f" %(n / t))
        n = 0
        a = perf_counter()


