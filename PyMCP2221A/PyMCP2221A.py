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

PACKET_SIZE_65 = 65 # for compile_packet function

PACKET_SIZE = 64
DIR_OUTPUT  = 0
DIR_INPUT   = 1

CMD_STATUS_SET_PARAMETERS         = 0x10
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

FLASH_DATA_CHIP_SETTINGS          = 0x00
FLASH_DATA_GP_SETTINGS            = 0x01
FLASH_DATA_USB_MANUFACTURER       = 0x02
FLASH_DATA_USB_PRODUCT            = 0x03
FLASH_DATA_USB_SERIALNUM          = 0x04
FLASH_DATA_CHIP_SERIALNUM         = 0x05


class PyMCP2221A:
    def __init__(self, VID = DEV_DEFAULT_VID, PID = DEV_DEFAULT_PID, devnum=0):
        self.CLKDUTY_0  = 0x00
        self.CLKDUTY_25 = 0x08
        self.CLKDUTY_50 = 0x10
        self.CLKDUTY_75 = 0x18

        # self.CLKDIV_1 = 0x00    # 48MHz  Dont work.
        self.CLKDIV_2   = 0x01  # 24MHz
        self.CLKDIV_4   = 0x02  # 12MHz
        self.CLKDIV_8   = 0x03  # 6MHz
        self.CLKDIV_16  = 0x04  # 3MHz
        self.CLKDIV_32  = 0x05  # 1.5MHz
        self.CLKDIV_64  = 0x06  # 750KHz
        self.CLKDIV_128 = 0x07  # 375KHz

        self.mcp2221a = hid.device()
        self.mcp2221a.open_path(hid.enumerate(VID, PID)[devnum]["path"])


    # Obsolete
    def compile_packet(self, buf):
        """
        :param list buf:
        """
        assert len(buf) <= PACKET_SIZE_65

        buf = buf + [0 for i in range(PACKET_SIZE_65 - len(buf))]
        return buf


    def send_cmd(self, buf):
        REPORT_NUM = 0x00
        padding = [0x00] * (PACKET_SIZE - len(buf))
        self.mcp2221a.write([REPORT_NUM] + buf + padding)
        
        if buf[0] == CMD_RESET_CHIP:
            return none
        else:
            return self.mcp2221a.read(PACKET_SIZE)


    #######################################################################
    # HID DeviceDriver Info
    #######################################################################
    def DeviceDriverInfo(self):
        print("Manufacturer: %s" % self.mcp2221a.get_manufacturer_string())
        print("Product: %s" % self.mcp2221a.get_product_string())
        print("Serial No: %s" % self.mcp2221a.get_serial_number_string())

    #######################################################################
    # Command Structure
    #######################################################################
    def Command_Structure(self, I2C_Cancel_Bit, I2C_Speed_SetUp_Bit, I2C_Speed_SetVal_Byte):
        I2C_Cancel_Bit = 0
        I2C_Speed_SetUp_Bit = 0
        I2C_Speed_SetVal_Byte = 0
        buf = self.compile_packet([0x00, CMD_STATUS_SET_PARAMETERS, 0x00,
                                   I2C_Cancel_Bit << 4,
                                   I2C_Speed_SetUp_Bit << 5,
                                   I2C_Speed_SetVal_Byte])

        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

        print(chr(buf[46]))
        print(chr(buf[47]))
        print(chr(buf[48]))
        print(chr(buf[49]))

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
        cmd_echo  = buf[0]
        cmd_error = buf[1]
        strlen    = buf[2] - 2
        three     = buf[3]
        w_str     = buf[4:4+strlen]
        str = bytes(w_str).decode('utf-16')
        return str
        
    def parse_factory_serial(self, buf):
        cmd_echo  = buf[0]
        cmd_error = buf[1]
        strlen    = buf[2]
        three     = buf[3]
        str       = buf[4:4+strlen]
        str = bytes(str).decode('ascii')
        return str

    def parse_chip_settings_struct(self, buf):
        # "CDC serial number enumeration enable"
        # "Chip configuration security"
        # "Clock output divider value"
        # "DAC reference voltage"
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
        pass
        # Write_Deta_Setting_Byte = 0x00
        # Write_Chip_Settings             = 0x00
        # Write_GP_Settings               = 0x01
        # Write_USB_Manufacturer_Settings = 0x02
        # Write_USB_Product_Settings      = 0x03
        # Write_USB_SerialNum_Settings    = 0x04
        # buf = [0x00,0xB1,Write_Deta_Setting_Byte]
        # buf = buf + [0 for i in range(PACKET_SIZE_65-len(buf))]
        # !!!! Be careful when making changes !!!!
        # buf[6+1] =  0xD8    # VID (Lower)
        # buf[7+1] =  0x04    # VID (Higher)
        # buf[8+1] =  0xDD    # PID (Lower)
        # buf[9+1] =  0x00    # PID (Higher)

        # print ("Write")
        # print (buf)
        # h.write(buf)
        # buf = h.read(PACKET_SIZE_65)
        # print ("Read")
        # print (buf)

    #######################################################################
    # GPIO Init
    #######################################################################
    def GPIO_Init(self):
        buf = self.compile_packet([0x00, CMD_GET_SRAM_SETTINGS])
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)

        buf = self.compile_packet([0x00, CMD_SET_SRAM_SETTINGS])
        buf[2 + 1] = rbuf[5]  # Clock Output Divider value
        buf[3 + 1] = rbuf[6]  # DAC Voltage Reference
        buf[4 + 1] = 0x00  # Set DAC output value
        buf[5 + 1] = 0x00  # ADC Voltage Reference
        # buf[6+1] = 0x00     #   Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0x80  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80

        self.GPIO_0_BIT = (rbuf[22 + 1] >> 4) & 0x01  # 1:Hi 0:LOW
        self.GPIO_0_DIR = (rbuf[22 + 1] >> 3) & 0x01  # 0:OutPut 1:Input
        self.GPIO_0_MODE = rbuf[22 + 1] & 0x07  # GPIO MODE = 0x00
        self.GPIO_1_BIT = (rbuf[23 + 1] >> 4) & 0x01  # 1:Hi 0:LOW
        self.GPIO_1_DIR = (rbuf[23 + 1] >> 3) & 0x01  # 0:OutPut 1:Input
        self.GPIO_1_MODE = rbuf[23 + 1] & 0x07  # GPIO MODE = 0x00
        self.GPIO_2_BIT = (rbuf[24 + 1] >> 4) & 0x01  # 1:Hi 0:LOW
        self.GPIO_2_DIR = (rbuf[24 + 1] >> 3) & 0x01  # 0:OutPut 1:Input
        self.GPIO_2_MODE = rbuf[24 + 1] & 0x07  # GPIO MODE = 0x00
        self.GPIO_3_BIT = (rbuf[25 + 1] >> 4) & 0x01  # 1:Hi 0:LOW
        self.GPIO_3_DIR = (rbuf[25 + 1] >> 3) & 0x01  # 0:OutPut 1:Input
        self.GPIO_3_MODE = rbuf[25 + 1] & 0x07  # GPIO MODE = 0x00

        # for(i in range(64)):
        #    buf[i] = rbuf[i] | buf[i]
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

    #######################################################################
    # GPIO Set Direction and Set Value commands
    #######################################################################
    def GPIO_SetDirection(self, pin, direction):

        buf = self.compile_packet([0x00, CMD_SET_GPIO_OUTPUT_VALUES])
        offset = (pin + 1) * 4
        buf[offset + 1] = 0x01  # set pin direction
        buf[offset + 1 + 1] = direction  # to this
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)
        if rbuf[1] != 0x00:
            raise RuntimeError("GPIO_SetDirection Failed")

    def GPIO_SetValue(self, pin, value):

        buf = self.compile_packet([0x00, CMD_SET_GPIO_OUTPUT_VALUES])
        offset = ((pin + 1) * 4) - 1
        buf[offset - 1 + 1] = 0x01  # set pin value
        buf[offset + 1] = value  # to this
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)
        if rbuf[1] != 0x00:
            raise RuntimeError("GPIO_SetValue Failed")

    #######################################################################
    # Read GPIO Data command
    #######################################################################
    def GPIO_Read(self):

        buf = self.compile_packet([0x00, CMD_GET_GPIO_VALUES])
        self.mcp2221a.write(buf)

        buf = self.mcp2221a.read(PACKET_SIZE_65)
        self.GPIO_0_INPUT = buf[2]
        self.GPIO_0_DIR = buf[3]
        self.GPIO_1_INPUT = buf[4]
        self.GPIO_1_DIR = buf[5]
        self.GPIO_2_INPUT = buf[6]
        self.GPIO_2_DIR = buf[7]
        self.GPIO_3_INPUT = buf[8]
        self.GPIO_3_DIR = buf[9]
        return buf

    # Return the GPIO value as an integer instead of tuple
    def GPIO_GetValue(self, pin):
        rbuf = self.GPIO_Read()
        offset = (pin + 1) * 2
        if rbuf[offset] == 0xEE:
            raise RuntimeError("GPIO_GetValue Failed, pin is not set for GPIO operation")
        return rbuf[offset]

    #######################################################################
    # GPIO Outpu/Input Data
    #######################################################################
    def GPIO_0_Output(self, bit):
        self.GPIO_0_BIT = bit  # 1:Hi 0:LOW
        self.GPIO_0_OutputMode()
        self.GPIO_SetValue(pin=0, value=self.GPIO_0_BIT)

    def GPIO_0_InputMode(self):
        self.GPIO_0_DIR = DIR_INPUT  # 0:OutPut 1:Input
        self.GPIO_SetDirection(pin=0, direction=self.GPIO_0_DIR)

    def GPIO_0_OutputMode(self):
        self.GPIO_0_DIR = DIR_OUTPUT  # 0:OutPut 1:Input
        self.GPIO_SetDirection(pin=0, direction=self.GPIO_0_DIR)

    def GPIO_0_Input(self):
        self.GPIO_Read()
        return self.GPIO_0_INPUT, self.GPIO_0_DIR

    def GPIO_1_Output(self, bit):
        self.GPIO_1_BIT = bit  # 1:Hi 0:LOW
        self.GPIO_1_OutputMode()
        self.GPIO_SetValue(pin=1, value=self.GPIO_1_BIT)

    def GPIO_1_InputMode(self):
        self.GPIO_1_DIR = DIR_INPUT  # 0:OutPut 1:Input
        self.GPIO_SetDirection(pin=1, direction=self.GPIO_1_DIR)

    def GPIO_1_OutputMode(self):
        self.GPIO_1_DIR = DIR_OUTPUT  # 0:OutPut 1:Input
        self.GPIO_SetDirection(pin=1, direction=self.GPIO_1_DIR)

    def GPIO_1_Input(self):
        self.GPIO_Read()
        return self.GPIO_1_INPUT, self.GPIO_1_DIR

    def GPIO_2_Output(self, bit):
        self.GPIO_2_BIT = bit  # 1:Hi 0:LOW
        self.GPIO_2_OutputMode()
        self.GPIO_SetValue(pin=2, value=self.GPIO_2_BIT)

    def GPIO_2_InputMode(self):
        self.GPIO_2_DIR = DIR_INPUT  # 0:OutPut 1:Input
        self.GPIO_SetDirection(pin=2, direction=self.GPIO_2_DIR)

    def GPIO_2_OutputMode(self):
        self.GPIO_2_DIR = DIR_OUTPUT  # 0:OutPut 1:Input
        self.GPIO_SetDirection(pin=2, direction=self.GPIO_2_DIR)

    def GPIO_2_Input(self):
        self.GPIO_Read()
        return self.GPIO_2_INPUT, self.GPIO_2_DIR

    def GPIO_3_Output(self, bit):
        self.GPIO_3_BIT = bit  # 1:Hi 0:LOW
        self.GPIO_3_OutputMode()
        self.GPIO_SetValue(pin=3, value=self.GPIO_3_BIT)

    def GPIO_3_InputMode(self):
        self.GPIO_3_DIR = DIR_INPUT  # 0:OutPut 1:Input
        self.GPIO_SetDirection(pin=3, direction=self.GPIO_3_DIR)

    def GPIO_3_OutputMode(self):
        self.GPIO_3_DIR = DIR_OUTPUT  # 0:OutPut 1:Input
        self.GPIO_SetDirection(pin=3, direction=self.GPIO_3_DIR)

    def GPIO_3_Input(self):
        self.GPIO_Read()
        return self.GPIO_3_INPUT, self.GPIO_3_DIR

    #######################################################################
    # Clock Out Value & Duty
    #######################################################################
    def ClockOut(self, duty, value):
        """
        :param int duty:    Bit 4-3: Duty cycle
                            00 | 0% duty cycle
                            01 | 25% duty cycle
                            10 | 50% duty cycle
                            11 | 75% duty cycle
        :param int value:   Bit 2-0: Clock divider value
        """
        buf = self.compile_packet([0x00, CMD_GET_SRAM_SETTINGS])  # Get SRAM Settings

        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(PACKET_SIZE_65)

        buf = self.compile_packet([0x00, CMD_SET_SRAM_SETTINGS])  # Set SRAM Settings
        buf[2 + 1] = 0x80 | duty | (0x07 & value)  # Clock Output Divider value
        buf[3 + 1] = rbuf[6]  # DAC Voltage Reference
        buf[4 + 1] = 0x00  # Set DAC output value
        buf[5 + 1] = rbuf[7]  # ADC Voltage Reference
        buf[6 + 1] = 0x00  # Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0x80  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80
        buf[8 + 1] = rbuf[22]  # GP0 settings
        buf[9 + 1] = 0x01  # GP1 settings - 001 Dedicated function operation (Clock Output)
        buf[10 + 1] = rbuf[24]  # GP2 settings
        buf[11 + 1] = rbuf[25]  # GP3 settings
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

    #######################################################################
    # ADC 1
    #######################################################################
    def ADC_1_Init(self):
        buf = self.compile_packet([0x00, CMD_GET_SRAM_SETTINGS])
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)

        buf = self.compile_packet([0x00, CMD_SET_SRAM_SETTINGS])
        buf[2 + 1] = rbuf[5]  # Clock Output Divider value
        buf[3 + 1] = rbuf[6]  # DAC Voltage Reference
        buf[4 + 1] = 0x00  # Set DAC output value
        buf[5 + 1] = 0x00  # ADC Voltage Reference
        buf[6 + 1] = 0x00  # Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0xFF  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80
        buf[8 + 1] = rbuf[22]  # GP0 settings
        buf[9 + 1] = 0x02  # GP1 settings
        buf[10 + 1] = rbuf[24]  # GP2 settings
        buf[11 + 1] = rbuf[25]  # GP3 settings
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

    #######################################################################
    # ADC 2
    #######################################################################

    def ADC_2_Init(self):
        buf = self.compile_packet([0x00, CMD_GET_SRAM_SETTINGS])
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)

        buf = self.compile_packet([0x00, CMD_SET_SRAM_SETTINGS])
        buf[2 + 1] = rbuf[5]  # Clock Output Divider value
        buf[3 + 1] = rbuf[6]  # DAC Voltage Reference
        buf[4 + 1] = 0x00  # Set DAC output value
        buf[5 + 1] = rbuf[7]  # ADC Voltage Reference
        buf[6 + 1] = 0x00  # Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0x80  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80
        buf[8 + 1] = rbuf[22]  # GP0 settings
        buf[9 + 1] = rbuf[23]  # GP1 settings
        buf[10 + 1] = 0x02  # GP2 settings
        buf[11 + 1] = rbuf[25]  # GP3 settings
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

    #######################################################################
    # ADC 3
    #######################################################################

    def ADC_3_Init(self):
        buf = self.compile_packet([0x00, CMD_GET_SRAM_SETTINGS])

        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(PACKET_SIZE_65)

        buf = self.compile_packet([0x00, CMD_SET_SRAM_SETTINGS])
        buf[2 + 1] = rbuf[5]  # Clock Output Divider value
        buf[3 + 1] = rbuf[6]  # DAC Voltage Reference
        buf[4 + 1] = 0x00  # Set DAC output value
        buf[5 + 1] = rbuf[7]  # ADC Voltage Reference
        buf[6 + 1] = 0x00  # Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0x80  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80
        buf[8 + 1] = rbuf[22]  # GP0 settings
        buf[9 + 1] = rbuf[23]  # GP1 settings
        buf[10 + 1] = rbuf[24]  # GP2 settings
        buf[11 + 1] = 0x02  # GP3 settings
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

    #######################################################################
    # ADC Deta Get
    #######################################################################

    def ADC_DataRead(self):
        buf = self.compile_packet([0x00, CMD_STATUS_SET_PARAMETERS])
        self.mcp2221a.write(buf)

        buf = self.mcp2221a.read(PACKET_SIZE_65)
        # for i in range(len(buf)):
        #    print ("[%d]: 0x{:02x}".format(buf[i]) % (i))
        self.ADC_1_data = buf[50] | (buf[51] << 8)  # ADC Data (16-bit) values
        self.ADC_2_data = buf[52] | (buf[53] << 8)  # ADC Data (16-bit) values
        self.ADC_3_data = buf[54] | (buf[55] << 8)  # ADC Data (16-bit) values

    #######################################################################
    # DAC 1
    #######################################################################
    def DAC_1_Init(self):
        buf = self.compile_packet([0x00, CMD_GET_SRAM_SETTINGS])
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)

        buf = self.compile_packet([0x00, CMD_SET_SRAM_SETTINGS])
        buf[2 + 1] = rbuf[5]  # Clock Output Divider value
        buf[3 + 1] = 0x00  # DAC Voltage Reference
        buf[4 + 1] = 0x00  # Set DAC output value
        buf[5 + 1] = rbuf[7]  # ADC Voltage Reference
        buf[6 + 1] = 0x00  # Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0xFF  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80
        buf[8 + 1] = rbuf[22]  # GP0 settings
        buf[9 + 1] = rbuf[23]  # GP1 settings
        buf[10 + 1] = 0x03  # GP2 settings
        buf[11 + 1] = rbuf[25]  # GP3 settings
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

    #######################################################################
    # DAC 2
    #######################################################################

    def DAC_2_Init(self):
        buf = self.compile_packet([0x00, CMD_GET_SRAM_SETTINGS])
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)

        buf = self.compile_packet([0x00, CMD_SET_SRAM_SETTINGS])
        buf[2 + 1] = rbuf[5]  # Clock Output Divider value
        buf[3 + 1] = 0x00  # DAC Voltage Reference
        buf[4 + 1] = 0x00  # Set DAC output value
        buf[5 + 1] = rbuf[7]  # ADC Voltage Reference
        buf[6 + 1] = 0x00  # Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0xFF  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80
        buf[8 + 1] = rbuf[22]  # GP0 settings
        buf[9 + 1] = rbuf[23]  # GP1 settings
        buf[10 + 1] = rbuf[24]  # GP2 settings
        buf[11 + 1] = 0x03  # GP3 settings
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

    #######################################################################
    # DAC Output
    #######################################################################

    def DAC_Datawrite(self, value):
        buf = self.compile_packet([0x00, CMD_GET_SRAM_SETTINGS])
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)

        buf = self.compile_packet([0x00, CMD_SET_SRAM_SETTINGS])
        buf[2 + 1] = rbuf[5]  # Clock Output Divider value
        buf[3 + 1] = 0x00  # DAC Voltage Reference
        buf[4 + 1] = 0x80 | (0x1F & value)  # Set DAC output value
        buf[5 + 1] = rbuf[7]  # ADC Voltage Reference
        buf[6 + 1] = 0x00  # Setup the interrupt detection mechanism and clear the detection flag
        buf[7 + 1] = 0xFF  # Alter GPIO configuration: alters the current GP designation
        #   datasheet says this should be 1, but should actually be 0x80
        buf[8 + 1] = rbuf[22]  # GP0 settings
        buf[9 + 1] = rbuf[23]  # GP1 settings
        buf[10 + 1] = rbuf[24]  # GP2 settings
        buf[11 + 1] = rbuf[25]  # GP3 settings
        self.mcp2221a.write(buf)
        buf = self.mcp2221a.read(PACKET_SIZE_65)

    #######################################################################
    # I2C Init
    #######################################################################
    def I2C_Init(self, speed=100000):  # speed = 100000
        self.MCP2221_I2C_SLEEP = float(os.environ.get("MCP2221_I2C_SLEEP", 0))

        buf = self.compile_packet([0x00, CMD_STATUS_SET_PARAMETERS])
        buf[2 + 1] = 0x00  # Cancel current I2C/SMBus transfer (sub-command)
        buf[3 + 1] = 0x20  # Set I2C/SMBus communication speed (sub-command)
        # The I2C/SMBus system clock divider that will be used to establish the communication speed
        buf[4 + 1] = int((12000000 / speed) - 3)
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)
        # print("Init")
        if (rbuf[22] == 0):
            raise RuntimeError("SCL is low.")
        if (rbuf[23] == 0):
            raise RuntimeError("SDA is low.")

        # time.sleep(0.001)

    #######################################################################
    # I2C State Check
    #######################################################################
    def I2C_State_Check(self):
        buf = self.compile_packet([0x00, CMD_STATUS_SET_PARAMETERS])
        self.mcp2221a.write(buf)

        rbuf = self.mcp2221a.read(PACKET_SIZE_65)
        return rbuf[8]

    #######################################################################
    # I2C Cancel
    #######################################################################

    def I2C_Cancel(self):
        buf = self.compile_packet([0x00, CMD_STATUS_SET_PARAMETERS])
        buf[2 + 1] = 0x10  # Cancel current I2C/SMBus transfer (sub-command)
        self.mcp2221a.write(buf)

        self.mcp2221a.read(PACKET_SIZE_65)
        # time.sleep(0.1)

    #######################################################################
    # I2C Write
    #######################################################################
    def I2C_Write(self, addrs, data):
        """ Writes a block of data with Start and Stop c condition on bus
        :param int addrs: 7-bit I2C slave address
        :param list data: list of int

        Referring to MCP2221A Datasheet(Rev.B 2017), section 3.1.5
        """
        buf = self.compile_packet([0x00, CMD_I2C_WRITE_DATA])
        self._i2c_write(addrs, data, buf)

    def I2C_Write_Repeated(self, addrs, data):
        """ Writes a block of data with Repeated Start and Stop conditions on bus
        :param int addrs: 7-bit I2C slave address
        :param list data: list of int

        Referring to MCP2221A Datasheet(Rev.B 2017), section 3.1.6
        """
        buf = self.compile_packet([0x00, CMD_I2C_WRITE_DATA_REPEATED_START])
        self._i2c_write(addrs, data, buf)

    def I2C_Write_No_Stop(self, addrs, data):
        """ Writes a block of data with Start condition on bus
        :param int addrs: 7-bit I2C slave address
        :param list data: list of int

        Referring to MCP2221A Datasheet(Rev.B 2017), section 3.1.7
        """
        buf = self.compile_packet([0x00, CMD_I2C_WRITE_DATA_NO_STOP])
        self._i2c_write(addrs, data, buf)

    def _i2c_write(self, addrs, data, buf):

        buf[1 + 1] = (len(data) & 0x00FF)  # Cancel current I2C/SMBus transfer (sub-command)
        buf[2 + 1] = (len(data) & 0xFF00) >> 8  # Set I2C/SMBus communication speed (sub-command)
        # The I2C/SMBus system clock divider that will be used to establish the communication speed
        buf[3 + 1] = 0xFF & (addrs << 1)
        for i in range(len(data)):
            # print ("{:d}: 0x{:02x}".format(i,data[i]))
            buf[4 + 1 + i] = data[
                i]  # The I2C/SMBus system clock divider that will be used to establish the communication speed
        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(PACKET_SIZE_65)
        time.sleep(0.008)

    #######################################################################
    # I2C Read
    #######################################################################
    def I2C_Read(self, addrs, size):
        """ Reads a block of data with Start and Stop conditions on bus
        :param int addrs: 7-bit I2C slave address
        :param int size: size of read out in bytes

        Referring to MCP2221A Datasheet(Rev.B 2017), section 3.1.8
        """
        buf = self.compile_packet([0x00, CMD_I2C_READ_DATA])
        return self._i2c_read(addrs, size, buf)

    def I2C_Read_Repeated(self, addrs, size):
        """ Reads a block of data with Repeated Start and Stop conditions on bus
        :param int addrs: 7-bit I2C slave address
        :param int size: size of read out in bytes

        Referring to MCP2221A Datasheet(Rev.B 2017), section 3.1.9
        """
        buf = self.compile_packet([0x00, CMD_I2C_READ_DATA_REPEATED_START])
        return self._i2c_read(addrs, size, buf)

    def _i2c_read(self, addrs, size, buf):

        buf[1 + 1] = (size & 0x00FF)  # Read LEN
        buf[2 + 1] = (size & 0xFF00) >> 8  # Read LEN
        buf[3 + 1] = 0xFF & (addrs << 1)  # addrs
        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(PACKET_SIZE_65)
        if (rbuf[1] != 0x00):
            # print("[0x91:0x{:02x},0x{:02x},0x{:02x}]".format(rbuf[1],rbuf[2],rbuf[3]))
            self.I2C_Cancel()
            self.I2C_Init()
            raise RuntimeError("I2C Read Data Failed: Code " + rbuf[1])
        time.sleep(self.MCP2221_I2C_SLEEP)

        buf = self.compile_packet([0x00, 0x40])
        buf[1 + 1] = 0x00
        buf[2 + 1] = 0x00
        buf[3 + 1] = 0x00
        self.mcp2221a.write(buf)
        rbuf = self.mcp2221a.read(PACKET_SIZE_65)
        if (rbuf[1] != 0x00):
            # print("[0x40:0x{:02x},0x{:02x},0x{:02x}]".format(rbuf[1],rbuf[2],rbuf[3]))
            self.I2C_Cancel()
            self.I2C_Init()
            print("You can try increasing environment variable MCP2221_I2C_SLEEP")
            raise RuntimeError("I2C Read Data - Get I2C Data Failed: Code " + rbuf[1])
        if (rbuf[2] == 0x00 and rbuf[3] == 0x00):
            self.I2C_Cancel()
            self.I2C_Init()
            return rbuf[4]
        if (rbuf[2] == 0x55 and rbuf[3] == size):
            rdata = [0] * size
            for i in range(size):
                rdata[i] = rbuf[4 + i]
            return rdata

    #######################################################################
    # reset
    #######################################################################
    def Reset(self):
        print("Reset")
        buf = self.compile_packet([0x00, CMD_RESET_CHIP, 0xAB, 0xCD, 0xEF])

        self.mcp2221a.write(buf)
        time.sleep(1)
