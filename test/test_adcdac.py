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


    def test_adc_volts(self):
        """Test ADC volts for all Vref."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        self.mcp.status["vdd_voltage"] = None

        self.mcp.DAC_config(ref = "1.024V", out = 31)
        expected = 1.024 / 32 * 31
        error = 0.1  # 10% error
        vmin = expected * (1 - error)
        vmax = expected * (1 + error)

        # Vref = OFF
        self.mcp.ADC_config(ref = "OFF")
        v = self.mcp.ADC_read(volts = True)[2]
        self.assertTrue(v == 0)

        # Vref = "1.024V"
        self.mcp.ADC_config(ref = "1.024V")
        v = self.mcp.ADC_read(volts = True)[2]
        self.assertTrue(vmin <= v <= vmax)

        # Vref = "2.048V"
        self.mcp.ADC_config(ref = "2.048V")
        v = self.mcp.ADC_read(volts = True)[2]
        self.assertTrue(vmin <= v <= vmax)

        # Vref = "4.096V"
        self.mcp.ADC_config(ref = "4.096V")
        v = self.mcp.ADC_read(volts = True)[2]
        self.assertTrue(vmin <= v <= vmax)

        # Vref = "VDD", but no vdd indicated
        self.mcp.ADC_config(ref = "VDD")
        with self.assertRaises(ValueError):
            self.mcp.ADC_read(volts = True)

        # Vref = "VDD", vdd = 5
        self.mcp.ADC_config(ref = "VDD", vdd = 5)
        v = self.mcp.ADC_read(volts = True)[2]
        self.assertTrue(vmin <= v <= vmax)

        # norm and volts at the same time
        with self.assertRaises(ValueError):
            self.mcp.ADC_read(volts = True, norm = True)


    def test_adc_dac_volts(self):
        """ADC and DAC in volts. Match DAC return with ADC read value."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        error = 0.05  # Max 5% error tolerated

        # Vref = "1.024V"
        self.mcp.ADC_config(ref = "1.024V")
        self.mcp.DAC_config(ref = "1.024V")
        expected = self.mcp.DAC_write(out = 0.5, volts = True)
        read = self.mcp.ADC_read(volts = True)[2]
        self.assertLess(abs(expected - read)/expected, error)

        # Vref = "2.048V"
        self.mcp.ADC_config(ref = "2.048V")
        self.mcp.DAC_config(ref = "2.048V")
        expected = self.mcp.DAC_write(out = 1.5, volts = True)
        read = self.mcp.ADC_read(volts = True)[2]
        self.assertLess(abs(expected - read)/expected, error)

        # Vref = "4.096V"
        self.mcp.ADC_config(ref = "4.096V")
        self.mcp.DAC_config(ref = "4.096V")
        expected = self.mcp.DAC_write(out = 3, volts = True)
        read = self.mcp.ADC_read(volts = True)[2]
        self.assertLess(abs(expected - read)/expected, error)

        # Vref = "2.048V"
        self.mcp.ADC_config(ref = "VDD")
        self.mcp.DAC_config(ref = "VDD", vdd = 5)
        expected = self.mcp.DAC_write(out = 3.33, volts = True)
        read = self.mcp.ADC_read(volts = True)[2]
        self.assertLess(abs(expected - read)/expected, error)

        # norm and volts at the same time
        with self.assertRaises(ValueError):
            self.mcp.DAC_write(1, volts = True, norm = True)


    def test_adc_dac_vrm_crash(self):
        """ADC/DAC VDD to 1.024V crash workaround"""
        self.mcp.set_pin_function(
            gp2 = "DAC",
            gp3 = "ADC")

        self.mcp.DAC_config(ref="VDD", out=27) # any value above 26
        
        # Switching from VDD to 1.024V when out > 26 will trigger OSError exception.
        # The workaround must prevent that.
        self.mcp.DAC_config(ref="1.024V", out=27)



if __name__ == '__main__':
    unittest.main()
