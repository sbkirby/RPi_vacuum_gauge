import RPi.GPIO as GPIO
import time
import sys
from hx711 import HX711

def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()

hx = HX711(5, 6) # DOUT, PD_SCK, GAIN=128
# DOUT = GPIO.IN
# PD_SCK = GPIO.OUT

hx.set_reading_format("LSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# The first step is to determine the offset value.  I obtain the value for
# the MD-PS002 by calling hx.tare(30), and then reading hx.OFFSET.
# Next, the reference unit or "scale" for mmHg is determined by connecting the
# MD-PS002 to a Vacuum Pump and Vacuum Gauge and reading the hx.get_weight(3).
# The value on the Gauge and  value = value / self.REFERENCE_UNIT
hx.set_reference_unit(230000)
# Reset and set offset for the HX711 amplifier board
hx.reset()
hx.set_offset(11448294) # offset for MD-PS002 Pressure Sensor
hx.tare(5)

while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment the three lines to see what it prints.
        #np_arr8_string = hx.get_np_arr8_string()
        #binary_string = hx.get_binary_string()
        #print binary_string + " " + np_arr8_string

        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        val = hx.get_weight(1)
        print '{0:.1f}'.format(val)

        hx.power_down()
        hx.power_up()
        time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
