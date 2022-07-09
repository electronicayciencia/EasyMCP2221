#############################################################
#    MIT License                                            #
#    Copyright (c) 2017 Yuta KItagami                       #
#############################################################

import hid
# import hid
# pip install hidapi
# https://github.com/trezor/cython-hidapi
import time
import os

DEV_DEFAULT_VID = 0x04D8
DEV_DEFAULT_PID = 0x00DD

PACKET_SIZE = 64
DIR_OUTPUT  = 0
DIR_INPUT   = 1

# Commands
CMD_POLL_STATUS_SET_PARAMETERS    = 0x10
CMD_SET_GPIO_OUTPUT_VALUES        = 0x50
CMD_GET_GPIO_VALUES               = 0x51
CMD_SET_SRAM_SETTINGS             = 0x60
CMD_GET_SRAM_SETTINGS             = 0x61
CMD_I2C_READ_DATA_GET_I2C_DATA    = 0x40
CMD_I2C_WRITE_DATA                = 0x90
CMD_I2C_READ_DATA                 = 0x91
CMD_I2C_WRITE_DATA_REPEATED_START = 0x92
CMD_I2C_READ_DATA_REPEATED_START  = 0x93
CMD_I2C_WRITE_DATA_NO_STOP        = 0x94
CMD_READ_FLASH_DATA               = 0xB0
CMD_WRITE_FLASH_DATA              = 0xB1
CMD_SEND_FLASH_ACCESS_PASSWORD    = 0xB2
CMD_RESET_CHIP                    = 0x70

RESPONSE_RESULT_OK = 0
RESPONSE_ECHO_BYTE   = 0
RESPONSE_STATUS_BYTE = 1

# Flash data constants
FLASH_DATA_CHIP_SETTINGS          = 0x00
FLASH_DATA_GP_SETTINGS            = 0x01
FLASH_DATA_USB_MANUFACTURER       = 0x02
FLASH_DATA_USB_PRODUCT            = 0x03
FLASH_DATA_USB_SERIALNUM          = 0x04
FLASH_DATA_CHIP_SERIALNUM         = 0x05

# GPIO constants
GPIO_GP0 = 0
GPIO_GP1 = 1
GPIO_GP2 = 2
GPIO_GP3 = 3

ALTER_GPIO_CONF    = 1 << 7 # bit 7: alters the current GP designation
PRESERVE_GPIO_CONF = 0 << 7
GPIO_OUT_VAL_1  = 1 << 4
GPIO_OUT_VAL_0  = 0 << 4
GPIO_DIR_IN     = 1 << 3
GPIO_DIR_OUT    = 0 << 3
GPIO_FUNC_GPIO  = 0b000
GPIO_FUNC_DEDICATED = 0b001
GPIO_FUNC_ALT_0  = 0b010
GPIO_FUNC_ALT_1  = 0b011
GPIO_FUNC_ALT_2  = 0b100
GPIO_FUNC_ADC = GPIO_FUNC_ALT_0
GPIO_FUNC_DAC = GPIO_FUNC_ALT_1


ALTER_INT_CONF    = 1 << 7 # Enable the modification of the interrupt detection conditions
PRESERVE_INT_CONF = 0 << 7
INT_POS_EDGE_ENABLE  = 0b11 << 3
INT_POS_EDGE_DISABLE = 0b10 << 3
INT_NEG_EDGE_ENABLE  = 0b11 << 1
INT_NEG_EDGE_DISABLE = 0b10 << 1
INT_FLAG_CLEAR    = 1
INT_FLAG_PRESERVE = 0

ALTER_ADC_REF    = 1 << 7 # Enable loading of a new ADC reference
PRESERVE_ADC_REF = 0 << 7
ADC_VRM_OFF  = 0b00 << 1
ADC_VRM_1024 = 0b01 << 1
ADC_VRM_2048 = 0b10 << 1
ADC_VRM_4096 = 0b11 << 1
ADC_REF_VRM  = 1
ADC_REF_VDD  = 0

ALTER_DAC_REF    = 1 << 7 # Enable loading of a new DAC reference
PRESERVE_DAC_REF = 0 << 7
DAC_VRM_OFF  = 0b00 << 1
DAC_VRM_1024 = 0b01 << 1
DAC_VRM_2048 = 0b10 << 1
DAC_VRM_4096 = 0b11 << 1
DAC_REF_VRM  = 1
DAC_REF_VDD  = 0

ALTER_DAC_VALUE    = 1 << 7 # Enable loading of a new DAC value
PRESERVE_DAC_VALUE = 0 << 7

