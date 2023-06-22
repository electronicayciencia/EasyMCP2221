# I2C transfer rate estimation
# - Reading individual bytes
# - Wrtiting individual bytes
# - Reading in chunks
# - Writing in chunks

import time
import EasyMCP2221


def single_byte_read():
    """Read one byte at a time one after the other, no seeking.
    Return bytes per second.
    """
    i = 0
    start = time.perf_counter()
    while time.perf_counter() <= start + 1:
        data = mcp.I2C_read(addr, 1)
        i = i + 1

    return i


def single_byte_seekread():
    """Seek to register 0 and read one byte.
    Return bytes per second.
    """
    i = 0
    start = time.perf_counter()

    while time.perf_counter() <= start + 1:
        mcp.I2C_write(addr, b"\0\0", "nonstop")
        data = mcp.I2C_read(addr, 1, "restart")
        i = i + 1

    return i


def single_byte_write():
    """Write one byte at a time at register 0. Write and seek are the same transfer.
    Return bytes per second.
    """
    i = 0
    start = time.perf_counter()
    while time.perf_counter() <= start + 1:
        mcp.I2C_write(addr, b"\0\0A")
        i = i + 1

    return i


def multiple_bytes_read(len=10000):
    """Read multiple bytes in a row (actual reading is done in chunks).
    Return bytes per second.
    """
    start = time.perf_counter()
    data = mcp.I2C_read(addr, len)
    end = time.perf_counter()

    rate = len / (end-start)
    return rate


def multiple_bytes_write(len=10000):
    """Write multiple bytes in a row (actual reading is done in chunks).
    Return bytes per second.
    """
    buffer = b"C" * len
    start = time.perf_counter()
    data = mcp.I2C_write(addr, b"\0\0"+buffer)
    end = time.perf_counter()

    rate = len / (end-start)
    return rate


# Connect to MCP2221
mcp = EasyMCP2221.Device()

# Optionally configure GP3 to show I2C bus activity.

mcp.set_pin_function(
    gp0 = "GPIO_OUT", out0 = True,
    gp1 = "GPIO_OUT", out1 = True,
    gp2 = "GPIO_IN",
    gp3 = "LED_I2C")

addr = 0x50
mcp.I2C_speed(100_000)

print("single_byte_read:",      single_byte_read())
print("single_byte_seekread:",  single_byte_seekread())
print("single_byte_write:",     single_byte_write())

print(100000)
print("multiple_bytes_read:",   int(multiple_bytes_read()))
print("multiple_bytes_write:",  int(multiple_bytes_write()))

mcp.I2C_speed(400000)
print(400000)
print("multiple_bytes_read:",   int(multiple_bytes_read()))
print("multiple_bytes_write:",  int(multiple_bytes_write()))


