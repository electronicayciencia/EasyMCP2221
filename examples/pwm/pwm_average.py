# One bit DAC (PWM output). 
# GP0 will be the output.
# Average approach:
#   - Count slots On vs Off
#   - Calculate moving average
#   - For each slot:
#     - If count on is greater than on/slots: turn this slot on
#     - else: turn this slot off

# Different averages modifies the output.

class FIR_MovingAverage:
    def __init__(self, n, start):
        self.window = [start] * n

    def update(self, v):
        self.window.pop(0)
        self.window.append(v)
        #print(self.window)
    
    def get(self):
        return sum(self.window) / len(self.window)


class IIR_MovingAverage:
    def __init__(self, a, start):
        self.a = a
        self.value = start

    def update(self, v):
        self.value = self.a*self.value + (1-self.a)*v
    
    def get(self):
        return self.value



import EasyMCP2221

# Actual frequency depends on USB mode
slots = 100

# Number of ON slots
on = 4


# Connect to the device
mcp = EasyMCP2221.Device()
mcp.set_pin_function(gp0 = "GPIO_OUT")

average = FIR_MovingAverage(n = slots, start = on/slots)
#average = IIR_MovingAverage(a = 0.9, start = on/slots)

while True:
    print(average.get())
    if average.get() < on/slots:
        mcp.GPIO_write(gp0 = True)
        average.update(1)
    else:
        mcp.GPIO_write(gp0 = False)
        average.update(0)

