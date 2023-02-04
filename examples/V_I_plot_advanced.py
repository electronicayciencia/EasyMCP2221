# V/I plotter for 2xADC and 1 buffered DAC
# Iterate through all DAC reference values to get more accurate results.
import EasyMCP2221
from time import sleep
import matplotlib.pyplot as plt

Vcc = 5
R = 100

#     V+
#     |
#     +----- DAC3, ADC2
#     |
#     -
#     <  R
#     >
#     -
#     |
#     +----- ADC1
#     |
#     v  LED
#     -
#     |
#     |
#     _ Gnd
#     

# Configure device pins ADC and DAC reference.

mcp = EasyMCP2221.Device()
mcp.set_pin_function(
    gp1 = "ADC",   # on the led 
    gp2 = "ADC",   # on the resistor
    gp3 = "DAC")   # power supply
mcp.DAC_config()
mcp.ADC_config()  # Vcc for ADC reference

DACrefs = {
  "1.024V": 1.024,
  "2.048V": 2.048,
  "4.096V": 4.096,
  "VDD": Vcc,
}


values =  {}

for ref_str in DACrefs:
    Vref = DACrefs[ref_str]
    mcp.DAC_config(ref = ref_str)
    mcp.DAC_write(0)
    sleep(0.005)
    
    for step in range(0,32):
        mcp.DAC_write(step)
        (V1, V2, _) = mcp.ADC_read()
    
        # 10 bit ADC
        V1 = V1 / 1024 * Vcc
        V2 = V2 / 1024 * Vcc
    
        I = (V2 - V1) / R * 1000 # mA
    
        values[V1] = I
        
        print("Ref:", ref_str, "Step:", step+1, "/ 32")
        
        sleep(0.005)

mcp.DAC_config()
mcp.DAC_write(0)

V = sorted(values)
I = [values[i] for i in V]

plt.plot(V, I, 'o-')
plt.axis([-0,5,-0.1,25])
plt.xlabel("V (V)")
plt.ylabel("I (mA)")
plt.title("I vs V diagram")
plt.grid()
plt.show()

