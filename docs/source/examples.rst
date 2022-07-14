Examples
========

.. currentmodule:: EasyMCP2221

First thing is to import ``EasyMCP2221`` and create a new :class:`Device`. If you can, that's great news! If you don't, check if OS is able to "see" the device or not.

.. literalinclude:: ../../examples/device.py
   :lines: 6-

The output should be like this:

.. code-block:: console

	MCP2221 is there!
	{
		"Chip settings": {
			"Power management options": "enabled",
			"USB PID": "0x00DD",
			"USB VID": "0x04D8",
			"USB requested number of mA": 100
		},
		"Factory Serial": "01234567",
		"GP settings": {},
		"USB Manufacturer": "Microchip Technology Inc.",
		"USB Product": "MCP2221 USB-I2C/UART Combo",
		"USB Serial": "0000000000"
	}



.. currentmodule:: EasyMCP2221.Device


Basic GPIO
----------

Basic digital output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



Configure pin function using :func:`set_pin_function`, then use :func:`GPIO_write` to change its output.

.. literalinclude:: ../../examples/gpio_simplest.py
   :lines: 6-


Digital output: LED blinking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. currentmodule:: EasyMCP2221.Device

Same as before, but use :func:`GPIO_write` in a loop to change its output periodically.

.. literalinclude:: ../../examples/gpio_blink.py
   :lines: 6-


Digital input: Mirror state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We introduce :func:`GPIO_read` this time.

In order to illustrate how to read from GPIO digital input, let's setup GP2 and GP3 to mimic the state of GP0 and GP1.

.. literalinclude:: ../../examples/gpio_mirror.py
   :lines: 6-



Analog signals
--------------


ADC basics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, we setup GP1, GP2 and GP3 as analog inputs using :func:`set_pin_function`. Configure ADC reference with :func:`ADC_config` and lastly, read ADC values using :func:`ADC_read`.

It works better if you take off the LED and connect three potentiometers to the inputs.

Remember to **always put a 330 ohm resistor** right in series with any GP pin. That way, if you by mistake configured it as an output, the short circuit current won't exceed the 20mA.

.. literalinclude:: ../../examples/ADC.py
   :lines: 6-

This is the console output when you move a variable resistor in GP3.

.. code-block:: console

	ADC0:  0.3%    ADC1:  0.2%    ADC2:  0.0%
	ADC0:  0.3%    ADC1:  0.1%    ADC2:  0.0%
	ADC0:  0.3%    ADC1:  0.2%    ADC2:  9.9%
	ADC0:  0.2%    ADC1:  0.1%    ADC2: 21.7%
	ADC0:  0.3%    ADC1:  0.3%    ADC2: 31.7%
	ADC0:  0.2%    ADC1:  0.0%    ADC2: 38.2%
	ADC0:  0.4%    ADC1:  0.3%    ADC2: 45.5%
	ADC0:  0.2%    ADC1:  0.0%    ADC2: 52.3%
	ADC0:  0.3%    ADC1:  0.3%    ADC2: 56.2%
	ADC0:  0.1%    ADC1:  0.0%    ADC2: 58.8%
	ADC0:  0.4%    ADC1:  0.2%    ADC2: 61.6%
	ADC0:  0.1%    ADC1:  0.0%    ADC2: 64.6%
	ADC0:  0.3%    ADC1:  0.2%    ADC2: 67.1%
	ADC0:  0.2%    ADC1:  0.2%    ADC2: 70.4%
	ADC0:  0.3%    ADC1:  0.1%    ADC2: 74.5%
	ADC0:  0.2%    ADC1:  0.1%    ADC2: 79.2%
	ADC0:  0.2%    ADC1:  0.1%    ADC2: 80.6%


Mixed signal: level meter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We will use the analog level in GP3 to set the state or three leds connected to GP0, GP1 and GP2.

.. literalinclude:: ../../examples/level_meter.py
   :lines: 6-


DAC: LED fading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We use :func:`DAC_config` and :func:`DAC_write` to make a LED (connected to GP3 or GP2) to fade-in and fade-out.

.. literalinclude:: ../../examples/DAC.py
   :lines: 6-



I2C bus
----------

I2C bus scan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We will use :func:`I2C_read` to send a read command to any possible I2C address in the bus. The moment we get an acknowledge, we know there is some slave connected.

To make this example work, you need to get an EEPROM (e.g. 24LC128) and connect it properly to the SCA and SCL lines, as well as power supply.

.. literalinclude:: ../../examples/I2C_scan.py
   :lines: 6-

This is my output:

.. code-block:: console

	$ python I2C_scan.py
	Searching...
	I2C slave found at address 0x50


Write to an EEPROM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, we will use :func:`I2C_write` to write some string in the first memory position of an EEPROM.

.. literalinclude:: ../../examples/EEPROM_write.py
   :lines: 6-


Result:

.. code-block:: console

    $ python EEPROM_write.py
    Tell me a phrase: This is an example.
    Saved to EEPROM.


Read from an EEPROM
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Same as before but reading

We seek the first position writing ``0x0000``, then func:`I2C_read` 100 bytes and print until the first null.

On slower devices, the read may fail. Yo need to :func:`I2C_cancel` then and try again increasing func:`I2C_read`'s timeout.

.. literalinclude:: ../../examples/EEPROM_read.py
   :lines: 6-

Output:

.. code-block:: console

    $ python EEPROM_read.py
    Phrase stored was: This is an example.

