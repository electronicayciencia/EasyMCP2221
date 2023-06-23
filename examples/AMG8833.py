# Let's play with a AMG8833

import EasyMCP2221
import os
from time import sleep
from binascii import hexlify

def print_array(values):
    for row in range(7, -1, -1):
        for col in range(7,-1, -1):
            by = values[row*(2*col):row*(2*col)+1]
            p = int.from_bytes(by, "little")
            
            #print("% 4d" % p, end = "")
            print("%s" % "*" if p > 110 else " ", end = "")
        
        print()

sensor = EasyMCP2221.Device().I2C_Slave(0x69)

while True:
    values = sensor.read_register(0x80, 128)
    os.system("clear")
    print_array(values)
    sleep(0.1)