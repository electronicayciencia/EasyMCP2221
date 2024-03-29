# V/I plotter DAC/ADC example.
import EasyMCP2221
from time import sleep

import matplotlib.pyplot as plt

# Configure device pins ADC and DAC reference.
# DAC output impedance is about 5k according to datasheet
# so measurements could be inaccurate as the current increases.
mcp = EasyMCP2221.Device()
mcp.set_pin_function(gp2 = "DAC", gp3 = "ADC")
mcp.DAC_config()
mcp.ADC_config()

R = 1000

V = 32 * [0]
I = 32 * [0]

for step in range(0,32):
    mcp.DAC_write(step)
    (_, V2, V3) = mcp.ADC_read()
    
    # 10 bit, 5V ref
    V2 = V2 / 1024 * 5
    V3 = V3 / 1024 * 5
    
    # I = V/R
    I_r = (V2 - V3) / R
    
    V[step] = V2
    I[step] = I_r * 1000 # mA
    
    print("Step:", step+1, "/ 32")
    
    sleep(0.05)


mcp.DAC_write(0)

plt.plot(V, I, 'o-')
plt.axis([0,5,0,1])
plt.xlabel("V (V)")
plt.ylabel("I (mA)")
plt.title("I vs V diagram")
plt.grid()
plt.show()

