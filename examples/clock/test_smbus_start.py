from EasyMCP2221 import SMBus

bus = SMBus()
#bus.mcp.trace_packets = True
bus.write_byte_data(0x68, 0x00, 0)
