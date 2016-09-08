from distance import *
from camera import *
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

d = Distance()
c = Camera()

plt.ion()
fig = plt.figure(figsize = (2, 2))
ax = fig.add_subplot(111)

while True:
    d.getDistance()
    
    img = c.capture()
    ax.imshow(img)
    fig.canvas.draw()
    
    time.sleep(0.5)