# I2C example to read PCF8591 module values.
from time import sleep
import EasyMCP2221

# Connect to MCP2221
mcp = EasyMCP2221.Device()

# Default address is 0x48
addr = 0x48

# Control register:
#                      .0.. .... - No DAC output
#                      ..00 .... - 4 individual inputs
#                      .... .1.. - Auto-increment channel
#                      .... ..01 - ADC start channel 1
mcp.I2C_write(addr, [0b0000_0101])

while True:
    (ntc, ldr, flo, pot) = mcp.I2C_read(addr, 4)
    print("NTC: %2d%%,  LDR: %2d%%,  Float: %2d%%,  Pot: %2d%%" %
        (ntc / 256 * 100,
         ldr / 256 * 100,
         flo / 256 * 100,
         pot / 256 * 100))

    sleep(0.1)
