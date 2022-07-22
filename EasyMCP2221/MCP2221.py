# API library for MCP2221(A).
# Electronicayciencia. 10/07/2022
# Original work: Yuta KItagami (https://github.com/nonNoise/PyMCP2221A)

import hid
import time

from .Constants import *
from . import I2C_Slave


class Device:
    """ MCP2221(A) device

    Parameters:
        VID (int, optional): Vendor Id (default to ``0x04D8``)
        PID (int, optional): Product Id (default to ``0x00DD``)
        devnum (int, optional): Device index if multiple device found with the same PID and VID.

    Raises:
        RuntimeError: if no device found with given VID and PID.

    Example:
        >>> import EasyMCP2221
        >>> mcp = EasyMCP2221.Device()
        >>> print(mcp)
        {
            "Chip settings": {
                "Power management options": "enabled",
                "USB PID": "0x00DD",
                "USB VID": "0x04D8",
                "USB requested number of mA": 100
            },
            "Factory Serial": "01234567",
            "GP settings": {},
            "USB Manufacturer": "Microchip Technology Inc.",
            "USB Product": "MCP2221 USB-I2C/UART Combo",
            "USB Serial": "0000000000"
        }
    """


    debug_packets = False
    """bool: Print all binary commands and responses."""


    def __init__(self, VID = DEV_DEFAULT_VID, PID = DEV_DEFAULT_PID, devnum=0):
        self.hidhandler = hid.device()
        devices = hid.enumerate(VID, PID)
        if not devices or len(devices) < devnum:
            raise RuntimeError("No device found with VID %04X and PID %04X." % (VID, PID))

        self.hidhandler.open_path(hid.enumerate(VID, PID)[devnum]["path"])


    def __repr__(self):
        import json
        data = self._read_flash_info(raw = False)
        return json.dumps(data, indent=4, sort_keys=True)


    def __del__(self):
        """ Releases the device. """
        self.hidhandler.close()
        del self.hidhandler


    def send_cmd(self, buf, sleep = 0):
        """ Write a raw USB command to device and get the response.

        Write 64 bytes to the HID interface, starting by ``buf`` bytes.
        Optionally wait ``sleep`` seconds.
        Then read 64 bytes from HID and return them as a list.

        Parameters:
            buf (list of bytes): Full data to write, including command (64 bytes max).

        Other parameters:
            sleep (float, optional): Delay (seconds) between writing the command and reading the response.

        Returns:
            list of bytes: Full response data (64 bytes).

        Example:
            >>> from EasyMCP2221.Constants import *
            >>> r = mcp.send_cmd([CMD_GET_GPIO_VALUES])
            [81, 0, 238, 239, 238, 239, 238, 239, 238, 239, 0, 0, 0, ... 0, 0]
        """
        if self.debug_packets:
            print(buf)

        REPORT_NUM = 0x00
        padding = [0x00] * (PACKET_SIZE - len(buf))
        self.hidhandler.write([REPORT_NUM] + buf + padding)

        time.sleep(sleep)

        if buf[0] == CMD_RESET_CHIP:
            return None

        r = self.hidhandler.read(PACKET_SIZE)

        if self.debug_packets:
            print(r)

        return r


    #######################################################################
    # Flash
    #######################################################################
    def _read_flash_raw(self, setting):
        """
        Read flash data and return a list of bytes.
        """
        rbuf = self.send_cmd([CMD_READ_FLASH_DATA, setting])

        if rbuf[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
            raise RuntimeError("Read flash data command failed.")

        return rbuf[0:64]

    def _write_flash_raw(self, setting, data):
        """
        Write flash data.
        Data payload does not include command and register bytes.
        """
        if setting == FLASH_DATA_CHIP_SETTINGS and (data[0] & 0b11) != 0:
            raise AssertionError("Chip protection prevented!")

        rbuf = self.send_cmd([CMD_WRITE_FLASH_DATA, setting] + data)

        if rbuf[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
            raise RuntimeError("Write flash data command failed.")

        return rbuf[0:64]

    def _read_flash_info(self, raw = False):
        """ Read flash data.

        Return USB enumeration strings, power-up GPIO settings and internal chip configuration.

        Parameters:
            raw (bool, optional):
                If ``False``, return only parsed data (this is the default).
                If ``True``, return all data unparsed.

        Return:
            dict: Flash data (parsed or raw)

        Hint:
            This is the function used to stringfy the object.
        """
        CHIP_SETTINGS_STR   = "Chip settings"
        GP_SETTINGS_STR     = "GP settings"
        USB_VENDOR_STR      = "USB Manufacturer"
        USB_PRODUCT_STR     = "USB Product"
        USB_SERIAL_STR      = "USB Serial"
        USB_FACT_SERIAL_STR = "Factory Serial"

        data = {
            CHIP_SETTINGS_STR:    self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_CHIP_SETTINGS]),
            GP_SETTINGS_STR:      self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_GP_SETTINGS]),
            USB_VENDOR_STR:       self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_USB_MANUFACTURER]),
            USB_PRODUCT_STR:      self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_USB_PRODUCT]),
            USB_SERIAL_STR:       self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_USB_SERIALNUM]),
            USB_FACT_SERIAL_STR:  self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_CHIP_SERIALNUM]),
        }

        if raw:
            return data

        data[USB_VENDOR_STR]      = self._parse_wchar_structure(data[USB_VENDOR_STR])
        data[USB_PRODUCT_STR]     = self._parse_wchar_structure(data[USB_PRODUCT_STR])
        data[USB_SERIAL_STR]      = self._parse_wchar_structure(data[USB_SERIAL_STR])
        data[USB_FACT_SERIAL_STR] = self._parse_factory_serial(data[USB_FACT_SERIAL_STR])
        data[CHIP_SETTINGS_STR]   = self._parse_chip_settings_struct(data[CHIP_SETTINGS_STR])
        data[GP_SETTINGS_STR]     = self._parse_gp_settings_struct(data[GP_SETTINGS_STR])

        return data

    def _parse_wchar_structure(self, buf):
        cmd_echo  = buf[RESPONSE_ECHO_BYTE]
        cmd_error = buf[RESPONSE_STATUS_BYTE]
        strlen    = buf[2] - 2
        three     = buf[3]
        w_str     = buf[4:4+strlen]
        str = bytes(w_str).decode('utf-16')
        return str

    def _parse_factory_serial(self, buf):
        cmd_echo  = buf[RESPONSE_ECHO_BYTE]
        cmd_error = buf[RESPONSE_STATUS_BYTE]
        strlen    = buf[2]
        three     = buf[3]
        str       = buf[4:4+strlen]
        str = bytes(str).decode('ascii')
        return str

    def _parse_chip_settings_struct(self, buf):
        data = {
            "USB VID": "0x{:02X}{:02X}".format(buf[9], buf[8]),
            "USB PID": "0x{:02X}{:02X}".format(buf[11], buf[10]) ,
            "USB requested number of mA": buf[13] * 2,
            "Power management options":
                "enabled" if buf[12] & 0b00100000 else "disabled",
        }
        return data

    def _parse_gp_settings_struct(self, buf):
        data = { }
        return data


    #######################################################################
    # SRAM
    #######################################################################
    def SRAM_config(self,
        clk_output = None,
        dac_ref    = None,
        dac_value  = None,
        adc_ref    = None,
        int_conf   = None,
        gp0        = None,
        gp1        = None,
        gp2        = None,
        gp3        = None):
        """ Low level SRAM configuration.

        Configure Runtime GPIO pins and parameters.
        All arguments are optional.
        Apply given settings, preserve the rest.

        Parameters:
            clk_output (int, optional): settings
            dac_ref    (int, optional): settings
            dac_value  (int, optional): settings
            adc_ref    (int, optional): settings
            int_conf   (int, optional): settings
            gp0        (int, optional): settings
            gp1        (int, optional): settings
            gp2        (int, optional): settings
            gp3        (int, optional): settings

        Raises:
            RuntimeError: if command failed.

        Examples:
            >>> from EasyMCP2221.Constants import *
            >>> mcp.SRAM_config(gp1 = GPIO_FUNC_GPIO | GPIO_DIR_IN)

            >>> mcp.SRAM_config(dac_ref = ADC_REF_VRM | ADC_VRM_2048)

        Note:
            Calling this function unexpectedly resets (not preserve):

            - All GPIO values set via :func:`GPIO_write` method.
            - Reference voltage for ADC set by :func:`ADC_config` (not affected if ref = VDD)
            - Reference voltage for DAC set by :func:`DAC_config` (not affected if ref = VDD)
        """
        if clk_output is not None: clk_output |= ALTER_CLK_OUTPUT
        if dac_ref    is not None: dac_ref    |= ALTER_DAC_REF
        if dac_value  is not None: dac_value  |= ALTER_DAC_VALUE
        if adc_ref    is not None: adc_ref    |= ALTER_ADC_REF
        if int_conf   is not None: int_conf   |= ALTER_INT_CONF

        new_gpconf = None
        if (gp0, gp1, gp2, gp3) != (None, None, None, None):
            new_gpconf = ALTER_GPIO_CONF
            # Preserve GPx for non specified pins
            status = self.send_cmd([CMD_GET_SRAM_SETTINGS])
            if gp0 is None: gp0 = status[22]
            if gp1 is None: gp1 = status[23]
            if gp2 is None: gp2 = status[24]
            if gp3 is None: gp3 = status[25]

        cmd = [0] * 12
        cmd[0]  = CMD_SET_SRAM_SETTINGS
        cmd[1]  = 0   # don't care
        cmd[2]  = clk_output or PRESERVE_CLK_OUTPUT # Clock Output Divider value
        cmd[3]  = dac_ref    or PRESERVE_DAC_REF    # DAC Voltage Reference
        cmd[4]  = dac_value  or PRESERVE_DAC_VALUE  # Set DAC output value
        cmd[5]  = adc_ref    or PRESERVE_ADC_REF    # ADC Voltage Reference
        cmd[6]  = int_conf   or PRESERVE_INT_CONF   # Setup the interrupt detection
        cmd[7]  = new_gpconf or PRESERVE_GPIO_CONF  # Alter GPIO configuration
        cmd[8]  = gp0        or PRESERVE_GPIO_CONF  # GP0 settings
        cmd[9]  = gp1        or PRESERVE_GPIO_CONF  # GP1 settings
        cmd[10] = gp2        or PRESERVE_GPIO_CONF  # GP2 settings
        cmd[11] = gp3        or PRESERVE_GPIO_CONF  # GP3 settings

        r = self.send_cmd(cmd)

        if r[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
            raise RuntimeError("SRAM write error.")


    #######################################################################
    # GPIO
    #######################################################################
    def GPIO_write(self, gp0 = None, gp1 = None, gp2 = None, gp3 = None):
        """ Set pin output values.

        If a pin is omitted, it will preserve the value.

        To change the output state of a pin, it must be assigned to GPIO_IN or GPIO_OUT
        (see :func:`set_pin_function`).

        Parameters:
            gp0 (bool, optional): Set GP0 logic value.
            gp1 (bool, optional): Set GP1 logic value.
            gp2 (bool, optional): Set GP2 logic value.
            gp3 (bool, optional): Set GP3 logic value.

        Raises:
            RuntimeError: If given pin is not assigned to GPIO function.

        Examples:

            Configure GP1 as output (defaults to False) and then set the value to logical True.

            >>> mcp.set_pin_function(gp1 = "GPIO_OUT")
            >>> mcp.GPIO_write(gp1 = True)

            If will fail if the pin is not assigned to GPIO:

            >>> mcp.set_pin_function(gp2 = 'DAC')
            >>> mcp.GPIO_write(gp2 = False)
            Traceback (most recent call last):
                ...
            RuntimeError: Pin GP2 is not assigned to GPIO function.
        """
        ALTER_VALUE = 1
        PRESERVE_VALUE = 0
        GPIO_ERROR = 0xEE

        buf = [0] * 18
        buf[0]  = CMD_SET_GPIO_OUTPUT_VALUES
        buf[2]  = PRESERVE_VALUE if gp0 is None else ALTER_VALUE
        buf[3]  = gp0 or 0
        buf[6]  = PRESERVE_VALUE if gp1 is None else ALTER_VALUE
        buf[7]  = gp1 or 0
        buf[10] = PRESERVE_VALUE if gp2 is None else ALTER_VALUE
        buf[11] = gp2 or 0
        buf[14] = PRESERVE_VALUE if gp3 is None else ALTER_VALUE
        buf[15] = gp3 or 0

        r = self.send_cmd(buf)

        if gp0 is not None and r[3] == GPIO_ERROR:
            raise RuntimeError("Pin GP0 is not assigned to GPIO function.")
        elif gp1 is not None and r[7] == GPIO_ERROR:
            raise RuntimeError("Pin GP1 is not assigned to GPIO function.")
        elif gp2 is not None and r[11] == GPIO_ERROR:
            raise RuntimeError("Pin GP2 is not assigned to GPIO function.")
        elif gp3 is not None and r[15] == GPIO_ERROR:
            raise RuntimeError("Pin GP3 is not assigned to GPIO function.")


    def GPIO_read(self):
        """ Read all GPIO pins logic state.

        Returned values can be True, False or None if the pin is not set for GPIO operation.
        For an output pin, the returned status is the actual value.

        Return:
            tuple of bool: 4 logic values for the pins status gp0, gp1, gp2 and gp3.

        Example:
            >>> mcp.GPIO_read()
            (None, 0, 1, None)
        """
        r = self.send_cmd([CMD_GET_GPIO_VALUES])
        gp0 = r[2] if r[2] != 0xEE else None
        gp1 = r[4] if r[4] != 0xEE else None
        gp2 = r[6] if r[6] != 0xEE else None
        gp3 = r[8] if r[8] != 0xEE else None

        return (gp0, gp1, gp2, gp3)


    def set_pin_function(
        self,
        gp0 = None, gp1 = None, gp2 = None, gp3 = None,
        out0 = False, out1 = False, out2 = False, out3 = False):
        """ Configure pin function and, optionally, output value.

        You can set multiple pins at once.

        Accepted functions depends on the pin.

        - For **GP0**:

            - **GPIO_IN**  (*in*) : Digital input
            - **GPIO_OUT** (*out*): Digital output
            - **SSPND**    (*out*): Signals when the host has entered Suspend mode
            - **LED_URX**  (*out*): UART Rx LED activity output (factory default)

        - For **GP1**:

            - **GPIO_IN**  (*in*) : Digital input
            - **GPIO_OUT** (*out*): Digital output
            - **ADC**      (*in*) : ADC Channel 1
            - **CLK_OUT**  (*out*): Clock Reference Output
            - **IOC**      (*in*) : External Interrupt Edge Detector
            - **LED_UTX**  (*out*): UART Tx LED activity output (factory default)

        - For **GP2**:

            - **GPIO_IN**  (*in*) : Digital input
            - **GPIO_OUT** (*out*): Digital output
            - **ADC**      (*in*) : ADC Channel 2
            - **DAC**      (*out*): DAC Output 1
            - **USBCFG**   (*out*): USB device-configured status (factory default)

        - For **GP3**:

            - **GPIO_IN**  (*in*) : Digital input
            - **GPIO_OUT** (*out*): Digital output
            - **ADC**      (*in*) : ADC Channel 3
            - **DAC**      (*out*): DAC Output 2
            - **LED_I2C**  (*out*): USB/I2C traffic indicator (factory default)


        Parameters:
            gp0  (str, optional): Function for pin GP0. If None, don't alter function.
            gp1  (str, optional): Function for pin GP1. If None, don't alter function.
            gp2  (str, optional): Function for pin GP2. If None, don't alter function.
            gp3  (str, optional): Function for pin GP3. If None, don't alter function.
            out0 (bool, optional): Logic output for GP0 if configured as GPIO_OUT (default: False).
            out1 (bool, optional): Logic output for GP1 if configured as GPIO_OUT (default: False).
            out2 (bool, optional): Logic output for GP2 if configured as GPIO_OUT (default: False).
            out3 (bool, optional): Logic output for GP3 if configured as GPIO_OUT (default: False).

        Raises:
            ValueError: If invalid function for that pin is specified.
            ValueError: If given out value for non GPIO_OUT pin.

        Examples:

            Set all pins at once:

            >>> mcp.set_pin_function(
            ...     gp0 = "GPIO_IN",
            ...     gp1 = "GPIO_OUT",
            ...     gp2 = "ADC",
            ...     gp3 = "LED_I2C")
            >>>

            Change pin function at runtime:

            >>> mcp.set_pin_function(gp1 = "GPIO_IN")
            >>>

            It is not permitted to set the output of a non GPIO_OUT pin.

            >>> mcp.set_pin_function(
            ...     gp1 = "GPIO_OUT", out1 = True,
            ...     gp2 = "ADC", out2 = True)
            Traceback (most recent call last):
            ...
            ValueError: Pin output value can only be set if pin function is GPIO_OUT.
            >>>

            Only some functions are allowed for each pin.

            >>> mcp.set_pin_function(gp0 = "ADC")
            Traceback (most recent call last):
            ...
            ValueError: Invalid function for GP0. Could be: GPIO_IN, GPIO_OUT, SSPND, LED_URX
            >>>
        """
        gp0_funcs = {
            "GPIO_IN"  : GPIO_FUNC_GPIO | GPIO_DIR_IN,
            "GPIO_OUT" : GPIO_FUNC_GPIO | GPIO_DIR_OUT,
            "SSPND"    : GPIO_FUNC_DEDICATED,
            "LED_URX"  : GPIO_FUNC_ALT_0
            }

        gp1_funcs = {
            "GPIO_IN"  : GPIO_FUNC_GPIO | GPIO_DIR_IN,
            "GPIO_OUT" : GPIO_FUNC_GPIO | GPIO_DIR_OUT,
            "CLK_OUT"  : GPIO_FUNC_DEDICATED,
            "ADC"      : GPIO_FUNC_ALT_0,
            "LED_UTX"  : GPIO_FUNC_ALT_1,
            "IOC"      : GPIO_FUNC_ALT_2,
            }

        gp2_funcs = {
            "GPIO_IN"  : GPIO_FUNC_GPIO | GPIO_DIR_IN,
            "GPIO_OUT" : GPIO_FUNC_GPIO | GPIO_DIR_OUT,
            "USBCFG"   : GPIO_FUNC_DEDICATED,
            "ADC"      : GPIO_FUNC_ALT_0,
            "DAC"      : GPIO_FUNC_ALT_1,
            }

        gp3_funcs = {
            "GPIO_IN"  : GPIO_FUNC_GPIO | GPIO_DIR_IN,
            "GPIO_OUT" : GPIO_FUNC_GPIO | GPIO_DIR_OUT,
            "LED_I2C"  : GPIO_FUNC_DEDICATED,
            "ADC"      : GPIO_FUNC_ALT_0,
            "DAC"      : GPIO_FUNC_ALT_1,
            }

        if gp0 is not None and gp0 not in gp0_funcs:
            raise ValueError("Invalid function for GP0. Could be: " + ", ".join(gp0_funcs))
        if gp1 is not None and gp1 not in gp1_funcs:
            raise ValueError("Invalid function for GP1. Could be: " + ", ".join(gp1_funcs))
        if gp2 is not None and gp2 not in gp2_funcs:
            raise ValueError("Invalid function for GP2. Could be: " + ", ".join(gp2_funcs))
        if gp3 is not None and gp3 not in gp3_funcs:
            raise ValueError("Invalid function for GP3. Could be: " + ", ".join(gp3_funcs))

        if ( (out0 is True and gp0 != "GPIO_OUT") or
             (out1 is True and gp1 != "GPIO_OUT") or
             (out2 is True and gp2 != "GPIO_OUT") or
             (out3 is True and gp3 != "GPIO_OUT") ):
            raise ValueError("Pin output value can only be set if pin function is GPIO_OUT.")

        self.SRAM_config(
            gp0 = None if gp0 is None else gp0_funcs[gp0] | (GPIO_OUT_VAL_1 if out0 else GPIO_OUT_VAL_0),
            gp1 = None if gp1 is None else gp1_funcs[gp1] | (GPIO_OUT_VAL_1 if out1 else GPIO_OUT_VAL_0),
            gp2 = None if gp2 is None else gp2_funcs[gp2] | (GPIO_OUT_VAL_1 if out2 else GPIO_OUT_VAL_0),
            gp3 = None if gp3 is None else gp3_funcs[gp3] | (GPIO_OUT_VAL_1 if out3 else GPIO_OUT_VAL_0))


    #######################################################################
    # CLOCK
    #######################################################################
    def clock_config(self, duty, freq):
        """ Configure clock output frequency and Duty Cycle.

        Accepted values for **duty** are: `0`, `25`, `50` and `75`.

        Valid **freq** values are:
        `375kHz`, `750kHz`, `1.5MHz`, `3MHz`, `6MHz`, `12MHz` or `24MHz`.

        To output clock signal, you also need to assign GP1 function to `CLK_OUT`
        (see :func:`set_pin_function`).

        Parameters:
            duty (int): Output duty cycle in percent.
            freq (str): Output frequency.

        Raises:
            ValueError: if any of the parameters is not valid.

        Examples:

            >>> mcp.set_pin_function(gp1 = "CLK_OUT")
            >>> mcp.clock_config(50, "375kHz")
            >>>

            >>> mcp.clock_config(100, "375kHz")
            Traceback (most recent call last):
            ...
            ValueError: Accepted values for duty are 0, 25, 50, 75.

            >>> mcp.clock_config(25, "175kHz")
            Traceback (most recent call last):
            ...
            ValueError: Freq is one of 375kHz, 750kHz, 1.5MHz, 3MHz, 6MHz, 12MHz or 24MHz
        """
        if duty == 0:
            duty = CLK_DUTY_0
        elif duty == 25:
            duty = CLK_DUTY_25
        elif duty == 50:
            duty = CLK_DUTY_50
        elif duty == 75:
            duty = CLK_DUTY_75
        else:
            raise ValueError("Accepted values for duty are 0, 25, 50, 75.")

        if freq == "375kHz":
            div = CLK_FREQ_375kHz
        elif freq == "750kHz":
            div = CLK_FREQ_750kHz
        elif freq == "1.5MHz":
            div = CLK_FREQ_1_5MHz
        elif freq == "3MHz":
            div = CLK_FREQ_3MHz
        elif freq == "6MHz":
            div = CLK_FREQ_6MHz
        elif freq == "12MHz":
            div = CLK_FREQ_12MHz
        elif freq == "24MHz":
            div = CLK_FREQ_24MHz
        else:
            raise ValueError("Freq is one of 375kHz, 750kHz, 1.5MHz, 3MHz, 6MHz, 12MHz or 24MHz")

        self.SRAM_config(clk_output = duty | div)


    #######################################################################
    # ADC
    #######################################################################
    def ADC_config(self, ref):
        """ Configure ADC reference voltage.

        Accepted values for ``ref`` are "0", "1.024V", "2.048V", "4.096V" and "VDD".

        Parameters:
            ref (str): ADC reference voltage.

        Raises:
            ValueError: if ``ref`` value is not valid.

        Examples:

            >>> mcp.ADC_config(ref = "VDD")

            >>> mcp.ADC_config("1.024V")

            >>> mcp.ADC_config(ref = "5V")
            Traceback (most recent call last):
            ...
            ValueError: Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.
        """
        if ref == "OFF":
            ref = ADC_REF_VRM
            vrm = ADC_VRM_OFF
        elif ref == "1.024V":
            ref = ADC_REF_VRM
            vrm = ADC_VRM_1024
        elif ref == "2.048V":
            ref = ADC_REF_VRM
            vrm = ADC_VRM_2048
        elif ref == "4.096V":
            ref = ADC_REF_VRM
            vrm = ADC_VRM_4096
        elif ref == "VDD":
            ref = ADC_REF_VDD
            vrm = ADC_VRM_OFF
        else:
            raise ValueError("Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.")

        self.SRAM_config(adc_ref = ref | vrm)


    def ADC_read(self):
        """ Read all Analog to Digital Converter (ADC) channels.

        Analog value is always available regardless of pin function (see :func:`set_pin_function`).
        If pin is configured as output (GPIO_OUT or LED_I2C), the read value is always the output state.

        ADC is 10 bits, so the minimum value is 0 and the maximum value is 1023.

        Return:
            tuple of int: Value of 3 channels (gp1, gp2, gp3).

        Examples:
            All three pins configured as ADC inputs.

            >>> mcp.ADC_config(ref = "VDD")
            >>> mcp.set_pin_function(
            ...    gp1 = "ADC",
            ...    gp2 = "ADC",
            ...    gp3 = "ADC")
            >>> mcp.ADC_read()
            (185, 136, 198)

            Reading the ADC value of a digital output gives the actual voltage in the pin.
            For a logic output ``1`` is equal to ``Vdd`` unless something is pulling that pin low (i.e. a LED).

            >>> mcp.set_pin_function(
            ...    gp1 = "GPIO_OUT", out1 = True,
            ...    gp2 = "GPIO_OUT", out2 = False)
            >>> mcp.ADC_read()
            (1023, 0, 198)
        """
        buf = self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])
        adc1 = buf[50] + 256*buf[51]
        adc2 = buf[52] + 256*buf[53]
        adc3 = buf[54] + 256*buf[55]
        return (adc1, adc2, adc3)


    #######################################################################
    # DAC
    #######################################################################
    def DAC_config(self, ref, out = 0):
        """ Configure Digital to Analog Converter (DAC) reference.

        Valid values from ``ref`` are "0", "1.024V", "2.048V", "4.096V" and "VDD".

        MCP2221's DAC is 5 bits. So valid values for ``out`` are from 0 to 31.

        ``out`` parameter is optional and defaults to 0.
        Use :func:`DAC_write` to set the DAC output value.

        Parameters:
            ref (str): Reference voltage for DAC.
            out (int, optional): value to output. Default is 0.

        Raises:
            ValueError: if ``ref`` or ``out`` values are not valid.

        Examples:

            >>> mcp.set_pin_function(gp2 = "DAC")
            >>> mcp.DAC_config(ref = "4.096V")

            >>> mcp.DAC_config(ref = 0)
            Traceback (most recent call last):
            ...
            ValueError: Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.
        """
        if ref == "OFF":
            ref = DAC_REF_VRM
            vrm = DAC_VRM_OFF
        elif ref == "1.024V":
            ref = DAC_REF_VRM
            vrm = DAC_VRM_1024
        elif ref == "2.048V":
            ref = DAC_REF_VRM
            vrm = DAC_VRM_2048
        elif ref == "4.096V":
            ref = DAC_REF_VRM
            vrm = DAC_VRM_4096
        elif ref == "VDD":
            ref = DAC_REF_VDD
            vrm = DAC_VRM_OFF
        else:
            raise ValueError("Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.")

        if out not in range(0, 32):
            raise ValueError("Accepted values for out are from 0 to 31.")

        self.SRAM_config(
            dac_ref = ref | vrm,
            dac_value = out)


    def DAC_write(self, out):
        """ Set the DAC output value.

        Valid ``out`` values are 0 to 31.

        To use a GP pin as DAC, you must assign the function "DAC" (see :func:`set_pin_function`).
        MCP2221 only have 1 DAC. So if you assign to "DAC" GP2 and GP3 you will
        see the same output value in both.

        Parameters:
            out (int): Value to output (max. 32) referenced to DAC ref voltage.

        Examples:
            >>> mcp.set_pin_function(gp2 = "DAC")
            >>> mcp.DAC_config(ref = "VDD")
            >>> mcp.DAC_write(31)
            >>>

            >>> mcp.DAC_write(32)
            Traceback (most recent call last):
            ...
            ValueError: Accepted values for out are from 0 to 31.
        """
        if out not in range(0, 32):
            raise ValueError("Accepted values for out are from 0 to 31.")

        self.SRAM_config(dac_value = out)


    #######################################################################
    # I2C
    #######################################################################
    def I2C_speed(self, speed=100000):
        """ Set I2C bus speed.

        Acceptable values for speed are between 50kHz and 400kHz.

        Parameters:
            speed (int): Bus clock frequency in Hz. Default bus speed is 100kHz.

        Raises:
            ValueError: if speed parameter is out of range.
            RuntimeError: if command failed (I2C engine is busy)."

        Example:
            >>> mcp.I2C_speed(100000)
            >>>
        """
        bus_speed = round(12_000_000 / speed) - 2

        if bus_speed < 0 or bus_speed > 255:
            raise ValueError("Speed must be between 47kHz and 400kHz.")

        buf = [0] * 5
        buf[0] = CMD_POLL_STATUS_SET_PARAMETERS
        buf[1] = 0
        buf[2] = 0
        buf[3] = I2C_CMD_SET_BUS_SPEED
        buf[4] = bus_speed
        rbuf = self.send_cmd(buf)

        if (rbuf[3] != 0x20):
            raise RuntimeError("I2C speed is not valid or bus is busy.")


    def I2C_is_idle(self):
        """ Check if the I2C engine is idle.

        Returns:
            bool: True if idle, False if engine is in the middle of a transfer (timeout detected).

        Example:
            >>> mcp.I2C_is_idle()
            True
            >>>
        """
        rbuf = self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])

        if rbuf[8]:
            return False
        else:
            return True


    def I2C_cancel(self):
        """ Cancel an active I2C transfer.

        This command can fail in two ways.

        - SCL keeps low. This is caused by:

          - Missing pull-up resistor or to high value.
          - A slave device is using clock stretching while doing an operation (e.g. writing to EEPROM).
          - Another device is using the bus.

        - SDA keeps low. Caused by:

          - Missing pull-up resistor or to high value.
          - A i2c read transfer timed out while slave was sending data and now the I2C
            bus is locked-up. Read the Hint.

        Return:
            bool: True if device is now ready to go. False if the engine is not idle.

        Raises:
            RuntimeError: if I2C engine detects the **SCL** line does not go up (read description).
            RuntimeError: if I2C engine detects the **SDA** line does not go up (read description).

        Examples:

            Last transfer was cancel, and engine is ready for the next operation:
            >>> mcp.I2C_cancel()
            True

            >>> mcp.I2C_cancel()
            Traceback (most recent call last):
            ...
            RuntimeError: SCL is low. I2C bus is busy or missing pull-up resistor.

        Hint:
            About the I2C bus locking-up.

            Sometimes, due to a glitch or premature timeout, the master terminates the transfer.
            But the slave was in the middle of sending a byte. So it is expecting a few more clocks
            cycles to send the rest of the byte.

            Since the master gave up, it will not clock the bus anymore, and so the slave won't
            release SDA line. The master, seeing SDA line busy, refuses to initiate any new
            I2C transfer. If the slave does not implement any timeout (SMB slaves do have it,
            but I2C ones don't), the I2C bus is locked-up forever.

            MCP2221's I2C engine cannot solve this problem. You can either manually clock the
            bus using any GPIO line, or cycle the power supply.

        Note:
            Do not call this function without issuing a :func:`I2C_read` or
            :func:`I2C_write` first. It could render I2C engine inoperative until
            the next reset.

            >>> mcp.reset()
            >>> mcp.I2C_is_idle()
            True
            >>> mcp.I2C_cancel()
            False

            Now the bus is busy until the next reset.

            >>> mcp.I2C_speed(100000)
            Traceback (most recent call last):
            ...
            RuntimeError: I2C speed is not valid or bus is busy.
            >>> mcp.I2C_cancel()
            False
            >>> mcp.I2C_is_idle()
            False
            >>> mcp.I2C_cancel()
            False

            After a reset, it will work again.

            >>> mcp.reset()
            >>> mcp.I2C_is_idle()
            True
        """
        buf = [0] * 3
        buf[0] = CMD_POLL_STATUS_SET_PARAMETERS
        buf[1] = 0
        buf[2] = I2C_CMD_CANCEL_CURRENT_TRANSFER

        # More than one time is needed to clear timeout status.
        # And device half writing.
        rbuf = self.send_cmd(buf)
        time.sleep(10/1000)
        rbuf = self.send_cmd(buf)

        if (rbuf[22] == 0):
            raise RuntimeError("SCL is low. I2C bus is busy or missing pull-up resistor.")

        if (rbuf[23] == 0):
            raise RuntimeError("SDA is low. Missing pull-up resistor, I2C bus is busy or slave device in the middle of sending data.")

        return self.I2C_is_idle()


    def I2C_write(self, addr, data, kind = "regular"):
        """ Write data to an address on I2C bus.

        Maximum ``data`` length is 65536 bytes. If data length is 0, this function
        will not write anything to the bus.

        Valid values for ``kind`` are:

        - **regular**: start - data to write - stop (this is the default)
        - **restart**: repeated start - data to write - stop
        - **nonstop**: start - data to write

        Parameters:
            addr (int): I2C slave device **base** address.
            data (bytes): bytes to write
            kind (str, optional): kind of transfer (see description).

        Raises:
            ValueError: if any parameter is not valid.
            RuntimeError: if the I2C slave didn't acknowledge.

        Examples:
            >>> mcp.I2C_write(0x50, b'This is data')
            >>>

            Writing data to a non-existent device:

            >>> mcp.I2C_write(0x60, b'This is data'))
            Traceback (most recent call last):
            ...
            RuntimeError: I2C write error: device NAK.
            """
        if addr < 0 or addr > 127:
            raise ValueError("Slave address not valid.")

        if len(data) > 2**16:
            raise ValueError("Data too long (max. 65536).")

        if kind == "regular":
            cmd = CMD_I2C_WRITE_DATA
        elif kind == "restart":
            cmd = CMD_I2C_WRITE_DATA_REPEATED_START
        elif kind == "nonstop":
            cmd = CMD_I2C_WRITE_DATA_NO_STOP
        else:
            raise ValueError("Invalid kind of transfer. Allowed: 'regular', 'restart', 'nonstop'.")

        header = [0] * 4
        header[0] = cmd
        header[1] = len(data)      & 0xFF
        header[2] = len(data) >> 8 & 0xFF
        header[3] = addr << 1      & 0xFF

        # send data in 60 bytes chunks, repeating the header above
        for i in range(0, len(data), 60):
            first_byte = i
            last_byte  = min(i+60, len(data))
            data_chunk = list(data)[first_byte:last_byte]
            r = self.send_cmd(header + data_chunk)

            # Send more data when buffer is empty.
            # But buffer may not be fully empty in the last chunk
            # This loop could get stuck?
            while last_byte < len(data) and self._i2c_buffer_counter() > 0:
                time.sleep(1e-6)
                pass

            if r[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK or not self._i2c_ack():
                self.I2C_cancel()
                raise RuntimeError("I2C write error: device NAK.")


    def _i2c_buffer_counter(self):
        """
        Get the internal databuffer counter.
        Useful to know when to send more data.
        """
        return self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])[13]


    def _i2c_ack(self):
        """
        Get the internal engine ACK status.
        Useful to know when the write transfer has failed.
        """
        if self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])[20] & (1 << 6):
            return False
        else:
            return True



    #######################################################################
    # I2C Read
    #######################################################################
    def I2C_read(self, addr, size = 1, kind = "regular", timeout_ms = 10):
        """ Read data from I2C bus.

        Maximum value for ``size`` is 65536 bytes.
        If ``size`` is 0, only expect acknowledge from device, but do not read any bytes.
        Note that reading 0 bytes might cause unexpected behavior in some devices.

        Valid values for ``kind`` are:

        - **regular**: start - read data - stop
        - **restart**: repeated start - read data - stop

        Parameters:
            addr (int): I2C slave device **base** address.
            size (int, optional): how many bytes to read, default 1 byte.
            kind (str, optional): kind of transfer (see description).
            timeout_ms (int, optional): time to wait for the data in milliseconds (default 10 ms).

        Return:
            bytes: data read

        Raises:
            ValueError: if any parameter is not valid.
            RuntimeError: if the I2C slave didn't acknowledge or the I2C engine was busy.

        Examples:

            >>> mcp.I2C_read(0x50, 12)
            b'This is data'

            Solve timeout by increasing ``timeout_ms`` parameter:

            >>> mcp.I2C_read(0x50, 64)
            Traceback (most recent call last):
            ...
            RuntimeError: Device did not ACK or did not send enough data. Try increasing timeout_ms.
            >>> mcp.I2C_read(0x50, 64, timeout_ms = 25)
            b'This is a very long long data stream that may trigger a timeout.'

        Hint:
            You can use :func:`I2C_read` with size 0 to check if there is any device listening
            with that address.

            There is a device in ``0x50`` (EEPROM):

            >>> mcp.I2C_read(0x50)
            b''

            No device in ``0x60``:

            >>> mcp.I2C_read(0x60)
            Traceback (most recent call last):
            ...
            RuntimeError: Device did not ACK or did not send enough data. Try increasing timeout_ms.

        Note:
            If a timeout occurs in the middle of character reading, the I2C but may stay busy.
            See :func:`I2C_cancel`.
        """
        if addr < 0 or addr > 127:
            raise ValueError("Slave address not valid.")

        if size > 2**16:
            raise ValueError("Data too long (max. 65536).")

        if kind == "regular":
            cmd = CMD_I2C_READ_DATA
        elif kind == "restart":
            cmd = CMD_I2C_READ_DATA_REPEATED_START
        else:
            raise ValueError("Invalid kind of transfer. Allowed: 'regular' or 'restart'.")

        # Removed in order to support repeated-start operation.
        #if not self.I2C_is_idle():
        #    raise RuntimeError("I2C read error, engine is not in idle state.")

        buf = [0] * 4
        buf[0] = cmd
        buf[1] = size      & 0xFF
        buf[2] = size >> 8 & 0xFF
        buf[3] = (addr << 1 & 0xFF) + 1  # address for read operation

        # Send read command to i2c bus.
        # This command return OK always unless bus were busy.
        # Also triggers data reading and place it into a buffer (until 60 bytes).
        rbuf = self.send_cmd(buf)
        if rbuf[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
            self.I2C_cancel()
            raise RuntimeError("I2C command read error.")

        data = []

        # You must call CMD_I2C_READ_DATA_GET_I2C_DATA at least once,
        # even for 0 byte read to get if device ack'ed or not.
        while True:
            time.sleep(timeout_ms/1000)

            # Retrieve data from buffer
            # This command must be issued after all bytes have arrived.
            # Return OK if got all data needed (or at least first 60 bytes).
            # Return 0x41 if device did not ACK or did not send enough data.
            rbuf = self.send_cmd([CMD_I2C_READ_DATA_GET_I2C_DATA])

            if rbuf[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
                self.I2C_cancel()
                raise RuntimeError("Device did not ACK or did not send enough data. Try increasing timeout_ms.")

            else:
                chunk_size = rbuf[3]
                data += rbuf[4:4+chunk_size]

            if len(data) >= size:
                break

        return bytes(data)


    def I2C_Slave(self, addr):
        """ Create a new I2C_Slave object.

        See :class:`EasyMCP2221.I2C_Slave.I2C_Slave` for detailed information.

        Parameters:
            addr (int): Slave's I2C bus address

        Return:
            I2C_Slave object.

        Example:
            >>> pcf    = mcp.I2C_Slave(0x48)
            >>> eeprom = mcp.I2C_Slave(0x50)
            >>> eeprom
            EasyMCP2221's I2C slave device at bus address 0x50.

        Note:
            New from v1.5.1.
        """
        return I2C_Slave.I2C_Slave(self, addr)


    #######################################################################
    # Wake-up
    #######################################################################
    def enable_power_management(self, enable = False):
        """ Enable or disable USB Power Management options for this device.

        Set or clear Remote Wake-up Capability bit in flash configuration.

        If enabled, Power Management Tab is available for this device in the Device Manager (Windows).
        So you can mark *"Allow this device to wake the computer"* option.

        A device :func:`reset` (or power supply cycle) is needed in order for changes to take effect.

        Parameters:
            enable (bool): Enable or disable Power Management.

        Raises:
            RuntimeError: If write to flash command failed.
            AssertionError: In rare cases, when some bug might have inadvertently activated Flash protection or permanent chip lock.

        Example:
            >>> mcp.enable_power_management(True)
            >>> print(mcp)
            ...
                "Chip settings": {
                    "Power management options": "enabled",
            ...
            >>> mcp.reset()
            >>>
        """
        chip_settings = self._read_flash_raw(FLASH_DATA_CHIP_SETTINGS)
        USBPWRATTR = chip_settings[12]

        if enable:
            USBPWRATTR |= 0b00100000
        else:
            USBPWRATTR &= 0b11011111

        chip_settings[12] = USBPWRATTR
        self._write_flash_raw(FLASH_DATA_CHIP_SETTINGS, chip_settings[4:64])


    def wake_up_config(self, edge = "none"):
        """ Configure interruption edge.

        Valid values for ``edge``:

        - **none**: disable interrupt detection
        - **raising**: fire interruption in raising edge (i.e. when GP1 goes from Low to High).
        - **falling**: fire interruption in falling edge (i.e. when GP1 goes from High to Low).
        - **both**: fire interruption in both (i.e. when GP1 state changes).

        In order to trigger, GP1 must be assigned to IOC function (see :func:`set_pin_function`).

        To wake-up the computer, Power Management options must be enabled (see :func:`enable_power_management`).
        And *"Allow this device to wake the computer"* option must be set in Device Manager.

        Parameters:
            edge (str): which edge triggers the interruption (see description).

        Raises:
            ValueError: if edge detection given.

        Example:
            >>> mcp.wake_up_config("both")
            >>>
        """
        if edge == "none":
            edge = INT_POS_EDGE_DISABLE | INT_NEG_EDGE_DISABLE
        elif edge == "raising":
            edge = INT_POS_EDGE_ENABLE  | INT_NEG_EDGE_DISABLE
        elif edge == "falling":
            edge = INT_POS_EDGE_DISABLE | INT_NEG_EDGE_ENABLE
        elif edge == "both":
            edge = INT_POS_EDGE_ENABLE  | INT_NEG_EDGE_ENABLE
        else:
            raise ValueError("Invalid edge detection. Allowed: 'raising', 'falling', 'both' or 'none'.")

        self.SRAM_config(int_conf = edge | INT_FLAG_CLEAR)


    #######################################################################
    # Reset
    #######################################################################
    def reset(self):
        """ Reset MCP2221.

        Reboot the device and load stored configuration from flash.

        This operation do not reset any I2C slave devices.

        """
        buf = [0] * 4
        buf[0] = CMD_RESET_CHIP
        buf[1] = RESET_CHIP_SURE
        buf[2] = RESET_CHIP_VERY_SURE
        buf[3] = RESET_CHIP_VERY_VERY_SURE
        self.send_cmd(buf, sleep = 1)

        self.__init__()

