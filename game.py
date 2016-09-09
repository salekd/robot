import sys
import pygame
from pygame.locals import *
from distance import *
from camera import *
from led import *
from motor import *


def main():

    STOP, LEFT, RIGHT, UP, DOWN = range(5)

    motor = Motor()
    distance = Distance()
    camera = Camera()
    led = Led()
    
    pygame.init()
    pygame.display.set_mode((640, 480))

    direction = STOP
    
    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a):
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d):
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w):
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s):
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()
            elif event.type == KEYUP:
                direction = STOP
        
        
        dist = distance.getDistance()    
        if dist < 10:
            led.on(Led.BLUE)
            if direction == UP: direction = STOP
        else:
            led.off(Led.BLUE)
        
        
        motion = camera.detect_motion()
        if motion: led.on(Led.RED)
        else: led.off(Led.RED)
                

        if direction == UP: motor.Forwards()
        elif direction == DOWN: motor.Backwards()
        elif direction == LEFT: motor.Left()
        elif direction == RIGHT: motor.Right()
        elif direction == STOP: motor.StopMotors()


def terminate():
    pygame.quit()
    sys.exit()
    
    
if __name__ == '__main__':
    main()