from time import sleep
import RPi.GPIO as GPIO
import ky040

CLOCKPIN  = 18 #GPIO Pin 18 - Pin 12
DATAPIN   = 17 #GPIO Pin 17 - Pin 11
SWITCHPIN = 27 #GPIO Pin 27 - Pin 13

def rotaryChange(direction):
    if (direction == 1):  # Clockwise
    	ky040.globalCounter = ky040.globalCounter + 1
    if (direction == 0):  # Coutner Clockwise
    	ky040.globalCounter = ky040.globalCounter - 1
    #print "turned - " + str(direction)
    print 'globalCounter = %d' % ky040.globalCounter

def switchPressed():
    print "button pressed"

GPIO.setmode(GPIO.BCM)
ky040 = ky040.KY040(CLOCKPIN, DATAPIN, SWITCHPIN, rotaryChange, switchPressed)
ky040.start()
ky040.globalCounter = 0

try:
    while True:
        sleep(0.1)
finally:
    ky040.stop()
    GPIO.cleanup()
