# Read ADS115 while blinking a LED

import time
import ADS1x15

ADS = ADS1x15.ADS1115(1, 0x48)

# ADS1x15 library initializes the SMBus internally. So it already
# creates an instance of EasyMCP2221.Device class. To interact
# with MCP2221 GPIO pins, we need to get this object from the
# ADS1x15 inner attributes and reuse it.
mcp = ADS.i2c.mcp

# Set GP2 as output pin.
mcp.set_pin_function(gp2 = "GPIO_OUT")


# Configure ADS1115 device
ADS.setGain(ADS.PGA_4_096V)
ADS.setDataRate(ADS.DR_ADS111X_128)
ADS.setMode(ADS.MODE_CONTINUOUS)
ADS.requestADC(0)         # First read to trigger

# We keep the LED status in a variable instead of reading it from
# the device in order to save USB slots for the ADC.
led = False

# Sleeping in the main loop will decrease ADC sampling rate
# so we sill use timing instead of sleep
t_blink = 0

# Main loop
while True:
    v = ADS.toVoltage(ADS.getValue())
    print("{0:.3f} V".format(v))

    # Notice that GPIO interactions will use some USB slots.
    # So we must keep them to the bare minimum or ADC sampling
    # rate will decrease.

    # Turn the LED Off only if it was previously On
    if v >= 1.0 and led is True:
        led = False
        mcp.GPIO_write(gp2 = led)


    # Blink the LED while v < 1V
    # We don´t use sleep because that would stop ADC sampling
    if v < 1.0:
        t = time.perf_counter()
        if t - t_blink >= 0.5: # 0.5s semiperiod = 1 Hz
            led = not led
            mcp.GPIO_write(gp2 = led)
            t_blink = t
