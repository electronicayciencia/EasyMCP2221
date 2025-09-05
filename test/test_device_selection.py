import unittest

import EasyMCP2221
from EasyMCP2221.exceptions import *
from EasyMCP2221 import SMBus
from time import sleep


SERIAL_OK="0002596888"
SERIAL_WRONG="9999999999"
DEV_DEFAULT_VID = 0x04D8
DEV_DEFAULT_PID = 0x00DD

class DevSelect(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

#----- single selection ---------------

    def test_select_by_default(self):
        """Select the default device"""
        mcp = EasyMCP2221.Device()

        serial = mcp.read_flash_info()['USB_SERIAL']
        self.assertEqual(serial, SERIAL_OK)

    def test_select_by_index_0(self):
        """Select the first device found"""
        mcp = EasyMCP2221.Device(devnum=0)

        serial = mcp.read_flash_info()['USB_SERIAL']
        self.assertEqual(serial, SERIAL_OK)

    def test_VID_PID_index_pos(self):
        """Forcing the default parameters, positional"""
        mcp = EasyMCP2221.Device(DEV_DEFAULT_VID, DEV_DEFAULT_PID, 0)

        serial = mcp.read_flash_info()['USB_SERIAL']
        self.assertEqual(serial, SERIAL_OK)

    def test_VID_PID_index_named(self):
        """Forcing the default parameters, named"""
        mcp = EasyMCP2221.Device(VID=DEV_DEFAULT_VID, PID=DEV_DEFAULT_PID, devnum=0)

        serial = mcp.read_flash_info()['USB_SERIAL']
        self.assertEqual(serial, SERIAL_OK)

    def test_wrong_VID(self):
        """Select wrong VID"""
        with self.assertRaises(RuntimeError):
            mcp = EasyMCP2221.Device(VID=DEV_DEFAULT_VID+1)

    def test_wrong_PID(self):
        """Select wrong PID"""
        with self.assertRaises(RuntimeError):
            mcp = EasyMCP2221.Device(PID=DEV_DEFAULT_PID+1)

    def test_select_by_serial(self):
        """Select a device by its serial number"""
        mcp = EasyMCP2221.Device(usbserial=SERIAL_OK)

        serial = mcp.read_flash_info()['USB_SERIAL']
        self.assertEqual(serial, SERIAL_OK)

    def test_select_by_wrong_serial(self):
        """Select a wrong serial number"""
        with self.assertRaises(RuntimeError):
            mcp = EasyMCP2221.Device(usbserial=SERIAL_WRONG)

    def test_select_by_serial_and_index(self):
        """Select with serial and index, serial must take precedence"""
        mcp = EasyMCP2221.Device(devnum=1,usbserial=SERIAL_OK)

        serial = mcp.read_flash_info()['USB_SERIAL']
        self.assertEqual(serial, SERIAL_OK)

    def test_select_by_wrong_index(self):
        """Select with a wrong index"""
        with self.assertRaises(RuntimeError):
            mcp = EasyMCP2221.Device(devnum=10)

#----- double selections ---------------

    def test_double_select_by_default(self):
        """Double select the default device"""
        mcp1 = EasyMCP2221.Device()
        mcp2 = EasyMCP2221.Device()

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_default_pos(self):
        """Double select the default device. Explicit positional parameters."""
        mcp1 = EasyMCP2221.Device(DEV_DEFAULT_VID, DEV_DEFAULT_PID, 0)
        mcp2 = EasyMCP2221.Device(DEV_DEFAULT_VID, DEV_DEFAULT_PID, 0)

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_default_named(self):
        """Double select the default device. Explicit named parameters."""
        mcp1 = EasyMCP2221.Device(VID=DEV_DEFAULT_VID, PID=DEV_DEFAULT_PID, devnum=0)
        mcp2 = EasyMCP2221.Device(VID=DEV_DEFAULT_VID, PID=DEV_DEFAULT_PID, devnum=0)

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_default_and_pos(self):
        """Double select the default device. Default implicit and explicit positional parameters."""
        mcp1 = EasyMCP2221.Device()
        mcp2 = EasyMCP2221.Device(DEV_DEFAULT_VID, DEV_DEFAULT_PID, 0)

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_default_and_named(self):
        """Double select the default device. Default implicit and explicit named parameters."""
        mcp1 = EasyMCP2221.Device()
        mcp2 = EasyMCP2221.Device(VID=DEV_DEFAULT_VID, PID=DEV_DEFAULT_PID, devnum=0)

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_serial(self):
        """Double select the device by serial."""
        mcp1 = EasyMCP2221.Device(usbserial=SERIAL_OK)
        mcp2 = EasyMCP2221.Device(usbserial=SERIAL_OK)

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_serial_devnum(self):
        """Double select the device, both by serial and devnum."""
        mcp1 = EasyMCP2221.Device(devnum=0)
        mcp2 = EasyMCP2221.Device(usbserial=SERIAL_OK)

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_serial_devnum2(self):
        """Double select the device, both by serial and devnum, reverse order."""
        mcp1 = EasyMCP2221.Device(usbserial=SERIAL_OK)
        mcp2 = EasyMCP2221.Device(devnum=0)

        self.assertTrue(mcp1 is mcp2)

#----- double selections SMBus default ---------------

    def test_double_select_smbus_default(self):
        """Double select the device via SMBus. Default parameters."""
        bus1 = SMBus()
        bus2 = SMBus()

        mcp1 = bus1.mcp
        mcp2 = bus2.mcp

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_smbus_default_forced(self):
        """Double select the device via SMBus. Forced default parameters."""
        bus1 = SMBus(1)
        bus2 = SMBus(1)

        mcp1 = bus1.mcp
        mcp2 = bus2.mcp

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_smbus_default_implicit_forced(self):
        """Double select the device via SMBus. Implicit and forced default parameters."""
        bus1 = SMBus()
        bus2 = SMBus(1)

        mcp1 = bus1.mcp
        mcp2 = bus2.mcp

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_smbus_main(self):
        """Double select the device. Once via SMBus. The other with main library."""
        bus = SMBus()
        mcp2 = EasyMCP2221.Device()

        mcp1 = bus.mcp

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_smbus_main_serial(self):
        """Double select the device. Once via SMBus. The other with main library. Usign serial."""
        bus = SMBus(usbserial = SERIAL_OK)
        mcp2 = EasyMCP2221.Device(usbserial = SERIAL_OK)

        mcp1 = bus.mcp

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_smbus_main_serial_idx(self):
        """Double select the device. Once via SMBus by index. The other with main library by serial."""
        bus = SMBus(1)
        mcp2 = EasyMCP2221.Device(usbserial = SERIAL_OK)

        mcp1 = bus.mcp

        self.assertTrue(mcp1 is mcp2)

    def test_double_select_smbus_main_serial_idx_2(self):
        """Double select the device. Once via SMBus by index. The other with main library by serial. Reverse."""
        mcp2 = EasyMCP2221.Device(usbserial = SERIAL_OK)
        bus = SMBus(1)

        mcp1 = bus.mcp

        self.assertTrue(mcp1 is mcp2)


#----- selection corner cases ---------------

    def test_select_serial_scan_enum(self):
        """Select by serial, serial enumeration disabled/enabled, scan devices disabled/enabled."""
        debug_messages = False

        # Disable serial enumeration in the device
        mcp = EasyMCP2221.Device()
        mcp.enable_cdc_serial(False)
        mcp.save_config()
        mcp.reset()
        # Clear the catalog
        EasyMCP2221.Device._catalog = {}
        sleep(1)

        # Try to find it in the USB list
        with self.assertRaises(RuntimeError):
            mcp = EasyMCP2221.Device(usbserial=SERIAL_OK, debug_messages = debug_messages)

        # Try to find it scanning all
        mcp1 = EasyMCP2221.Device(usbserial=SERIAL_OK, scan_serial = True, debug_messages = debug_messages)

        serial = mcp1.read_flash_info()['USB_SERIAL']
        self.assertEqual(serial, SERIAL_OK)

        # Try to find it again, no scan, must be found in the catalog
        mcp2 = EasyMCP2221.Device(usbserial = SERIAL_OK, scan_serial = False, debug_messages = debug_messages)

        self.assertTrue(mcp1 is mcp2)


        # Enable serial enumeration in the device
        mcp = EasyMCP2221.Device()
        mcp.enable_cdc_serial(True)
        mcp.save_config()
        mcp.reset()
        # Clear the catalog
        EasyMCP2221.Device._catalog = {}
        sleep(1)

        # Try to find it by USB enumeration
        mcp1 = EasyMCP2221.Device(usbserial=SERIAL_OK, debug_messages = debug_messages)

        serial = mcp1.read_flash_info()['USB_SERIAL']
        self.assertEqual(serial, SERIAL_OK)



if __name__ == '__main__':
    unittest.main()
