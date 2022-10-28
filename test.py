# GP0 <-1k-> SCL
# GP1 <-1k-> SDA
# GP2 <-1k-> GP3
# SCL, SDA -> EEPROM (0x50)


import unittest
import json
from random import randbytes
from time import sleep

import EasyMCP2221
from EasyMCP2221.exceptions import *


class GPIO(unittest.TestCase):

    def setUp(self):
        self.mcp = EasyMCP2221.Device()
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")



    def tearDown(self):
        """ Safe status """
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")


    def test_device_presence(self):
        """Test device presence and __repr__."""
        data = json.loads(str(self.mcp))
        self.assertEqual(
            data["USB Product"],
            "MCP2221 USB-I2C/UART Combo")


    def test_all_off_with_pinfunction(self):
        """All outputs, all 0, using set_pin_function."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT",
            gp1 = "GPIO_OUT",
            gp2 = "GPIO_OUT",
            gp3 = "GPIO_OUT",
            out0 = 0,
            out1 = 0,
            out2 = 0,
            out3 = 0)

        self.assertEqual(
            self.mcp.GPIO_read(),
            (0,0,0,0))


    def test_all_on_with_pinfunction(self):
        """All outputs, all 1, using set_pin_function."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT",
            gp1 = "GPIO_OUT",
            gp2 = "GPIO_OUT",
            gp3 = "GPIO_OUT",
            out0 = 1,
            out1 = 1,
            out2 = 1,
            out3 = 1)

        self.assertEqual(
            self.mcp.GPIO_read(),
            (1,1,1,1))


    def test_all_off_with_pinfunction(self):
        """All outputs, all 0, using GPIO_write."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT",
            gp1 = "GPIO_OUT",
            gp2 = "GPIO_OUT",
            gp3 = "GPIO_OUT")

        self.mcp.GPIO_write(0,0,0,0)

        self.assertEqual(
            self.mcp.GPIO_read(),
            (0,0,0,0))


    def test_all_on_with_pinfunction(self):
        """All outputs, all 1, using GPIO_write."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT",
            gp1 = "GPIO_OUT",
            gp2 = "GPIO_OUT",
            gp3 = "GPIO_OUT")

        self.mcp.GPIO_write(1,1,1,1)

        self.assertEqual(
            self.mcp.GPIO_read(),
            (1,1,1,1))


    def test_pin_input_not_gpio(self):
        """Pin GP0 not assigned to GPIO. Try to read."""
        self.mcp.set_pin_function(
            gp0 = "LED_URX",
            gp1 = "GPIO_OUT", out1 = 0,
            gp2 = "GPIO_OUT", out2 = 0,
            gp3 = "GPIO_OUT", out3 = 0)

        self.assertEqual(
            self.mcp.GPIO_read(),
            (None,0,0,0))


    def test_pin_output_not_gpio(self):
        """Pin GP0 not assigned to GPIO. Try to write."""
        self.mcp.set_pin_function(gp0 = "LED_URX")

        with self.assertRaises(RuntimeError):
            self.mcp.GPIO_write(gp0 = 1)



    def test_gpio_read_gp2_3_on(self):
        """GP2 output, GP3 input, write and read."""
        self.mcp.set_pin_function(
            gp2 = "GPIO_OUT",
            gp3 = "GPIO_IN")

        self.mcp.GPIO_write(gp2 = 0)

        self.assertEqual(
            self.mcp.GPIO_read()[3],
            False)

        self.mcp.GPIO_write(gp2 = 1)

        self.assertEqual(
            self.mcp.GPIO_read()[3],
            True)

    def test_gpio_read_gp2_3_on(self):
        """SRAM_config must preserve GPIO_write values."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "GPIO_OUT", out2 = 1,
            gp3 = "GPIO_IN")

        gp3_in = self.mcp.GPIO_read()[3]
        self.assertTrue(self.mcp.GPIO_read()[3])

        self.mcp.GPIO_write(gp2 = False)
        self.assertFalse(self.mcp.GPIO_read()[3])

        # This shall not change gp2 output value
        self.mcp.set_pin_function(gp0 = "GPIO_IN")
        self.assertFalse(self.mcp.GPIO_read()[3])


class ADC_DAC(unittest.TestCase):

    def setUp(self):
        self.mcp = EasyMCP2221.Device()
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")


    def tearDown(self):
        """ Safe status """
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")


    def test_set_adc_pins(self):
        """GP1, GP2 and GP3 have ADC. But not GP0."""
        self.mcp.set_pin_function(
            gp1 = "ADC",
            gp2 = "ADC",
            gp3 = "ADC")

        with self.assertRaises(ValueError):
            self.mcp.set_pin_function(gp0 = "ADC")


    def test_read_max_adc(self):
        """Set GP1, GP2 and GP3 digital output to true. Read ADC."""
        self.mcp.set_pin_function(
            gp1 = "GPIO_OUT", out1 = 1,
            gp2 = "GPIO_OUT", out2 = 1,
            gp3 = "GPIO_OUT", out3 = 1)

        adc = self.mcp.ADC_read()

        self.assertTrue(adc[0] > 1020)
        self.assertTrue(adc[1] > 1020)
        self.assertTrue(adc[2] > 1020)



    def test_set_dac_pins(self):
        """GP2 and GP3 have DAC, but not GP0 or GP1"""
        self.mcp.set_pin_function(
            gp2 = "DAC",
            gp3 = "DAC")

        with self.assertRaises(ValueError):
            self.mcp.set_pin_function(gp0 = "DAC")

        with self.assertRaises(ValueError):
            self.mcp.set_pin_function(gp1 = "DAC")



    def test_adc_dac_vdd(self):
        """Cross-check DAC with ADC both in Vdd."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        self.mcp.ADC_config(ref = "VDD")
        self.mcp.DAC_config(ref = "VDD")
        self.mcp.DAC_write(31)
        adc = self.mcp.ADC_read()[1]
        self.assertTrue(adc > 950)


    def test_adc_vdd_dac_vrm(self):
        """DAC ref is VRM and ADC ref is Vdd."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        self.mcp.ADC_config(ref = "VDD")
        self.mcp.DAC_config(ref = "4.096V")
        self.mcp.DAC_write(31)
        sleep(0.01) # time to settle-up
        adc = self.mcp.ADC_read()[1]
        self.assertTrue(800 < adc < 1000)


    def test_adc_vrm_dac_vdd(self):
        """DAC ref is VDD and ADC ref is VRM."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        self.mcp.ADC_config(ref = "2.048V")
        self.mcp.DAC_config(ref = "VDD")
        self.mcp.DAC_write(13)
        sleep(0.05) # time to settle-up
        adc = self.mcp.ADC_read()[1]
        self.assertTrue(990 < adc < 1023)


    def test_adc_vrm_dac_vrm(self):
        """DAC ref is VRM and ADC ref is VRM."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        self.mcp.ADC_config(ref = "2.048V")
        self.mcp.DAC_config(ref = "2.048V")
        self.mcp.DAC_write(15)
        sleep(0.01) # time to settle-up
        adc = self.mcp.ADC_read()[1]
        self.assertTrue(400 < adc < 600)


    def test_adc_vrm_dac_vrm_gpio(self):
        """DAC ref is VRM and ADC ref is VRM and GPIO reconfig."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        self.mcp.ADC_config(ref = "2.048V")
        self.mcp.DAC_config(ref = "2.048V")
        self.mcp.DAC_write(15)
        self.mcp.set_pin_function(gp0 = "LED_URX")
        sleep(0.01) # time to settle-up
        adc = self.mcp.ADC_read()[1]
        self.assertTrue(400 < adc < 600)


    def test_adc_vdd_dac_vrm_gpio(self):
        """DAC ref is VRM and ADC ref is VDD and GPIO reconfig."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        self.mcp.ADC_config(ref = "VDD")
        self.mcp.DAC_config(ref = "2.048V")
        self.mcp.DAC_write(31)
        self.mcp.set_pin_function(gp0 = "LED_URX")
        sleep(0.01) # time to settle-up
        adc = self.mcp.ADC_read()[1]
        self.assertTrue(350 < adc < 450)


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




class Persistence(unittest.TestCase):

    def setUp(self):
        self.mcp = EasyMCP2221.Device()
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")


    def tearDown(self):
        """ Safe status """
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")


    def test_power_management(self):
        """ Change power management setting. """
        self.mcp.enable_power_management(True)

        data = json.loads(str(self.mcp))
        self.assertEqual(
            data["Chip settings"]["Power management options"],
            "enabled")

        self.mcp.enable_power_management(False)

        data = json.loads(str(self.mcp))
        self.assertEqual(
            data["Chip settings"]["Power management options"],
            "disabled")


    def test_edge_detection(self):
        """ Change and persist IOC edge detection."""
        for e in ("none", "raising", "falling", "both"):
            self.mcp.wake_up_config(edge=e)
            self.mcp.save_config()
            data = json.loads(str(self.mcp))
            self.assertEqual(
                data["Chip settings"]["Interrupt detection edge"],
                e)


    def test_set_pin_function_io(self):
        """ Persist I/O setted via set_pin_function method."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT", out0 = True,
            gp1 = "GPIO_OUT", out1 = True,
            gp2 = "GPIO_OUT", out2 = False,
            gp3 = "GPIO_IN")
        self.mcp.save_config()
        self.mcp.reset()
        self.assertEqual(
            self.mcp.GPIO_read(),
            (1,1,0,0))


    def test_set_pin_function_func(self):
        """ Persist I/O setted via set_pin_function method."""
        self.mcp.set_pin_function(
            gp0 = "LED_URX",
            gp1 = "LED_UTX",
            gp2 = "USBCFG",
            gp3 = "LED_I2C")
        self.mcp.save_config()
        self.mcp.reset()
        self.assertEqual(
            self.mcp.GPIO_read(),
            (None,None,None,None))


    def test_adc_dac_vdd(self):
        """ Persist ADC/DAC using in Vdd."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "ADC",
            gp3 = "DAC")
        self.mcp.ADC_config("VDD")
        self.mcp.DAC_config("VDD")

        self.mcp.DAC_write(16)

        self.mcp.save_config()
        self.mcp.reset()
        
        adc1 = self.mcp.ADC_read()[1]
        
        # should be around 512
        self.assertTrue(450 < adc1 < 550)


    def test_adc_vrm_dac_vdd(self):
        """ Persist ADC Vref=Vrm and DAC Vref=Vdd."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "ADC",
            gp3 = "DAC")
        self.mcp.ADC_config("2.048V")
        self.mcp.DAC_config("VDD")

        self.mcp.DAC_write(10)

        self.mcp.save_config()
        self.mcp.reset()
        
        adc1 = self.mcp.ADC_read()[1]
        
        # should be around 781
        # (10/32*5)/2,048*1024
        #print(adc1)
        self.assertTrue(750 < adc1 < 800)


    def test_adc_vdd_dac_vrm(self):
        """ Persist ADC Vref=Vdd and DAC Vref=Vrm."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_IN",
            gp1 = "GPIO_IN",
            gp2 = "ADC",
            gp3 = "DAC")
        self.mcp.ADC_config("VDD")
        self.mcp.DAC_config("4.096V")

        self.mcp.DAC_write(31)

        self.mcp.save_config()
        self.mcp.reset()
        
        adc1 = self.mcp.ADC_read()[1]
        print(adc1)
        import pdb
        pdb.set_trace()
        # should be around 812
        # (31/32*4.096)/5*1024
        #print(adc1)
        self.assertTrue(800 < adc1 < 850)



#    def test_user(self):
#        import pdb;
#        pdb.set_trace()

# write non-stop, write normal


# test saveconfig,
# saveconfig and recover Vrm just after reset
# gpio_write se mantiene cuando set pin funcion no cambia ese pin


if __name__ == '__main__':
    unittest.main()




#encuentra device
#no encuentra device
#saveconfig + reset
#saveconfig + gpio_write
