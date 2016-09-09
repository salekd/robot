import RPi.GPIO as GPIO # Import the GPIO Library
import time # Import the Time library
import logging

class Led:

    # Define GPIO pins to use on the Pi
    pinBlue = 22
    pinRed = 23
    
    # LED masks
    BLUE = 0b01
    RED = 0b10
    
    
    def __init__(self):
        # Set the GPIO naming convention
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Set the three GPIO pins for Output
        GPIO.setup(self.pinBlue, GPIO.OUT)
        GPIO.setup(self.pinRed, GPIO.OUT)


    def __del__(self):
        # Reset GPIO settings
        GPIO.cleanup()
        
        
    def on(self, mask = 0b11):
        if mask & self.BLUE: GPIO.output(self.pinBlue, GPIO.HIGH)
        if mask & self.RED: GPIO.output(self.pinRed, GPIO.HIGH)


    def off(self, mask = 0b11):
        if mask & self.BLUE: GPIO.output(self.pinBlue, GPIO.LOW)
        if mask & self.RED: GPIO.output(self.pinRed, GPIO.LOW)


    def blink(self, mask = 0b11):
        self.on(mask)
        time.sleep(0.1)
        self.off(mask)