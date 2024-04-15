import hid
import time

from .Constants import *
from . import I2C_Slave
from .exceptions import NotAckError, TimeoutError, LowSCLError, LowSDAError

class Device:
    """ MCP2221(A) device

    Parameters:
        VID (int, optional): Vendor Id (default to ``0x04D8``)
        PID (int, optional): Product Id (default to ``0x00DD``)
        devnum (int, optional): Device index if multiple device found with the same PID and VID. Default is first device (index 0).
        trace_packets (bool, optional): For debug only. See :any:`trace_packets`.

    Raises:
        RuntimeError: if no device found with given VID and PID.

    Example:
        >>> import EasyMCP2221
        >>> mcp = EasyMCP2221.Device()
        >>> print(mcp)
        {
            "Chip settings": {
                "Interrupt detection edge": "both",
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

    cmd_retries = 1
    """int: Times to retry an USB command if it fails."""

    trace_packets = False
    """bool: Print all binary commands and responses."""

    debug_messages = False
    """bool: Print debugging messages."""

    unsaved_SRAM = {}
    """Some options, like USB power attributes, are read from Flash into SRAM at start-up
    and cannot be changed in SRAM at run time. So we must store them somewhere to save
    then in save_config.
    """

    status = {
        # 4   -> output value
        # 3   -> direction
        # 2:0 -> designation
        "GPIO": {
            "gp0": None,
            "gp1": None,
            "gp2": None,
            "gp3": None
        },
        # 2:1 -> reference value,
        # 0   -> reference source
        "dac_ref": None,
        "dac_value": None,
        # 2:1 -> reference value,
        # 0   -> reference source
        "adc_ref": None,
        # mark i2c bus as dirty, to call cancel before then next operation
        "i2c_dirty": None
    }
    """ Internal status """

    VID = DEV_DEFAULT_VID
    PID = DEV_DEFAULT_PID
    devnum = 0
    device_open_timeout = 5


    def __init__(self, VID=None, PID=None, devnum=None, trace_packets=None):

        if trace_packets is not None:
            self.trace_packets = trace_packets

        if VID is not None:
            self.VID = VID

        if PID is not None:
            self.PID = PID

        if devnum is not None:
            self.devnum  = devnum

        self.hidhandler = hid.device()

        timeout = time.perf_counter() + self.device_open_timeout
        while True:
            try:
                devices = hid.enumerate(self.VID, self.PID)
                if not devices or len(devices) < self.devnum:
                    raise RuntimeError("No device found with VID %04X and PID %04X." % (self.VID, self.PID))

                self.hidhandler.open_path(hid.enumerate(self.VID, self.PID)[self.devnum]["path"])
                break

            except:
                if time.perf_counter() > timeout:
                    raise
                else:
                    continue

        # Initialize current GPIO settings
        settings = self.send_cmd([CMD_GET_SRAM_SETTINGS])
        self.status["GPIO"]["gp0"] = settings[22]
        self.status["GPIO"]["gp1"] = settings[23]
        self.status["GPIO"]["gp2"] = settings[24]
        self.status["GPIO"]["gp3"] = settings[25]

        # Initialize current DAC/ADC Vref (not the same for Get SRAM and for Set SRAM)
        self.status["dac_ref"]   = (settings[6] >> 5) & 0b00000111
        self.status["dac_value"] = (settings[6])      & 0b00011111
        self.status["adc_ref"]   = (settings[7] >> 2) & 0b00000111

        ## After power-up, Vrm may be set-up but not working, it's like when you apply new GPIO in SRAM
        self._reinforce_SRAM()

        # Read I2C status and try to release the bus if needed.
        # (i2c lines might not be up right now)
        try:
            self._i2c_release()
        except:
            pass

        # Set I2C speed to a safer value. In some device revision, default speed is 500kHz.
        self.I2C_speed(100_000)


    def __repr__(self):
        import json
        data = self.read_flash_info(human=True)
        return json.dumps(data, indent=4, sort_keys=True)


    def __del__(self):
        """ Releases the device. """
        self.hidhandler.close()
        del self.hidhandler


    def send_cmd(self, buf):
        """ Write a raw USB command to device and get the response.

        Write 64 bytes to the HID interface, starting by ``buf`` bytes.
        Then read 64 bytes from HID and return them as a list.
        In case of failure (USB read/write or command error) it will retry.
        To prevent this, set :attr:`cmd_retries` to zero.

        Parameters:
            buf (list of bytes): Full data to write, including command (64 bytes max).

        Returns:
            list of bytes: Full response data (64 bytes).

        Example:
            >>> from EasyMCP2221.Constants import *
            >>> r = mcp.send_cmd([CMD_GET_GPIO_VALUES])
            [81, 0, 238, 239, 238, 239, 238, 239, 238, 239, 0, 0, 0, ... 0, 0]

        See also:
            Class variables :attr:`cmd_retries`, :attr:`debug_messages` and :attr:`trace_packets`.

        Hint:
            The response does not wait until the actual command execution is finished. Instead, it is generated right after the device receives the command. So an error response might indicate:

            - the most recent command is not valid
            - the previous command finished with an error condition (case of I2C write).
        """
        if self.trace_packets:
            print("CMD:", " ".join("%02x" % i for i in buf))

        REPORT_NUM = 0x00
        padding = [0x00] * (PACKET_SIZE - len(buf))

        for retry in range(0, self.cmd_retries + 1):

            if self.debug_messages and retry > 0:
                print("Command re-try", retry)

            # Write command
            try:
                self.hidhandler.write([REPORT_NUM] + buf + padding)
            except OSError:
                if retry < self.cmd_retries:
                    continue
                else:
                    raise

            # This command does not return anything
            if buf[0] == CMD_RESET_CHIP:
                return None

            # Read response
            try:
                # timeout 50 removed due to Issue
                # https://github.com/electronicayciencia/EasyMCP2221/issues/7
                r = self.hidhandler.read(PACKET_SIZE)
            except OSError:
                if retry < self.cmd_retries:
                    continue
                else:
                    raise

            if self.trace_packets:
                print("RES:", " ".join("%02x" % i for i in r))

            # Always return if the error is caused by non idempotent commands
            if buf[0] not in (
                CMD_READ_FLASH_DATA,
                CMD_POLL_STATUS_SET_PARAMETERS,
                CMD_SET_GPIO_OUTPUT_VALUES,
                CMD_SET_SRAM_SETTINGS,
                CMD_GET_SRAM_SETTINGS,
                CMD_READ_FLASH_DATA,
                CMD_WRITE_FLASH_DATA,
                CMD_RESET_CHIP
                ):
                return r

            # Return if ok
            if r[RESPONSE_STATUS_BYTE] == RESPONSE_RESULT_OK:
                return r
            else:
                if retry < self.cmd_retries:
                    continue
                else:
                    return r

        raise RuntimeError("Command failed.")


    def _update_gp_setting_out(self, gp, out):
        """Update the GP setting (like in SRAM setting) with output values from Set GPIO Output Values command."""
        if out == True:
            self.status["GPIO"][gp] = self.status["GPIO"][gp] | GPIO_OUT_VAL_1
        else:
            self.status["GPIO"][gp] = self.status["GPIO"][gp] & GPIO_OUT_VAL_0


    #######################################################################
    # Flash
    #######################################################################
    def save_config(self):
        """
        Write current status (pin assignments, GPIO output values,
        DAC reference and value, ADC reference, etc.) to flash memory.

        You can save a new configuration as many times as you wish.
        That will be the default state at power up.

        Raises:
            RuntimeError: if command failed.
            AssertionError: if an accidental flash protection attempt was prevented.

        Example:
            Set all GPIO pins as digital inputs (high impedance state) at start-up to prevent short circuits
            while breadboarding.

            >>> mcp.set_pin_function(
            ...     gp0 = "GPIO_IN",
            ...     gp1 = "GPIO_IN",
            ...     gp2 = "GPIO_IN",
            ...     gp3 = "GPIO_IN")
            >>> mcp.DAC_config(ref = "OFF")
            >>> mcp.ADC_config(ref = "VDD")
            >>> mcp.save_config()
        """
        chip = self._read_flash_raw(FLASH_DATA_CHIP_SETTINGS)
        gp   = self._read_flash_raw(FLASH_DATA_GP_SETTINGS)
        sram = self.send_cmd([CMD_GET_SRAM_SETTINGS])

        chip = chip[4:14]
        gp   = gp[4:8]
        sram = sram[4:26]

        chip.extend([0] * 8) # 8 bytes for writing password that don't come on reading

        if self.debug_messages:
            print("OLD CHIP:", " ".join("%02x" % i for i in chip))

        chip[FLASH_CHIP_SETTINGS_CDC_SEC] = sram[SRAM_CHIP_SETTINGS_CDC_SEC]
        chip[FLASH_CHIP_SETTINGS_CLOCK]   = sram[SRAM_CHIP_SETTINGS_CLOCK]
        chip[FLASH_CHIP_SETTINGS_DAC]     = sram[SRAM_CHIP_SETTINGS_DAC]
        chip[FLASH_CHIP_SETTINGS_INT_ADC] = sram[SRAM_CHIP_SETTINGS_INT_ADC]
        chip[FLASH_CHIP_SETTINGS_LVID]    = sram[SRAM_CHIP_SETTINGS_LVID]
        chip[FLASH_CHIP_SETTINGS_HVID]    = sram[SRAM_CHIP_SETTINGS_HVID]
        chip[FLASH_CHIP_SETTINGS_LPID]    = sram[SRAM_CHIP_SETTINGS_LPID]
        chip[FLASH_CHIP_SETTINGS_HPID]    = sram[SRAM_CHIP_SETTINGS_HPID]
        chip[FLASH_CHIP_SETTINGS_USBPWR]  = sram[SRAM_CHIP_SETTINGS_USBPWR]
        chip[FLASH_CHIP_SETTINGS_USBMA]   = sram[SRAM_CHIP_SETTINGS_USBMA]
        chip[FLASH_CHIP_SETTINGS_PWD1]    = sram[SRAM_CHIP_SETTINGS_PWD1]
        chip[FLASH_CHIP_SETTINGS_PWD2]    = sram[SRAM_CHIP_SETTINGS_PWD2]
        chip[FLASH_CHIP_SETTINGS_PWD3]    = sram[SRAM_CHIP_SETTINGS_PWD3]
        chip[FLASH_CHIP_SETTINGS_PWD4]    = sram[SRAM_CHIP_SETTINGS_PWD4]
        chip[FLASH_CHIP_SETTINGS_PWD5]    = sram[SRAM_CHIP_SETTINGS_PWD5]
        chip[FLASH_CHIP_SETTINGS_PWD6]    = sram[SRAM_CHIP_SETTINGS_PWD6]
        chip[FLASH_CHIP_SETTINGS_PWD7]    = sram[SRAM_CHIP_SETTINGS_PWD7]
        chip[FLASH_CHIP_SETTINGS_PWD8]    = sram[SRAM_CHIP_SETTINGS_PWD8]

        if self.debug_messages:
            print("NEW CHIP:", " ".join("%02x" % i for i in chip))
            print("OLD GP:", " ".join("%02x" % i for i in gp))

        # Take status instead of SRAM variables because GPIO_write command won't alter SRAM
        gp[FLASH_GP_SETTINGS_GP0]         = self.status["GPIO"]["gp0"]
        gp[FLASH_GP_SETTINGS_GP1]         = self.status["GPIO"]["gp1"]
        gp[FLASH_GP_SETTINGS_GP2]         = self.status["GPIO"]["gp2"]
        gp[FLASH_GP_SETTINGS_GP3]         = self.status["GPIO"]["gp3"]

        for k in self.unsaved_SRAM:
            chip[k] = self.unsaved_SRAM[k]

        if self.debug_messages:
            print("NEW GP:", " ".join("%02x" % i for i in gp))

        self._write_flash_raw(FLASH_DATA_CHIP_SETTINGS, chip)
        self._write_flash_raw(FLASH_DATA_GP_SETTINGS,   gp)


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


    def read_flash_info(self, raw=False, human=False):
        """ Read flash data.

        Return USB enumeration strings, power-up GPIO settings and internal chip configuration.

        Parameters:
            raw (bool, optional):
                If ``False``, return only parsed data (this is the default).
                If ``True``, return all data unparsed.
            human (bool, optional):
                If ``False``, return variable names untranslated, for API (this is the default).
                If ``True``, return variable names in readable text.

        Return:
            dict: Flash data (parsed or raw)

        Example:
            >>> mcp.read_flash_info()
            {
                "CHIP_SETTINGS": {
                    "adc_ref": "VDD",
                    "clk_duty": 50,
                    "clk_freq": "12MHz",
                    "dac_ref": "VDD",
                    "dac_val": 0,
                    "ioc": "both",
                    "ma": 100,
                    "pid": "0x00DD",
                    "pwr": "disabled",
                    "vid": "0x04D8"
                },
                "GP_SETTINGS": {
                    "GP0": {
                        "func": "GPIO_IN",
                        "outval": 0
                    },
                    "GP1": {
                        "func": "GPIO_IN",
                        "outval": 0
                    },
                    "GP2": {
                        "func": "GPIO_IN",
                        "outval": 0
                    },
                    "GP3": {
                        "func": "GPIO_IN",
                        "outval": 0
                    }
                },
                "USB_FACT_SERIAL": "01234567",
                "USB_PRODUCT": "MCP2221 USB-I2C/UART Combo",
                "USB_SERIAL": "0000033333",
                "USB_VENDOR": "Microchip Technology Inc."
            }


        Hint:
            When called with `human = true` parameter, this is the function used to
            stringfy the object.
        """


        data = {
            "CHIP_SETTINGS"   : self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_CHIP_SETTINGS]),
            "GP_SETTINGS"     : self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_GP_SETTINGS]),
            "USB_VENDOR"      : self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_USB_MANUFACTURER]),
            "USB_PRODUCT"     : self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_USB_PRODUCT]),
            "USB_SERIAL"      : self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_USB_SERIALNUM]),
            "USB_FACT_SERIAL" : self.send_cmd([CMD_READ_FLASH_DATA, FLASH_DATA_CHIP_SERIALNUM]),
        }

        if raw:
            return data

        data["USB_VENDOR"]      = self._parse_wchar_structure(data["USB_VENDOR"])
        data["USB_PRODUCT"]     = self._parse_wchar_structure(data["USB_PRODUCT"])
        data["USB_SERIAL"]      = self._parse_wchar_structure(data["USB_SERIAL"])
        data["USB_FACT_SERIAL"] = self._parse_factory_serial(data["USB_FACT_SERIAL"])
        data["CHIP_SETTINGS"]   = self._parse_chip_settings_struct(data["CHIP_SETTINGS"])
        data["GP_SETTINGS"]     = self._parse_gp_settings_struct(data["GP_SETTINGS"])

        if not human:
            return data

        return self._humanify(data)


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
        vid = (buf[FLASH_CHIP_SETTINGS_HVID + FLASH_OFFSET_READ] << 8) \
            +  buf[FLASH_CHIP_SETTINGS_LVID + FLASH_OFFSET_READ]

        pid = (buf[FLASH_CHIP_SETTINGS_HPID + FLASH_OFFSET_READ] << 8) \
            +  buf[FLASH_CHIP_SETTINGS_LPID + FLASH_OFFSET_READ]

        mA = buf[FLASH_CHIP_SETTINGS_USBMA + FLASH_OFFSET_READ] * 2

        if buf[FLASH_CHIP_SETTINGS_USBPWR + FLASH_OFFSET_READ] & 0b00100000:
            pmo_str = "enabled"
        else:
            pmo_str = "disabled"

        ide_bits = (buf[FLASH_CHIP_SETTINGS_INT_ADC + FLASH_OFFSET_READ] & 0b01100000) >> 5
        ide_str = ("both"    if ide_bits == 3 else
                   "falling" if ide_bits == 2 else
                   "rising"  if ide_bits == 1 else
                   "none")

        ADCREF = (buf[FLASH_CHIP_SETTINGS_INT_ADC + FLASH_OFFSET_READ] & 0b00000100) >> 2
        ADCVRM = (buf[FLASH_CHIP_SETTINGS_INT_ADC + FLASH_OFFSET_READ] & 0b00011000) >> 3
        adc_ref_str = ("VDD"    if ADCREF == 0 else
                       "1.024V" if ADCVRM == 0b01 else
                       "2.048V" if ADCVRM == 0b10 else
                       "4.096V" if ADCVRM == 0b11 else
                       "OFF")

        CLKDC  = (buf[FLASH_CHIP_SETTINGS_CLOCK + FLASH_OFFSET_READ] & 0b00011000) >> 3
        clk_dc_str = (75 if CLKDC == 0b11 else
                      50 if CLKDC == 0b10 else
                      25 if CLKDC == 0b01 else
                      0)

        CLKDIV = (buf[FLASH_CHIP_SETTINGS_CLOCK + FLASH_OFFSET_READ] & 0b00000111) >> 0
        clk_freq_str = ("375kHz" if CLKDIV == 0b111 else
                        "750kHz" if CLKDIV == 0b110 else
                        "1.5MHz" if CLKDIV == 0b101 else
                        "3MHz"   if CLKDIV == 0b100 else
                        "6MHz"   if CLKDIV == 0b011 else
                        "12MHz"  if CLKDIV == 0b010 else
                        "24MHz"  if CLKDIV == 0b001 else
                        "reserved")

        DACREF = (buf[FLASH_CHIP_SETTINGS_DAC + FLASH_OFFSET_READ] & 0b00100000) >> 5
        DACVRM = (buf[FLASH_CHIP_SETTINGS_DAC + FLASH_OFFSET_READ] & 0b11000000) >> 6
        dac_ref_str = ("VDD"    if DACREF == 0 else
                       "1.024V" if DACVRM == 0b01 else
                       "2.048V" if DACVRM == 0b10 else
                       "4.096V" if DACVRM == 0b11 else
                       "OFF")

        DACVAL = (buf[FLASH_CHIP_SETTINGS_DAC + FLASH_OFFSET_READ] & 0b00011111) >> 0

        data = {
            "vid": "0x{:04X}".format(vid),
            "pid": "0x{:04X}".format(pid),
            "ma": mA,
            "pwr": pmo_str,
            "ioc": ide_str,
            "clk_duty": clk_dc_str,
            "clk_freq": clk_freq_str,
            "adc_ref": adc_ref_str,
            "dac_ref": dac_ref_str,
            "dac_val": DACVAL,
        }

        return data

    def _parse_gp_settings_struct(self, buf):
        GPSETTING0 = buf[FLASH_GP_SETTINGS_GP0 + FLASH_OFFSET_READ]
        GPSETTING1 = buf[FLASH_GP_SETTINGS_GP1 + FLASH_OFFSET_READ]
        GPSETTING2 = buf[FLASH_GP_SETTINGS_GP2 + FLASH_OFFSET_READ]
        GPSETTING3 = buf[FLASH_GP_SETTINGS_GP3 + FLASH_OFFSET_READ]

        data = {}
        data["GP0"] = self._parse_gp_settings_register(GPSETTING0, 0)
        data["GP1"] = self._parse_gp_settings_register(GPSETTING1, 1)
        data["GP2"] = self._parse_gp_settings_register(GPSETTING2, 2)
        data["GP3"] = self._parse_gp_settings_register(GPSETTING3, 3)

        return data

    def _parse_gp_settings_register(self, GPSETTING, pin):
        GPIOOUTVAL = (GPSETTING & 0b00010000) >> 4
        GPIODIR    = (GPSETTING & 0b00001000) >> 3
        GPDES      = (GPSETTING & 0b00000111)

        data = {}
        data["outval"] = GPIOOUTVAL

        # GPIO operation
        if GPDES == 0:
            if GPIODIR == 0: data["func"] = "GPIO_OUT"
            else: data["func"] = "GPIO_IN"

        #  Dedicated function operation
        elif GPDES == 1:
            if pin == 0: data["func"] = "SSPND"
            if pin == 1: data["func"] = "CLK_OUT"
            if pin == 2: data["func"] = "USBCFG"
            if pin == 3: data["func"] = "LED_I2C"

        #  Alternate function 0
        elif GPDES == 2:
            if pin == 0: data["func"] = "LED_URX"
            if pin == 1: data["func"] = "ADC"
            if pin == 2: data["func"] = "ADC"
            if pin == 3: data["func"] = "ADC"

        #  Alternate function 1
        elif GPDES == 3:
            if pin == 0: data["func"] = "reserved"
            if pin == 1: data["func"] = "LED_UTX"
            if pin == 2: data["func"] = "DAC"
            if pin == 3: data["func"] = "DAC"

        #  Alternate function 2
        elif GPDES == 4:
            if pin == 0: data["func"] = "reserved"
            if pin == 1: data["func"] = "IOC"
            if pin == 2: data["func"] = "reserved"
            if pin == 3: data["func"] = "reserved"

        else:
            data["func"] == "reserved"

        return data

    def _humanify(self, data):
        """Convert variable names into human strings recursively."""
        h = {}
        for k,v in data.items():
            if isinstance(v, dict):
                h[self._var2str(k)] = self._humanify(v)
            else:
                h[self._var2str(k)] = v
        return h

    def _var2str(self, varname):
        """Convert variable names into human strings."""
        strings = {
            "vid"             : "USB VID",
            "pid"             : "USB PID",
            "ma"              : "USB requested number of mA",
            "pwr"             : "Power management options",
            "ioc"             : "Interrupt detection edge",
            "adc_ref"         : "ADC reference value",
            "clk_duty"        : "Clock output duty cycle",
            "clk_freq"        : "Clock output frequency",
            "dac_ref"         : "DAC reference value",
            "dac_val"         : "DAC output value",
            "CHIP_SETTINGS"   : "Chip settings",
            "GP_SETTINGS"     : "General Purpose IO settings",
            "USB_VENDOR"      : "USB Manufacturer",
            "USB_PRODUCT"     : "USB Product",
            "USB_SERIAL"      : "USB Serial Number",
            "USB_FACT_SERIAL" : "Factory Serial Number",
            "func"            : "Pin designated operation",
            "outval"          : "Default output value",
        }

        return strings.get(varname, varname)


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
            Calling this function to change GPIO when DAC is active and DAC reference is not Vdd
            will create a 2ms gap in DAC output.
        """

        # Note that when ALTER_GPIO_CONF is active, Vrm will be reset.
        new_gpconf = None if (gp0, gp1, gp2, gp3) == (None, None, None, None) else ALTER_GPIO_CONF

        # This is to preserve current GPIO output status when writing to SRAM.
        # Otherwise, output status given with GPIO_write() command will be overwritten.
        if gp0 is None:
            gp0 = self.status["GPIO"]["gp0"]
        else:
            self.status["GPIO"]["gp0"] = gp0

        if gp1 is None:
            gp1 = self.status["GPIO"]["gp1"]
        else:
            self.status["GPIO"]["gp1"] = gp1

        if gp2 is None:
            gp2 = self.status["GPIO"]["gp2"]
        else:
            self.status["GPIO"]["gp2"] = gp2

        if gp3 is None:
            gp3 = self.status["GPIO"]["gp3"]
        else:
            self.status["GPIO"]["gp3"] = gp3

        # This is to fix a MCP2221's bug:
        #   "When the Set SRAM settings command is used for GPIO control,
        #   the reference voltage for VRM is always reinitialized to the default value (VDD)
        #   if it is not explicitly set." (datasheet, section 1.8)
        if dac_ref is None:
            dac_ref = self.status["dac_ref"]
        else:
            self.status["dac_ref"] = dac_ref

        if adc_ref is None:
            adc_ref = self.status["adc_ref"]
        else:
            self.status["adc_ref"] = adc_ref

        if dac_value is None:
            dac_value = self.status["dac_value"]
        else:
            self.status["dac_value"] = dac_value

        # Must turn off VRM when applying new GPIO configuration
        # otherwise it fails if ADC_ref = VDD and DAC_ref = VRM
        # dac value seems also to be lost
        if new_gpconf and ( (dac_ref & DAC_REF_VRM) or (adc_ref & ADC_REF_VRM) ):
            dac_ref = DAC_REF_VRM | DAC_VRM_OFF
            adc_ref = ADC_REF_VRM | ADC_VRM_OFF

        # Set Alter flag for all non-none parameters
        if clk_output is not None: clk_output |= ALTER_CLK_OUTPUT
        if int_conf   is not None: int_conf   |= ALTER_INT_CONF
        if dac_value  is not None: dac_value  |= ALTER_DAC_VALUE
        if dac_ref    is not None: dac_ref    |= ALTER_DAC_REF
        if adc_ref    is not None: adc_ref    |= ALTER_ADC_REF

        cmd = [0] * 12
        cmd[0]  = CMD_SET_SRAM_SETTINGS
        cmd[1]  = 0   # don't care
        cmd[2]  = clk_output or PRESERVE_CLK_OUTPUT # Clock Output Divider value
        cmd[3]  = dac_ref                           # DAC Voltage Reference
        cmd[4]  = dac_value  or PRESERVE_DAC_VALUE  # Set DAC output value
        cmd[5]  = adc_ref                           # ADC Voltage Reference
        cmd[6]  = int_conf   or PRESERVE_INT_CONF   # Setup the interrupt detection
        cmd[7]  = new_gpconf or PRESERVE_GPIO_CONF  # Alter GPIO configuration
        cmd[8]  = gp0                               # GP0 settings
        cmd[9]  = gp1                               # GP1 settings
        cmd[10] = gp2                               # GP2 settings
        cmd[11] = gp3                               # GP3 settings

        r = self.send_cmd(cmd)

        if r[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
            raise RuntimeError("SRAM write error.")

        # If ADC/DAC Ref is Vrm and changed GPIO, we need to explicitly restore Vrm.
        # It is not valid just sending the desired Vrm value in the above command because
        # ALTER_GPIO_CONF flag will reset Vrm anyways.
        # Note: this will cause a 2ms gap at DAC output.
        if new_gpconf and ( (dac_ref & DAC_REF_VRM) or (adc_ref & ADC_REF_VRM) ):
            self._reclaim_vrm()


    def _reclaim_vrm(self):
        """ Configure only Vrm part and nothing more """
        cmd = [0] * 12
        cmd[0]  = CMD_SET_SRAM_SETTINGS
        cmd[3]  = self.status["dac_ref"]   | ALTER_DAC_REF
        cmd[4]  = self.status["dac_value"] | ALTER_DAC_VALUE
        cmd[5]  = self.status["adc_ref"]   | ALTER_ADC_REF
        r = self.send_cmd(cmd)
        if r[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
            raise RuntimeError("SRAM write error.")


    def _reinforce_SRAM(self):
        """ The only purpose of this function is to solve some weird bugs on MCP2221. """
        self.SRAM_config(
            dac_ref    = self.status["dac_ref"],
            dac_value  = self.status["dac_value"],
            adc_ref    = self.status["adc_ref"],
            gp0        = self.status["GPIO"]["gp0"],
            gp1        = self.status["GPIO"]["gp1"],
            gp2        = self.status["GPIO"]["gp2"],
            gp3        = self.status["GPIO"]["gp3"])



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

        if gp0 is not None and r[3]  != GPIO_ERROR: self._update_gp_setting_out("gp0", gp0)
        if gp1 is not None and r[7]  != GPIO_ERROR: self._update_gp_setting_out("gp1", gp1)
        if gp2 is not None and r[11] != GPIO_ERROR: self._update_gp_setting_out("gp2", gp2)
        if gp3 is not None and r[15] != GPIO_ERROR: self._update_gp_setting_out("gp3", gp3)

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

        .. figure:: img/MCP2221_pinout.svg

        **GP0** functions:
            - **GPIO_IN**  (*in*) : Digital input
            - **GPIO_OUT** (*out*): Digital output
            - **SSPND**    (*out*): Signals when the host has entered Suspend mode
            - **LED_URX**  (*out*): UART Rx LED activity output (factory default)

        **GP1** functions:
            - **GPIO_IN**  (*in*) : Digital input
            - **GPIO_OUT** (*out*): Digital output
            - **ADC**      (*in*) : ADC Channel 1
            - **CLK_OUT**  (*out*): Clock Reference Output
            - **IOC**      (*in*) : External Interrupt Edge Detector
            - **LED_UTX**  (*out*): UART Tx LED activity output (factory default)

        **GP2** functions:
            - **GPIO_IN**  (*in*) : Digital input
            - **GPIO_OUT** (*out*): Digital output
            - **ADC**      (*in*) : ADC Channel 2
            - **DAC**      (*out*): DAC Output 1
            - **USBCFG**   (*out*): USB device-configured status (factory default)

        **GP3** functions:
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
            ...     gp1 = "GPIO_OUT", out1 = True,
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

        Hint:
            Pin assignments are active until reset or power cycle. Use :func:`save_config()` to
            make this configuration the default at next start.
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

        ``duty`` values:
            - 0
            - 25
            - 50
            - 75

        ``freq`` values:
            - "375kHz"
            - "750kHz"
            - "1.5MHz"
            - "3MHz"
            - "6MHz"
            - "12MHz"
            - "24MHz"

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
    def ADC_config(self, ref = "VDD"):
        """ Configure ADC reference voltage.

        ``ref`` values:
            - "OFF"
            - "1.024V"
            - "2.048V"
            - "4.096V"
            - "VDD"

        Parameters:
            ref (str, optional): ADC reference value. Default to supply voltage (Vdd).

        Raises:
            ValueError: if ``ref`` value is not valid.

        Examples:

            >>> mcp.ADC_config()

            >>> mcp.ADC_config("1.024V")

            >>> mcp.ADC_config(ref = "5V")
            Traceback (most recent call last):
            ...
            ValueError: Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.

        Hint:
            ADC configuration is saved when you call :func:`save_config` and reloaded at power-up.
            You only need to call this function if you want to change it.
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

        # When GP1, 2 and 3 are ADC and ADC_REF is Vdd. If Vrm ref is selected, ADC stop working.
        self._reinforce_SRAM()


    def ADC_read(self, norm=False):
        """ Read all Analog to Digital Converter (ADC) channels.

        Analog value is always available regardless of pin function (see :func:`set_pin_function`).
        If pin is configured as output (GPIO_OUT or LED_I2C), the read value is always the output state.

        ADC is 10 bits, so the minimum value is 0 and the maximum value is 1023.

        Parameters:
            norm (bool, optional): Divide output values by 1024 and return output between 0 and 1. Default  is ``False``.

        Return:
            tuple: Value of 3 channels (gp1, gp2, gp3).

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
        adc1 = buf[I2C_POLL_RESP_ADC_CH0_LSB] + 256*buf[I2C_POLL_RESP_ADC_CH0_MSB]
        adc2 = buf[I2C_POLL_RESP_ADC_CH1_LSB] + 256*buf[I2C_POLL_RESP_ADC_CH1_MSB]
        adc3 = buf[I2C_POLL_RESP_ADC_CH2_LSB] + 256*buf[I2C_POLL_RESP_ADC_CH2_MSB]

        if norm:
            adc1 = adc1 / 1024
            adc2 = adc2 / 1024
            adc3 = adc3 / 1024

        return (adc1, adc2, adc3)


    #######################################################################
    # DAC
    #######################################################################
    def DAC_config(self, ref = "VDD", out = None):
        """ Configure Digital to Analog Converter (DAC) reference.

        ``ref`` values:
            - "OFF"
            - "1.024V"
            - "2.048V"
            - "4.096V"
            - "VDD"

        MCP2221's DAC is 5 bits. So valid values for ``out`` are from 0 to 31.

        ``out`` parameter is optional and defaults last value.
        Use :func:`DAC_write` to set the DAC output value.

        Parameters:
            ref (str, optional): Reference voltage for DAC. Default to supply voltage (Vdd).
            out (int, optional): value to output. Default is last value.

        Raises:
            ValueError: if ``ref`` or ``out`` values are not valid.

        Examples:

            >>> mcp.set_pin_function(gp2 = "DAC")
            >>> mcp.DAC_config(ref = "4.096V")

            >>> mcp.DAC_config(ref = 0)
            Traceback (most recent call last):
            ...
            ValueError: Accepted values for ref are 'OFF', '1.024V', '2.048V', '4.096V' and 'VDD'.

        Hint:
            DAC configuration is saved when you call :func:`save_config` and reloaded at power-up.
            You only need to call this function if you want to change it.
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

        if out is not None and out not in range(0, 32):
            raise ValueError("Accepted values for out are from 0 to 31.")

        self.SRAM_config(
            dac_ref = ref | vrm,
            dac_value = out)


    def DAC_write(self, out, norm=False):
        """ Set the DAC output value.

        Valid ``out`` values are 0 to 31.

        To use a GP pin as DAC, you must assign the function "DAC" (see :func:`set_pin_function`).
        MCP2221 only have 1 DAC. So if you assign to "DAC" GP2 and GP3 you will
        see the same output value in both.

        Parameters:
            out (int): Value to output (max. 32) referenced to DAC ref voltage.
            norm (bool, optional): Accept input values as floats between 0 and 1. Default  is ``False``.

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
        if norm:
            if not 0 <= out <= 1:
                raise ValueError("Accepted values for out when norm=True are from 0 to 1.")

            out = out * 32
            if out > 31: out = 31

        else:
            if out not in range(0, 32):
                raise ValueError("Accepted values for out are from 0 to 31.")

        self.SRAM_config(dac_value = out)


    #######################################################################
    # Interrupt On Change
    #######################################################################

    def IOC_read(self):
        """ Read Interruption On Change flag.

        To enable Interruption Detection mechanism, pin designation must be *IOC*. See :func:`set_pin_function`.

        Return:
            int: Value of interrupt flag.

        Example:
            >>> mcp.IOC_read()
            1

        """
        rbuf = self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])
        intflag = rbuf[I2C_POLL_RESP_INT_FLAG]
        return intflag


    def IOC_clear(self):
        """ Clear Interruption On Change flag.

        Example:
            >>> mcp.IOC_read()
            1
            >>> mcp.IOC_clear()
            >>> mcp.IOC_read()
            0
            >>>
        """
        self.SRAM_config(int_conf = INT_FLAG_CLEAR)


    def IOC_config(self, edge = "both"):
        """ Configure Interruption On Change edge.

        Valid values for ``edge``:
            - **none**: disable interrupt detection
            - **rising**: fire interruption on rising edge (i.e. when GP1 goes from Low to High).
            - **falling**: fire interruption on falling edge (i.e. when GP1 goes from High to Low).
            - **both**: fire interruption on both (i.e. when GP1 state changes).

        Remember to call :func:`save_config` to persist this configuration when reset the chip.

        Parameters:
            edge (str): which edge triggers the interruption (see description).

        Raises:
            ValueError: if edge detection value is not valid.

        Example:
            >>> mcp.IOC_config(edge = "rising")
            >>>

        See also:
            :func:`set_pin_function`, :func:`IOC_clear`, :func:`IOC_read`.
        """
        if edge == "none":
            edge = INT_POS_EDGE_DISABLE | INT_NEG_EDGE_DISABLE
        elif edge == "rising":
            edge = INT_POS_EDGE_ENABLE  | INT_NEG_EDGE_DISABLE
        elif edge == "falling":
            edge = INT_POS_EDGE_DISABLE | INT_NEG_EDGE_ENABLE
        elif edge == "both":
            edge = INT_POS_EDGE_ENABLE  | INT_NEG_EDGE_ENABLE
        else:
            raise ValueError("Invalid edge detection. Allowed: 'rising', 'falling', 'both' or 'none'.")

        self.SRAM_config(int_conf = edge | INT_FLAG_CLEAR)



    #######################################################################
    # I2C
    #######################################################################
    def I2C_speed(self, speed=100000):
        """ Set I2C bus speed.

        Acceptable values are between 47kHz and 400kHz. This is not stored on the flash configuration.

        Parameters:
            speed (int): Bus clock frequency in Hz. Default bus speed is 100kHz.

        Raises:
            ValueError: if speed parameter is out of range.
            RuntimeError: if command failed (I2C engine is busy).

        Example:
            >>> mcp.I2C_speed(100000)
            >>>

        Note:
            The recommended values are between 47kHz and 400kHz. Out of this range, the minimum value is 46693, which corresponds to a clock of approximately 46.5kHz. And the maximum is 6000000, that generates about 522kHz clock.
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

        # On error, try to clean last I2C error condition and retry
        if (rbuf[I2C_POLL_RESP_NEWSPEED_STATUS] != 0x20):
            if self.status["i2c_dirty"]:
                self._i2c_release()
                rbuf = self.send_cmd(buf)

        # If fails after cleaning attempt, croak
        if (rbuf[I2C_POLL_RESP_NEWSPEED_STATUS] != 0x20):
            self.status["i2c_dirty"] = True
            raise RuntimeError("I2C speed is not valid or bus is busy.")



    def I2C_write(self, addr, data, kind = "regular", timeout_ms = 20):
        """ Write data to an address on I2C bus.

        Valid values for ``kind`` are:

            regular
                It will send **start**, *data*, **stop** (this is the default)
            restart
                It will send **repeated start**, *data*, **stop**
            nonstop
                It will send **start**, data to write, (no stop). Please note that you must use 'restart' mode to read or write after a *nonstop* write.

        Parameters:
            addr (int): I2C slave device **base** address.
            data (bytes): bytes to write. Maximum length is 65535 bytes, minimum is 1.
            kind (str, optional): kind of transfer (see description).
            timeout_ms (int, optional): maximum time to write data chunk in milliseconds (default 20 ms).
                Note this time applies for each 60 bytes chunk.
                The whole write operation may take much longer.

        Raises:
            ValueError: if any parameter is not valid.
            NotAckError: if the I2C slave didn't acknowledge.
            TimeoutError: if the writing timeout is exceeded.
            LowSDAError: if I2C engine detects the **SCL** line does not go up (read exception description).
            LowSCLError: if I2C engine detects the **SDA** line does not go up (read exception description).
            RuntimeError: if some other error occurs.

        Examples:
            >>> mcp.I2C_write(0x50, b'This is data')
            >>>

            Writing data to a non-existent device:

            >>> mcp.I2C_write(0x60, b'This is data'))
            Traceback (most recent call last):
            ...
            EasyMCP2221.exceptions.NotAckError: Device did not ACK.

        Note:
            MCP2221 writes data in 60-byte chunks.

            The default timeout of 20 ms is twice the time required to send 60 bytes at
            the minimum supported rate (47 kHz).

            MCP2221's internal I2C engine has additional timeout controls.
        """
        if addr < 0 or addr > 127:
            raise ValueError("Slave address not valid.")

        # If data length is 0, MCP2221 will do nothing at all
        if len(data) < 1:
            raise ValueError("Minimum data length is 1 byte.")
        elif len(data) > 2**16-1:
            raise ValueError("Data too long (max. 65535).")

        if kind == "regular":
            cmd = CMD_I2C_WRITE_DATA
        elif kind == "restart":
            cmd = CMD_I2C_WRITE_DATA_REPEATED_START
        elif kind == "nonstop":
            cmd = CMD_I2C_WRITE_DATA_NO_STOP
        else:
            raise ValueError("Invalid kind of transfer. Allowed: 'regular', 'restart', 'nonstop'.")

        # Try to clean last I2C error condition
        # Also test for bus confusion due to external SDA activity
        if self.status["i2c_dirty"] or self._i2c_status()["confused"]:
            self._i2c_release()

        header = [0] * 4
        header[0] = cmd
        header[1] = len(data)      & 0xFF
        header[2] = len(data) >> 8 & 0xFF
        header[3] = addr << 1      & 0xFF

        chunks = [data[i:i+I2C_CHUNK_SIZE] for i in range(0, len(data), I2C_CHUNK_SIZE)]

        # send data in 60 bytes chunks, repeating the header above
        for chunk in chunks:

            watchdog = time.perf_counter() + timeout_ms/1000

            while True:
                # Protect against infinite loop due to noise in I2C bus
                if time.perf_counter() > watchdog:
                    self._i2c_release()
                    raise TimeoutError("Timeout.")


                # Send more data when buffer is empty.
                rbuf = self.send_cmd(header + list(chunk))

                # data sent, ok, try to send next chunk
                if rbuf[RESPONSE_STATUS_BYTE] == RESPONSE_RESULT_OK:
                    break

                # data not sent, why?
                else:
                    # temporary error, try again until timeout
                    if rbuf[I2C_INTERNAL_STATUS_BYTE] in (
                        I2C_ST_WRITEDATA,
                        I2C_ST_WRITEDATA_WAITSEND,
                        I2C_ST_WRITEDATA_ACK):
                        continue

                    # internal timeout condition
                    elif rbuf[I2C_INTERNAL_STATUS_BYTE] in (
                        I2C_ST_WRITEDATA_TOUT,
                        I2C_ST_STOP_TOUT):
                        self._i2c_release()
                        raise RuntimeError("Internal I2C engine timeout.")

                    # device did not ack last transfer
                    elif rbuf[I2C_INTERNAL_STATUS_BYTE] == I2C_ST_WRADDRL_NACK_STOP:
                        self._i2c_release()
                        raise NotAckError("Device did not ACK.")

                    # after non-stop
                    elif rbuf[I2C_INTERNAL_STATUS_BYTE] == I2C_ST_WRITEDATA_END_NOSTOP:
                        self._i2c_release()
                        raise RuntimeError("You must use 'restart' mode to write after a 'nonstop' write.")

                    # something else
                    else:
                        self._i2c_release()
                        raise RuntimeError("I2C write error. Internal status %02x. Try again." %
                            (rbuf[I2C_INTERNAL_STATUS_BYTE]))

        # check final status using CMD_POLL_STATUS_SET_PARAMETERS instead another write
        watchdog = time.perf_counter() + timeout_ms/1000

        while True:
            # Protect against infinite loop due to noise in I2C bus
            if time.perf_counter() > watchdog:
                self._i2c_release()
                raise TimeoutError("Timeout.")

            i2c_status = self._i2c_status()

            if i2c_status["st"] in (I2C_ST_IDLE, I2C_ST_WRITEDATA_END_NOSTOP):
                return

            # data not sent, why?
            else:
                # temporary error, try again until timeout
                if i2c_status["st"] in (
                    I2C_ST_WRITEDATA,
                    I2C_ST_WRITEDATA_WAITSEND,
                    I2C_ST_WRITEDATA_ACK):
                    continue

                # internal timeout condition
                elif i2c_status["st"] in (
                    I2C_ST_WRITEDATA_TOUT,
                    I2C_ST_STOP_TOUT):
                    self._i2c_release()
                    raise RuntimeError("Internal I2C engine timeout.")

                # device did not ack last transfer
                elif i2c_status["st"] == I2C_ST_WRADDRL_NACK_STOP:
                    self._i2c_release()
                    raise NotAckError("Device did not ACK.")

                # after non-stop
                elif i2c_status["st"] == I2C_ST_WRITEDATA_END_NOSTOP:
                    self._i2c_release()
                    raise RuntimeError("You must use 'restart' mode to write after a 'nonstop' write.")

                # something else
                else:
                    self._i2c_release()
                    raise RuntimeError("I2C write error. Internal status %02x. Try again." %
                        (i2c_status["st"]))



    def I2C_read(self, addr, size = 1, kind = "regular", timeout_ms = 20):
        """ Read data from I2C bus.

        Valid values for ``kind`` are:

            regular
                It will send **start**, *data*, **stop** (this is the default)
            restart
                It will send **repeated start**, *data*, **stop**

        Parameters:
            addr (int): I2C slave device **base** address.
            size (int, optional): how many bytes to read. Maximum is 65535 bytes. Minimum is 1 byte.
            kind (str, optional): kind of transfer (see description).
            timeout_ms (int, optional): time to wait for the data in milliseconds (default 20 ms).
                Note this time applies for each 60 bytes chunk.
                The whole read operation may take much longer.

        Return:
            bytes: data read

        Raises:
            ValueError: if any parameter is not valid.
            NotAckError: if the I2C slave didn't acknowledge.
            TimeoutError: if the writing timeout is exceeded.
            LowSDAError: if I2C engine detects the **SCL** line does not go up (read exception description).
            LowSCLError: if I2C engine detects the **SDA** line does not go up (read exception description).
            RuntimeError: if some other error occurs.

        Examples:

            >>> mcp.I2C_read(0x50, 12)
            b'This is data'

            Write then Read without releasing the bus:

            .. code-block:: python

                >>> mcp.I2C_write(0x50, position, 'nonstop')
                >>> mcp.I2C_read(0x50, length, 'restart')
                b'En un lugar de la Mancha...'

        Hint:
            You can use :func:`I2C_read` with size 1 to check if there is any device listening
            with that address.

            There is a device in ``0x50`` (EEPROM):

            >>> mcp.I2C_read(0x50)
            b'1'

            No device in ``0x60``:

            >>> mcp.I2C_read(0x60)
            Traceback (most recent call last):
            ...
            EasyMCP2221.exceptions.NotAckError: Device did not ACK.


        Note:
            MCP2221 reads data in 60-byte chunks.

            The default timeout of 20 ms is twice the time required to receive 60 bytes at
            the minimum supported rate (47 kHz).
            If a timeout or other error occurs in the middle of character reading, the I2C may get locked.
            See :any:`LowSDAError`.
        """
        if addr < 0 or addr > 127:
            raise ValueError("Slave address not valid.")

        if size < 1:
            raise ValueError("Minimum read size is 1 byte.")
        elif size > 2**16-1:
            raise ValueError("Data too long (max. 65535).")

        if kind == "regular":
            cmd = CMD_I2C_READ_DATA
        elif kind == "restart":
            cmd = CMD_I2C_READ_DATA_REPEATED_START
        else:
            raise ValueError("Invalid kind of transfer. Allowed: 'regular' or 'restart'.")

        # Removed in order to support repeated-start operation.
        #if not self.I2C_is_idle():
        #    raise RuntimeError("I2C read error, engine is not in idle state.")

        # Try to clean last I2C error condition
        if self.status["i2c_dirty"] or self._i2c_status()["confused"]:
            self._i2c_release()

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

            self._i2c_release()

            if rbuf[I2C_INTERNAL_STATUS_BYTE] == I2C_ST_WRADDRL_NACK_STOP:
                raise NotAckError("Device did not ACK read command.")

            # after non-stop
            elif rbuf[I2C_INTERNAL_STATUS_BYTE] == I2C_ST_WRITEDATA_END_NOSTOP:
                raise RuntimeError("You must use 'restart' mode to read after a 'nonstop' write.")

            else:
                raise RuntimeError("I2C command read error. Internal status %02x. Try again." %
                    (rbuf[I2C_INTERNAL_STATUS_BYTE]))


        data = []

        watchdog = time.perf_counter() + timeout_ms/1000

        while True:
            # Protect against infinite loop due to noise in I2C bus
            if time.perf_counter() > watchdog:
                self._i2c_release()
                raise TimeoutError("Timeout.")

            # Try to read  MCP's buffer content
            rbuf = self.send_cmd([CMD_I2C_READ_DATA_GET_I2C_DATA])

            if self.debug_messages:
                print("Internal status: %02x" % (rbuf[I2C_INTERNAL_STATUS_BYTE]))

            # still reading...
            if rbuf[I2C_INTERNAL_STATUS_BYTE] in (
                I2C_ST_READDATA,
                I2C_ST_READDATA_ACK,
                I2C_ST_STOP_WAIT):
                continue

            # buffer ready, more to come
            elif rbuf[I2C_INTERNAL_STATUS_BYTE] == I2C_ST_READDATA_WAIT:
                chunk_size = rbuf[3]
                data += rbuf[4:4+chunk_size]
                # reset watchdog
                watchdog = time.perf_counter() + timeout_ms/1000
                continue

            # buffer ready, no more data expected
            elif rbuf[I2C_INTERNAL_STATUS_BYTE] == I2C_ST_READDATA_WAITGET:
                chunk_size = rbuf[3]
                data += rbuf[4:4+chunk_size]
                return bytes(data)

            elif rbuf[I2C_INTERNAL_STATUS_BYTE] == I2C_ST_WRADDRL_NACK_STOP:
                self._i2c_release()
                raise NotAckError("Device did not ACK read command.")

            else:
                self._i2c_release()
                raise RuntimeError("I2C read error. Internal status %02x." % (rbuf[I2C_INTERNAL_STATUS_BYTE]))



    def I2C_Slave(self, addr, force = False, speed = 100000, reg_bytes = 1, reg_byteorder = 'big'):
        """ Create a new I2C_Slave object.

        See :class:`EasyMCP2221.I2C_Slave.I2C_Slave` for detailed information.

        Parameters:
            addr  (int) : Slave's I2C bus address
            force (bool, optional): Create an I2C_Slave even if the target device does not answer. Default: False.
            speed (int, optional): I2C bus speed. Valid values from 50000 to 400000. See :func:`EasyMCP2221.Device.I2C_speed`.
            reg_bytes     (int, optional): How many bytes is the register, position or command to send (default 1 byte).
            reg_byteorder (str, optional): Byte order of the register address. *'little'* or *'big'*. Default 'big'.

        Return:
            I2C_Slave object.

        Example:
            >>> pcf    = mcp.I2C_Slave(0x48)
            >>> eeprom = mcp.I2C_Slave(0x50, reg_bytes = 2)
            >>> eeprom
            EasyMCP2221's I2C slave device at bus address 0x50.

        """
        return I2C_Slave.I2C_Slave(
            self,
            addr = addr,
            force = force,
            speed = speed,
            reg_bytes = reg_bytes,
            reg_byteorder = reg_byteorder)



    def _i2c_release(self):
        """ Try to make the I2C bus ready for the next operation.

        This is a private method, the **API can change** without previous notice.

        If there is an active transfer, cancel it. Try multiple times.

        Determine if the bus is ready monitoring SDA and SCL lines.

        Raises:
            LowSDAError: if **SCL** line is down (read exception description).
            LowSCLError: if **SDA** line is down (read exception description).
            RuntimeError: if multiple cancel attempts did not work. Undetermined cause.

        Note:
            Calling *Cancel* command on an uninitialized I2C engine can make it crash in 0x62 status until next reset. This function uses :func:`_i2c_status` heuristics to determine if it can issue a Cancel now or not.
        """
        i2c_status = self._i2c_status()

        # Only call a cancel command if I2C has been used already,
        # otherwise I2C will crash in 0x62 status.
        if i2c_status["initialized"]:
            buf = [0] * 3
            buf[0] = CMD_POLL_STATUS_SET_PARAMETERS
            buf[1] = 0
            buf[2] = I2C_CMD_CANCEL_CURRENT_TRANSFER

            for _ in range(3):
                rbuf = self.send_cmd(buf)
                # Cancel always return status 60. Cannot use rbuf.
                # You need to check idle status as it own.
                i2c_status = self._i2c_status()

                if (i2c_status["st"] == 0 and
                    i2c_status["sda"] == 1 and
                    i2c_status["scl"] == 1):

                    self.status["i2c_dirty"] = False
                    return

                # Otherwise, sleep and try again
                time.sleep(10/1000)

        i2c_status = self._i2c_status()

        if (i2c_status["st"] == 0 and
            i2c_status["sda"] == 1 and
            i2c_status["scl"] == 1):

            self.status["i2c_dirty"] = False
            return True

        if i2c_status["scl"] == 0:
            self.status["i2c_dirty"] = True
            raise LowSCLError("SCL is low. I2C bus is busy or missing pull-up resistor.")

        if i2c_status["sda"] == 0:
            self.status["i2c_dirty"] = True
            raise LowSDAError("SDA is low. Missing pull-up resistor, I2C bus is busy or slave device in the middle of sending data.")

        self.status["i2c_dirty"] = True
        raise RuntimeError("Unable to cancel. I2C crashed.")


    def _i2c_status(self):
        """ Return I2C status based on POLL_STATUS_SET_PARAMETERS command.

        This is a private method, the **API could change** without previous notice.

        Returns:
            Dictionary with I2C internal details.

            .. code-block:: text

                {
                  'rlen' : 65,  <- Value of the requested I2C transfer length
                  'txlen': 0,   <- Value of the already transferred (through I2C) number of bytes
                  'div'  : 118, <- Current I2C communication speed divider value
                  'ack'  : 0,   <- If ACK was received from client value is 0, else 1.
                  'st'   : 98,  <- Internal state of I2C status machine
                  'scl'  : 1,   <- SCL line value as read from the pin
                  'sda'  : 0,   <- SDA line value as read from the pin
                  'confused': False,   <- see note
                  'initialized': True  <- see note
                }


        Hint:
            If your project does not use I2C, you could reuse SCL and SDA as digital inputs. Call this method to get its logic value.

        Note:
            About **confused** status.

                For some reason, ticking SDA line while I2C bus is initialized but idle will cause the next transfer to be bogus. To prevent this, you need to issue a Cancel command before the next *read* or *write* command.

                Unfortunately, there is no official way to determine that we are in this situation. The only byte that changes when it happens seems to be byte 18, which is *not documented*.

            About **initialized** status:

                Same way, calling cancel when the I2C engine has not been used yet will make it to stall and stay in status ``0x62`` until next reset.

                Unfortunately, there is no official way to determine when it is appropriate to call *Cancel* and when it's not. Moreover, MCP2221's I2C status after a reset is different from MCP2221A's (the last one clears the *last transfer length* and the former does not). I found that Cancel fails when byte 21 is ``0x00`` and works when it is ``0x60``. This is, again, *not documented*.

        """
        rbuf = self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])
        i2c_status = {
            "rlen" : (rbuf[I2C_POLL_RESP_REQ_LEN_H] << 8) + rbuf[I2C_POLL_RESP_REQ_LEN_L],
            "txlen": (rbuf[I2C_POLL_RESP_TX_LEN_H]  << 8) + rbuf[I2C_POLL_RESP_TX_LEN_L],

            "div" : rbuf[I2C_POLL_RESP_CLKDIV],

            "ack" : rbuf[I2C_POLL_RESP_ACK] & (1 << 6),
            "st"  : rbuf[I2C_POLL_RESP_STATUS],
            "scl" : rbuf[I2C_POLL_RESP_SCL],
            "sda" : rbuf[I2C_POLL_RESP_SDA],


            # Meaning of this byte might be:
            #   0x00 -> unused bus yet
            #   0x08 -> sda activity detected ? (also is normal after nonstop write)
            #   0x10 -> ok
            "confused" : (
                rbuf[I2C_POLL_RESP_UNDOCUMENTED_18] == 8 and
                rbuf[I2C_POLL_RESP_STATUS]         != I2C_ST_WRITEDATA_END_NOSTOP ),

            # Determine if you can call cancel or not.
            "initialized" : rbuf[I2C_POLL_RESP_UNDOCUMENTED_21] != 0
        }

        return i2c_status


    #######################################################################
    # Wake-up
    #######################################################################
    def enable_power_management(self, enable=True):
        """ Enable or disable USB Power Management options for this device.

        Set or clear Remote Wake-up Capability bit.
        Remember to call :func:`save_config` after this function to save the new settings.

        Remote wake-up is triggered by Interrupt detection on GP1
        (see :func:`set_pin_function` and :func:`IOC_config`).

        When enabled, Power Management Tab is available for this device in the Device Manager (Windows).
        To wake-up the computer *"Allow this device to wake the computer"* option must be set in Device Manager.

        USB power attributes are only read while USB device enumeration. So :func:`reset`
        (or power supply cycle) is needed in order for changes to take effect.

        Parameters:
            enable (bool): Enable or disable Power Management.

        Raises:
            RuntimeError: If flash read command failed.

        Example:
            >>> mcp.enable_power_management(True)
            >>> mcp.save_config()
            >>> print(mcp)
            ...
                "Chip settings": {
                    "Power management options": "enabled",
            ...
            >>> mcp.reset()
        """
        chip_settings = self._read_flash_raw(FLASH_DATA_CHIP_SETTINGS)
        USBPWRATTR = chip_settings[FLASH_CHIP_SETTINGS_USBPWR + FLASH_OFFSET_READ]

        if enable:
            USBPWRATTR |= 0b00100000
        else:
            USBPWRATTR &= 0b11011111

        self.unsaved_SRAM[FLASH_CHIP_SETTINGS_USBPWR] = USBPWRATTR


    #######################################################################
    # Reset
    #######################################################################
    def reset(self):
        """ Reset MCP2221.

        Reboot the device and load stored configuration from flash.

        This operation do not reset any I2C slave devices.

        Note:
            The host needs to re-enumerate the device after a reset command.
            There is a 5 seconds timeout to do that.
        """
        buf = [0] * 4
        buf[0] = CMD_RESET_CHIP
        buf[1] = RESET_CHIP_SURE
        buf[2] = RESET_CHIP_VERY_SURE
        buf[3] = RESET_CHIP_VERY_VERY_SURE
        self.send_cmd(buf)
        time.sleep(0.5)

        self.status["i2c_dirty"] = False
        self.__init__()


    #######################################################################
    # Hardware and firmware revision
    #######################################################################
    def revision(self):
        """ Get the hardware and firmware revision number.

        Return:
            dict: Value of mayor and minor revisions of hardware and software.

        Example:
            >>> mcp.revision()
            {'firmware': {'mayor': 'A', 'minor': '6'},
            'hardware': {'mayor': '1', 'minor': '2'}}
        """
        buf = self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])

        data = {
            "firmware": {
                "mayor": chr(buf[I2C_POLL_RESP_HARD_MAYOR]),
                "minor": chr(buf[I2C_POLL_RESP_HARD_MINOR]),
            },
            "hardware": {
                "mayor": chr(buf[I2C_POLL_RESP_FIRM_MAYOR]),
                "minor": chr(buf[I2C_POLL_RESP_FIRM_MINOR]),
            }
        }

        return data
