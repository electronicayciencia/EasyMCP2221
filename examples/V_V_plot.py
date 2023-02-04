# V/V to correlate DAC and ADC values
import EasyMCP2221
from time import sleep

import matplotlib.pyplot as plt

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

Vexpected = 32 * [0]
Vmeasured = 32 * [0]
Verrorrel = 32 * [0]

mcp.ADC_config(ref = ADC_ref)
mcp.DAC_config(ref = DAC_ref)
sleep(0.1)

for step in range(0,32):
    mcp.DAC_write(step)
    
    
    V3 = mcp.ADC_read()[2]
    
    Vexpected[step] = Vrefs[DAC_ref] * step / 32
    Vmeasured[step] = Vrefs[ADC_ref] / 1024 * V3
    
    if (step == 0):
        Verrorrel[step] = 0
    else:
        Verrorrel[step] = (Vmeasured[step] - Vexpected[step]) / Vexpected[step]
    
    print("Step:", step+1, "/ 32")
    
    sleep(0.01)


mcp.DAC_write(0)

plt.plot(Vexpected, Verrorrel, 'o-')
plt.axis([0,Vrefs[DAC_ref],-0.25,0.25])
plt.xlabel("Expected Voltage (V)")
plt.ylabel("Relative error")
plt.title("Voltage error diagram")
plt.grid()
plt.show()

