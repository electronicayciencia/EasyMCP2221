# DAC output, advanced example.
# Generate SIN signal using a recurrence relation to avoid calculate sin(x) in the main loop.
import EasyMCP2221
import time
from math import sqrt, cos, pi

# Output freq
sample_rate = 250 # Hz (unstable above 500Hz)
freq        = 0.1  # Hz

# Configure device pins and DAC reference.
# MCP2221 have only 1 DAC, connected to GP2 and/or GP3.
mcp = EasyMCP2221.Device()
mcp.set_pin_function(gp2 = "DAC", gp3 = "DAC")
mcp.DAC_config(ref="VDD")

# Initial values
W              = cos(2*pi*freq/sample_rate)
last_s         = sqrt(1-W**2)  # y_n-1  (y1)
before_last_s  = 0             # y_n-2  (y0)

# No trigonometric function in the main loop
while True:
    # set-up next sample time before doing anything else
    next_sample = time.perf_counter() + 1/sample_rate
    
    # Calculate next output value and write it to DAC
    s = 2*W*last_s - before_last_s    # s between -1 and 1
    out = (s + 1) / 2   # out between 0 and 1 now
    out = out * 31      # 5 bit DAC, 0 to 31
    out = int(out)      # integer
    mcp.DAC_write(out)

    # Update recurrence values
    (before_last_s, last_s) = (last_s, s)
    
    # Warn if we can't keep up with the sample rate!
    if time.perf_counter() > next_sample:
        print("Undersampling!")
    
    # Wait fixed delay for next sample (do not use sleep)
    while time.perf_counter() < next_sample: 
        pass
