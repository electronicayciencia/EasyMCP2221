import unittest
import time
from random import randbytes

import EasyMCP2221
from EasyMCP2221.exceptions import *


class I2C_Slave(unittest.TestCase):

    def setUp(self):
        self.i2caddr = 0x50
        self.mcp = EasyMCP2221.Device(trace_packets = 0)

        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT", out0 = 1, # pull-up SCL
            gp1 = "GPIO_OUT", out1 = 1, # pull-up SCL
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")


    def test_full_eeprom(self):
        """Write full EEPROM at maximum speed. Read it back, compare and time it."""

        max_w_time = 4
        max_r_time = 2

        speed = 500_000
        wait_ms = 1
        memsize = 128*1024//8
        pagesize = 64

        content = randbytes(memsize)

        eeprom = self.mcp.I2C_Slave(self.i2caddr, speed=speed)

        # Write EEPROM in blocks of pagesize bytes.
        start_write = time.perf_counter()
        page = 0
        for i in range(0, memsize, pagesize):
            #print("reg: %d (%d - %d)" % (page * pagesize, 0+i, pagesize+i))
            buffer = content[0+i:pagesize+i]

            eeprom.write_register(page * pagesize, buffer, reg_bytes=2)

            page = page + 1

            until = time.perf_counter() + wait_ms / 1000
            while time.perf_counter() < until:
                pass

        end_write = time.perf_counter()

        # Read EEPROM (65535 is the max I2C_read transfer)
        start_read = time.perf_counter()
        buffer = eeprom.read_register(0, memsize, reg_bytes=2)
        end_read = time.perf_counter()

        w_time = end_write - start_write
        r_time = end_read  - start_read

        self.assertTrue( buffer == content, msg = "Write / read differences.")
        self.assertTrue( r_time < max_r_time, msg = "Slow reading: %.2fs." % (r_time))
        self.assertTrue( w_time < max_w_time, msg = "Slow writing: %.2fs." % (w_time))


if __name__ == '__main__':
    unittest.main()
