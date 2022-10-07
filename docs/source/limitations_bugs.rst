Limitations and bugs
====================

.. currentmodule:: EasyMCP2221.Device

Limitations
-----------

USB speed limits:

- GPIO update rate :func:`GPIO_write`: 500Hz
- GPIO read rate for :func:`GPIO_read`: 500Hz
- ADC sample rate for :func:`ADC_read`: 500Hz.
- DAC update rate for :func:`DAC_write`: 500Hz.
- GPIO update rate using :func:`set_pin_function`: 250Hz.


The ADC seems to be always connected. So leakage current for GP1, GP2 and GP3 is greater than for GP0. Think of it as a very weak *pull-down* resistor on these pins.




Bugs
----

None reported.

Bug tracking system: https://github.com/electronicayciencia/EasyMCP2221/issues

