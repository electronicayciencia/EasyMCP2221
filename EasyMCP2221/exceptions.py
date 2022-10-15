class NotAckError(Exception):
    """ I2C device did not acknowledge last command or data.
    Possible causes are incorrect I2C address, device missing or busy.
    """

class TimeoutError(Exception):
    """ I2C transaction timed out.
    Possible causes are noise in the I2C bus, incorrect command, or device busy.
    """