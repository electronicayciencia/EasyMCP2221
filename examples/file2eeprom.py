# Read or write a full serial EEPROM like 24xx512/128/64 etc
import time
import EasyMCP2221
import argparse
import textwrap

def hexint(x):
    return int(x, 16)

parser = argparse.ArgumentParser(
    description = 'Write or clear an EEPROM.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog = textwrap.dedent("""
        Delete a 24LC512:
          file2eeprom.py -k 512 -p 128 -r 400 -w 5 -d 
            
        Write file to a 24LC128: 
          file2eeprom.py -k 128 -p 64 -r 400 -w 5 -f /tmp/eeprom
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
    '-p','--page', 
    type=int,
    required=True, 
    help = "Page size (EEPROM's internal buffer) in bytes. E.g.: 64 for a 24xx128, 128 for a 24xx512.")

parser.add_argument(
    '-f','--file', 
    type=str,
    required=False, 
    help = "File to save EEPROM content.")

parser.add_argument(
    '-w','--wait', 
    type=int,
    default=5,
    required=False, 
    help = "Wait time for write cycle in ms. Usually 5.")

#parser.add_argument(
#    '-d','--delete', 
#    type=bool,
#    required=False, 
#    help = "Clear memory contents instead of reading a file.")
parser.add_argument(
    '-d', '--delete', 
    action='store_true',
    help = "Clear memory contents instead of reading a file.")

args = parser.parse_args()

if not args.file and not args.delete:
    print("Error: File is needed if not delete.")
    parser.print_help()
    exit()

mcp = EasyMCP2221.Device()
eeprom = mcp.I2C_Slave(args.address, speed = args.rate * 1000)

memsize = int(1024 * args.kbits / 8)

print("Writing EEPROM...")

start = time.perf_counter()

if args.delete:
    for i in range(memsize//args.page):
        print("Page %d/%d." %(i+1, memsize / args.page))
        buffer = b'\xff' * args.page
        buffer = eeprom.write_register(i * args.page, buffer, reg_bytes=2)
        
        until = time.perf_counter() + args.wait / 1000
        while time.perf_counter() < until:
            pass
    
else:
    with open(args.file, 'rb') as f:
        for i in range(memsize//args.page):
            print("Page %d/%d." %(i+1, memsize / args.page))
            buffer = f.read(args.page)
            buffer = eeprom.write_register(i * args.page, buffer, reg_bytes=2)
            
            until = time.perf_counter() + args.wait / 1000
            while time.perf_counter() < until:
                pass
    
end = time.perf_counter()
    
print("Elapsed time: %.1fs" % (end - start))
