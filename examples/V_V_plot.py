# V/V to correlate DAC and ADC values
import EasyMCP2221
from time import sleep

import matplotlib.pyplot as plt
from numpy import mean
from scipy.stats import sem  # standard error of the mean

# Configure device pins ADC and DAC reference.
mcp = EasyMCP2221.Device()
mcp.set_pin_function(gp2 = "DAC", gp3 = "ADC")
mcp.DAC_config()
mcp.ADC_config()

Vcc = 5

Vrefs = {
  "1.024V": 1.024,
  "2.048V": 2.048,
  "4.096V": 4.096,
  "VDD": Vcc,
}

DAC_ref = "4.096V"
ADC_ref = "4.096V"

measures = {}

oversampling = 10 # to calculate average

waittime = 0.01

mcp.ADC_config(ref = ADC_ref)
mcp.DAC_config(ref = DAC_ref)

for step in range(0,32):

    Vexpected = Vrefs[DAC_ref] * step / 32

    mcp.DAC_write(step)
    sleep(waittime)

    samples = []
    for i in range(oversampling):
        samples.append(mcp.ADC_read()[2] / 1024 * Vrefs[ADC_ref])

    measures[Vexpected] = {
        "V":     mean(samples),
        "Error": sem(samples)
    }

    print("Step:", step+1, "/ 32")

    sleep(waittime)


mcp.DAC_write(0)

print(measures)

Vdac  = sorted(measures)
Vreal = [measures[i]["V"] for i in Vdac]
Error = [measures[i]["Error"] for i in Vdac]
plt.errorbar(x = Vdac, y = Vreal, fmt = 'o-', yerr = Error)
plt.show()

#plt.errorbar(x = Vdac, y = Vreal, fmt = 'o-', yerr = Error)
#plt.axis([0,Vrefs[DAC_ref],-0.25,0.25])
#plt.xlabel("Expected Voltage (V)")
#plt.ylabel("Relative error")
#plt.title("Voltage error diagram")
#plt.grid()
#plt.show()

