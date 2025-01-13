# Test DAC / ADC switching references with several oputput values
import EasyMCP2221

mcp = EasyMCP2221.Device()

Vrm = {
    "OFF"   : 0,
    "1.024V": 1.024,
    "2.048V": 2.048,
    "4.096V": 4.096,
    "VDD"   : 5
}


for v_src in Vrm.keys():
    for v_dst in Vrm.keys():
        for i in range(0,32):

            mcp.set_pin_function(
                gp2 = "DAC",
                gp3 = "ADC")

            # Turn off ADC
            mcp.DAC_config(ref = "OFF", out = 0)
            
            # Set up first Vref
            mcp.DAC_config(ref = v_src, out = i)

            # Try to switch to the second Vref
            try:
                mcp.DAC_config(ref = v_dst)
                print("%s\t%s\t%d\tOk" % (v_src, v_dst, i))
                
            except OSError:
                print("%s\t%s\t%d\tError" % (v_src, v_dst, i))
                mcp.reset()

