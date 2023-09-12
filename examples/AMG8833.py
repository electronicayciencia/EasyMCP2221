# Let's play with an AMG8833
# "Grid-EYE" 8x8 Infrared Array Sensor
import EasyMCP2221
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

mcp = EasyMCP2221.Device()
mcp.set_pin_function(
    gp0 = "GPIO_IN",
    gp1 = "GPIO_IN",
    gp2 = "GPIO_OUT", out2 = 0,
    gp3 = "LED_I2C")


mcp.GPIO_write(gp2=True)  # restart the device just in case
sleep(0.1)

mcp.I2C_speed(400_000)

sensor = mcp.I2C_Slave(0x69)

img = None
while True:
    data = sensor.read_register(0x0E, 2)
    thr_tmp = int.from_bytes(data, byteorder="little", signed=True) * 0.0625

    data = sensor.read_register(0x80, 128)
    T = 0.25/16 * (np.frombuffer(data, dtype=np.int16).reshape(8,8) << 4)
    T = np.flipud(T)
    T = np.fliplr(T)

    print("Min: %3.1fC  Max: %3.1fC  Thermistor temperature: %3.1fC" % (np.min(T), np.max(T), thr_tmp))

    if img is None:
        img = plt.imshow(T, cmap='jet', interpolation='sinc')
        cbar = plt.colorbar()

    else:
        img.set_data(T)
        cbar.mappable.set_clim(vmin=20, vmax=34)

    plt.pause(0.01)
