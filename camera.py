import picamera
import picamera.array
import numpy as np
import time


class Camera:
    
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (100, 100)
        self.camera.start_preview()
        
        self.stream = picamera.array.PiYUVArray(self.camera)
        
        
    def capture(self):
        #self.stream.truncate(0)
        self.stream.seek(0)
        self.camera.capture(self.stream, 'yuv')
        #print self.stream.array.shape
        
        return self.stream.array