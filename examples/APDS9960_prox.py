# From https://github.com/liske/python-apds9960
# This example requires apds9960 library.

from apds9960 import APDS9960
from EasyMCP2221 import SMBus
from time import sleep

bus = SMBus(1)
apds = APDS9960(bus)

print("Proximity Sensor Test")
print("=====================")

apds.enableProximitySensor()
oval = -1
while True:
    sleep(0.25)
    val = apds.readProximity()
    if val != oval:
        print("proximity={}".format(val))
        oval = val
