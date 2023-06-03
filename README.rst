=====================================================
Easy MCP2221
=====================================================

Easy MCP2221 is a Python module to interface with Microchip MCP2221 and MCP2221A.

Connected to the USB port, this 14 pin chip part can provide a **normal computer** with the capabilities of a **basic microcontroller**.


MCP2221's peripherals:

- 4 GPIO
- 3 channel ADC
- DAC
- I2C
- UART
- Clock Output
- USB Wake-up via Interrupt Detection.

So you can practice the basics of digital electronics, microcontrollers, and robotics using nothing more than a regular computer, a breadboard, a few parts, and Python.


Quick start
-----------

Install:

.. code-block:: console

	$ pip install EasyMCP2221


First run:

.. code-block:: python

    >>> import EasyMCP2221
    >>> mcp = EasyMCP2221.Device()
    >>> print(mcp)
    {
        "Chip settings": {
            "Power management options": "enabled",
            "USB PID": "0x00DD",
            "USB VID": "0x04D8",
            "USB requested number of mA": 100
        },
        "Factory Serial": "01234567",
        "GP settings": {},
        "USB Manufacturer": "Microchip Technology Inc.",
        "USB Product": "MCP2221 USB-I2C/UART Combo",
        "USB Serial": "0000000000"
    }


GUI
---

*EasyMCP2221 Workbench* is a GUI to play with MCP2221 and MCP2221A chips based on EasyMCP2221 library.

https://github.com/electronicayciencia/EasyMCP2221-GUI


Documentation
-------------

Read the Install Guide, Examples and full API Reference here: https://easymcp2221.readthedocs.io/


Author
----------------------------------------------------

Reinoso Guzman (https://www.electronicayciencia.com).

Initially based on PyMCP2221A library by Yuta KItagami (https://github.com/nonNoise/PyMCP2221A).


License
----------------------------------------------------

The MIT License (MIT).
