# Read or write a full serial EEPROM like 24xx512/128/64 etc
import time
import EasyMCP2221
import argparse
import textwrap

def hexint(x):
    return int(x, 16)

parser = argparse.ArgumentParser(
    description='Save EEPROM contents to a file.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog = textwrap.dedent("""
        Read a 24LC512:
          eeprom2file.py -k 512 -p 128 -f /tmp/eeprom

        Read a 24LC128:
          eeprom2file.py -k 128 -p 64 -f /tmp/eeprom

        24AA16 uses a different protocol.
        """)
        )

parser.add_argument(
    '-a','--address',
    type=hexint,
    required=False,
    default=0x50,
    help = "I2C slave 7 bit address in hex. E.g.: 50 for a common 24xx.")

parser.add_argument(
    '-r','--rate',
    type=int,
    required=False,
    default=400,
    help = "I2C clock rate in kHz (default 400kHz).")

parser.add_argument(
    '-k','--kbits',
    type=int,
    required=True,
    help = "Memory size in kbits. E.g.: 128 for a 24xx128.")

parser.add_argument(
    '-f','--file',
    type=str,
    required=True,
    help = "File to save EEPROM content.")

args = parser.parse_args()

mcp = EasyMCP2221.Device()
eeprom = mcp.I2C_Slave(args.address, speed = args.rate * 1000)

memsize = int(1024 * args.kbits / 8)

print("Reading EEPROM...")


with open(args.file, 'wb') as f:

    start = time.perf_counter()
    index = 0

    while index < memsize:
        # MCP2221's max length for a I2C operation is 65535 bytes.
        if memsize - index > 65535:
            m = 65535
        else:
            m = memsize - index

        buffer = eeprom.read_register(index, m, reg_bytes=2)
        f.write(buffer)
        index = index + m

end = time.perf_counter()

print("Elapsed time: %.1fs" % (end - start))
print("Saved to", args.file)
