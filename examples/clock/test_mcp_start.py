import EasyMCP2221
from time import sleep

mcp = EasyMCP2221.Device()
#mcp.I2C_speed(50000)
#mcp.trace_packets = True
rc = mcp.I2C_write(0x68, b'\0\1')
