# -*- coding: utf-8 -*-
"""
Compiled, mashed and generally mutilated 2014-2015 by Denis Pleic
Made available under GNU GENERAL PUBLIC LICENSE

# Modified Python I2C library for Raspberry Pi
# as found on http://www.recantha.co.uk/blog/?p=4849
# Joined existing 'i2c_lib.py' and 'lcddriver.py' into a single library
# added bits and pieces from various sources
# By DenisFromHR (Denis Pleic)
# 2015-02-10, ver 0.1

A large amount of the code was included from Adafruit_CharLCDPlate

"""
#
#
import smbus
from time import *

class i2c_device:
   def __init__(self, addr, port=1):
      self.addr = addr
      self.bus = smbus.SMBus(port)

# Write a single command
   def write_cmd(self, cmd):
      self.bus.write_byte(self.addr, cmd)
      sleep(0.0001)

# Write a command and argument
   def write_cmd_arg(self, cmd, data):
      self.bus.write_byte_data(self.addr, cmd, data)
      sleep(0.0001)

# Write a block of data
   def write_block_data(self, cmd, data):
      self.bus.write_block_data(self.addr, cmd, data)
      sleep(0.0001)

# Read a single byte
   def read(self):
      return self.bus.read_byte(self.addr)

# Read
   def read_data(self, cmd):
      return self.bus.read_byte_data(self.addr, cmd)

# Read a block of data
   def read_block_data(self, cmd):
      return self.bus.read_block_data(self.addr, cmd)



class lcd:
    # LCD Address
    ADDRESS = 0x27

    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    # flags for backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    # Offset for up to 4 rows.
    LCD_ROW_OFFSETS         = (0x00, 0x40, 0x14, 0x54)

    # Line addresses for up to 4 line displays.  Maps line number to DDRAM address for line.
    LINE_ADDRESSES = { 1: 0xC0, 2: 0x94, 3: 0xD4 }

    # Truncation constants for message function truncate parameter.
    NO_TRUNCATE       = 0
    TRUNCATE          = 1
    TRUNCATE_ELLIPSIS = 2

    En = 0b00000100 # Enable bit
    Rw = 0b00000010 # Read/Write bit
    Rs = 0b00000001 # Register select bit

    #initializes objects and lcd
    def __init__(self):
        self.lcd_device = i2c_device(self.ADDRESS)

        # Initialize display control, function, and mode registers.
        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_2LINE | self.LCD_5x8DOTS
        self.displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT

        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)

        # Write registers.
        self.lcd_write(self.LCD_DISPLAYCONTROL | self.displaycontrol)
        self.lcd_write(self.LCD_FUNCTIONSET | self.displayfunction)
        self.lcd_write(self.LCD_ENTRYMODESET | self.displaymode)  # set the entry mode

        sleep(0.2)

    # clocks EN to latch command
    def lcd_strobe(self, data):
        self.lcd_device.write_cmd(data | self.En | self.LCD_BACKLIGHT)
        sleep(.0005)
        self.lcd_device.write_cmd(((data & ~self.En) | self.LCD_BACKLIGHT))
        sleep(.0001)

    def lcd_write_four_bits(self, data):
        self.lcd_device.write_cmd(data | self.LCD_BACKLIGHT)
        self.lcd_strobe(data)

    # write a command to lcd
    def lcd_write(self, cmd, mode=0):
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

    # write a character to lcd (or character rom) 0x09: backlight | RS=DR<
    # works!
    def lcd_write_char(self, charvalue, mode=1):
        self.lcd_write_four_bits(mode | (charvalue & 0xF0))
        self.lcd_write_four_bits(mode | ((charvalue << 4) & 0xF0))

    # put string function
    def lcd_display_string(self, string, line):
        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)
        if line == 3:
            self.lcd_write(0x94)
        if line == 4:
            self.lcd_write(0xD4)

        for char in string:
            self.lcd_write(ord(char), self.Rs)

    # clear lcd and set to home
    def lcd_clear(self):
        self.lcd_write(self.LCD_CLEARDISPLAY)
        self.lcd_write(self.LCD_RETURNHOME)

    # define backlight on/off (lcd.backlight(1); off= lcd.backlight(0)
    def backlight(self, state): # for state, 1 = on, 0 = off
        if state == 1:
            self.lcd_device.write_cmd(self.LCD_BACKLIGHT)
        elif state == 0:
            self.lcd_device.write_cmd(self.LCD_NOBACKLIGHT)

    # add custom characters (0 - 7)
    def lcd_load_custom_chars(self, fontdata):
        self.lcd_write(0x40);
        for char in fontdata:
            for line in char:
                self.lcd_write_char(line)

    # define precise positioning (addition from the forum)
    def lcd_display_string_pos(self, string, line, pos):
        if line == 1:
            pos_new = pos
        elif line == 2:
            pos_new = 0x40 + pos
        elif line == 3:
            pos_new = 0x14 + pos
        elif line == 4:
            pos_new = 0x54 + pos

        self.lcd_write(0x80 + pos_new)

        for char in string:
            self.lcd_write(ord(char), self.Rs)

#============= from Adafruit_CharLCDPlate =======================
#       Written by Adafruit Industries.  MIT license.

    def begin(self, cols, lines):
        self.currline = 0
        self.numlines = lines
        self.numcols = cols
        self.lcd_clear()

    def home(self):
        self.lcd_write(self.LCD_RETURNHOME)
        sleep(.3)  # this command takes a long time!

    def message(self, text, truncate=NO_TRUNCATE):
        """ Send string to LCD. Newline wraps to second line"""
        lines = str(text).split('\n')    # Split at newline(s)
        for i, line in enumerate(lines): # For each substring...
            address = self.LINE_ADDRESSES.get(i, None)
            if address is not None:      # If newline(s),
                self.lcd_write(address)      #  set DDRAM address to line
            # Handle appropriate truncation if requested.
            linelen = len(line)
            if truncate == self.TRUNCATE and linelen > self.numcols:
                # Hard truncation of line.
                for char in line[0:self.numcols]:
                    self.lcd_write(ord(char), self.Rs)
            elif truncate == self.TRUNCATE_ELLIPSIS and linelen > self.numcols:
                # Nicer truncation with ellipses.
                for char in (line[0:self.numcols-3] + '...'):
                    self.lcd_write(ord(char), self.Rs)
            else:
                for char in line:
                    self.lcd_write(ord(char), self.Rs)
