# V/V plotter DAC/ADC example.
import EasyMCP2221
from time import sleep
import matplotlib.pyplot as plt

# DAC output impedance is about 5k per step according to datasheet
# so measurements could be inaccurate as the current increases.
# Thus, we need GP1 to measure the actual DAC output.

mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp1 = "ADC",  # monitoring DAC output
    gp2 = "DAC",  # DAC output
    gp3 = "ADC")  # device voltage

# Configure device pins ADC and DAC reference.
mcp.DAC_config() # set Vref = Vdd
mcp.ADC_config() # set Vref = Vdd

Vr = 32 * [0]
Vd = 32 * [0]

for step in range(0,32):
    mcp.DAC_write(step)
    #sleep(0.05) # settle time

    (V1, _, V3) = mcp.ADC_read()

    # 10 bit, 5V ref
    Vr[step] = V1 / 1024 * 5
    Vd[step] = V3 / 1024 * 5

    print("Step: %2d of 32: Vr = %3.1fV,  Vd = %3.1fV" %
        (step+1, Vr[step], Vd[step]))


mcp.DAC_write(0)

plt.plot(Vr, Vd, 'o-')
plt.axis([0,5,0,5])
plt.xlabel("Vr (V)")
plt.ylabel("Vd (V)")
plt.title("Curve tracer")
plt.grid()
plt.show()

