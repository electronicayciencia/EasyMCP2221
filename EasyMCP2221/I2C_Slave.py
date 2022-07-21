# API library for MCP2221(A).
# Electronicayciencia. 21/07/2022

class I2C_Slave:

    mcp = None
    addr = None

    def __init__(self, mcp, addr):
        self.mcp = mcp
        self.addr = addr

        if not self.check_slave():
            raise RuntimeError("No device found at address 0x%02X." % (addr))


    def __repr__(self):
        return "EasyMCP2221's I2C slave device at bus address 0x%02X." % (self.addr)


    def check_slave(self):
        """ return True if slave anwser, False if not"""
        try:
            self.mcp.I2C_read(self.addr)
            return True
        except RuntimeError:
            return False


    def read_register(self, register, size = 1, reg_bytes = 1, reg_byteorder = 'big'):
        """ Seek register and read. """
        self.mcp.I2C_write(
            self.addr,
            register.to_bytes(reg_bytes, byteorder=reg_byteorder),
            kind = 'nonstop')

        data = self.mcp.I2C_read(
            self.addr,
            size,
            kind = 'restart')

        return data

