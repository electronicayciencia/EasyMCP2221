# Basic PCA9685 class
# Uses EasyMCP2221's I2C Slave interface instead of SMBus.
# Electronicayciencia 01/08/2023
from struct import pack

class PCA9685:

    # I2C Registers
    MODE1         = 0x00
    MODE2         = 0x01

    LED0_ON_L     = 0x06
    LED0_ON_H     = 0x07
    LED0_OFF_L    = 0x08
    LED0_OFF_H    = 0x09

    ALL_LED_ON_L  = 0xFA
    ALL_LED_ON_H  = 0xFB
    ALL_LED_OFF_L = 0xFC
    ALL_LED_OFF_H = 0xFD

    PRE_SCALE     = 0xFE

    # MODE1 bits
    RESTART       = 1<<7
    EXTCLK        = 1<<6
    AI            = 1<<5
    SLEEP         = 1<<4
    NOT_SLEEP     = 0<<4
    SUB1          = 1<<3
    SUB2          = 1<<2
    SUB3          = 1<<1
    ALLCALL       = 1<<0

    # MODE2 bits
    INVRT         = 1<<4
    OCH_ACK       = 1<<3
    OCH_STOP      = 0<<3
    OUTDRV_TOTEM  = 1<<2
    OUTDRV_OD     = 0<<2
    OUTNE_HD      = 0b10
    OUTNE_OUTDRV  = 0b01
    OUTNE_OFF     = 0b00

    # Misc
    TIMER_COUNTS  = 4096
    N_LEDS        = 16
    INT_OSC_FREQ  = 25e6


    def __init__(self, dev):
        self.pca = dev

        self.duties = [0] * self.N_LEDS
        self.delays = [0] * self.N_LEDS

        self.mode1 = self.AI | self.NOT_SLEEP
        self.mode2 = self.OUTDRV_TOTEM | self.OCH_STOP

        self.pca.write_register(self.MODE1, self.mode1)
        self.pca.write_register(self.MODE2, self.mode2)


    def calculate_timers(self, duty, delay = 0):
        """Calculate timer_on and timer_off given delay and duty values."""

        if   duty < 0: duty = 0
        elif duty > 1: duty = 1

        if   delay < 0: delay = 0
        elif delay > 1: delay = 1

        if duty == 0:
            timer_on  = 0
            timer_off = self.TIMER_COUNTS # set always off flag

        elif duty == 1:
            timer_on  = self.TIMER_COUNTS # set always on flag
            timer_off = 0

        else:
            timer_on  = round(self.TIMER_COUNTS * delay) - 1
            timer_off = round(self.TIMER_COUNTS * duty) + timer_on

            if timer_on < 0:
                timer_on = timer_on + self.TIMER_COUNTS

            if timer_off > self.TIMER_COUNTS:
                timer_off = timer_off - self.TIMER_COUNTS;

        return timer_on, timer_off


    def set_all_leds(self, duty, delay = 0):
        """Set all leds at one. Update not needed"""
        timer_on, timer_off = self.calculate_timers(duty, delay)
        self.pca.write_register(self.ALL_LED_ON_L ,     timer_on % 256)
        self.pca.write_register(self.ALL_LED_ON_H , int(timer_on / 256))
        self.pca.write_register(self.ALL_LED_OFF_L,     timer_off % 256)
        self.pca.write_register(self.ALL_LED_OFF_H, int(timer_off / 256))


    def set_led(self, led, duty, delay=0, update=0):
        """Set the properties of one led.
        If update is false, store the new value and wait until update is called.
        If update is true, write new I2C value right now!
        """

        if led not in range(0, self.N_LEDS):
            raise ValueError('LED number must be 0 to 15.')

        self.duties[led] = duty
        self.delays[led] = delay

        if update:
            timer_on, timer_off = self.calculate_timers(duty, delay)
            v = [
                timer_on % 256,
                int(timer_on / 256),
                timer_off % 256,
                int(timer_off / 256)
                ]
            self.pca.write_register(self.LED0_ON_L + 4*led, v)


    def update(self):
        """Write LED values to the chip"""
        v = []
        for duty, delay in zip(self.duties, self.delays):
            timer_on, timer_off = self.calculate_timers(duty, delay)
            v = v + [timer_on, timer_off]

        self.pca.write_register(self.LED0_ON_L, pack("<32h", *v))


    def set_rate(self, rate, osc=INT_OSC_FREQ):
        """Set prescaler to get desired update rate"""
        presc = round(osc / (self.TIMER_COUNTS * rate)) - 1

        if presc < 0: presc = 0
        if presc > 255: presc = 255

        mode = self.mode1
        self.pca.write_register(self.MODE1, mode | self.SLEEP)
        self.pca.write_register(self.PRE_SCALE, presc)
        self.pca.write_register(self.MODE1, mode)

