# This is to make examples work just by cloning the repo.
import sys
sys.path.append('../')
# ----------------------

# DAC output, advanced example.
# Generate SIN signal using a recurrence relation to avoid calculate sin(x) in the main loop.
import EasyMCP2221
import time
from math import sqrt, cos, pi

# Output freq
sample_rate = 313 # Hz (unstable above 500Hz)
freq        = 10  # Hz

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
    # set-up next sample time right at the beginning
    next_sample = time.perf_counter() + 1/sample_rate
    
    # Calculate next value and write it to DAC
    s = 2*W*last_s - before_last_s
    mcp.DAC_write(int(s*15+15))  # 1 => 30, -1 = 0

    # Update recurrence values
    before_last_s = last_s
    last_s = s
    
    # Warning if we couldn't catch on time with sample rate!
    if time.perf_counter() > next_sample:
        print("Undersampling!")
    
    # Wait fixed delay for next sample (do not use sleep)
    while time.perf_counter() < next_sample: 
        pass
