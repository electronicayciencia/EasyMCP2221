# V/I plotter for multiple LEDs.
import EasyMCP2221
from time import sleep

import matplotlib.pyplot as plt
import numpy as np

# Configure device pins and DAC reference.
mcp = EasyMCP2221.Device()
mcp.set_pin_function(gp2 = "DAC", gp3 = "ADC")
mcp.DAC_config()
mcp.ADC_config()


for color in (["grey", "red", "green", "blue"]):

    print("Place the", color, "LED a press enter.")
    input()

    V = 32 * [0]
    I = 32 * [0]

    for step in range(0,32):
        mcp.DAC_write(step)
        (_, V2, V3) = mcp.ADC_read()

        # 10 bit, 5V ref
        V2 = V2 / 1024 * 5
        V3 = V3 / 1024 * 5

        # I = V/R
        I_r = (V2 - V3) / 1000

        V[step] = V2
        I[step] = I_r * 1000 # mA

        print(color, "-> step:", step+1, "/ 32")

        sleep(0.05)

    mcp.DAC_write(0)

    plt.plot(V, I, 'o-', c=color)

plt.axis([0,3.5,0,1])
plt.xticks(np.arange(0,3.5,0.5))

plt.xlabel("V (V)")
plt.ylabel("I (mA)")
plt.title("I vs V diagram for some colored LEDs")
plt.grid()
plt.show()

