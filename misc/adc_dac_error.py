# DAC -> ADC matching error for all Vref

from time import sleep
import EasyMCP2221

Vdd = 5
Vrm = {
    #"OFF"   : 0,
    "1.024V": 1.024,
    "2.048V": 2.048,
    "4.096V": 4.096,
    "VDD"   : Vdd
}

mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp0 = "GPIO_IN",  # Does this matters?
    gp1 = "GPIO_IN",
    gp2 = "ADC",
    gp3 = "DAC")



adc_ref = "2.048V"
dac_ref = "1.024V"

mcp.DAC_config(vdd = Vdd)

for dac_ref in Vrm.keys():
    print("\n\nDAC ref: " + dac_ref)
    mcp.DAC_config(ref = dac_ref, out = 0)
 
    for i in range(0,32):
        # theoretical value
        exp_v = i * Vrm[dac_ref] / 32

        print("\n%d,%.4f" % (i,exp_v), end="")

        mcp.DAC_write(i)

        for adc_ref in Vrm.keys():
            mcp.ADC_config(ref = adc_ref)

            sleep(0.1)
            v = mcp.ADC_read()[2]
            
            # actual value
            act_v = v * Vrm[adc_ref] / 1024
            print(",%.4f" % act_v, end = "")
