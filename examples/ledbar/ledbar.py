"""Simulate a thermal inertia LED bar.
Features:
 - Use an I2C PCA9685 to manage LEDs with PWM
 - ADC on gp1 is used for speed adjustment
 - ADC on gp2 is used for inertia adjustment
 - ADC on gp3 is used for brightness adjustment
 - Use of perf_counter to get delays on a multitasking system
 - Use Numpy to calculate brightness values
 - Use a generator to create back and forward led sequence.

To simulate thermal inertia we need two status:
- Final status: the target, steady state. We mark this to set on and off the leds.
- Transient status: the reality, the actual status in the output on PCA9685.

Both status are connected only via an Exponential Moving Average.
"""

import EasyMCP2221
import PCA9685

from time import sleep, perf_counter
import numpy as np

def update_led_bar(pca, brights):
    """Update PCA9685"""
    i = 0 # first led
    for b in brights:
        pca.set_led(i, b, delay=0, update=0)
        i = i + 1

    pca.update()


def read_adc(mcp):
    """Read MCP2221A ADC and normalize the value"""
    (adc1, adc2, adc3) = mcp.ADC_read()
    adc1 = adc1 / 1024
    adc2 = adc2 / 1024
    adc3 = adc3 / 1024
    print("%2d%%, %2d%%, %2d%%" % (adc1*100, adc2*100, adc3*100))
    return adc1, adc2, adc3


def init():
    mcp = EasyMCP2221.Device()
    mcp.set_pin_function(
        gp0 = "GPIO_IN",  # not used
        gp1 = "ADC",      # speed adjustment
        gp2 = "ADC",      # inertia adjustment
        gp3 = "ADC")      # brightness adjustment

    pca = PCA9685.PCA9685(mcp.I2C_Slave(0x40))

    # A bit high refresh rate for smoother effect
    pca.set_rate(1000)

    return mcp, pca


def led_sequence(n):
    """Let's use a generator to create back and forward sequence"""
    led = 0
    increment = 1

    while True:
        if led == n-1 and increment == 1:
            increment = -1
        elif led == 0 and increment == -1:
            increment = 1

        yield led

        led += increment



def main():
    mcp, pca = init()

    status_final = np.array([0.0,0,0,0,0,0,0,0]) # final status: steady state
    status_trans = np.array([0.0,0,0,0,0,0,0,0]) # transitory status: the current brights

    led = led_sequence(8)
    last_update = 0

    # Main loop
    while True:

        # Update adjustments
        (adj_delay, adj_inertia, adj_bright) = read_adc(mcp)

        # Once in a time, update final status
        # setting the current led to selected brightness and turning off the others
        if perf_counter() - last_update > adj_delay:
            last_update = perf_counter()

            status_final = 0 * status_final
            status_final[next(led)] = adj_bright

        # Progress towards final status using an Exponential Moving Average
        status_trans = adj_inertia * status_trans + (1 - adj_inertia) * status_final

        # Update led bar
        update_led_bar(pca, status_trans)

        # update every 10ms
        sleep(0.01)


if __name__ == "__main__":
    main()
