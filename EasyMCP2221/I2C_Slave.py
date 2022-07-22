# API library for MCP2221(A).
# Electronicayciencia. 21/07/2022


class I2C_Slave:
    """ EasyMCP2221's I2C slave device.

    I2C_Slave helper class allows you to interact with I2C devices in a more object-oriented way.

    Usually you create new instances of this class using :func:`EasyMCP2221.Device.I2C_Slave` function. See *examples* section.

    Parameters:
        mcp (EasyMCP2221.Device): MCP2221 connected to this slave
        addr  (int) : Slave's I2C bus address
        force (bool, optional): Create an I2C_Slave even if the target device does not answer. Default: False.

    Raises:
        RuntimeError: If the device didn't acknowledge.

    Examples:
        You should create I2C_Slave objects from the inside of an EasyMCP2221.Device:

        >>> import EasyMCP2221
        >>> mcp = EasyMCP2221.Device()
        >>> eeprom = mcp.I2C_Slave(0x50)
        >>> eeprom
        EasyMCP2221's I2C slave device at bus address 0x50.

        Or in a stand-alone way:

        >>> import EasyMCP2221
        >>> from EasyMCP2221 import I2C_Slave
        >>> mcp = EasyMCP2221.Device()
        >>> eeprom = I2C_Slave.I2C_Slave(mcp, 0x50)

    Note:
        MCP2221 firmware exposes a subset of predefined I2C operations, but does not allow I2C primitives (i.e. start, stop, read + ack, read + nak, clock bus, etc.).
    """

    mcp = None
    addr = None

    def __init__(self, mcp, addr, force = False):
        self.mcp = mcp
        self.addr = addr

        if not force and not self.is_present():
            raise RuntimeError("No device found at address 0x%02X." % (addr))


    def __repr__(self):
        return "EasyMCP2221's I2C slave device at bus address 0x%02X." % (self.addr)


    def is_present(self):
        """ Check if slave is present.

        Perform a read operation (of 1 bytes length) to the slave address and expect acknowledge.

        Return:
            bool: True if the slave answer, False if not.
        """
        try:
            self.mcp.I2C_read(self.addr)
            return True
        except RuntimeError:
            return False


    #######################################################################
    # Read
    #######################################################################
    def read_register(self, register, length = 1, reg_bytes = 1, reg_byteorder = 'big'):
        """ Read from a specific register, position or command.

        Sequence:

        - Start
        - Send device I2C address + R/W bit 0
        - Send register byte, memory position or command
        - Repeated start
        - Send device I2C address + R/W bit 1
        - Read ``length`` bytes
        - Stop

        See :func:`EasyMCP2221.Device.I2C_read` for more information.

        Parameters:
            register      (int): Register to read, memory position or command.
            length        (int, optional): How many bytes is the answer to read (default read 1 byte).
            reg_bytes     (int, optional): How many bytes is the register, position or command to send (default 1 byte).
            reg_byteorder (str, optional): Byte order of the register address. *'little'* or *'big'*. Default 'big'.

        Return:
            list of bytes

        Examples:
            Read from a regular i2c device, register 0x0D:

            >>> bme.read_register(0x0D)
            >>> b'\xff'

            Read 10 bytes from I2C EEPROM (2 bytes memory position):

            >>> eeprom.read_register(2000, 25, reg_bytes=2)
            >>> b'en muchas partes hallaba '
        """
        self.mcp.I2C_write(
            self.addr,
            register.to_bytes(reg_bytes, byteorder = reg_byteorder),
            kind = 'nonstop')

        data = self.mcp.I2C_read(
            self.addr,
            length,
            kind = 'restart')

        return data


    def read(self, length = 1):
        """ Read from I2C slave.

        See :func:`EasyMCP2221.Device.I2C_read`.

        Parameters:
            length (int): How many bytes to read. Default 1 byte.

        Return:
            list of bytes

        Raises:
            RuntimeError: if the I2C slave didn't acknowledge or the I2C engine was busy.
        """
        return self.mcp.I2C_read(self.addr, length)



    #######################################################################
    # Write
    #######################################################################
    def write_register(self, register, data, reg_bytes = 1, reg_byteorder = 'big'):
        """ Write to a specific register, position or command.

        Sequence:

        - Start
        - Send device I2C address + R/W bit 0
        - Send register byte, memory position or command
        - Repeated start
        - Send device I2C address + R/W bit 0
        - Write ``data``
        - Stop

        See :func:`EasyMCP2221.Device.I2C_write` for more information.

        Parameters:
            register      (int): Register to read, memory position or command.
            data        (bytes): Data to write. Bytes, int from 0 to 255, or list of ints from 0 to 255.
            reg_bytes     (int, optional): How many bytes is the register, position or command to send (default 1 byte).
            reg_byteorder (str, optional): Byte order of the register address. *'little'* or *'big'*. Default 'big'.

        Examples:
            Set PCF8591's DAC output to 255. Command 0bx1xxxxxx.

            >>> pcf.write_register(0b01000000, 255)

            Write a stream of bytes to an EEPROM at position 0x1A00 (2 bytes memory position):

            >>> eeprom.write_register(0x1A00, b'Testing 123...', reg_bytes=2)
            >>> eeprom.read_register(0x1A00, 14, reg_bytes=2)
            b'Testing 123...'
        """
        if type(data) == int:
            data = bytes([data])
        elif type(data) == list:
            data = bytes(data)

        self.mcp.I2C_write(
            self.addr,
            register.to_bytes(reg_bytes, byteorder=reg_byteorder) + data)

    def write(self, data):
        """ Write to I2C slave.

        See :func:`EasyMCP2221.Device.I2C_write` for more information.

        Parameters:
            data (bytes): Data to write. Bytes, int from 0 to 255, or list of ints from 0 to 255.

        Raises:
            RuntimeError: if the I2C slave didn't acknowledge or the I2C engine was busy.
        """
        if type(data) == int:
            data = bytes([data])
        elif type(data) == list:
            data = bytes(data)

        self.mcp.I2C_write(self.addr, data)
