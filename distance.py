import RPi.GPIO as GPIO # Import the GPIO Library
import time # Import the Time library
import logging

class Distance:

    # Define GPIO pins to use on the Pi
    pinTrigger = 17
    pinEcho = 18
    
    
    def __init__(self):
        # Set the GPIO modes
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Set pins as output and input
        GPIO.setup(self.pinTrigger, GPIO.OUT)  # Trigger
        GPIO.setup(self.pinEcho, GPIO.IN)      # Echo

        # Set trigger to False (Low)
        GPIO.output(self.pinTrigger, False)

        # Allow module to settle
        time.sleep(0.5)
        

    def __del__(self):
        # Reset GPIO settings
        GPIO.cleanup()
        
        
    def getDistance(self):

        # Send 10us pulse to trigger
        GPIO.output(self.pinTrigger, True)
        time.sleep(0.00001)
        GPIO.output(self.pinTrigger, False)

        # Start the timer
        StartTime = StopTime = time.time()
        
        # The start time is reset until the Echo pin is taken high (==1)
        while GPIO.input(self.pinEcho)==0:
            StartTime = time.time()
            if StartTime-StopTime >= 0.04:
                logging.warning("Echo pin remains low.")
                break

        # Stop when the Echo pin is no longer high - the end time
        while GPIO.input(self.pinEcho)==1:
            StopTime = time.time()
            # If the sensor is too close to an object, the Pi cannot
            # see the echo quickly enough, so we have to detect that
            # problem and say what has happened.
            if StopTime-StartTime >= 0.04:
                logging.warning("Hold on there!  You're too close for me to see.")
                StopTime = StartTime
                break

        # Calculate pulse length
        ElapsedTime = StopTime - StartTime

        # Distance pulse travelled in that time is
        # time multiplied by the speed of sound (cm/s)
        Distance = ElapsedTime * 34326

        # That was the distance there and back so halve the value
        Distance = Distance / 2

        logging.debug("Distance : %.1f cm" % Distance)

        return Distance