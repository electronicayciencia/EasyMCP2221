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


    def test_gpio_poll_gp2_3(self):
        """Poll mode, default behavior."""
        self.mcp.set_pin_function(
            gp2 = "GPIO_OUT",
            gp3 = "GPIO_IN")

        self.mcp.GPIO_write(gp2 = 0)

        self.assertEqual(
            self.mcp.GPIO_read()[3],
            False)

        # Setup poll, empty array
        changes = self.mcp.GPIO_poll()
        self.assertEqual(len(changes), 0)

        # Rise GP2
        self.mcp.GPIO_write(gp2 = 1)

        # Must be 2 changes, for GPIO2 and GPIO3
        changes = self.mcp.GPIO_poll()
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0]["id"], "GPIO2_RISE")
        self.assertEqual(changes[1]["id"], "GPIO3_RISE")

        # Fall GP2
        self.mcp.GPIO_write(gp2 = 0)

        # Must be 2 changes, for GPIO2 and GPIO3
        changes = self.mcp.GPIO_poll()
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0]["id"], "GPIO2_FALL")
        self.assertEqual(changes[1]["id"], "GPIO3_FALL")


    def test_gpio_poll_filtered_gp2_3(self):
        """Poll mode, filtered behavior."""
        self.mcp.set_pin_function(
            gp2 = "GPIO_OUT",
            gp3 = "GPIO_IN")

        self.mcp.GPIO_write(gp2 = 0)

        self.assertEqual(
            self.mcp.GPIO_read()[3],
            False)

        # Setup poll and filter, return empty array
        changes = self.mcp.GPIO_poll(["GPIO3_RISE"])
        self.assertEqual(len(changes), 0)

        # Rise GP2
        self.mcp.GPIO_write(gp2 = 1)

        # Must be 2 changes, for GPIO2 and GPIO3. But only GPIO3_RISE must be returned.
        changes = self.mcp.GPIO_poll()
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["id"], "GPIO3_RISE")

        # Fall GP2
        self.mcp.GPIO_write(gp2 = 0)

        # Poll with a new filter, must be 2 changes, for GPIO2 and GPIO3
        changes = self.mcp.GPIO_poll(["GPIO2_FALL", "GPIO3_FALL"])
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0]["id"], "GPIO2_FALL")
        self.assertEqual(changes[1]["id"], "GPIO3_FALL")

        # Rise GP2, nothing must be returned
        self.mcp.GPIO_write(gp2 = 1)
        changes = self.mcp.GPIO_poll()
        self.assertEqual(len(changes), 0)

        # Fall GP2
        self.mcp.GPIO_write(gp2 = 0)

        # Set all changes
        changes = self.mcp.GPIO_poll([])

        # Rise GP2
        self.mcp.GPIO_write(gp2 = 1)

        # Poll with latest filter, must be 2 changes, for GPIO2 and GPIO3
        changes = self.mcp.GPIO_poll()
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[0]["id"], "GPIO2_RISE")
        self.assertEqual(changes[1]["id"], "GPIO3_RISE")


    def test_gpio_sram_preserve_gpio(self):
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


if __name__ == '__main__':
    unittest.main()
