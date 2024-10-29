# Plot a rolling window of GP1 ADC input
import EasyMCP2221
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

SR = 30   # Sample rate in frames per second (Hz)
N = 5*SR  # number of samples to store, aprox 5 seconds

# Connect to device
mcp = EasyMCP2221.Device()

# Use GP1, GP2 and GP3 as analog input.
mcp.set_pin_function(gp1 = "ADC", gp2 = "ADC", gp3 = "ADC")

# Configure ADC reference
mcp.ADC_config(ref="VDD")

# Array variables Voltage and Time
V = deque(maxlen=N)
T = deque(maxlen=N)

# Create figure
fig = plt.figure()
ax  = plt.axes()

# Set options
ax.set_ylim(0, 100)
ax.set_xlabel("Time (s)")
ax.set_ylabel("V (%)")
ax.set_title("ADC reading")
ax.grid(axis='y')

line, = ax.plot(T, V, 'o-')

def animate(i):
    t = time.perf_counter()
    v = mcp.ADC_read()[0] / 1024 * 100

    T.append(t)
    V.append(v)

    ax.relim()
    ax.autoscale_view()
    line.set_data(T, V)


# Start animation
ani = animation.FuncAnimation(fig, animate, interval=1/SR*1000)
plt.show()
