# This could be a battery level meter.
# GP0 and GP1 and GP2 are digital outputs.
# GP2 is analog input.
# Connect:
#   A red    LED between GP0 and positive (with a resistor).
#   A yellow LED between GP1 and positive (with a resistor).
#   A green  LED between GP2 and positive (with a resistor).
#   A potentiometer to GP3, between positive and ground.
# If potentiometer is below 25%, red led will blink.
# Between 25% and 50%, only red will light still.
# Between 50% and 75%, red and yellow light.
# Above 75%, all three leds light.

import sys
sys.path.append('../')

import EasyMCP2221
from time import sleep

# Connect to device
mcp = EasyMCP2221.Device()

# GP0 and GP1 are inputs, GP2 and GP3 are outputs.
mcp.set_pin_function(
    gp0 = "GPIO_OUT",
    gp1 = "GPIO_OUT",
    gp2 = "GPIO_OUT",
    gp3 = "ADC")

mcp.ADC_config(ref="VDD")

while True:
    pot = mcp.ADC_read()[2]   # ADC channel 2 is GP3
    pot_pct = pot / 1024 * 100

    if pot_pct < 25:
        red_led_status = mcp.GPIO_read()[0]
        mcp.GPIO_write(
            gp0 = not red_led_status,
            gp1 = False,
            gp2 = False)

        sleep(0.1)

    elif 25 < pot_pct < 50:
        mcp.GPIO_write(
            gp0 = True,
            gp1 = False,
            gp2 = False)

    elif 50 < pot_pct < 75:
        mcp.GPIO_write(
            gp0 = True,
            gp1 = True,
            gp2 = False)

    elif pot_pct > 75:
        mcp.GPIO_write(
            gp0 = True,
            gp1 = True,
            gp2 = True)

