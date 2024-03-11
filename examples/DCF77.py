# DCF77 radio-clock module
import EasyMCP2221
from time import perf_counter
import numpy as np

outfile = "d:/tmp/times.npy"

try:
    values = np.load(outfile)
except:
    values = np.array([])


# Connect to device
mcp = EasyMCP2221.Device()

# Input on GP1
mcp.set_pin_function(
    gp0 = "GPIO_IN"
)

gp0_old = 0;
gp0_last_change = perf_counter()

while True:
    try:
        gp0 = mcp.GPIO_read()[0]

        if gp0 != gp0_old:
            now = perf_counter()
            elapsed = now - gp0_last_change
            
            gp0_old = gp0
            gp0_last_change = now

            values = np.append(values, elapsed)

            print("%.2f" % elapsed)

    except BaseException as e:
        break

np.save(outfile, values)

print(values.size, "values saved to", outfile)

