# GPIO output True
import EasyMCP2221

# Connect to device
mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp0 = "GPIO_OUT", out0 = True,
    gp1 = "GPIO_OUT", out1 = True,
    gp2 = "GPIO_OUT", out2 = True,
    gp3 = "GPIO_OUT", out3 = True)
