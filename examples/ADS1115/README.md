# ADS1115

We will use a SMBus compatible ready-to-use library from [chandrawi/ADS1x15-ADC](https://github.com/chandrawi/ADS1x15-ADC).

Need to replace the SMBus import line in the library to use EasyMCP2221's SMBus class. See [SMBus compatible class](https://easymcp2221.readthedocs.io/en/latest/smbus.html) for more information.

Replace this:

```python
from smbus2 import SMBus
```

with:

```python
from EasyMCP2221 import SMBus
```

Run the examples in [chandrawi/ADS1x15-ADC](https://github.com/chandrawi/ADS1x15-ADC) repository with no further modifications. 

```console
$ python ADS_continuous.py
ADS_continuous.py
ADS1X15_LIB_VERSION: 1.2.2
0.000 V
0.104 V
1.954 V
2.359 V
3.285 V
3.085 V
2.922 V
2.463 V
2.085 V
1.622 V
```
