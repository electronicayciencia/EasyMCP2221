from sys import exit
import time
from time import sleep
import EasyMCP2221
from EasyMCP2221.Constants import *

mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp0 = "GPIO_OUT", out0 = 1,
    gp1 = "GPIO_OUT", out1 = 1,
    gp2 = "ADC",
    gp3 = "DAC")

text = b"And Saint Attila raised the hand grenade up on high, saying, 'O Lord, bless this thy hand grenade, that with it thou mayst blow thine enemies to tiny bits, in thy mercy.' And the Lord did grin. And the people did feast upon the lambs, and sloths, and carp, and anchovies, and orangutans, and breakfast cereals, and fruit bats, and large chulapas. And the Lord spake, saying, 'First shalt thou take out the Holy Pin. Then shalt thou count to three, no more, no less. Three shall be the number thou shalt count, and the number of the counting shall be three. Four shalt thou not count, neither count thou two, excepting that thou then proceed to three. Five is right out. Once the number three, being the third number, be reached, then lobbest thou thy Holy Hand Grenade of Antioch towards thy foe, who, being naughty in My sight, shall snuff it."

mcp.I2C_speed(47000)

#mcp.I2C_write(0x50, b"\0\0" + text[0:200])
mcp.I2C_read(0x50, 77)


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






