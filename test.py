from distance import *
from camera import *
from led import *
from motor import *
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

distance = Distance()
camera = Camera()
led = Led()
motor = Motor()

#plt.ion()
#fig = plt.figure(figsize = (2, 2))
#ax = fig.add_subplot(111)

while True:
    dist = distance.getDistance()
    
    if dist < 10:
        led.on(Led.BLUE)
        motor.StopMotors()
    else:
        led.off(Led.BLUE)
        motor.Forwards()
    
    #img = c.capture()
    #ax.imshow(img)
    #fig.canvas.draw()
    motion = camera.detect_motion()
    
    if motion: led.on(Led.RED)
    else: led.off(Led.RED)
    
    #time.sleep(0.5)
