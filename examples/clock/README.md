# Digital clock example

MCP2221 controls two I2C chips:
- DS1307 as RTC
- LCD display, working with PCF8574 I2C adapter.

Setup:
- DS1307 is configured as 1Hz square oscillator. 
- MCP2221's GP2 is configured as Interrupt on Change.
- I2C bus speed is set to 100kHz.
- The rising edge of DS1307's output will trigger the update cycle every second.


To use other MCP2221 features together with SMBus class, do not create a new MCP2221 Device.
It will interfere with existing bus with unexpected results.
Always re-use `bus.mcp` object.
