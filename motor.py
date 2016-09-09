import RPi.GPIO as GPIO # Import the GPIO Library
import time # Import the Time library
import logging

class Motor:

    # Set variables for the GPIO motor pins
    pinMotorAForwards = 10
    pinMotorABackwards = 9
    pinMotorBForwards = 8
    pinMotorBBackwards = 7

    # How many times to turn the pin on and off each second
    Frequency = 20
    # How long the pin stays on each cycle, as a percent
    DutyCycleA = 30
    DutyCycleB = 30
    # Settng the duty cycle to 0 means the motors will not turn
    Stop = 0


    def __init__(self):
        
        # Set the GPIO modes
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Set the GPIO Pin mode to be Output
        GPIO.setup(self.pinMotorAForwards, GPIO.OUT)
        GPIO.setup(self.pinMotorABackwards, GPIO.OUT)
        GPIO.setup(self.pinMotorBForwards, GPIO.OUT)
        GPIO.setup(self.pinMotorBBackwards, GPIO.OUT)

        # Set the GPIO to software PWM at 'Frequency' Hertz
        self.pwmMotorAForwards = GPIO.PWM(self.pinMotorAForwards, self.Frequency)
        self.pwmMotorABackwards = GPIO.PWM(self.pinMotorABackwards, self.Frequency)
        self.pwmMotorBForwards = GPIO.PWM(self.pinMotorBForwards, self.Frequency)
        self.pwmMotorBBackwards = GPIO.PWM(self.pinMotorBBackwards, self.Frequency)

        # Start the software PWM with a duty cycle of 0 (i.e. not moving)
        self.pwmMotorAForwards.start(self.Stop)
        self.pwmMotorABackwards.start(self.Stop)
        self.pwmMotorBForwards.start(self.Stop)
        self.pwmMotorBBackwards.start(self.Stop)


    def __del__(self):
        # Reset GPIO settings
        GPIO.cleanup()
        

    # Turn all motors off
    def StopMotors(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorABackwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.Stop)


    # Turn both motors forwards
    def Forwards(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.DutyCycleA)
        self.pwmMotorABackwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBForwards.ChangeDutyCycle(self.DutyCycleB)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.Stop)


    # Turn both motors backwards
    def Backwards(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorABackwards.ChangeDutyCycle(self.DutyCycleA)
        self.pwmMotorBForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.DutyCycleB)


    # Turn left
    def Left(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorABackwards.ChangeDutyCycle(self.DutyCycleA)
        self.pwmMotorBForwards.ChangeDutyCycle(self.DutyCycleB)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.Stop)


    # Turn Right
    def Right(self):
        self.pwmMotorAForwards.ChangeDutyCycle(self.DutyCycleA)
        self.pwmMotorABackwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBForwards.ChangeDutyCycle(self.Stop)
        self.pwmMotorBBackwards.ChangeDutyCycle(self.DutyCycleB)