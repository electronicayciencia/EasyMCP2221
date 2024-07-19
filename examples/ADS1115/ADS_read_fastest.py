# Read ADS115 in continuous mode using raw I2C read for fastest results.
# We can get 167 SPS this way.

import time
import ADS1x15

ADS = ADS1x15.ADS1115(1, 0x48)

# Configure device
ADS.setGain(ADS.PGA_4_096V)
ADS.setDataRate(ADS.DR_ADS111X_128)
ADS.setMode(ADS.MODE_CONTINUOUS)
ADS.requestADC(0)         # First read to trigger

# Read once from Conversion Register 
# in order to set the Address Pointer Register
ADS.getValue() 

n = 0
t_start = time.perf_counter()
while True :
    t = time.perf_counter()
    if t - t_start >= 1:
        print("%d SPS" % n)
        n = 0
        t_start = t

    # Address Pointer Register is preserved between reads
    # so we can read the Conversion Register directly
    # to save one write operation.
    raw = ADS.i2c._read(0x48, 2)
    
    # Process the raw value (16 bits)
    value = int.from_bytes(raw, "big", signed=True)
    
    #print("{0:.3f} V".format(ADS.toVoltage(value)))
    n = n + 1
