import RPi.GPIO as GPIO
import math
import threading
from Queue import Queue

EventLeft  = 'L'
EventRight = 'R'
EventUp    = 'U'
EventDown  = 'D'


class RotaryEncoderWorker(object):

    def __init__(self, a_pin, b_pin, s_pin, Q):

        self.gpio = GPIO
        self.gpio.setwarnings(False)
        self.queue = Q

        self.a_pin = a_pin
        self.b_pin = b_pin
        self.s_pin = s_pin

        self.gpio.setmode(GPIO.BCM)
        #Rotary
        self.gpio.setup(self.a_pin, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
        self.gpio.setup(self.b_pin, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)

        self.gpio.add_event_detect(self.a_pin, GPIO.BOTH, callback=self.RotaryCall)
        self.gpio.add_event_detect(self.b_pin, GPIO.BOTH, callback=self.RotaryCall)

        #Switch
        self.gpio.setup(self.s_pin, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
        self.gpio.add_event_detect(self.s_pin, GPIO.BOTH, callback=self.SwitchCall, bouncetime=50) # depending on hardware the debouncing can be done by software or hardware here we used software version 

        self.SWPrev = 1

        self.last_delta = 0
        self.r_seq = 0

        # steps_per_cycle and remainder are only used in get_cycles which
        # returns a coarse-granularity step count.  By default
        # steps_per_cycle is 4 as there are 4 steps per
        # detent on my encoder, and get_cycles() will return -1 or 1
        # for each full detent step.
        self.steps_per_cycle = 4
        self.remainder = 0
        self.cycles = 0

        #self.lock = threading.Lock()
        self.delta = 0

    def SwitchCall(self, channel):
        state = self.gpio.input(self.s_pin)
        if state == 0:
            if self.SWPrev == 1:
                #print ("Switch Down")
                self.SWPrev = 0
                self.queue.put(EventDown)
            else: #still pressed
                pass
        else: # state = 1
            if self.SWPrev == 0:
                #print ("Switch Up")
                self.SWPrev = 1
                self.queue.put(EventUp)
            else: #still pressed
                pass

    # Inspired by http://guy.carpenter.id.au/gaugette/blog/2013/01/14/rotary-encoder-library-for-the-raspberry-pi/
    # Returns the quadrature encoder state converted into
    # a numerical sequence 0,1,2,3,0,1,2,3...
    #
    # Turning the encoder clockwise generates these
    # values for switches B and A:
    #  B A
    #  0 0
    #  0 1
    #  1 1
    #  1 0
    # We convert these to an ordinal sequence number by returning
    #   seq = (A ^ B) | B << 2

    def RotaryCall(self, channel):
        delta = 0
        a_state = self.gpio.input(self.a_pin)
        b_state = self.gpio.input(self.b_pin)
        r_seq = (a_state ^ b_state) | b_state << 1
        if r_seq != self.r_seq:
            delta = (r_seq - self.r_seq) % 4
            if delta==3:
                delta = -1
            elif delta==2:
                delta = int(math.copysign(delta, self.last_delta))  # same direction as previous, 2 steps
            self.last_delta = delta
            self.r_seq = r_seq
        self.delta += delta
        self.remainder += delta #self.get_delta()
        self.cycles = self.remainder // self.steps_per_cycle
        self.remainder %= self.steps_per_cycle # remainder always remains positive
        # Check rotary status
        if self.cycles == 1:
            self.queue.put(EventLeft)
            self.delta = 0
        elif self.cycles == -1:
            self.queue.put(EventRight)
            self.delta = 0
        else:
            pass

    # it does not work as expected fix me
    def __del__(self):
        self.gpio.cleanup()
        
    #workaround to close gpio in a proper way, function shall be called at exit 
    def Exit(self):
        self.gpio.cleanup()
        
        