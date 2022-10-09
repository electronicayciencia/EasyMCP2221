Full API reference
==================


Device Initialization
---------------------

.. currentmodule:: EasyMCP2221

.. autoclass:: Device


Pin configuration
-----------------

.. autofunction:: EasyMCP2221.Device.set_pin_function
.. autofunction:: EasyMCP2221.Device.save_config

GPIO
----

.. autofunction:: EasyMCP2221.Device.GPIO_read
.. autofunction:: EasyMCP2221.Device.GPIO_write


ADC
---

.. autofunction:: EasyMCP2221.Device.ADC_config
.. autofunction:: EasyMCP2221.Device.ADC_read


DAC
---

.. autofunction:: EasyMCP2221.Device.DAC_config
.. autofunction:: EasyMCP2221.Device.DAC_write


I2C
---

.. autofunction:: EasyMCP2221.Device.I2C_Slave
.. autofunction:: EasyMCP2221.Device.I2C_write
.. autofunction:: EasyMCP2221.Device.I2C_read
.. autofunction:: EasyMCP2221.Device.I2C_cancel
.. autofunction:: EasyMCP2221.Device.I2C_is_idle
.. autofunction:: EasyMCP2221.Device.I2C_speed

Clock output
------------

.. autofunction:: EasyMCP2221.Device.clock_config


USB wake-up
-----------

.. autofunction:: EasyMCP2221.Device.enable_power_management
.. autofunction:: EasyMCP2221.Device.wake_up_config


Device reset
------------

.. autofunction:: EasyMCP2221.Device.reset


Low level and debug
-------------------

.. autofunction:: EasyMCP2221.Device.SRAM_config
.. autofunction:: EasyMCP2221.Device.send_cmd
.. autoattribute:: EasyMCP2221.Device.cmd_retries
.. autoattribute:: EasyMCP2221.Device.debug_messages
.. autoattribute:: EasyMCP2221.Device.trace_packets

