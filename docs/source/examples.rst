Examples
========

Check device communication
--------------------------

.. literalinclude:: ../../examples/device.py


The output should be like this:

::

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



Basic digital I/O
-----------------

.. literalinclude:: ../../examples/gpio_simplest.py
   :emphasize-lines: 5-8
   :linenos:



