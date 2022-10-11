Changelog
=========

V1.6
--------

.. currentmodule:: EasyMCP2221.Device

Improved USB stability:

    * Add timeout in HID read.
    * Add retries in send_cmd.
    * Better USB trace_commands output format.
    * Removed sleep parameter in :func:`send_cmd`.


GPIO output values given with :func:`GPIO_write` function are now preserved when calling :func:`SRAM_config` (like to change DAC value, or pin function).

Restore ADC/DAC Vref when calling :func:`SRAM_config` (see :doc:`limitations_bugs`).

DAC and ADC reference values now defaults to Vdd.

Removed *self* argument from *autodoc* methods.

Add a new function to save current state: :func:`save_config`.

Check for ACK state in :func:`I2C_write` to prevent infinite loop. Also removed sleep.


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



