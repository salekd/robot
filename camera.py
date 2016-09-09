import picamera
import picamera.array
import numpy as np
import time
import io
import logging
from PIL import Image
from PIL import ImageChops


class Camera:
    
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (100, 100)
        self.camera.start_preview()
        
        #self.stream = picamera.array.PiYUVArray(self.camera)
        # Define a circular buffer and start recording
        self.stream = picamera.PiCameraCircularIO(self.camera, seconds=10)
        self.camera.start_recording(self.stream, format='h264')

        self.prior_image = None
        self.threshold = 200
        
        
    def capture(self):
        #self.stream.truncate()
        #self.stream.seek(0)
        #self.camera.capture(self.stream, 'yuv')
        #print self.stream.array.shape
        #return self.stream.array

        stream = io.BytesIO()
        self.camera.capture(stream, format='jpeg', use_video_port=True)
        stream.seek(0)
        return Image.open(stream)


    def detect_motion(self):
        
        # Take new snapshot
        current_image = self.capture()

        if self.prior_image is None:
            self.prior_image = current_image
            return False

        else:
            # Compare current_image to prior_image to detect motion
            #diff = ImageChops.difference(current_image, self.prior_image)

            # Mean squared error
            img1 = PIL2array(current_image)
            img2 = PIL2array(self.prior_image)
            mse = np.sum(img1 - img2)
            mse /= img1.shape[0] * img1.shape[1]
            logging.debug("Mean squared error between the two images: %d" % mse)

            self.prior_image = current_image
            return mse > self.threshold


def PIL2array(img):
    return np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
