Changelog
=========

.. currentmodule:: EasyMCP2221.Device

Latest (unreleased)
-------------------

No changes.


V1.8
--------

V1.8.3 (last release)
~~~~~~~~~~~~~~~~~~~~~~~~

Misc:
    * Fixed bug in debug messages.
    * Fixed initialization bug when a pin function value is not valid, so documented as "reserved".


V1.8.2
~~~~~~

GPIO:
    * Added :func:`GPIO_poll` to read GPIO changes easier.

ADC/DAC:
    * :func:`ADC_write` and :func:`DAC_read` accept and return values in volts.
    * :func:`DAC_write` returns the expected DAC output.
    * :func:`DAC_config` will turn Off DAC before selecting a new reference voltage.

I2C:
    * Fixed: some I2C states are not handled correctly.

Documentation:
    * Added an example of LCD drive using :class:`EasyMCP2221.SMBus` with the Luma library.
    * Documented a weird crash when switching between DAC voltage reference sources (see :doc:`limitations_bugs`).


V1.8.1
~~~~~~

Misc:
    * New feature: Device instance catalog.
      Multiple :class:`EasyMCP2221.Device` instances pointing to the same physical device can cause conflict.
      EasyMCP2221 keeps an internal catalog of devices initialized in the same program. It tries to detect when
      double initialization happens and return the same object to prevent conflicts.
    * Improved device selection flow.
    * Test for device selection and catalog.

I2C:
    * Added serial number to :class:`EasyMCP2221.SMBus` initialization parameters.

Documentation:
    * Examples with ADS1115 ADC.
    * Improved device selection flow explanation.
    * Add I2C expected performance table in :doc:`limitations_bugs`



V1.8.0
~~~~~~

Improvements for multiple devices:
    * Allow selecting a device via USB serial.
    * Added :func:`enable_cdc_serial` to locate the matching CDC interface.
    * Fixed: State variables were defined as class variables.

Misc:
    * Added I2C scan code in :func:`I2C_read` documentation.
    * Removed open timeout unless in reset operation.
    * Fixed: Preserve non-default initialization parameters on reset.
    * Removed the 5 seconds delay at initialization when no devices found (except when :func:`reset` is called).


V1.7
--------

V1.7.2
~~~~~~

ADC/DAC:
    * Added ``norm`` parameter to :func:`ADC_read` and :func:`DAC_write`.
    * Added LED bar example.

I2C:
    * In I2C Slave Helper class, *register bytes* and *register byte order* can be indicated in the class constructor.

Misc:
    * Removed timeout parameter on USB HID read, introduced in V1.6.1. This parameter causes a delay in some systems (https://github.com/electronicayciencia/EasyMCP2221/issues/7) due to unknown reasons. The default timeout is now 1000 ms.


V1.7.1
~~~~~~

I2C:
    * Set I2C default speed to 100kHz. In some chips, the default speed is 500kHz and can cause trouble with some slave devices or noisy buses. You can adjust it with :func:`I2C_speed` function.
    * Added clock frequency parameter in SMBus class.

Misc:
    * Added function :func:`revision` to get the mayor and minor hardware and firmware revision.
    * Fixed test about Interrupt On Change.
    * Moved GUI to a separate application on its own repository.


V1.7.0
~~~~~~

ADC/DAC:
    * Fixed bug. When GP1, 2 and 3 are all in ADC mode and ADC reference is VDD. If just after reset VRM reference is selected, ADC stops working.

Interrupt on Change:
    * Added new section about Interrupt On Change (IOC) detection.
    * Renamed function *wake_up_config* to :func:`IOC_config`.
    * Added :func:`IOC_read` to read Interrupt On Change flag.
    * Added :func:`IOC_clear` to clear Interrupt On Change flag.
    * Replaced *raising* edge with *rising* edge.

I2C:
    * Removed deprecated functions *I2C_is_idle* and *I2C_cancel*.

Misc:
    * Solved bug USB remote Wake-up is not saved with :func:`save_config`.
    * New behavior for :func:`enable_power_management`. Changes are not saved immediately to Flash. Call to :func:`save_config` is needed instead.
    * New function :func:`read_flash_info`.
    * Device information now returns GPIO designation and default status.
    * Document as limitation a weird MCP2221's bug related to interrupt flag and ADC reference.


V1.6
--------

V1.6.3
~~~~~~

I2C:
    * New :doc:`smbus`. Useful to use other Python I2C modules with MCP2221 interface.
    * Fixed. I2C slave class exception when device is not present.

Documentation:
    * Conflict with kernel module ``hid_mcp2221``. See *Delay at the end of script (Linux)* in :doc:`install`.
    * Explain I2C speed limit for very short transfers.
    * Document :doc:`smbus`. Include example code for BME280 (Temperature, Pressure, Humidity sensor).


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
    * Added developers section with details about I2C transfers. See :doc:`internals`.

Misc:
    * Added test suite.
    * Added IOC edge detection setting in device representation.
    * Fixed. Bug when reset a device with customized VID/PID.
    * Multiple tries to find the device after a :func:`reset` (until timeout).


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



