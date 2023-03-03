# From https://github.com/liske/python-apds9960
# This example requires apds9960 library.

from apds9960 import APDS9960
from EasyMCP2221 import smbus
from time import sleep

bus = smbus.SMBus(1)
apds = APDS9960(bus)

print("Light Sensor Test")
print("=================")

apds.enableLightSensor()
oval = -1
while True:
    sleep(0.25)
    if apds.isLightAvailable():
        val = apds.readAmbientLight()
        r = apds.readRedLight()
        g = apds.readGreenLight()
        b = apds.readBlueLight()
        if val != oval:
            print("AmbientLight={} (R: {}, G: {}, B: {})".format(val, r, g, b))
            oval = val
