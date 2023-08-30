# Plotter for capacitor change/discharge
import EasyMCP2221
import time
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np

capture_time = 1

# Configure device pins
mcp = EasyMCP2221.Device()
mcp.set_pin_function(
    gp2 = "GPIO_OUT",
    gp3 = "ADC")

mcp.ADC_config()

V = []
T = []

print("Discharging...")
mcp.GPIO_write(gp2 = False)

while mcp.ADC_read()[2] / 1024:
    pass

print("Charging...")
mcp.GPIO_write(gp2 = True)

start = time.perf_counter()

while time.perf_counter() - start <= capture_time:

    t = time.perf_counter()
    Vc = mcp.ADC_read()[2]

    # 10 bit
    Vc = Vc / 1024 * 100

    T.append(t - start)
    V.append(Vc)


mcp.GPIO_write(gp2 = False)

plt.plot(T, V, 'o-')
plt.axis([-0.05, capture_time, 0, 105])
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())
plt.gca().xaxis.set_major_locator(mtick.MultipleLocator(0.1))

#plt.xticks(np.arange(0,capture_time,0.1))
plt.xlabel("Time (s)")
plt.ylabel("V (%)")
plt.title("Capacitor charge plot")

# 1st RC line
plt.axhline(y = 100 * (1-1/math.e) , color='g', linestyle='dotted')

plt.grid()
plt.show()
