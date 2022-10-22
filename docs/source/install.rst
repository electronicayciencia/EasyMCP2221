Install
=======


Regular installation via PIP
----------------------------

Pip command for Linux:

.. code-block:: console

    pip install EasyMCP2221

Pip command for Windows:

.. code-block:: console

    py -m pip install EasyMCP2221


Troubleshooting
~~~~~~~~~~~~~~~

EasyMCP2221 depends on ``hidapi``, which in fact needs some backend depending on OS. Sometimes this is troublesome.

If you get an error like this:

.. code-block:: console

    ImportError: Unable to load any of the following libraries:libhidapi-hidraw.so libhidapi-hidraw.so.0 libhidapi-libusb.so libhidapi-libusb.so.0 libhidapi-iohidmanager.so libhidapi-iohidmanager.so.0 libhidapi.dylib hidapi.dll libhidapi-0.dll


Try to install the following packages using ``pip``:

- libusb
- libusb1

If that doesn't work, try manually installing libhidapi from https://github.com/libusb/hidapi/releases.

Sometimes, yo need to manually copy ``libusb-1.0.dll`` to ``C:\Windows\System32``. It used to be in ``C:\Users\[username]\AppData\Local\Programs\Python\Python39\Lib\site-packages\libusb\_platform\_windows\x64\libusb-1.0.dll`` or similar path.

If the library loads but it does not find your device, try using any of the Microchip's official tools to verify that everything is working fine.


Editable for testing
--------------------

You may want to install this library from a cloned GitHub repository, usually for testing or development purposes.

First create and activate a new virtual environment. Update pip if needed.

.. code-block:: console

	> python -m venv init easymcp_dev
	> cd easymcp_dev
	> Scripts\activate
	> python -m pip install --upgrade pip


Then, clone the home repository inside that virtual environment and perform the 
installation in *editable* (``-e``) mode.

.. code-block:: console

    > git clone https://github.com/electronicayciencia/EasyMCP2221
    Cloning into 'EasyMCP2221'...
    ...

    > pip install -e EasyMCP2221
    Obtaining file:///D:/tmp/easymcp_dev/EasyMCP2221
      Installing build dependencies ... done
    ...
    Successfully installed EasyMCP2221-0.0+unreleased.local


If you get this error: *"File "setup.py" not found. Directory cannot be installed in editable mode"*, update PIP.

.. code-block:: console

    > python -m pip install --upgrade pip


If you get this one: *"EasyMCP2221 does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found."*, please check working directory. You must be in the root of the cloned GitHub repository.


Local documentation
~~~~~~~~~~~~~~~~~~~

This is an optional step. To compile documentation locally you will need ``sphinx`` and ``RTD theme``.

.. code-block:: console

    pip install -U sphinx
    pip install -U sphinx_rtd_theme

Compilation:

.. code-block:: console

    cd docs
    make html

Main HTML file is *EasyMCP2221/docs/build/html/index.html*.
