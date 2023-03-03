SMBus compatible class
======================

Usage
-----

This is a *smbus* compatibility class. You can use it to run any I2C Python library for Raspberry Pi or micropython just using MCP2221's I2C device interface.

Usage:

.. code-block:: python

    from EasyMCP2221 import SMBus

    bus = SMBus(1)


or

.. code-block:: python

    from EasyMCP2221 import smbus

    bus = smbus.SMBus(1)


Example
-------

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


Full reference
--------------

Based on `kplindegaard/smbus2 <https://github.com/kplindegaard/smbus2>`_ interface.

See `The SMBus Protocol <https://www.kernel.org/doc/html/next/i2c/smbus-protocol.html>`_ for more information.

.. currentmodule:: EasyMCP2221

.. autoclass:: SMBus
    :members:
