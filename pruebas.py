from sys import exit
import time
from time import sleep
import EasyMCP2221
from EasyMCP2221.Constants import *

mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp0 = "GPIO_IN",
    gp1 = "GPIO_OUT",
    gp2 = "GPIO_OUT",
    gp3 = "GPIO_OUT")

# Output latching opamp circuit in GP0
while True:
    if mcp.GPIO_read()[0]:
        print("\nInt!\n")
        mcp.set_pin_function(gp0 = "GPIO_OUT", out0 = 0)
        mcp.set_pin_function(gp0 = "GPIO_IN")
        if mcp.GPIO_read()[0]:
            print("Can't clear it!")


    sleep(2)
    print(".")

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


def counter():

    mcp.set_pin_function(
        gp0 = "GPIO_IN",
        gp1 = "GPIO_IN",
        gp2 = "GPIO_IN",
        gp3 = "GPIO_IN")


    c = 0
    gp_old = mcp.GPIO_read()

    while True:
        gp = mcp.GPIO_read()

        if not gp == gp_old:
            c = c + 1
            print(c)
            gp_old = gp






