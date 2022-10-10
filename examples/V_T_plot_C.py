# Plotter for capacitor change/discharge
import EasyMCP2221
import time
import matplotlib.pyplot as plt
import numpy as np

capture_time = 1
Vdd = 5

# Configure device pins
mcp = EasyMCP2221.Device()
mcp.ADC_config()
mcp.set_pin_function(gp2 = "GPIO_OUT", gp3 = "ADC")

V = []
T = []

print("Initial discharge on course. Press enter to start charging.")
mcp.GPIO_write(gp2 = False)

input()
print("Charging...")
mcp.GPIO_write(gp2 = True)

start = time.perf_counter()

while time.perf_counter() - start <= capture_time:

    t = time.perf_counter()
    (_, _, V3) = mcp.ADC_read()

    # 10 bit, 5V ref
    V3 = V3 / 1024 * Vdd

    T.append(t - start)
    V.append(V3)


mcp.GPIO_write(gp2 = False)


plt.plot(T, V, 'o-')
plt.axis([-0.05, capture_time, 0, Vdd + 0.5])
plt.xticks(np.arange(0,capture_time,0.1))
plt.xlabel("Time (s)")
plt.ylabel("V (V)")
plt.title("Capacitor charge plot")
plt.grid()
plt.show()

