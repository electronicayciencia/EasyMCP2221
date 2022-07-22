# This is to make examples work just by cloning the repo.
import sys
sys.path.append('../')
# ----------------------

# How to use I2C Slave helper class.
# Data logger: Read 10 ADC values from a PCF8591 with 1 second interval
# and store them in an EEPROM. Then, print the stored values.
import EasyMCP2221
from time import sleep

# Connect to MCP2221
mcp = EasyMCP2221.Device()

# Create two I2C Slaves
pcf    = mcp.I2C_Slave(0x48) # 8 bit ADC
eeprom = mcp.I2C_Slave(0x50) # serial memory

# Setup analog reading (and ignore the first value)
pcf.read_register(0b00000001)

print("Storing...")
for position in range (0, 10):
    v = pcf.read()
    eeprom.write_register(position, v, reg_bytes=2)
    sleep(1)

# Dump the 10 values
v = eeprom.read_register(0x0000, 10, reg_bytes=2)
print("Data: ")
print(list(v))
