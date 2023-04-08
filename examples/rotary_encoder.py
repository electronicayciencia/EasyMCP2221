# GPIO incremental rotary encoder connected to GP0 and GP1.
import EasyMCP2221

# Device initialization
mcp = EasyMCP2221.Device()

mcp.set_pin_function(
    gp0 = "GPIO_IN",   # PIN A
    gp1 = "GPIO_IN")   # PIN B
# Ground: PIN C (common)
# Pull up resistors to A and B.

count = 0

print("Incremental rotary encoder example.\nPress Ctrl+C to quit.")
print("Count:", count)

# Upcounting sequence   (CW):  change A, then change B
# Downcounting sequence (CCW): change B, then change A
# Mark step when both A and B are at the same level
sequence = ""

old = [0,0]

while True:
    signal = mcp.GPIO_read()[0:2]

    if signal[0] != old[0] and signal[1] == old[1]:
        #print("Changed A")
        sequence = sequence + "A"
    elif signal[0] == old[0] and signal[1] != old[1]:
        #print("Changed B")
        sequence = sequence + "B"
    elif signal[0] != old[0] and signal[1] != old[1]:
        #print("Changed both")
        sequence = ""

    old = signal

    # Mark step when both signals are at the same level
    if signal[0] == signal[1] and sequence != "":
        if sequence == "AB":
            count = count + 1
            print("Count:", count)
        elif sequence == "BA":
            count = count - 1
            print("Count:", count)
            
        sequence = ""




