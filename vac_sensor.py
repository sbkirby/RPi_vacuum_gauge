#!/usr/bin/python
#
# Originally lcdmenu.py created by Alan Aufderheide, February 2013
# Modified by Stephen Kirby, November 2017
#
# This provides a menu driven application using the Adafruit_CharLCDPlate
# driver

import commands
import os
from string import split
from time import sleep, strftime, localtime
from datetime import datetime, timedelta
from xml.dom.minidom import *
from ListSelector import ListSelector

import smbus

import json
import sys
from Queue import Queue
import RotaryEncoder
import RPi_I2C_driver
from hx711 import HX711
import RPi.GPIO as GPIO

# Load configuration from config JSON file.
with open('config.json', 'r') as infile:
    config = json.load(infile)

menu_file = 'vac_menu.xml' # Menu Tree

# Rotary Encoder wiring
A_PIN  = 21 # A pin on rotary encoder or DT on KY040
B_PIN  = 16 # B pin on rotary encoder or CLK on KY040
SW_PIN = 20 # press pin on rotary or SW on KY040

# Init Queue and Encoder
RotQueue = Queue()                                                              # define global queue for events
encoder = RotaryEncoder.RotaryEncoderWorker(A_PIN, B_PIN, SW_PIN, RotQueue)     # create a new rotary switch

# set DEBUG=1 for print debug statements
DEBUG = 0
DISPLAY_ROWS = 4
DISPLAY_COLS = 20

# set to 0 if you want the LCD to stay on, 1 to turn off and on auto
AUTO_OFF_LCD = 0

# Menu Folders to display Selected items
menu_select = ["units"]

# init LCD
lcd = RPi_I2C_driver.lcd()
lcd.lcd_clear()
lcd.backlight(1) # turn ON LED

# HX711(dout, sck) - initialize Wheatstone Bridge amplifier
hx = HX711(5, 6)  # DOUT = GPIO.IN, SCK = GPIO.OUT
# The value on the Gauge = value / self.REFERENCE_UNIT
hx.set_reference_unit(config['calibration_factor'])
# Reset and set offset for the HX711 amplifier board
hx.reset()
hx.set_offset(config['offset']) # set offset for MD-PS002 Pressure Sensor
hx.tare(5) # with no Vacuum on Sensor

# Init GPIO output port for Relay control
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.output(12, False) # Turn OFF Relay

# save data to config.json data file
def save_data():
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile)

# save the data, cleanup GPIO and exit
def clean_and_exit(doExit):
    save_data() # save data file
    lcd.lcd_clear() # clear LCD
    sleep(0.1)
    lcd.backlight(0) # turn OFF LED
    sleep(0.1)
    GPIO.cleanup() # cleanup GPIO
    if doExit:
        sys.exit() #exit python to system

def DoShutdown():
    lcd.lcd_clear()
    lcd.message("Shutting Down!")
    sleep(3)
    clean_and_exit(False)
    commands.getoutput("sudo shutdown -h now")

def DoReboot():
    lcd.lcd_clear()
    lcd.message("I'm Rebooting!")
    sleep(3)
    clean_and_exit(False)
    commands.getoutput("sudo reboot")

# Go BACK in the Menu
def DoBack():
    lcd.lcd_clear()
    display.update('l')
    #display.update('s')
    display.display()
    sleep(0.05)

# Calculate Cutoff range
def SetCutoffRange(state):
    # Range of Vacuum Pump activation
    cutoff_range = config['cutoff_range'] / 100
    if state == 'ON':
        return (-cutoff_range * config["vacuum_set"]) + config["vacuum_set"]
    if state == 'OFF':
        return (cutoff_range * config["vacuum_set"]) + config["vacuum_set"]

# Fetch Units String
def GetUnit():
    if config['units'] == 0: # in-Hg    DEFAULT
        unit = 'in-Hg'
    elif config['units'] == 1: # mm-Hg
        unit = 'mm-Hg'
    elif config['units'] == 2: # psi
        unit = 'psi'
    return unit

