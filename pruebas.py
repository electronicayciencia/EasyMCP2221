import time
from MCP2221 import MCP2221

mcp = MCP2221.MCP2221()

def tested():
    mcp.GPIO_Config(
    gp1 = MCP2221.GPIO_FUNC_DEDICATED,
    gp2 = MCP2221.GPIO_FUNC_GPIO | MCP2221.GPIO_DIR_OUT | MCP2221.GPIO_OUT_VAL_0)

    mcp.Clock_Config(duty = 50, freq = "3MHz")

    # When Clock_Conf calls to GPIO_Config, it resets previous SetValue and SetAsInput commands.

    # DAC
    mcp.DAC_Channel("GP3")
    mcp.DAC_Config(ref = "2.048V", out = 0)
    mcp.DAC_Write(20)

    mcp.ADC_Channel("GP1")
    mcp.ADC_Read()

    mcp.GPIO_Output("GP3", True)
    mcp.GPIO_Input("GP3")
    mcp.GPIO_Read()



    ###############################
    # Unexpected Reset of GP status
    ###############################
    mcp.GPIO_Config(gp2 = PyMCP2221A.GPIO_FUNC_GPIO | PyMCP2221A.GPIO_DIR_OUT | PyMCP2221A.GPIO_OUT_VAL_0)
    # LED is on
    mcp.GPIO_FastSetAsInput(gp2 = True)
    # LED is off
    mcp.GPIO_Config(gp3 = PyMCP2221A.GPIO_FUNC_ALT_1) # unrelated pin
    # LED is on again


    ###############################
    # Unexpected Reset of Vrm
    ###############################
    mcp.GPIO_Config(gp3 = PyMCP2221A.GPIO_FUNC_ALT_1)
    # DAC is Zero
    mcp.DAC_Config(ref = "2.048V", out = 31)
    # DAC is Vrm
    mcp.GPIO_FastSetAsInput(gp2 = True) # unrelated pin
    # DAC goes to Zero again only if ref is not Vdd

    mcp.I2C_Led()


text = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho tiempo que vivía un hidalgo de los de lanza en astillero, adarga antigua, rocín flaco y galgo corredor. Una olla de algo más vaca que carnero, salpicón las más noches, duelos y quebrantos los sábados, lentejas los viernes, algún palomino de añadidura los domingos, consumían las tres partes de su hacienda."
text = bytes(text, 'utf-8')


# Note: Invoking I2C_Cancel() when not needed may leave bus in busy state.
#mcp.I2C_Cancel()

#mcp.I2C_Speed(100_000)

#mcp.I2C_Write(0x50, text)
mem_addr = 0;
mem_addr_low = mem_addr & 0xFF
mem_addr_hi  = mem_addr >> 8 & 0xFF
# Read all 24lc128 (128*1024/8)
# mcp.I2C_Write(0x50, b'\0\1') # memhi, memlo
#mcp.I2C_Read(0x50, 16384)

def I2C_Scan():
    for addr in range(0, 127):
        try:
            mcp.I2C_Read(addr, size = 0)
        except:
            continue

        print("0x%02x found!" % addr)


def Test_Wake_Up():

    mcp.Wake_Up_Enable(True)
    mcp.Reset()

    mcp.Pin_Function(gp1 = "IOC", gp2 = "USBCFG")
    mcp.Wake_Up_Config(edge = "both")


