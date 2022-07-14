Usage
=====

First, plug the board to one of your USB ports.

.. currentmodule:: EasyMCP2221

:class:`Device`

.. currentmodule:: EasyMCP2221.Device


Configure pin function:

- :func:`set_pin_function`


General purpose I/O functions:

- :func:`GPIO_read`
- :func:`GPIO_write`


Analog to digital Converter (ADC):

- :func:`ADC_config`
- :func:`ADC_read`


Digital to Analog Converter (DAC)

- :func:`DAC_config`
- :func:`DAC_write`


Inter-Integrated Circuit (I2C) bus

- :func:`I2C_write`
- :func:`I2C_read`
- :func:`I2C_cancel`
- :func:`I2C_is_idle`
- :func:`I2C_speed`


Clock output

- :func:`clock_config`


USB computer wake-up

- :func:`enable_power_management`
- :func:`wake_up_config`


Device reset

- :func:`reset`



