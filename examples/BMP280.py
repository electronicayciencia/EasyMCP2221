# Read pressure and temperature of BMP280 using I2C
# See https://www.electronicayciencia.com/2018/10/la-presion-atmosferica-bmp280.html
from time import sleep
from sys import exit
from struct import unpack
import EasyMCP2221


bmp_address    = 0x76
reg_id         = 0xD0
reg_config     = 0xF4
reg_press      = 0xF7
reg_dig_T1     = 0x88


def unpack_20bit(bytes):
    v24bits = bytes[0] | (bytes[1] << 8) | (bytes[2] << 16)
    return v24bits >> 4


def compensate(adc_T, adc_P):
    # Compensation formulas for T
    var1 = (adc_T/16384 - dig_T1/1024) * dig_T2
    var2 = (adc_T/131072 - dig_T1/8192) * (adc_T/131072 - dig_T1/8192) * dig_T3
    t_fine = var1 + var2
    T = (var1 + var2) / 5120
    
    # Compensation formulas for P
    var1 = t_fine / 2 - 64000
    var2 = var1 * var1 * dig_P6 / 32768
    var2 = var2 + var1 * dig_P5 * 2
    var2 = var2 / 4 + dig_P4 * 65536
    var1 = (dig_P3 * var1 * var1 / 524288 + dig_P2 * var1) / 524288
    var1 = (1.0 + var1 / 32768)*dig_P1
    p = 1048576.0 - adc_P
    p = (p - var2 / 4096) * 6250 / var1
    var1 = dig_P9 * p * p / 2147483648
    var2 = p * dig_P8 / 32768
    p = p + (var1 + var2 + dig_P7) / 16
    
    return (T, p)




mcp = EasyMCP2221.Device()
bmp = mcp.I2C_Slave(bmp_address)

device_id = ord(bmp.read_register(0xD0))

if device_id in (0x56, 0x57, 0x58):
    print("BMP 280 detected")
elif device_id == 0x60:
    print("BME 280 detected")
else:
    print("Unknown device id: 0x%02X" % device_id)
    exit()

#Read calibration data
cal = bmp.read_register(reg_dig_T1, 24)

(dig_T1,
 dig_T2,
 dig_T3,
 dig_P1,
 dig_P2,
 dig_P3,
 dig_P4,
 dig_P5,
 dig_P6,
 dig_P7,
 dig_P8,
 dig_P9) = unpack('HhhHhhhhhhhh', cal)


# No filter temp, no filter pressure, forced mode.
bmp.write_register(reg_config,0b00100101)
sleep(0.5)

# read 6 registers in a row (faster than 6 individual reads):
(press_msb,
 press_lsb,
 press_xlsb,
 temp_msb,
 temp_lsb,
 temp_xlsb) = list(bmp.read_register(reg_press, 6))

adc_P = unpack_20bit([press_xlsb, press_lsb, press_msb])
adc_T = unpack_20bit([temp_xlsb,  temp_lsb,  temp_msb])

(T, P) = compensate(adc_T, adc_P)
print("T: %.2fºC" % T)
print("P: %.1fhPa" % (P/100))

