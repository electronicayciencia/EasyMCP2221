=====================================================
Easy MCP2221
=====================================================


Easy MCP2221 is a Python module to interface with Microchip MCP2221 and MCP2221A.

Using this chip you can practice the basics of digital electronics, microcontrollers, and robotics using nothing more than a regular computer, a breadboard, a few parts, and Python.

MCP2221's peripherals:

- 4 GPIO
- 3 channel ADC
- DAC
- I2C
- UART
- Clock Output
- USB Wake-up via Interrupt Detection.


Disclaimer
----------

I am not related to Microchip Inc in any way. This library is unofficial and for personal use only.

Some examples in this documentation show bare connections from your USB port to a breadboard. Most USB port controllers are protected against short-circuit between power and/or data lines, but some are not. I am not responsible for any damage you may cause to your computer. To be safe, always use an isolated powered USB hub for experimentation.

Many thanks to Microchip for providing samples of MCP2221A, and for openly publishing the datasheet and documentation used to write this library.


.. toctree::
   :maxdepth: 1
   :caption: Table of Contents
   :hidden:

   install
   examples
   api_reference
   i2c_slave
   limitations_bugs
   history
   links
