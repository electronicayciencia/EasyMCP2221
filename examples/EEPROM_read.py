# This is to make examples work just by cloning the repo.
import sys
sys.path.append('../')
# ----------------------

# Simple EEPROM storage.
import EasyMCP2221

# Connect to MCP2221
mcp = EasyMCP2221.Device()

# Configure GP3 to show I2C bus activity.
mcp.set_pin_function(gp3 = "LED_I2C")

MEM_ADDR = 0x50
MEM_POS  = 0

# Seek EEPROM to position
mcp.I2C_write(
    addr = MEM_ADDR,
    data = MEM_POS.to_bytes(2, byteorder = 'little'))

# Read max 100 bytes
data = mcp.I2C_read(
    addr = MEM_ADDR,
    size = 100)

data = data.split(b'\0')[0]
print("Phrase stored was: " + data.decode('utf-8'))

