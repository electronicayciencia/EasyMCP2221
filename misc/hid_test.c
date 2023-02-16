/* Test smooth USB interaction.
 *
 * Usage:
 *  Plug the device. Run this program. Steps should run without delay.
 *  If a delay happens, a conflicting kernel driver may be present.
 *
 * Compile:
 *   gcc hid_test.c -o hid_test -lhidapi-libusb
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <hidapi/hidapi.h>

int main(int argc, char* argv[]) {
    wchar_t wstr[255];
    // cmd: gpio setup, all outputs, all off.
    unsigned char buf[65] = "\00\x60\x00\x00\x81\x95\x81\x00\x80\x00\x00\x00\x00";
    hid_device *handle;
    struct hid_device_info *devs, *cur_dev;

    puts("Start");

    if (hid_init())
         return -1;
    puts("HID initialized");

    handle = hid_open(0x04D8, 0x00DD, 0);
    if (!handle) {
        printf("unable to open device\n");
        return 1;
    }
    puts("Device opened");

    hid_get_product_string(handle, wstr, 255);
    printf("Read Id string: %ls\n", wstr);

    hid_write(handle, buf, 65);
    puts("Cmd sent: all outputs off");

    hid_read(handle, buf, 65);
    if (buf[1] != 0x00) {
        printf("command failed\n");
        return 1;
    }
    puts("Cmd succeded");

    hid_close(handle);
    puts("HID closed");

    hid_exit();
    puts("HID exited");

    puts("done");
    exit(0);
}
