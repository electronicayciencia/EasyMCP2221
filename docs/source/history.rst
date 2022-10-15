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

GPIO / ADC and DAC:

    * GPIO output values given with :func:`GPIO_write` function are now preserved when calling :func:`SRAM_config` (like to change DAC value, or pin function).
    * Restore ADC/DAC Vref when calling :func:`SRAM_config` (see :doc:`limitations_bugs`).
    * DAC and ADC reference values now defaults to Vdd.

More robust I2C functions:

    * Rewritten :func:`I2C_read` to take into account internal I2C engine status.
    * Rewritten :func:`I2C_write` to prevent infinite loop, quicker write and ACK checking.
    * Timeout and early failure check in read and write to prevent infinite loop.
    * Custom exceptions for better error handling (see *Exceptions* in :doc:`api_reference`)
    * Automatically try to recover an I2C error from past execution.

New features:
    
    * Function to save current state: :func:`save_config`.
    * Add speed parameter in I2C Slave class.

Documentation:

    * Removed *self* argument from *autodoc* methods.


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



