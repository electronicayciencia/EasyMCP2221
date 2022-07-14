Install
=======

EasyMCP2221 should work in Windows and Linux. Install it using ``pip``.

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