# Convert from in-Hg to other units
def ConvertVac(vac):
    if config['units'] == 0: # in-Hg    DEFAULT
        vac *= 1.0
    elif config['units'] == 1: # mm-Hg
        vac *= 25.3285
    elif config['units'] == 2: # psi
        vac *= 0.48977
    return vac

# Select Units
def SetinHg(): #DEFAULT
    config['units'] = 0
    display.display()

def SetmmHg():
    config['units'] = 1
    display.display()

def Setpsi():
    config['units'] = 2
    display.display()

# Display Vacuum and Cutoff on LCD Display
def DoDisplay():
    lcd.lcd_clear()
    unit = GetUnit()
    VacSet = ConvertVac(config['vacuum_set'])
    VacSetOFF = ConvertVac(SetCutoffRange('OFF'))
    VacSetON = ConvertVac(SetCutoffRange('ON'))
    GPIO.output(12, False) # Turn OFF Relay
    if DEBUG:
        print('OFF: {0:.2f}'.format(VacSetOFF) + ' ' + unit)
        print('ON: {0:.2f}'.format(VacSetON) + ' ' + unit)

    while True:
        # Read Vacuum Sensor
        val = VacVal = ConvertVac(hx.get_weight(1))
        if DEBUG:
            print('{0:.2f}'.format(VacVal) + ' ' + unit)
        # Monitor Vacuum Cutoff Value
        if VacVal <= VacSetOFF:
            GPIO.output(12, False) # Turn OFF Relay
            #sleep(0.05)
        elif VacVal > VacSetON:
            GPIO.output(12, True) # Turn ON Relay
            #sleep(0.05)
        # Display Results
        lcd.home()
        lcd.message('   VACUUM - ' + unit + '\n      [{0:.2f}]'.format(VacSet) + '\n\n')
        lcd.message('       {0:.2f}'.format(val))
        # Reset Wheatstone Bridge
        hx.power_down()
        hx.power_up()
        # Read RotaryEncoder
        if not(RotQueue.empty()):
            m = RotQueue.get_nowait()
            if (m == RotaryEncoder.EventDown): #SELECT
                GPIO.output(12, False) # Turn OFF Relay on Exit
                RotQueue.task_done()
                DoBack()
                return
            RotQueue.task_done()

# Display and set Cutoff Vacuum
def SetCutoff():
    lcd.lcd_clear()
    unit = GetUnit()
    while True:
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        val = ConvertVac(config["vacuum_set"]) # Stored in in-Hg reguardless of units selected
        if DEBUG:
            print('{0:.2f}'.format(val) + ' ' + unit)
        lcd.home()
        lcd.message('VAC CUTOFF - ' + unit + '\n\n')
        lcd.message('      {0:.2f}'.format(val))
        # Read RotaryEncoder
        if not(RotQueue.empty()):
            m = RotQueue.get_nowait()
            if (m == RotaryEncoder.EventDown): #SELECT - Exit
                RotQueue.task_done()
                DoBack()
                return
            if (m == RotaryEncoder.EventLeft): #LEFT - Subtract
                config["vacuum_set"] -= 0.25
            if (m == RotaryEncoder.EventRight): #RIGHT - Add
                config["vacuum_set"] += 0.25
            RotQueue.task_done()

# Tare Vacuum Sensor
def DoTare():
    lcd.lcd_clear()
    lcd.message('\n Tare Vac Sensor\n')
    hx.reset()
    hx.set_offset(config['offset']) # set offset for MD-PS002 Pressure Sensor
    hx.tare(5) # with no Vacuum on Sensor
    config['offset'] = hx.OFFSET # read and store the OFFSET
    save_data() # save the new OFFSET to config.json data file
    sleep(3)

def ShowIPAddress():
    if DEBUG:
        print('in ShowIPAddress')
    lcd.lcd_clear()
    lcd.message(commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:])
    while True:
        if not(RotQueue.empty()):
            m = RotQueue.get_nowait()
            if (m == RotaryEncoder.EventDown): #SELECT
                DoBack()
                return
            RotQueue.task_done()

