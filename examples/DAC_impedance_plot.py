# Plot DAC voltage vs. DAC expected voltage wen there is a load
import EasyMCP2221
from time import sleep
import math
import matplotlib.pyplot as plt

# DAC output impedance is about 5k per step according to datasheet
# so measurements could be inaccurate as the current increases.
# Thus, we need GP1 to measure the actual DAC output.

mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp1 = "ADC",  # monitoring DAC output
    gp2 = "DAC")  # DAC output

# Configure device pins ADC and DAC reference.
mcp.DAC_config() # set Vref = Vdd
mcp.ADC_config() # set Vref = Vdd

ADCref = 5
DACref = 5
Rload = 19.7e3

Vexp = 32 * [0]
Vact = 32 * [0]
Imp  = 32 * [0]

for step in range(0,32):
    mcp.DAC_write(step)

    adc = mcp.ADC_read()[0]

    # 10 bit, 5V ref
    Vexp[step] = step * DACref / 32
    Vact[step] = adc  * ADCref / 1024

    if Vact[step] == 0:
        Imp[step] = math.nan
    else:
        Imp[step] = (Vexp[step] / Vact[step] - 1) * Rload

    print("Step: %2d of 32: Vexp = %3.2fV,  Vact = %3.2fV. Imp: %.0f ohm" %
        (step+1, Vexp[step], Vact[step], Imp[step]))


mcp.DAC_write(0)

plt.figure(figsize=(10,4))
plt.plot(Vexp, Vact, 'o-')
plt.axline((1,1), slope=1, color='g', linestyle='dotted')
plt.axis([0,5,0,5])
plt.xlabel("Expected output (V)")
plt.ylabel("Actual output (V)")
plt.title("DAC output with a 20k load")
plt.grid()

plt.show()

