# GPIO output and input demo emulating a "logic gate"
import EasyMCP2221

# Connect to device
mcp = EasyMCP2221.Device()

# GP1 and GP2 are inputs. GP3 will be an input.
mcp.set_pin_function(
    gp1 = "GPIO_IN",
    gp2 = "GPIO_IN",
    gp3 = "GPIO_OUT")

while True:
    (gp0, gp1, gp2, gp3) = mcp.GPIO_read()

    mcp.GPIO_write(gp3 = gp1 ^ gp2) # XOR gate