# Classes Used in Menus
class CommandToRun:
    def __init__(self, myName, theCommand):
        self.text = myName
        self.commandToRun = theCommand
    def Run(self):
        self.clist = split(commands.getoutput(self.commandToRun), '\n')
        if len(self.clist) > 0:
            lcd.lcd_clear()
            lcd.message(self.clist[0])
            lcd.crlf()
            for i in range(1, len(self.clist)):
                while not(RotQueue.empty()):
                    m=RotQueue.get_nowait()
                    if m == RotaryEncoder.EventLeft: #DOWN
                        break
                    RotQueue.task_done()
                    #sleep(0.25)
                lcd.lcd_clear()
                lcd.message(self.clist[i-1]+'\n'+self.clist[i])
                lcd.crlf()
                sleep(0.5)
        while not(RotQueue.empty()):
            m=RotQueue.get_nowait()
            if m == RotaryEncoder.EventRight:  #UP
                break
            RotQueue.task_done()

class Widget:
    def __init__(self, myName, myFunction):
        self.text = myName
        self.function = myFunction

class Folder:
    def __init__(self, myName, myParent):
        self.text = myName
        self.items = []
        self.parent = myParent

# Process menu items based on type
def ProcessNode(currentNode, currentItem):
    children = currentNode.childNodes

    for child in children:
        if isinstance(child, xml.dom.minidom.Element):
            if child.tagName == 'folder':
                thisFolder = Folder(child.getAttribute('text'), currentItem)
                currentItem.items.append(thisFolder)
                ProcessNode(child, thisFolder)
            elif child.tagName == 'widget':
                thisWidget = Widget(child.getAttribute('text'), child.getAttribute('function'))
                currentItem.items.append(thisWidget)
            elif child.tagName == 'run':
                thisCommand = CommandToRun(child.getAttribute('text'), child.firstChild.data)
                currentItem.items.append(thisCommand)

class Display:
    def __init__(self, folder):
        self.curFolder = folder
        self.curTopItem = 0
        self.curSelectedItem = 0
    def display(self):
        isSelected = match_selected = ''
        # Check for Bottom of items list
        if self.curTopItem > len(self.curFolder.items) - DISPLAY_ROWS:
            self.curTopItem = len(self.curFolder.items) - DISPLAY_ROWS
        # Check for Top of items list
        if self.curTopItem < 0:
            self.curTopItem = 0
        if DEBUG:
            print('------------------')
        if self.curFolder.text[0:self.curFolder.text.find(' ')].lower() in menu_select:
            isSpace = self.curFolder.text.find(' ')
            if isSpace < 0:
                isSpace = self.curFolder.text.len()
            isSelected = self.curFolder.text[0:isSpace].lower()
        str = ''
        for row in range(self.curTopItem, self.curTopItem + DISPLAY_ROWS):
            if isSelected != '':
                if isSelected == 'units':
                    match_selected = GetUnit()
            if row > self.curTopItem:
                str += '\n'
            if row < len(self.curFolder.items):
                # Is row the current selected line
                if row == self.curSelectedItem:
                    # Current line with cursor
                    cmd = '>' + self.curFolder.items[row].text
                    if self.curFolder.items[row].text.lower() == match_selected.lower():
                        cmd += '*'
                    if len(cmd) < DISPLAY_COLS:
                        # Add spaces to END of line
                        for row in range(len(cmd), DISPLAY_COLS):
                            cmd += ' '
                    if DEBUG:
                        print('|'+cmd+'|')
                    str += cmd
                # If NOT currently selected line
                else:
                    # Lines without cursor - Add space for NO cursor
                    cmd = ' '+self.curFolder.items[row].text
                    if self.curFolder.items[row].text.lower() == match_selected.lower():
                        cmd += '*'
                    if len(cmd) < DISPLAY_COLS:
                        # Add spaces to END of line
                        for row in range(len(cmd), DISPLAY_COLS):
                            cmd += ' '
                    if DEBUG:
                        print('|'+cmd+'|')
                    str += cmd
        if DEBUG:
            print('------------------')
        lcd.lcd_clear()
        lcd.home()
        lcd.message(str)

    # Orignal update() designed for LCD with 4 Buttons (Left, Right, Up, Down)
    # This function has been utilized as follows:
    # UP = Clockwise knob turn
    # DOWN = Counter clockwise knob turn
    # SELECT = Press knob DOWN
    def update(self, command):
        global currentLcd
        global lcdstart
        #lcd.backlight(currentLcd)
        lcdstart = datetime.now()
        if DEBUG:
            print('do',command)
        if command == 'u':
            self.up()
        elif command == 'd':
            self.down()
        elif command == 'r':
            self.right()
        elif command == 'l':
            self.left()
        elif command == 's':
            self.select()

    def up(self):
        if self.curSelectedItem == 0:
            return
        elif self.curSelectedItem > self.curTopItem:
            self.curSelectedItem -= 1
        else:
            self.curTopItem -= 1
            self.curSelectedItem -= 1

    def down(self):
        if self.curSelectedItem+1 == len(self.curFolder.items):
            return
        elif self.curSelectedItem < self.curTopItem+DISPLAY_ROWS-1:
            self.curSelectedItem += 1
        else:
            self.curTopItem += 1
            self.curSelectedItem += 1

    def left(self):
        if isinstance(self.curFolder.parent, Folder):
            # find the current in the parent
            itemno = 0
            index = 0
            for item in self.curFolder.parent.items:
                if self.curFolder == item:
                    if DEBUG:
                        print('foundit')
                    index = itemno
                else:
                    itemno += 1
            if index < len(self.curFolder.parent.items):
                self.curFolder = self.curFolder.parent
                self.curTopItem = index
                self.curSelectedItem = index
            else:
                self.curFolder = self.curFolder.parent
                self.curTopItem = 0
                self.curSelectedItem = 0

    def right(self):
        if isinstance(self.curFolder.items[self.curSelectedItem], Folder):
            self.curFolder = self.curFolder.items[self.curSelectedItem]
            self.curTopItem = 0
            self.curSelectedItem = 0
        elif isinstance(self.curFolder.items[self.curSelectedItem], Widget):
            if DEBUG:
                print('eval', self.curFolder.items[self.curSelectedItem].function)
            eval(self.curFolder.items[self.curSelectedItem].function+'()')
        elif isinstance(self.curFolder.items[self.curSelectedItem], CommandToRun):
            self.curFolder.items[self.curSelectedItem].Run()

    def select(self):
        if DEBUG:
            print('check widget')
        if isinstance(self.curFolder.items[self.curSelectedItem], Widget):
            if DEBUG:
                print('eval', self.curFolder.items[self.curSelectedItem].function)
            eval(self.curFolder.items[self.curSelectedItem].function+'()')

