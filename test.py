# GP0 <-1k-> SCL
# GP1 <-1k-> SDA
# GP2 <-1k-> GP3
# SCL, SDA -> EEPROM (0x50)


import unittest
import json
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


#    Floating input in GP0 gives unexpected result.
#    def test_all_inputs(self):
#        """All inputs, no voltage source."""
#        self.mcp.set_pin_function(
#            gp0 = "GPIO_IN",
#            gp1 = "GPIO_IN",
#            gp2 = "GPIO_IN",
#            gp3 = "GPIO_IN")
#
#        self.assertEqual(
#            self.mcp.GPIO_read(),
#            (0,0,0,0))


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
        sleep(0.01) # time to settle-up
        adc = self.mcp.ADC_read()[1]
        self.assertTrue(990 < adc < 1010)


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
        
        self.mcp = EasyMCP2221.Device()
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT", out0 = 1, # pull-up SCL
            gp1 = "GPIO_OUT", out1 = 1, # pull-up SCL
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")

    def tearDown(self):
        """Safe status """
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT", out0 = 1, # pull-up SCL
            gp1 = "GPIO_OUT", out1 = 1, # pull-up SCL
            gp2 = "GPIO_IN",
            gp3 = "GPIO_IN")


    def test_i2c_idle(self):
        self.assertTrue(self.mcp.I2C_is_idle())


    def test_i2c_low_scl(self):
        """SCL down"""
        self.mcp.GPIO_write(gp0 = 0)
        
        with self.assertRaises(LowSCLError):
            self.assertTrue(self.mcp.I2C_is_idle())


    def test_i2c_low_sda(self):
        """SDA down"""
        self.mcp.GPIO_write(gp1 = 0)
        
        with self.assertRaises(LowSDAError):
            self.assertTrue(self.mcp.I2C_is_idle())


    def test_i2c_read_1_bit(self):
        """Read 1 bit from a known device"""
        self.mcp.I2C_read(self.i2caddr, 1)


    def test_i2c_read_1_bit_no_device(self):
        """Read 1 bit from a wrong device address."""
        
        with self.assertRaises(NotAckError):
            self.mcp.I2C_read(self.i2caddr + 1, 1)


    def test_i2c_write_1_bit(self):
        """Write 1 bit from a known device"""
        self.mcp.I2C_write(self.i2caddr, b'1')


    def test_i2c_write_1_bit_no_device(self):
        """Write 1 bit from a wrong device address."""
        
        with self.assertRaises(NotAckError):
            self.mcp.I2C_write(self.i2caddr + 1, b'1')




#    def test_user(self):
#        import pdb;
#        pdb.set_trace()


# test saveconfig, saveconfig tras gpio_write
# test ioc energy
#i2c low scl
#i2c low sda
#i2c timeout


if __name__ == '__main__':
    unittest.main()


