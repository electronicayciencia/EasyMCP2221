from sys import exit
import time
from time import sleep
import EasyMCP2221
from EasyMCP2221.Constants import *

mcp = EasyMCP2221.Device(trace_packets = False)

mcp.I2C_cancel()

exit()

mcp.set_pin_function(
    gp0 = "GPIO_OUT", out0 = 1, # pull-up SCL
    gp1 = "GPIO_OUT", out1 = 1, # pull-up SDA
    gp2 = "GPIO_IN",
    gp3 = "GPIO_IN")

mcp.I2C_speed(100000)

#mcp.I2C_cancel()
#mcp.I2C_is_idle()

mcp.GPIO_write(gp1=0)

try:
    mcp.I2C_write(0x50, b'A' * 65)
except:
    pass

mcp.GPIO_write(gp1=1)

try:
    mcp.I2C_read(0x51, 1)
except:
    print("Failed ok")

#mcp.reset()
exit()




mcp.set_pin_function(
    gp0 = "GPIO_OUT", out0 = 1, # pull-up SCL
    gp1 = "GPIO_OUT", out1 = 1, # pull-up SDA
    gp2 = "GPIO_IN",
    gp3 = "GPIO_IN")

mcp = EasyMCP2221.Device(trace_packets = True)



exit()

#import pdb
#pdb.set_trace()

#mcp.I2C_speed(100000)


#mcp.GPIO_write(gp1 = False)
    
try:
    mcp.I2C_read(0x51,1)
except:
    pass
    
#mcp.GPIO_write(gp1 = True)


mcp.I2C_read(0x51,1)


exit()


mcp.ADC_config(ref = "VDD")
mcp.DAC_config(ref = "2.048V")
mcp.DAC_write(31)

mcp.set_pin_function(
    gp2 = "ADC",
    gp3 = "DAC")



#In [36]: mcp.ADC_read()
#Out[36]: (1023, 991, 991)

exit()

mcp.I2C_write(0x50, b'\x00\x00', 'nonstop')
mcp.I2C_read(0x50, 25, 'restart')

exit()

#mcp.trace_packets = 1
mcp.debug_messages = 1
input()
print(mcp.ADC_read())


exit()


from EasyMCP2221.exceptions import *
mcp.trace_packets = 1
#mcp.I2C_write(0x50, b'This is data')
try:
    mcp.I2C_read(0x51, 1)
except NotAckError:
    print("No device")
    exit()
except EasyMCP2221.exceptions.LowSCLError:
    print("SCL low")

exit()


text = b"And Saint Attila raised the hand grenade up on high, saying, 'O Lord, bless this thy hand grenade, that with it thou mayst blow thine enemies to tiny bits, in thy mercy.' And the Lord did grin. And the people did feast upon the lambs, and sloths, and carp, and anchovies, and orangutans, and breakfast cereals, and fruit bats, and large chulapas. And the Lord spake, saying, 'First shalt thou take out the Holy Pin. Then shalt thou count to three, no more, no less. Three shall be the number thou shalt count, and the number of the counting shall be three. Four shalt thou not count, neither count thou two, excepting that thou then proceed to three. Five is right out. Once the number three, being the third number, be reached, then lobbest thou thy Holy Hand Grenade of Antioch towards thy foe, who, being naughty in My sight, shall snuff it.\n"

totalsize = int(512 * 1024 / 8)
pagesize  = 128

#text = "." * 100

text = b'\xff' * totalsize

#mcp.trace_packets = True


eeprom = mcp.I2C_Slave(0x50, speed = 47000)

pages = [text[i:i+pagesize] for i in range(0, len(text), pagesize)]

p = 0
for page in pages:

    eeprom.write_register(p * pagesize, page, reg_bytes=2)

    end = time.perf_counter() + 5/1000  # 5ms nominal write time
    while time.perf_counter() < end:
        pass

    p = p + 1
    print("Byte: %d / %d" % (p * pagesize, totalsize))

#p = 0
#while p < len(pages):
#
#    try:
#        eeprom.write_register(p * pagesize, pages[0], reg_bytes=2)
#
#        p = p + 1
#        print("Byte: %d / %d" % (p * pagesize, totalsize))
#
#    except:
#        print("waiting")
#        continue





def test_save_config():
    mcp.set_pin_function(
        gp0 = "GPIO_IN",
        gp1 = "GPIO_IN",
        gp2 = "GPIO_IN",
        gp3 = "GPIO_IN")

    mcp.DAC_config(ref = "OFF")
    mcp.ADC_config(ref = "VDD")

    input()

    mcp.debug_messages = True
    mcp.save_config()


def test_preserve_adc_ref():
    # SRAM_config shoudn't change ADC/ADC ref
    mcp.set_pin_function(gp1 = "GPIO_IN", gp2 = "ADC", gp3 = "DAC")
    mcp.DAC_config(ref="4.096V")
    mcp.DAC_write(16)
    mcp.ADC_config()
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