ALTER_CLK_OUTPUT    = 1 << 7 # Enable loading of a new clock divider
PRESERVE_CLK_OUTPUT = 0 << 7
CLK_DUTY_0  = 0b00 << 3
CLK_DUTY_25 = 0b01 << 3
CLK_DUTY_50 = 0b10 << 3
CLK_DUTY_75 = 0b11 << 3
CLK_DIV_1 = 0b001
CLK_DIV_2 = 0b010
CLK_DIV_3 = 0b011
CLK_DIV_4 = 0b100
CLK_DIV_5 = 0b101
CLK_DIV_6 = 0b110
CLK_DIV_7 = 0b111
CLK_FREQ_375kHz = CLK_DIV_7
CLK_FREQ_750kHz = CLK_DIV_6
CLK_FREQ_1_5MHz = CLK_DIV_5
CLK_FREQ_3MHz   = CLK_DIV_4
CLK_FREQ_6MHz   = CLK_DIV_3
CLK_FREQ_12MHz  = CLK_DIV_2
CLK_FREQ_24MHz  = CLK_DIV_1

I2C_CMD_CANCEL_CURRENT_TRANSFER = 0x10
I2C_CMD_SET_BUS_SPEED = 0x20

RESET_CHIP_SURE           = 0xAB
RESET_CHIP_VERY_SURE      = 0xCD
RESET_CHIP_VERY_VERY_SURE = 0xEF


