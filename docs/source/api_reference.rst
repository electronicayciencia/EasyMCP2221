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

.. autofunction:: EasyMCP2221.Device.ADC_read
.. autofunction:: EasyMCP2221.Device.ADC_config


DAC
---

.. autofunction:: EasyMCP2221.Device.DAC_write
.. autofunction:: EasyMCP2221.Device.DAC_config


I2C
---

.. autofunction:: EasyMCP2221.Device.I2C_Slave
.. autofunction:: EasyMCP2221.Device.I2C_write
.. autofunction:: EasyMCP2221.Device.I2C_read
.. autofunction:: EasyMCP2221.Device.I2C_speed

.. autofunction:: EasyMCP2221.Device.I2C_cancel
.. autofunction:: EasyMCP2221.Device.I2C_is_idle


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

.. autofunction:: EasyMCP2221.Device.read_flash_info

.. autofunction:: EasyMCP2221.Device.SRAM_config
.. autofunction:: EasyMCP2221.Device.send_cmd

.. autofunction:: EasyMCP2221.Device._i2c_release
.. autofunction:: EasyMCP2221.Device._i2c_status

.. autoattribute:: EasyMCP2221.Device.cmd_retries
.. autoattribute:: EasyMCP2221.Device.debug_messages
.. autoattribute:: EasyMCP2221.Device.trace_packets


Exceptions
----------

To capture EasyMCP2221.exceptions you must qualify them as ``EasyMCP2221.exceptions``:

.. code-block:: python

    try:
        mcp.I2C_read(0x51, 1)
    except EasyMCP2221.exceptions.NotAckError:
        print("No device")
        exit()
    except EasyMCP2221.exceptions.LowSCLError:
        print("SCL low")

or import them explicitly:

.. code-block:: python

    from EasyMCP2221.exceptions import *

    ...

    try:
        mcp.I2C_read(0x51, 1)
    except NotAckError:
        print("No device")
        exit()
    except LowSCLError:
        print("SCL low")


.. autoexception:: EasyMCP2221.exceptions.NotAckError
.. autoexception:: EasyMCP2221.exceptions.TimeoutError
.. autoexception:: EasyMCP2221.exceptions.LowSCLError
.. autoexception:: EasyMCP2221.exceptions.LowSDAError
