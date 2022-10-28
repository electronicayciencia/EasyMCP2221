import unittest
import json
from random import randbytes
from time import sleep

import EasyMCP2221
from EasyMCP2221.exceptions import *


class I2C(unittest.TestCase):

    def setUp(self):
        self.i2caddr = 0x50
        self.NO_i2caddr = 0x51

        self.mcp = EasyMCP2221.Device(trace_packets = 0)

        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT", out0 = 1, # pull-up SCL
            gp1 = "GPIO_OUT", out1 = 1, # pull-up SCL
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")

        self.mcp.I2C_speed(100000)


    def tearDown(self):
        """Safe status """
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT", out0 = 1, # pull-up SCL
            gp1 = "GPIO_OUT", out1 = 1, # pull-up SCL
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")

        self.assertTrue(self.check_rw(16))


    def check_rw(self, length):
        """Try to use I2C to write then read from EEPROM to test the bus."""

        self.mcp.I2C_speed(100000)

        content = randbytes(length)
        self.mcp.I2C_write(self.i2caddr, b"\x00\x00" + content)

        self.mcp.I2C_write(self.i2caddr, b'\x00\x00', "nonstop")
        response = self.mcp.I2C_read(self.i2caddr, len(content), "restart")

        return response == content



    def test_i2c_tick_sda_read(self):
        """Tick SDA line seems to confuse I2C engine: read"""
        # do something with the bus
        self.mcp.I2C_read(self.i2caddr,1)
        # cycle sda line
        self.mcp.GPIO_write(gp1 = 0)
        self.mcp.GPIO_write(gp1 = 1)

        # do a read  that should fail
        with self.assertRaises(NotAckError):
            self.mcp.I2C_read(self.NO_i2caddr,1)

        #self.mcp.trace_packets = 1
        #self.mcp._i2c_status()
        #self.mcp._i2c_status()
        #self.mcp.trace_packets = 0

    def test_i2c_tick_sda_write(self):
        """Tick SDA line seems to confuse I2C engine: write"""
        # do something with the bus
        self.mcp.I2C_read(self.i2caddr,1)
        # cycle sda line
        self.mcp.GPIO_write(gp1 = 0)
        self.mcp.GPIO_write(gp1 = 1)

        # do something that should fail
        with self.assertRaises(NotAckError):
            self.mcp.I2C_write(self.NO_i2caddr,b'1')


    def test_i2c_low_scl_read(self):
        """Read with SCL down"""
        self.mcp.GPIO_write(gp0 = 0)

        with self.assertRaises(LowSCLError):
            self.assertTrue(self.mcp.I2C_read(self.i2caddr, 1))

    def test_i2c_low_sda_read(self):
        """Read with SDA down"""
        self.mcp.GPIO_write(gp1 = 0)

        with self.assertRaises(LowSDAError):
            self.assertTrue(self.mcp.I2C_read(self.i2caddr, 1))

    def test_i2c_low_scl_write(self):
        """Write with SCL down"""
        self.mcp.GPIO_write(gp0 = 0)

        with self.assertRaises(LowSCLError):
            self.assertTrue(self.mcp.I2C_write(self.i2caddr, b'1'))


    def test_i2c_low_sda_write(self):
        """Write with SDA down"""
        self.mcp.GPIO_write(gp1 = 0)

        with self.assertRaises(LowSDAError):
            self.assertTrue(self.mcp.I2C_write(self.i2caddr, b'1'))


    def test_i2c_low_scl_speed(self):
        """Set speed with SCL down"""
        self.mcp.GPIO_write(gp0 = 0)
        self.mcp.I2C_speed(400000)


    def test_i2c_low_sda_speed(self):
        """Set speed with SDA down"""
        self.mcp.GPIO_write(gp1 = 0)
        self.mcp.I2C_speed(400000)



    def test_i2c_read_1_byte(self):
        """Read 1 byte from a known device"""
        self.mcp.I2C_read(self.i2caddr, 1)


    def test_i2c_read_1_byte_no_device(self):
        """Read 1 byte from a wrong device address."""

        with self.assertRaises(NotAckError):
            self.mcp.I2C_read(self.NO_i2caddr, 1)


    def test_i2c_write_1_byte(self):
        """Write 1 byte from a known device"""
        self.mcp.I2C_write(self.i2caddr, b'1')


    def test_i2c_write_1_byte_no_device(self):
        """Write 1 byte from a wrong device address."""

        with self.assertRaises(NotAckError):
            self.mcp.I2C_write(self.NO_i2caddr, b'1')


    def test_i2c_write_read_1_byte(self):
        """Write 1 byte to and EEPROM and read it back."""
        content = randbytes(1)

        self.mcp.I2C_write(self.i2caddr, b'\x00\x00' + content)
        sleep(0.01)

        self.mcp.I2C_write(self.i2caddr, b'\x00\x00', "nonstop")
        response = self.mcp.I2C_read(self.i2caddr, 1, "restart")

        self.assertEqual(response, content)


    def test_i2c_write_read_chunk(self):
        """Write 58,59,60,61,62 bytes to and EEPROM and read them back."""
        # The eeprom must have at least 64 bytes page (e.g. 24lc128)

        for l in range(55,65):

            content = randbytes(l)

            self.mcp.I2C_write(self.i2caddr, b'\x00\x00' + content)
            sleep(0.01)

            self.mcp.I2C_write(self.i2caddr, b'\x00\x00', "nonstop")
            response = self.mcp.I2C_read(self.i2caddr, l, "restart")

            self.assertEqual(response, content)


    def test_i2c_write_read_chunk_slowest(self):
        """Write multiple bytes to and EEPROM and read them back at slowest speed."""
        # The eeprom must have at least 64 bytes page (e.g. 24lc128)

        self.mcp.I2C_speed(47000)

        for l in range(55,65):

            content = randbytes(l)

            self.mcp.I2C_write(self.i2caddr, b'\x00\x00' + content)
            sleep(0.05)

            self.mcp.I2C_write(self.i2caddr, b'\x00\x00', "nonstop")
            response = self.mcp.I2C_read(self.i2caddr, l, "restart")

            self.assertEqual(response, content)


    def test_i2c_write_read_chunk_fastest(self):
        """Write multiple bytes to and EEPROM and read them back at fastest speed."""
        # The eeprom must have at least 64 bytes page (e.g. 24lc128)

        self.mcp.I2C_speed(500000)

        for l in range(55,65):

            content = randbytes(l)

            self.mcp.I2C_write(self.i2caddr, b'\x00\x00' + content)
            sleep(0.005)

            self.mcp.I2C_write(self.i2caddr, b'\x00\x00', "nonstop")
            response = self.mcp.I2C_read(self.i2caddr, l, "restart")

            self.assertEqual(response, content)


    def test_i2c_write_1_byte_scl_down(self):
        """Try to write while SCL is down."""
        self.mcp.GPIO_write(gp0 = False)

        with self.assertRaises(LowSCLError):
            self.mcp.I2C_write(self.i2caddr, b'1')


    def test_i2c_write_1_byte_sda_down(self):
        """Try to write while SDA is down."""
        self.mcp.GPIO_write(gp1 = False)

        with self.assertRaises(LowSDAError):
            self.mcp.I2C_write(self.i2caddr, b'1')


    def test_i2c_write_2_chunk_scl_down(self):
        """Try to write >1 chunk while SCL is down."""
        self.mcp.GPIO_write(gp0 = False)

        with self.assertRaises(LowSCLError):
            self.mcp.I2C_write(self.i2caddr,  b'A' * 65)


    def test_i2c_write_1_chunk_sda_down(self):
        """Try to write >1 chunk while SDA is down."""
        self.mcp.GPIO_write(gp1 = False)

        with self.assertRaises(LowSDAError):
            self.mcp.I2C_write(self.i2caddr, b'A' * 65)


    def test_i2c_write_1_chunk_no_device(self):
        """Try to write 1 chunk wrong address."""

        with self.assertRaises(NotAckError):
            self.mcp.I2C_write(self.NO_i2caddr, b'A'* 40)


    def test_i2c_write_2_chunks_no_device(self):
        """Try to write 2 chunks wrong address."""

        with self.assertRaises(NotAckError):
            self.mcp.I2C_write(self.NO_i2caddr, b'A' * 65)


    def test_i2c_read_1_chunk_no_device(self):
        """Try to read 1 chunk wrong address."""

        with self.assertRaises(NotAckError):
            self.mcp.I2C_read(self.NO_i2caddr, 40)


    def test_i2c_read_2_chunks_no_device(self):
        """Try to read 2 chunks wrong address."""

        with self.assertRaises(NotAckError):
            self.mcp.I2C_read(self.NO_i2caddr, 65)


    def test_i2c_dirty_recover_write_SCL(self):
        """Recover from dirty condition from SCL low, writing."""

        self.mcp.GPIO_write(gp0 = False)

        with self.assertRaises(LowSCLError):
            self.mcp.I2C_write(self.i2caddr, b'A' * 65)

        self.mcp.GPIO_write(gp0 = True)

        with self.assertRaises(NotAckError):
            self.mcp.I2C_write(self.NO_i2caddr, b'1')


    def test_i2c_dirty_recover_read_SCL(self):
        """Recover from dirty condition from SCL low, reading."""

        self.mcp.GPIO_write(gp0 = False)

        with self.assertRaises(LowSCLError):
            self.mcp.I2C_write(self.i2caddr, b'A' * 65)

        self.mcp.GPIO_write(gp0 = True)

        with self.assertRaises(NotAckError):
            self.mcp.I2C_read(self.NO_i2caddr, 1)


    def test_i2c_dirty_recover_write_SDA(self):
        """Recover from dirty condition from SDA low, writing."""

        self.mcp.GPIO_write(gp1 = False)

        with self.assertRaises(LowSDAError):
            self.mcp.I2C_write(self.i2caddr, b'A' * 65)

        self.mcp.GPIO_write(gp1 = True)

        with self.assertRaises(NotAckError):
            self.mcp.I2C_write(self.NO_i2caddr, b'1')


    def test_i2c_dirty_recover_read_SDA(self):
        """Recover from dirty condition from SDA low, reading."""

        self.mcp.GPIO_write(gp1 = False)

        with self.assertRaises(LowSDAError):
            self.mcp.I2C_write(self.i2caddr, b'A' * 65)

        self.mcp.GPIO_write(gp1 = True)

        with self.assertRaises(NotAckError):
            self.mcp.I2C_read(self.NO_i2caddr, 1)



if __name__ == '__main__':
    unittest.main()
