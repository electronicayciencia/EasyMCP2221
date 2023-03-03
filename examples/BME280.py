#!/usr/bin/env python

# From https://github.com/pimoroni/bme280-python
# This example requires pimoroni-bme280

import time
from EasyMCP2221 import SMBus
from bme280 import BME280

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

print("\nBME280 sensor. Press Ctrl+C to finish.\n")
print("Temperature, Pressure, Humidity")

while True:
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    print('{:05.2f}*C {:05.2f}hPa {:05.2f}%'.format(temperature, pressure, humidity))
    time.sleep(1)
