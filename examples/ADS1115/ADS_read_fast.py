# Read ADS115 in continuous mode using ADS1x15 library
# We can get up to 84 SPS

import time
import ADS1x15

ADS = ADS1x15.ADS1115(1, 0x48)

# Configure device
ADS.setGain(ADS.PGA_4_096V)
ADS.setDataRate(ADS.DR_ADS111X_128)
ADS.setMode(ADS.MODE_CONTINUOUS)
ADS.requestADC(0)         # First read to trigger

n = 0
t_start = time.perf_counter()
while True :
    t = time.perf_counter()
    if t - t_start >= 1:
        print("%d SPS" % n)
        n = 0
        t_start = t

    raw = ADS.getValue()
    #print("{0:.3f} V".format(ADS.toVoltage(raw)))
    n = n + 1
