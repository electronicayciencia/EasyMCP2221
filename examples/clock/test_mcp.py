import EasyMCP2221

mcp = EasyMCP2221.Device()
#mcp.trace_packets = True
#mcp.I2C_speed(50000)

rc = mcp.I2C_write(0x68, b'\0', "nonstop")
rc = mcp.I2C_read(0x68, 1, "restart")

print(f"{rc[0]:02x}")