class PyMCP2221A:
    def __init__(self, VID = DEV_DEFAULT_VID, PID = DEV_DEFAULT_PID, devnum=0):
        self.debug_packets = False
        self.mcp2221a = hid.device()
        self.mcp2221a.open_path(hid.enumerate(VID, PID)[devnum]["path"])


    def send_cmd(self, buf, sleep = 0):
        """
        Write a USB command.
        buf: bytes to write
        sleep: delay (senconds) between writing the command and reading the response.
        """
        if self.debug_packets:
            print(buf)

        REPORT_NUM = 0x00
        padding = [0x00] * (PACKET_SIZE - len(buf))
        self.mcp2221a.write([REPORT_NUM] + buf + padding)

        time.sleep(sleep)

        if buf[0] == CMD_RESET_CHIP:
            return None

        r = self.mcp2221a.read(PACKET_SIZE)

        if self.debug_packets:
            print(r)

        return r


    #######################################################################
    # HID DeviceDriver Info
    #######################################################################
    def DeviceDriverInfo(self):
        print("Manufacturer: %s" % self.mcp2221a.get_manufacturer_string())
        print("Product: %s" % self.mcp2221a.get_product_string())
        print("Serial No: %s" % self.mcp2221a.get_serial_number_string())


    #######################################################################
    # Read Flash Data
    #######################################################################
    def Read_Flash_Data(self):

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

        data[USB_VENDOR_STR]      = self.parse_wchar_structure(data[USB_VENDOR_STR])
        data[USB_PRODUCT_STR]     = self.parse_wchar_structure(data[USB_PRODUCT_STR])
        data[USB_SERIAL_STR]      = self.parse_wchar_structure(data[USB_SERIAL_STR])
        data[USB_FACT_SERIAL_STR] = self.parse_factory_serial(data[USB_FACT_SERIAL_STR])
        data[CHIP_SETTINGS_STR]   = self.parse_chip_settings_struct(data[CHIP_SETTINGS_STR])
        data[GP_SETTINGS_STR]     = self.parse_gp_settings_struct(data[GP_SETTINGS_STR])

        return data

    def parse_wchar_structure(self, buf):
        cmd_echo  = buf[RESPONSE_ECHO_BYTE]
        cmd_error = buf[RESPONSE_STATUS_BYTE]
        strlen    = buf[2] - 2
        three     = buf[3]
        w_str     = buf[4:4+strlen]
        str = bytes(w_str).decode('utf-16')
        return str

    def parse_factory_serial(self, buf):
        cmd_echo  = buf[RESPONSE_ECHO_BYTE]
        cmd_error = buf[RESPONSE_STATUS_BYTE]
        strlen    = buf[2]
        three     = buf[3]
        str       = buf[4:4+strlen]
        str = bytes(str).decode('ascii')
        return str

    def parse_chip_settings_struct(self, buf):
        data = {
            "USB VID": "0x{:02X}{:02X}".format(buf[9], buf[8]),
            "USB PID": "0x{:02X}{:02X}".format(buf[11], buf[10]) ,
            "USB requested number of mA": buf[13] * 2,
            "raw": buf[0:14],
        }
        return data

    def parse_gp_settings_struct(self, buf):
        data = {
            "raw": buf[0:7]
        }
        return data


   #######################################################################
    # Write Flash Data
    #######################################################################

    def Write_Flash_Data(self, data):
        """
        Unimplemented.
        """
        pass


    def GPIO_Config(self,
        clk_output = None,
        dac_ref    = None,
        dac_value  = None,
        adc_ref    = None,
        int_conf   = None,
        gp0        = None,
        gp1        = None,
        gp2        = None,
        gp3        = None):
        """
        Configure Runtime GPIO pins and parameters.
        This function unexpectedly resets:
            GPIO values set via CMD_SET_GPIO_OUTPUT_VALUES.
            Vrm (not affected if ref = VDD)
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

        self.send_cmd(cmd)


    #######################################################################
    # GPIO commands
    #######################################################################
    def GPIO_Input(self, pin):
        """
        Set pin as GPIO Input.
        Accepted values for pin are 'GP0', 'GP1', 'GP2' or 'GP3'.
        This function uses SET_SRAM_SETTINGS command instead of SET_GPIO_OUTPUT_VALUES.
        """
        if pin == "GP0":
            self.GPIO_Config(gp0 = GPIO_FUNC_GPIO | GPIO_DIR_IN)
        elif pin == "GP1":
            self.GPIO_Config(gp1 = GPIO_FUNC_GPIO | GPIO_DIR_IN)
        elif pin == "GP2":
            self.GPIO_Config(gp2 = GPIO_FUNC_GPIO | GPIO_DIR_IN)
        elif pin == "GP3":
            self.GPIO_Config(gp3 = GPIO_FUNC_GPIO | GPIO_DIR_IN)
        else:
            raise ValueError("Accepted values for pin are 'GP0', 'GP1', 'GP2' or 'GP3'.")


    def GPIO_Output(self, pin, value):
        """
        Set pin as GPIO Output with a value.
        Accepted values for pin are 'GP0', 'GP1', 'GP2' or 'GP3'.
        Value could be True or False.
        This function uses SET_SRAM_SETTINGS command instead of SET_GPIO_OUTPUT_VALUES.
        """
        if value:
            val = GPIO_OUT_VAL_1
        else:
            val = GPIO_OUT_VAL_0

        if pin == "GP0":
            self.GPIO_Config(gp0 = GPIO_FUNC_GPIO | GPIO_DIR_OUT | val)
        elif pin == "GP1":
            self.GPIO_Config(gp1 = GPIO_FUNC_GPIO | GPIO_DIR_OUT | val)
        elif pin == "GP2":
            self.GPIO_Config(gp2 = GPIO_FUNC_GPIO | GPIO_DIR_OUT | val)
        elif pin == "GP3":
            self.GPIO_Config(gp3 = GPIO_FUNC_GPIO | GPIO_DIR_OUT | val)
        else:
            raise ValueError("Accepted values for pin are 'GP0', 'GP1', 'GP2' or 'GP3'.")


    def GPIO_FastSetAsInput(self,
        gp0 = None,
        gp1 = None,
        gp2 = None,
        gp3 = None):
        """
        Define a pin as an input but not writes to SRAM.
        Any call to GPIO_Conf to configure any other pins will reset this settings.
        """

        ALTER_DIRECTION = 1
        PRESERVE_DIRECTION = 0
        GPIO_ERROR = 0xEE

        buf = [0] * 18
        buf[0]  = CMD_SET_GPIO_OUTPUT_VALUES
        buf[4]  = PRESERVE_DIRECTION if gp0 is None else ALTER_DIRECTION
        buf[5]  = gp0 or 0
        buf[8]  = PRESERVE_DIRECTION if gp1 is None else ALTER_DIRECTION
        buf[9]  = gp1 or 0
        buf[12] = PRESERVE_DIRECTION if gp2 is None else ALTER_DIRECTION
        buf[13] = gp2 or 0
        buf[16] = PRESERVE_DIRECTION if gp3 is None else ALTER_DIRECTION
        buf[17] = gp3 or 0

        r = self.send_cmd(buf)

        if gp0 is not None and r[4] == GPIO_ERROR:
            raise RuntimeError("Pin GP0 is not assigned to GPIO function.")
        elif gp1 is not None and r[8] == GPIO_ERROR:
            raise RuntimeError("Pin GP1 is not assigned to GPIO function.")
        elif gp2 is not None and r[12] == GPIO_ERROR:
            raise RuntimeError("Pin GP2 is not assigned to GPIO function.")
        elif gp3 is not None and r[16] == GPIO_ERROR:
            raise RuntimeError("Pin GP3 is not assigned to GPIO function.")


    def GPIO_FastSetValue(self,
        gp0 = None,
        gp1 = None,
        gp2 = None,
        gp3 = None):
        """
        Set pin output values but not write it to SRAM.
        Any call to GPIO_Conf to configure any other pins will reset this settings.
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


    def GPIO_Read(self):
        """
        Read all GPIO pins and return a tuple (gp0, gp1, gp2, gp3).
        Value is None if that pin is not set for GPIO operation.
        """

        r = self.send_cmd([CMD_GET_GPIO_VALUES])
        gp0 = r[2] if r[2] != 0xEE else None
        gp1 = r[4] if r[4] != 0xEE else None
        gp2 = r[6] if r[6] != 0xEE else None
        gp3 = r[8] if r[8] != 0xEE else None

        return (gp0, gp1, gp2, gp3)

    #######################################################################
    # CLOCK
    #######################################################################
    def Clock_Channel(self, pin = "GP1"):
        """
        Configure pin as clock output channel.
        pin valid values is only "GP1".
        """
        if pin == "GP1":
            self.GPIO_Config(gp1 = GPIO_FUNC_DEDICATED)
        else:
            raise ValueError("Accepted values for pin is only 'GP1'.")


    def Clock_Config(self, duty, freq):
        """
        Configure the clock output.
        Duty valid values are 0, 25, 50, 75.
        Freq is one of 375kHz, 750kHz, 1.5MHz, 3MHz, 6MHz, 12MHz or 24MHz.
        To output clock signal, you also need to set GP1 function to GPIO_FUNC_DEDICATED.
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

        self.GPIO_Config(clk_output = duty | div)


    #######################################################################
    # ADC
    #######################################################################
    def ADC_Channel(self, pin):
        """
        Configure pin as an analog input channel.
        pin valid values are "GP1", "GP2" and "GP3".
        """
        if pin == "GP1":
            self.GPIO_Config(gp1 = GPIO_FUNC_ADC)
        elif pin == "GP2":
            self.GPIO_Config(gp2 = GPIO_FUNC_ADC)
        elif pin == "GP3":
            self.GPIO_Config(gp3 = GPIO_FUNC_ADC)
        else:
            raise ValueError("Accepted values for pin are 'GP1', 'GP2' or 'GP3'.")


    def ADC_Config(self, ref):
        """
        Configure ADC reference.
        ref valid values are "0", "1.024V", "2.048V", "4.096V" and "VDD".
        You also need to set GP2/3 function to GPIO_FUNC_ADC using ADC_Channel.
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

        self.GPIO_Config(adc_ref = ref | vrm)


    def ADC_Read(self):
        """
        Read all 3 ADC and return a tuple (gp1, gp2, gp3).
        Each value is 10 bit (0 to 1023).
        Analog value is read regardless of pin funcion.
        """
        buf = self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])
        adc1 = buf[50] + 256*buf[51]
        adc2 = buf[52] + 256*buf[53]
        adc3 = buf[54] + 256*buf[55]
        return (adc1, adc2, adc3)


    #######################################################################
    # DAC
    #######################################################################
    def DAC_Channel(self, pin):
        """
        Configure DAC pin to use.
        pin valid values are "GP2" and "GP3"
        """
        if pin == "GP2":
            self.GPIO_Config(gp2 = GPIO_FUNC_DAC)
        elif pin == "GP3":
            self.GPIO_Config(gp3 = GPIO_FUNC_DAC)
        else:
            raise ValueError("Accepted values for pin are 'GP2' and 'GP3'.")


    def DAC_Config(self, ref, out = 0):
        """
        Configure DAC reference.
        ref valid values are "0", "1.024V", "2.048V", "4.096V" and "VDD".
        out valid values are from 0 to 31.
        To output DAC, you also need to set GP2/3 function to GPIO_FUNC_DAC using DAC_Channel.
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

        if out < 0 or out > 31:
            raise ValueError("Accepted values for out are from 0 to 31.")

        self.GPIO_Config(
            dac_ref = ref | vrm,
            dac_value = out)


    def DAC_Write(self, out):
        """
        Configure DAC output.
        out valid values are from 0 to 31.
        To output DAC, you also need to set GP2/3 function to GPIO_FUNC_ALT_1.
        """

        if out < 0 or out > 31:
            raise ValueError("Accepted values for out are from 0 to 31.")

        self.GPIO_Config(dac_value = out)


    #######################################################################
    # I2C
    #######################################################################
    def I2C_Led(self):
        """
        Set GP3 to indicate I2C activity.
        """
        self.GPIO_Config(gp3 = GPIO_FUNC_DEDICATED)


    def I2C_Speed(self, speed=100000):
        """
        Set I2C bus speed.
        Default bus speed is 100kHz.
        Acceptable values for speed are between 47kHz and 400kHz.
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


    def I2C_Idle(self):
        """
        Check bus idle state.
        Return True if idle, False if timeout detected.
        """
        rbuf = self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])

        if rbuf[8]:
            return False
        else:
            return True


    def I2C_Cancel(self):
        """
        Send Cancel Current Transfer command to I2C engine.
        Return true if success and I2C is in idle state.
        """
        buf = [0] * 3
        buf[0] = CMD_POLL_STATUS_SET_PARAMETERS
        buf[1] = 0
        buf[2] = I2C_CMD_CANCEL_CURRENT_TRANSFER

        # More than one time is needed to clear timeout status.
        # And device half writing.
        rbuf = self.send_cmd(buf, sleep = 0.1)
        rbuf = self.send_cmd(buf, sleep = 0.1)

        if (rbuf[22] == 0):
            raise RuntimeError("SCL is low. I2C bus is busy or missing pull-up resistor.")

        if (rbuf[23] == 0):
            raise RuntimeError("SDA is low. I2C bus is busy or missing pull-up resistor.")

        return self.I2C_Idle()


    def I2C_Write(self, addr, data, kind = "regular"):
        """
        Writes a block of data on I2C bus.
        addr: I2C slave device base address
        data: bytes to write (max length 65536)
        kind: one of
          regular: start - data to write - stop
          restart: repeated start - data to write - stop
          nonstop: start - data to write
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
                #time.sleep(1e-6)
                pass

        if r[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
            self.I2C_Cancel()
            raise RuntimeError("I2C write error: device NAK.")


    def _i2c_buffer_counter(self):
        """
        Get the internal databuffer counter.
        Useful to know when to send more data.
        """
        return self.send_cmd([CMD_POLL_STATUS_SET_PARAMETERS])[13]



    #######################################################################
    # I2C Read
    #######################################################################
    def I2C_Read(self, addr, size, kind = "regular", timeout_ms = 10):
        """
        Read data from I2C bus.
        addr: I2C slave device base address
        size: Read this number of bytes (max. 65536).
        kind: one of
          regular: start - read data - stop
          restart: repeated start - read data - stop
        timeout_ms: time to retrieve data in milliseconds
        return bytes read
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

        if not self.I2C_Idle():
            raise RuntimeError("I2C read error, engine is not in idle state.")

        buf = [0] * 4
        buf[0] = cmd
        buf[1] = size      & 0xFF
        buf[2] = size >> 8 & 0xFF
        buf[3] = (addr << 1 & 0xFF) + 1  # address for read operation

        # Send read command to i2c bus. Read bus data into a buffer (until 60 bytes).
        rbuf = self.send_cmd(buf)
        if rbuf[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
            self.I2C_Cancel()
            raise RuntimeError("I2C command read error.")

        data = []
        while len(data) < size:
            time.sleep(timeout_ms/1000)
            
            # Retrieve data from buffer
            # This command must be issued after all bytes have arrived.
            rbuf = self.send_cmd([CMD_I2C_READ_DATA_GET_I2C_DATA])
            
            if rbuf[RESPONSE_STATUS_BYTE] != RESPONSE_RESULT_OK:
                self.I2C_Cancel()
                raise RuntimeError("I2C command read data timeout or device not ready. Try increasing timeout_ms.")

            else:
                chunk_size = rbuf[3]
                data += rbuf[4:4+chunk_size]
            
        return bytes(data)


    #######################################################################
    # UART
    #######################################################################
    def UART_RX_Led(self):
        """
        Set GP0 to indicate UART RX activity.
        """
        self.GPIO_Config(gp0 = GPIO_FUNC_ALT_0)


    def UART_TX_Led(self):
        """
        Set GP1 to indicate UART TX activity.
        """
        self.GPIO_Config(gp1 = GPIO_FUNC_ALT_1)


    #######################################################################
    # USB INTERRUPTIONS
    #######################################################################
    def USB_Config_Led(self):
        """
        Set GP2 to indicate USB device configured status.
        """
        self.GPIO_Config(gp2 = GPIO_FUNC_DEDICATED)


    #######################################################################
    # reset
    #######################################################################
    def Reset(self):
        """
        Reset device.
        """
        buf = [0] * 4
        buf[0] = CMD_RESET_CHIP
        buf[1] = RESET_CHIP_SURE
        buf[2] = RESET_CHIP_VERY_SURE
        buf[3] = RESET_CHIP_VERY_VERY_SURE
        self.send_cmd(buf, sleep = 1)

        self.__init__()

