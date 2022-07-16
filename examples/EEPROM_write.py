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

# Take a phrase
phrase = input("Tell me a phrase: ")
# Encode into bytes using preferred encoding method
phrase_bytes = bytes(phrase, encoding = 'utf-8')

# Store in EEPROM
# Note that internal EEPROM buffer is only 64 bytes.
mcp.I2C_write(MEM_ADDR,
    MEM_POS.to_bytes(2, byteorder = 'little') +  # position to write
    bytes(phrase, encoding = 'utf-8') +          # data
    b'\0')                                       # null

print("Saved to EEPROM.")