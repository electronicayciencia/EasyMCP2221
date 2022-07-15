Limitations and bugs
====================

.. currentmodule:: EasyMCP2221.Device

Limitations
-----------

USB polling rate for this device is 250Hz. That means:

- Maximum GPIO output frequency using :func:`GPIO_write`: 250Hz
- Maximum GPIO output frequency using :func:`set_pin_function`: 120Hz aprox.
- Maximum GPIO input frequency for :func:`GPIO_read`: 250Hz
- This also affects to ADC reading rate, DAC updating, and so on.


The ADC seems to be always connected. So leakage current for GP1, GP2 and GP3 is greater than for GP0. Think of it as a very weak *pull-down* resistor on these pins.




Bugs
----

None reported.

Bug tracking system: https://github.com/electronicayciencia/EasyMCP2221/issues

