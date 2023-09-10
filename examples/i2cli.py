# I2C command line
import sys
import EasyMCP2221

try:
    import readline
except:
    pass #readline not available

address = -1
busy = False

# Connect to MCP2221
mcp = EasyMCP2221.Device()

print("I2C command line")

def scan():
    print("Searching...")

    for addr in range(0, 0x80):
        try:
            mcp.I2C_read(addr)
            print("I2C slave found at address 0x%02X" % (addr))

        except EasyMCP2221.exceptions.NotAckError:
            pass


def help():
    print("h: help")
    print("a: set new address")
    print("r NN: read NN bytes (default is read one byte)")
    print("w xx xx xx ... : write bytes in hex")
    print("wr xx xx xx ... : write bytes in hex, no stop signal")
    print("q: quit")


def data_dump(data):
    print(data.hex(" "))



while True:

    # Address selection mode
    if address < 0x00 or address > 0x80:
        cmd = input("\nEnter address from 0x00 to 0x80. S to scan, q to quit > ")

        if cmd == "S":
            scan()

        elif cmd == "q":
            sys.exit()

        else:
            try:
                address = int(cmd, 16)
                if address < 0x00 or address > 0x80:
                    raise ValueError

            except ValueError:
                print("Invalid address")

    # Read/write mode
    else:
        line = input("\n%s[%02x] (h for help) > " % ("*" if busy else "", address))

        if not line:
            line = "r 1" # default command: read 1 byte

        try:
            cmd, arg = line.split(" ", 1)
        except ValueError:
            cmd = line # no args
            arg = ""


        if cmd == 'h':
            help()

        elif cmd == 'a':
            address = -1

        elif cmd == 'q':
            sys.exit()


        elif cmd == 'r':
            try:
                n = int(arg)
            except ValueError:
                n = 1

            if not busy:
                kind = "regular"
            else:
                kind = "restart"

            try:
                data = mcp.I2C_read(address, n, kind)
            except EasyMCP2221.exceptions.NotAckError:
                print("Error: device did not ack")
                continue

            busy = False
            data_dump(data)


        elif cmd == 'wr':
            if not arg:
                print("Need one or more bytes.")
                continue

            try:
                data = bytes.fromhex(arg)
            except ValueError:
                print("Invalid input.")
                continue

            if not busy:
                try:
                    mcp.I2C_write(address, data, "nonstop")
                except EasyMCP2221.exceptions.NotAckError:
                    print("Error: device did not ack")
                    continue

                busy = True
            else:
                print("Not allowed. Use regular read o write commands.")


        elif cmd == 'w':
            if not arg:
                print("Need one or more bytes.")
                continue

            try:
                data = bytes.fromhex(arg)
            except ValueError:
                print("Invalid hex bytes.")
                continue

            if not busy:
                kind = "regular"

            else:
                kind = "restart"

            try:
                mcp.I2C_write(address, data, kind)
            except EasyMCP2221.exceptions.NotAckError:
                print("Error: device did not ack")
                continue

            busy = False


        else:
            print(cmd)
            print("Invalid command, try h for help.")
