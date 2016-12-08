from distance import *
from camera import *
from led import *
from motor import *
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import logging, sys
import faceid

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

distance = Distance()
camera = Camera()
led = Led()
motor = Motor()

#plt.ion()
#fig = plt.figure(figsize = (4, 3))
#ax = fig.add_subplot(111)

X,y = faceid.read_faces()
clf = faceid.train_classifier(X,y)


try:
    while True:
        dist = distance.getDistance()
    
        if dist < 30:
            led.on(Led.BLUE)
            motor.StopMotors()
        else:
            led.off(Led.BLUE)
            motor.Forwards()
    
        image = camera.capture()
#        ax.imshow(image)
#        fig.canvas.draw()
        
#        motion = camera.detect_motion()
    
#        if motion: led.on(Led.RED)
#        else: led.off(Led.RED)
    
        #faces = faceid.find_faces(image, save=True)
        faces = faceid.find_faces(image)
        if faces:
            faceid.identify_faces(faces, clf)
        #time.sleep(0.5)


# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    print("Bye!")
