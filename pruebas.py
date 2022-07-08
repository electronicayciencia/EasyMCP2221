import time
from PyMCP2221A import PyMCP2221A

mcp = PyMCP2221A.PyMCP2221A()

mcp.GPIO_Config(
  gp1 = PyMCP2221A.GPIO_FUNC_DEDICATED,
  gp2 = PyMCP2221A.GPIO_FUNC_GPIO | PyMCP2221A.GPIO_DIR_OUT | PyMCP2221A.GPIO_OUT_VAL_0)

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

mcp.I2C_Cancel()

mcp.I2C_Speed(100_000)

text = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho tiempo que vivía un hidalgo de los de lanza en astillero, adarga antigua, rocín flaco y galgo corredor. Una olla de algo más vaca que carnero, salpicón las más noches, duelos y quebrantos los sábados, lentejas los viernes, algún palomino de añadidura los domingos, consumían las tres partes de su hacienda."
text = bytes(text, 'utf-8')
#mcp.I2C_Write




