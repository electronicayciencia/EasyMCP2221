import unittest
import json
from random import randbytes
from time import sleep

import EasyMCP2221
from EasyMCP2221.exceptions import *


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
        self.mcp.save_config()

        data = json.loads(str(self.mcp))
        self.assertEqual(
            data["Chip settings"]["Power management options"],
            "enabled")

        self.mcp.enable_power_management(False)
        self.mcp.save_config()

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
        """ Persist I/O set via set_pin_function method."""
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
        """ Persist I/O function via set_pin_function method."""
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


    def test_persist_gpio_write(self):
        """ Persist I/O set via GPIO_write method."""
        self.mcp.set_pin_function(
            gp0 = "GPIO_OUT", out0 = True,
            gp1 = "GPIO_OUT", out1 = True,
            gp2 = "GPIO_OUT", out2 = True,
            gp3 = "GPIO_IN")

        self.mcp.GPIO_write(gp2 = False)

        self.mcp.save_config()
        self.mcp.reset()
        self.assertEqual(
            self.mcp.GPIO_read(),
            (1,1,0,0))


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

        # should be around 812
        # (31/32*4.096)/5*1024
        self.assertTrue(800 < adc1 < 850)


    def test_adc_dac_all_presistence(self):
        """Test all possible Vref combinations for DAC and ADC after a reset."""
        self.mcp.set_pin_function(
            gp2 = "ADC",
            gp3 = "DAC")

        Vdd = 5
        Vrm = {
        #    "OFF"   : 0,
            "1.024V": 1.024,
            "2.048V": 2.048,
            "4.096V": 4.096,
            "VDD"   : Vdd
        }
        margin = 30
        dac = 15

        for adc_ref in Vrm.keys():
            for dac_ref in Vrm.keys():

                self.mcp.ADC_config(adc_ref)
                self.mcp.DAC_config(dac_ref)
                self.mcp.DAC_write(dac)

                self.mcp.save_config()
                self.mcp.reset()

                adc = self.mcp.ADC_read()[1]

                expected = (Vrm[dac_ref] * dac / 32) * 1024 / Vrm[adc_ref]
                expected = round(expected)

                if expected > 1023:
                    expected = 1023

                self.assertTrue((expected - margin) < adc < (expected + margin),
                    msg = "ADC_ref: %s, DAC_ref: %s, Expected: %d, Got: %d" % (adc_ref, dac_ref, expected, adc))



#    def test_user(self):
#        import pdb;
#        pdb.set_trace()


if __name__ == '__main__':
    unittest.main()
