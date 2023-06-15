SMBus compatible class
======================

Usage
-----

This is a *smbus* compatibility class. You can use it to run any I2C Python library for Raspberry Pi or micropython just using MCP2221's I2C device interface.

Usage:

.. code-block:: python

    from EasyMCP2221 import SMBus

    bus = SMBus()


or

.. code-block:: python

    from EasyMCP2221 import smbus

    bus = smbus.SMBus()


.. note::

  To use other mcp functions in addition to SMBus, do not create a new MCP Device.
  It will interfere with existing bus resulting in unpredictable behavior.
  Always re-use ``bus.mcp`` object (see `example 2`).



Example 1: Basic weather station
--------------------------------

In this example, we are using a library from `Pimoroni/BME280 <https://github.com/pimoroni/bme280-python>`_ to read Temperature, Barometric Pressure and Relative Humidity from a BME280 sensor.

That library is designed for Raspberry Pi or any other system that supports SMBus protocol. It works together with EasyMCP2221 via **SMBus** class.

Install:

.. code-block:: console

    pip install pimoroni-bme280 EasyMCP2221


Example code:

.. code-block:: python

    import time
    from EasyMCP2221 import SMBus
    from bme280 import BME280

    bus = SMBus(1)
    bme280 = BME280(i2c_dev=bus)

    while True:
        temperature = bme280.get_temperature()
        pressure = bme280.get_pressure()
        humidity = bme280.get_humidity()
        print('{:05.2f}*C {:05.2f}hPa {:05.2f}%'.format(temperature, pressure, humidity))
        time.sleep(1)


Output:

.. code-block:: console

    17.93*C 933.76hPa 51.57%
    17.92*C 933.76hPa 51.57%
    17.91*C 933.77hPa 51.53%
    17.91*C 933.77hPa 51.50%
    17.91*C 933.77hPa 51.54%
    ...



Example 2: Real Time Clock with LCD
-----------------------------------

This is a digital clock with two I2C chips:

* DS1307 as RTC
* LCD display based on with PCF8574 I2C adapter.

It also shows how to re-use ``mcp`` object to further configure MCP2221.

Main loop:

- DS1307 is configured as 1Hz square oscillator.
- MCP2221's GP2 is configured as Interrupt on Change.
- The rising edge of DS1307's output triggers the update cycle.

Full code on `EasyMCP2221 examples/clock <https://github.com/electronicayciencia/EasyMCP2221/tree/master/examples/clock>`_


.. code-block:: python

    from EasyMCP2221 import SMBus
    from lcd_driver import LCD
    from DS1307 import DS1307

    # Create SMBus and instances
    bus = SMBus()
    lcd = LCD(bus, addr=0x3F)
    ds = DS1307(bus, addr=0x68)

    bus.mcp.I2C_speed(100_000) # DS1307 only supports 100kHz

    bus.mcp.set_pin_function(
        gp0 = "GPIO_IN",  # unused
        gp1 = "IOC",      # trigger update LCD each second
        gp2 = "DAC",      # simulate backup battery
        gp3 = "LED_I2C")  # i2c traffic indicator

    bus.mcp.DAC_write(21) # about 3.28V with 5V Vcc
    bus.mcp.IOC_config(edge = "rising")

    # Initialization after a complete power loss
    if ds.halted():
        ds.write_now()
        ds._write(0x07, 0b0001_0000) # sqwe 1Hz
        print("RTC initialized with current timestamp")
    else:
        print("RTC was already initialized")

    lcd.clear()

    # Update only when GP1 changes using Interrupt On Change
    while True:
        if bus.mcp.IOC_read():
            bus.mcp.IOC_clear()
            (year, month, day, dow, hours, minutes, seconds) = ds.read_all()

            lcd.display_string("%02d/%02d/20%02d" % (day, month, year), 1)
            lcd.display_string("%02d:%02d:%02d" % (hours, minutes, seconds), 2)




Full reference
--------------

Based on `kplindegaard/smbus2 <https://github.com/kplindegaard/smbus2>`_ interface.

See `The SMBus Protocol <https://www.kernel.org/doc/html/next/i2c/smbus-protocol.html>`_ for more information.

.. currentmodule:: EasyMCP2221

.. autoclass:: SMBus
    :members:
