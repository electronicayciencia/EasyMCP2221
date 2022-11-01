Limitations and bugs
====================

.. currentmodule:: EasyMCP2221.Device

Chip or software limitations
----------------------------

USB speed limits
~~~~~~~~~~~~~~~~

- GPIO update rate :func:`GPIO_write`: 500Hz
- GPIO read rate for :func:`GPIO_read`: 500Hz
- ADC sample rate for :func:`ADC_read`: 500Hz.
- DAC update rate for :func:`DAC_write`: 500Hz.

See :doc:`internals` for details.


Internal reference reset
~~~~~~~~~~~~~~~~~~~~~~~~

From MCP2221A's datasheet (section 1.8):

*When the Set SRAM settings command is used for GPIO control, the reference voltage for VRM is always reinitialized to the default value (VDD) if it is not explicitly set.*

This is compensated by software. But, due to the calling interval, there will be always a 2ms gap in the DAC output if it is using internal reference (not Vdd) when you change any pin function.


I2C crashes
~~~~~~~~~~~

Eventually, due to a glitch or unexpected timeout, the MCP2221 cancels an I2C transfer. The slave may be in the middle of sending a byte, and expecting some clocks cycles to send the rest of the byte.

MCP2221 is unable to start a new I2C transfer while SDA line is still busy. And the slave won't release SDA until next clock cycle. So the whole bus hangs.

See :any:`LowSDAError`.


Misc
~~~~

* The ADC seems to be always connected. So leakage current for GP1, GP2 and GP3 is greater than for GP0. Think of it as a very weak *pull-down* resistor on these pins.

* This library does not work with password protected devices. You cannot use it to set or clear MCP2221's Flash password.

* Changing VID/PID not supported.

* Maximum length for single I2C read or write operations is 65535 bytes.


Software Bugs
-------------

None reported.

Bug tracking system: https://github.com/electronicayciencia/EasyMCP2221/issues

