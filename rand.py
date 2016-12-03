import random
import time
from distance import *
from camera import *
from led import *
from motor import *


motor = Motor()
distance = Distance()
camera = Camera()
led = Led()

LEFT, RIGHT, UP, DOWN = range(4)

direction = UP
duration = 100
timer = 0
motor.Forwards()


try:
    while True: # main game loop
        
        dist = distance.getDistance()    
        print("Distance : %.1f cm" % dist)
        if dist < 30:
            led.on(Led.BLUE)
        else:
            led.off(Led.BLUE)

        if direction == UP:
            if dist < 30:
                direction = DOWN
                duration = 30
                timer = 0
                motor.SetDutyCycle(30, 30)
                motor.Backwards()
            elif dist < 60:
                motor.SetDutyCycle(30, 30)
                motor.Forwards()


        if duration == timer:
            if direction == UP or direction == DOWN:
                direction = int(random.random() * 2)
                duration = int(random.random() * 50) + 1
            else:
                direction = UP
                duration = 100
            timer = 0
            if direction == UP:
                motor.SetDutyCycle(60, 60)
                motor.Forwards()
            elif direction == LEFT:
                motor.SetDutyCycle(30, 30)
                motor.Left()
            elif direction == RIGHT:
                motor.SetDutyCycle(30, 30)
                motor.Right()

        time.sleep(0.1)
        timer = timer + 1


# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    motor.StopMotors()
    print("Bye!")
