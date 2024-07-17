# ADS1115

We will use a SMBus compatible ready-to-use library from [chandrawi/ADS1x15-ADC](https://github.com/chandrawi/ADS1x15-ADC).

In `ADS1x15.py` file, replace the SMBus import line to use EasyMCP2221's SMBus class. See [SMBus compatible class](https://easymcp2221.readthedocs.io/en/latest/smbus.html) for more information.

Replace this:

```python
from smbus2 import SMBus
```

with:

```python
from EasyMCP2221 import SMBus
```

Run the examples in [chandrawi/ADS1x15-ADC](https://github.com/chandrawi/ADS1x15-ADC) repository. No further modifications needed.

```console
$ python ADS_read.py
ADS_read.py
ADS1X15_LIB_VERSION: 1.2.2
Analog0: 12991  1.624 V
Analog1: 4647   0.581 V
Analog2: 4622   0.578 V
Analog3: 4646   0.581 V
```

