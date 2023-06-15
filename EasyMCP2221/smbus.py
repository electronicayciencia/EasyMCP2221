from struct import pack, unpack
import EasyMCP2221

I2C_SMBUS_BLOCK_MAX = 255  # len is one byte only

class SMBus(object):

    """
    Initialize and open an i2c bus connection.

    :param bus: (for compatibility only, not used) i2c bus number (e.g. 0 or 1)
        or an absolute file path (e.g. `/dev/i2c-42`).
        If not given, a subsequent  call to ``open()`` is required.
    :type bus: int or str
    :param force: (for compatibility only, not used) force using the slave address even when driver is already using it.
    :type force: boolean
    :param VID: Vendor Id (default to ``0x04D8``)
    :param PID: Product Id (default to ``0x00DD``)
    :param clock: I2C clock frequency (default to ``100kHz``)
    """

    def __init__(self, bus=None, force=False, VID=0x04D8, PID=0x00DD, devnum=0, clock=100_000):

        self.mcp = EasyMCP2221.Device(VID, PID, devnum)
        self.mcp.I2C_speed(clock)


    def _read_register(self, addr, register, length = 1, reg_bytes = 1, reg_byteorder = 'big'):
        """ Generic read from a register. See description in I2C_Slave class. """
        self.mcp.I2C_write(
            addr,
            register.to_bytes(reg_bytes, byteorder = reg_byteorder),
            kind = 'nonstop')

        data = self.mcp.I2C_read(
            addr,
            length,
            kind = 'restart')

        return data


    def _read(self, addr, length = 1):
        """ Generic read from an I2C slave. See description in I2C_Slave class. """
        return self.mcp.I2C_read(addr, length)


    def _write_register(self, addr, register, data, reg_bytes = 1, reg_byteorder = 'big'):
        """ Generic write to a specific register, position or command. See description in I2C_Slave class. """

        if type(data) == int:
            data = bytes([data])
        elif type(data) == list:
            data = bytes(data)

        self.mcp.I2C_write(
            addr,
            register.to_bytes(reg_bytes, byteorder=reg_byteorder) + data)


    def _write(self, addr, data):
        """ Generic write to I2C slave. See description in I2C_Slave class. """
        if type(data) == int:
            data = bytes([data])
        elif type(data) == list:
            data = bytes(data)

        self.mcp.I2C_write(addr, data)


    #### SMBUS interface ####

    def open(self, bus):
        """
        (For compatibility only, no effects)
        Open a given i2c bus.

        :param bus: i2c bus number (e.g. 0 or 1)
            or an absolute file path (e.g. '/dev/i2c-42').
        :type bus: int or str
        :raise TypeError: if type(bus) is not in (int, str)
        """
        pass


    def close(self):
        """
        (For compatibility only, no effects)
        Close the i2c connection.
        """
        pass


    def read_byte(self, i2c_addr, force=None):
        """
        Read a single byte from a device.

        :rtype: int
        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param force:
        :type force: Boolean
        :return: Read byte value
        """
        out = self._read(i2c_addr)
        return unpack("B", out)[0]


    def write_byte(self, i2c_addr, value, force=None):
        """
        Write a single byte to a device.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param value: value to write
        :type value: int
        :param force:
        :type force: Boolean
        """
        self._write(i2c_addr, value)


    def read_byte_data(self, i2c_addr, register, force=None):
        """
        Read a single byte from a designated register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to read
        :type register: int
        :param force:
        :type force: Boolean
        :return: Read byte value
        :rtype: int
        """
        out = self._read_register(i2c_addr, register)
        return unpack("B", out)[0]


    def write_byte_data(self, i2c_addr, register, value, force=None):
        """
        Write a byte to a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to write to
        :type register: int
        :param value: Byte value to transmit
        :type value: int
        :param force:
        :type force: Boolean
        :rtype: None
        """
        self._write_register(i2c_addr, register, value)


    def read_word_data(self, i2c_addr, register, force=None):
        """
        Read a single word (2 bytes) from a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to read
        :type register: int
        :param force:
        :type force: Boolean
        :return: 2-byte word
        :rtype: int
        """
        out = self._read_register(i2c_addr, register, length = 2)
        return unpack("h", out)[0]


    def write_word_data(self, i2c_addr, register, value, force=None):
        """
        Write a single word (2 bytes) to a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to write to
        :type register: int
        :param value: Word value to transmit
        :type value: int
        :param force:
        :type force: Boolean
        :rtype: None
        """
        data = pack("h", value)
        self._write_register(i2c_addr, register, data)


    def process_call(self, i2c_addr, register, value, force=None):
        """
        Executes a SMBus Process Call, sending a 16-bit value and receiving a 16-bit response

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to read/write to
        :type register: int
        :param value: Word value to transmit
        :type value: int
        :param force:
        :type force: Boolean
        :rtype: int
        """
        data = pack("h", value)
        self.mcp.I2C_write(i2c_addr, register + data, kind = 'nonstop')

        data = self.mcp.I2C_read(i2c_addr, length = 2, kind = 'restart')
        return unpack("h", data)[0]


    def read_block_data(self, i2c_addr, register, force=None):
        """
        Read a block of up to 32-bytes from a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Start register
        :type register: int
        :param force:
        :type force: Boolean
        :return: List of bytes
        :rtype: list
        """
        out = self._read_register(i2c_addr, register, length = I2C_SMBUS_BLOCK_MAX)
        length = out[0]
        return out[1:1+length]


    def write_block_data(self, i2c_addr, register, data, force=None):
        """
        Write a block of byte data to a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Start register
        :type register: int
        :param data: List of bytes
        :type data: list
        :param force:
        :type force: Boolean
        :rtype: None
        """
        length = len(data)
        if length > I2C_SMBUS_BLOCK_MAX:
            raise ValueError("Data length cannot exceed %d bytes" % I2C_SMBUS_BLOCK_MAX)

        self._write_register(i2c_addr, register, bytes([length]) + data)


    def block_process_call(self, i2c_addr, register, data, force=None):
        """
        Executes a SMBus Block Process Call, sending a variable-size data
        block and receiving another variable-size response

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to read/write to
        :type register: int
        :param data: List of bytes
        :type data: list
        :param force:
        :type force: Boolean
        :return: List of bytes
        :rtype: list
        """
        length = len(data)
        self.mcp.I2C_write(i2c_addr, register + bytes([length]) + data, kind = 'nonstop')

        out = self.mcp.I2C_read(i2c_addr, length = I2C_SMBUS_BLOCK_MAX, kind = 'restart')
        length = out[0]
        return out[1:1+length]


    def read_i2c_block_data(self, i2c_addr, register, length, force=None):
        """
        Read a block of byte data from a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Start register
        :type register: int
        :param length: Desired block length
        :type length: int
        :param force:
        :type force: Boolean
        :return: List of bytes
        :rtype: list
        """
        if length > I2C_SMBUS_BLOCK_MAX:
            raise ValueError("Desired block length over %d bytes" % I2C_SMBUS_BLOCK_MAX)

        out = self._read_register(i2c_addr, register, length = length)
        return out


    def write_i2c_block_data(self, i2c_addr, register, data, force=None):
        """
        Write a block of byte data to a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Start register
        :type register: int
        :param data: List of bytes
        :type data: list
        :param force:
        :type force: Boolean
        :rtype: None
        """
        length = len(data)
        if length > I2C_SMBUS_BLOCK_MAX:
            raise ValueError("Data length cannot exceed %d bytes" % I2C_SMBUS_BLOCK_MAX)

        self._write_register(i2c_addr, register, data)
