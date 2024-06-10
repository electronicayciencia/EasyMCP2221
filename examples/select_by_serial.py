# Choose between multiple MCP2221 based on serial number
import EasyMCP2221

serials = ["0002596891", "0002596888", "0000000000"]

for s in serials:
    try:
        mcp = EasyMCP2221.Device(usbserial = s, open_timeout = 0)
        print(f"MCP with serial {s} is present")
    except:
        print(f"MCP with serial {s} is absent")
