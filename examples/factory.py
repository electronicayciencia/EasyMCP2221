# Revert MCP2221 to factory default.
# VID, PID and other options not supported by EasyMCP2221 library are not modified.
import EasyMCP2221

# Connect to device
mcp = EasyMCP2221.Device()

print("Current configuration:")
print(mcp)

mcp.set_pin_function(
    gp0 = "LED_URX", out0 = 1,
    gp1 = "LED_UTX", out1 = 1,
    gp2 = "USBCFG",  out2 = 1,
    gp3 = "LED_I2C", out3 = 1)

mcp.ADC_config(ref="1.024V")
mcp.DAC_config(ref="VDD")
mcp.DAC_write(8)
mcp.IOC_config("both")
mcp.clock_config(50, "12MHz")
mcp.enable_power_management(False)
mcp.I2C_speed(speed=100000)

r = input("Restore factory default settings? [y/n] ")

if r == "y":
    mcp.save_config()
    print("Default configuration saved.")
else:
    print("Not modified.")
    
mcp.reset()

