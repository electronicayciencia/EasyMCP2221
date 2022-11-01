import unittest
import json
from random import randbytes
from time import sleep

import EasyMCP2221
from EasyMCP2221.exceptions import *


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


    def test_adc_dac_all(self):
        """Test all possible Vref combinations for DAC and ADC."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        Vdd = 5
        Vrm = {
            #"OFF"   : 0,
            "1.024V": 1.024,
            "2.048V": 2.048,
            "4.096V": 4.096,
            "VDD"   : Vdd
        }
        max_error = 0.05 # relative error
        dac = 10

        for adc_ref in Vrm.keys():
            for dac_ref in Vrm.keys():

                with self.subTest(ADC_Vref = adc_ref, DAC_Vref = dac_ref):
                    self.mcp.ADC_config(adc_ref)
                    self.mcp.DAC_config(dac_ref)
                    self.mcp.DAC_write(dac)

                    sleep(0.01) # time to settle-up

                    adc = self.mcp.ADC_read()[1]

                    expected = (Vrm[dac_ref] * dac / 32) * 1024 / Vrm[adc_ref]
                    expected = round(expected)

                    if expected > 1023:
                        expected = 1023

                    error = (adc-expected)/expected

                    self.assertLess(abs(error), max_error,
                        msg = "ADC_ref: %s, DAC_ref: %s, Expected: %d, Got: %d (%+.2f)%%" % 
                            (adc_ref, dac_ref, expected, adc, error*100))


if __name__ == '__main__':
    unittest.main()
