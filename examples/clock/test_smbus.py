from EasyMCP2221 import SMBus

bus = SMBus()

a = bus._read_register(0x68, 0x00)
print(f"{a[0]:02x}")
