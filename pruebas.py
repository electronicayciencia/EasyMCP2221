import time
import EasyMCP2221

mcp = EasyMCP2221.Device()

def freq_meter():

    mcp.set_pin_function(gp0 = "GPIO_IN")

    start = time.time()
    old = True
    n = 0
    while True:
        input = mcp.GPIO_read()[0]
        if input != old:
            n = n + 1

        if time.time() - start > 1:
            print(int(n/2))
            n = 0
            start = time.time()

        old = input


mcp.set_pin_function(
    gp3 = "LED_I2C")

data = b'\0\0' + b'This is data'