# Process Rotary Encoder Actions with a Queue
def process():
    # this function can be called in order to decide what is happening with the switch
    while True:
        if not(RotQueue.empty()):
            m=RotQueue.get_nowait()
            # DOWN = Counter clockwise knob turn
            if m == RotaryEncoder.EventLeft: #DOWN
                display.update('d') #DOWN
                display.display()
                sleep(0.1)
            # SELECT = Press knob DOWN
            if m == RotaryEncoder.EventDown: #SELECT
                display.update('r') #RIGHT
                #display.update('s') #SELECT
                display.display()
                sleep(0.1)
            # UP = Clockwise knob turn
            if m == RotaryEncoder.EventRight: #UP
                display.update('u') #UP
                display.display()
                sleep(0.1)

            if AUTO_OFF_LCD:
                lcdtmp = lcdstart + timedelta(seconds=5)
                if (datetime.now() > lcdtmp):
                    #lcd.backlight(lcd.OFF)
                    #sleep(0.1)
                    pass
            RotQueue.task_done()

# now start things up
uiItems = Folder('root','')

dom = parse(menu_file) # parse an XML file by name

top = dom.documentElement

currentLcd = False
#lcd.backlight(lcd.OFF)
ProcessNode(top, uiItems)

display = Display(uiItems)
display.display()

if DEBUG:
    print('start while')

lcdstart = datetime.now()

if __name__ == "__main__":
    try:
        while True:
            if DEBUG:
                print('__main__')
            #sleep (0.01)  # here you can process on RPI whatever you want and operate the rotary knob it won't be missed
            process()  # and check what has happened with rotary
    except KeyboardInterrupt:
        print('broken by keyboard')
        clean_and_exit(True)
