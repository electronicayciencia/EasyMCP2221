# This is to make examples work just by cloning the repo.
import sys
sys.path.append('../')
# ----------------------

# Just check if the MCP2221 is there.
import EasyMCP2221

try:
    mcp = EasyMCP2221.Device()

except RuntimeError:
    print("MCP2221 is not there... :(")
    exit()

print("MCP2221 is there!")
print(mcp)
