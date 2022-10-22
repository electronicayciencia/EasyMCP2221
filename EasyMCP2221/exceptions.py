class NotAckError(Exception):
    """ I2C slave device did not acknowledge last command or data.
    Possible causes are incorrect I2C address, device missing or busy.
    """

class TimeoutError(Exception):
    """ I2C transaction timed out.

    Possible causes:
        - I2C bus noise
        - incorrect command, protocol or speed
        - slave device busy (e.g. EEPROM write cycle)
    """

class LowSCLError(Exception):
    """ SCL remains low.

    SCL should go up when I2C bus is idle.

    Possible causes:
        - Missing pull-up resistor or too high.
        - Signal integrity issues due to noise.
        - A slave device is using clock stretching to indicate it is busy.
        - Another device is using the bus.
    """

class LowSDAError(Exception):
    """ SDA remains low.

    SDA should go up when I2C bus is idle.

    Possible causes:
        - Missing pull-up resistor or too high.
        - Signal integrity issues due to noise.
        - An I2C read transfer timed out while slave was sending data, and now the I2C
          bus is locked-up. Read the Hint.

    Hint:
        About the I2C bus locking-up.

        Sometimes, due to a glitch or premature timeout, the master terminates the transfer.
        But the slave was in the middle of sending a byte. So it is expecting a few more clocks
        cycles to send the rest of the byte.

        Since the master gave up, it will not clock the bus anymore, and so the slave won't
        release SDA line. The master, seeing SDA line busy, refuses to initiate any new
        I2C transfer. If the slave does not implement any timeout (SMB slaves do have it,
        but I2C ones don't), the I2C bus is locked-up forever.

        MCP2221's I2C engine cannot solve this problem. You can either manually clock the
        bus using any GPIO line, or cycle the power supply.
    """
