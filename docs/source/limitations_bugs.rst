Limitations and bugs
====================

.. currentmodule:: EasyMCP2221.Device

Chip or software limitations
----------------------------

USB speed limits
~~~~~~~~~~~~~~~~

MCP2221's command rate is limited by USB polling rate. Each command requires two USB slots. One to send the command to the device, and the other to get the response. See :doc:`internals` for details.

On xHCI controllers (USB 3.0), polling rate is 1000Hz. So you can issue one command every 2ms. That command could be a DAC update, ADC read, GPIO, I2C operation, etc.

- GPIO update rate :func:`GPIO_write`: 500Hz
- GPIO read rate for :func:`GPIO_read`: 500Hz
- ADC sample rate for :func:`ADC_read`: 500Hz.
- DAC update rate for :func:`DAC_write`: 500Hz.

On eHCI (USB 2.0), the maximum update rate I measured is 333 commands per second.

These ratios depend on multiple parameters. Like your USB hardware (including cable and hub), operating system, or the number of devices connected to the same bus.


I2C speed limit
~~~~~~~~~~~~~~~

Each I2C interaction requires multiple USB commands. See :doc:`internals` for details.

Sending one byte will require: setup, send data, and get the result.
Reading one byte will require: setup, finish test, and read data.

Depending on your USB polling rate, each of these commands can take 2ms or more.

I2C speed (100kHz / 400kHz) only matters when you are transmitting a lot of bytes in a row. For a few bytes interaction, speed is limited by the USB polling rate.

.. list-table:: Expected I2C performance
   :widths: 50 25 25
   :header-rows: 1

   * - Operation
     - 100kHz bus
     - 400kHz bus
   * - Read
     - 167 operations / s
     - 167 operations / s
   * - Write
     - 167 operations / s
     - 167 operations / s
   * - Write register address & read
     - 84 operations / s
     - 84 operations / s
   * - Read multiple bytes
     - 5980 bytes / s
     - 14872 bytes / s
   * - Write multiple bytes
     - 7485 bytes / s
     - 14933 bytes / s


Internal reference reset
~~~~~~~~~~~~~~~~~~~~~~~~

From MCP2221A's datasheet (section 1.8):

*When the Set SRAM settings command is used for GPIO control, the reference voltage for VRM is always reinitialized to the default value (VDD) if it is not explicitly set.*

This is compensated by software. But, due to the calling interval, there will be always a 2ms gap in the DAC output if it is using internal reference (not Vdd) when you change any pin function.


ADC/DAC VDD to 1.024V crash
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For unknown reasons, if DAC reference source is switched from VDD to 1.024V while GP2 is configured as DAC and GP3 as ADC (or viceversa), and DAC output is above 26, the chip crashes.

The following code will trigger an ``OSError: read error`` exception in `hidhandler.read`.

.. code-block:: python

    mcp.set_pin_function(
        gp2 = "DAC",
        gp3 = "ADC")

    mcp.DAC_config(ref="VDD", out=27)
    mcp.DAC_config(ref="1.024V", out=27)

As a workaround, since version 1.8.2, :func:`DAC_config` always turn off DAC before selecting a new reference.


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

* Regardless of the output frequency, MCP2221(A)'s clock output has glitch every 1ms.

* Cannot clear the Interrupt flag when ADC reference value is 4.096V and GP1 is low.


Software Bugs
-------------

Bug tracking system: https://github.com/electronicayciencia/EasyMCP2221/issues

