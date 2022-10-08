import time
from time import sleep
import EasyMCP2221
from EasyMCP2221.Constants import *

#from EasyMCP2221 import I2C_Slave

mcp = EasyMCP2221.Device()

#eeprom = mcp.I2C_Slave(0x50)
#pcf    = mcp.I2C_Slave(0x48)

#mcp.trace_packets = True

def test_preserve_adc_ref():
    # SRAM_config shoudn't change ADC/ADC ref 
    mcp.set_pin_function(gp1 = "GPIO_IN", gp2 = "ADC", gp3 = "DAC")
    mcp.DAC_config(ref="4.096V")
    mcp.DAC_write(16)
    mcp.ADC_config(ref="VDD")
    print(mcp.ADC_read())
    mcp.ADC_config(ref="2.048V")
    print(mcp.ADC_read())
    
    input()
    
    # This shall not change ADC reference
    mcp.set_pin_function(gp1 = "GPIO_OUT", out1 = 0)
    print(mcp.ADC_read())



def test_preserve_dac_ref():
    # SRAM_config shoudn't change ADC/ADC ref 
    mcp.set_pin_function(gp0 = "GPIO_IN", gp2 = "DAC")
    mcp.DAC_config(ref="4.096V")
    mcp.DAC_write(31)
    
    input()
    
    # This shall not change DAC reference
    mcp.set_pin_function(gp1 = "GPIO_OUT")



def test_preserve_gpio():
    # SRAM_config to preserve GPIO_write values 
    # GP0 and GP1 are inputs, GP2 and GP3 are outputs.
    mcp.set_pin_function(
        gp0 = "GPIO_OUT",
        gp1 = "GPIO_OUT",
        gp2 = "GPIO_OUT",
        gp3 = "GPIO_OUT")
    
    mcp.GPIO_write(gp2 = True, gp3 = True)
    
    input()
    
    # This shall not change gp2 output value
    mcp.set_pin_function(gp1 = "GPIO_IN")


def freq_meter():

    mcp.set_pin_function(gp0 = "GPIO_IN")

    start = time.time()
    old = True
    n = 0
    while True:
        input = mcp.GPIO_read()[0]
        if input != old:
            n = n + 1

        if time.time() - start > 1:
            print(int(n/2))
            n = 0
            start = time.time()

        old = input


def counter():

    mcp.set_pin_function(
        gp0 = "GPIO_IN",
        gp1 = "GPIO_IN",
        gp2 = "GPIO_IN",
        gp3 = "GPIO_IN")


    c = 0
    gp_old = mcp.GPIO_read()

    while True:
        gp = mcp.GPIO_read()

        if not gp == gp_old:
            c = c + 1
            print(c)
            gp_old = gp


test_preserve_adc_ref()




