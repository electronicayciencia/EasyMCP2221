Install
=======


Installation via PIP
--------------------

Pip command for Linux:

.. code-block:: console

    pip install EasyMCP2221

Pip command for Windows:

.. code-block:: console

    py -m pip install EasyMCP2221


EasyMCP2221 depends on ``hidapi``, which in fact needs some backend depending on OS. Sometimes this is troublesome.

If you get an error like this:

.. code-block:: console

    ImportError: Unable to load any of the following libraries:libhidapi-hidraw.so libhidapi-hidraw.so.0 libhidapi-libusb.so libhidapi-libusb.so.0 libhidapi-iohidmanager.so libhidapi-iohidmanager.so.0 libhidapi.dylib hidapi.dll libhidapi-0.dll


Try to install the following packages using ``pip``:

- libusb
- libusb1

If that doesn't work, try manually installing libhidapi from https://github.com/libusb/hidapi/releases.


Editable for testing
--------------------

You may want to install this library from a cloned GitHub repository, usually for testing or development purposes.

First create and activate a new virtual environment. Update pip if needed.

.. code-block:: console

	d:\tmp>python -m venv init easymcp_dev

	d:\tmp>cd easymcp_dev

	d:\tmp\easymcp_dev>Scripts\activate

	(easymcp_dev) d:\tmp\easymcp_dev> python -m pip install --upgrade pip


Then, clone the home repository and perform the installation in *editable* (``-e``) mode.

.. code-block:: console

    (easymcp_dev) d:\tmp\easymcp_dev>git clone https://github.com/electronicayciencia/EasyMCP2221
    Cloning into 'EasyMCP2221'...
    ...
    
    (easymcp_dev) d:\tmp\easymcp_dev>pip install -e EasyMCP2221
    Obtaining file:///D:/tmp/easymcp_dev/EasyMCP2221
      Installing build dependencies ... done
    ...
    Successfully installed EasyMCP2221-0.0+unreleased.local


