import EasyMCP2221
mcp = EasyMCP2221.Device()
ds = mcp.I2C_Slave(0x68)

a = ds.read_register(0x00)
print(f"{a[0]:02x}")
