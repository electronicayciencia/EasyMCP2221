Changelog
=========

.. currentmodule:: EasyMCP2221.Device

V1.6
--------

V1.6.2
~~~~~~

ADC/DAC:
    * Fixed bug: when ADC reference is VDD and DAC reference is VRM and a new GPIO configuration is applied, DAC stops working. It seems to be related with a known MCP limitation.
    * Fixed bug: Restore DAC reference value after reset.
    * In some cases MCP2221A's firmware does not restore DAC or ADC pin assignment when it boots. Software workaround.

I2C:
    * Deprecated :func:`I2C_cancel` and :func:`I2C_is_idle`. Bus is now managed automatically. You can use :any:`_i2c_release` and :any:`_i2c_status` as replacement if needed.
    * Fixed. Low SCL and low SDA exceptions were swapped.
    * When the I2C bus detects SDA activity, the next transfer does not work fine. Prevented via software. See :any:`_i2c_status`.

Documentation:
    * Instructions and schematic for testing in the :doc:`install` section.
    * Replaced PNG schematics by SVG versions in :doc:`examples`.
    * Troubleshooting section to run as an unprivileged user in Linux (udev rule).

Misc:
    * Added test suite.
    * Added IOC edge detection setting in device representation.


V1.6.1
~~~~~~

Improved USB stability:
    * Added timeout in HID read.
    * Added retries in send_cmd.
    * Better USB trace_commands output format.
    * Removed sleep parameter in :func:`send_cmd`.

GPIO / ADC and DAC:
    * GPIO output values given with :func:`GPIO_write` function are now preserved when calling :func:`SRAM_config` (like to change DAC value, or pin function).
    * Restore ADC/DAC Vref when calling :func:`SRAM_config` (see :doc:`limitations_bugs`).
    * Reload Vrm after power-up according to saved configuration.

More reliable I2C functions:
    * Rewritten :func:`I2C_read` to take into account internal I2C engine status.
    * Rewritten :func:`I2C_write` to prevent infinite loop, quicker write and ACK checking.
    * Timeout and early failure check in read and write to prevent infinite loop.
    * Custom exceptions for better error handling (see *Exceptions* in :doc:`api_reference`)
    * Automatically try to recover from an I2C error in past operation.

New features:
    * Function to save current state: :func:`save_config`.
    * Added speed parameter in I2C Slave class.

Documentation:
    * Removed *self* argument from *autodoc* methods.
    * Added pictures and schematics.
    * Added MCP2221 pinout guide.
    * Added advanced ADC/DAC examples section.
    * Added license.
    * Corrected typos.
    * Formatting.

V1.6.0
~~~~~~

Released 1.5.1 again by mistake.


V1.5
--------

V1.5.1
~~~~~~

Add I2C Slave helper class.


V1.5.0
~~~~~~

First EasyMCP2221 version.


Older releases
--------------

This project was initially a fork of PyMCP2221A library by Yuta KItagami (https://github.com/nonNoise/PyMCP2221A).

I made a few changes, then a few more, until I ended up rewriting almost all the code. Since the API is no longer compatible with PyMCP2221A, I decided to create a new package.

Tags v1.4 and earlier are from PyMCP2221A.



