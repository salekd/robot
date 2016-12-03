import os, sys, time
import cv2.cv as cv
import cv2
import numpy as np
import logging
import matplotlib.pyplot as plt

minSize = (20, 20)
imageScale = 1
haarScale = 2
minNeighbors = 3
haarFlags = cv.CV_HAAR_DO_CANNY_PRUNING

cdir = "/usr/share/opencv/haarcascades/"
cascade = cv.Load(cdir + "haarcascade_frontalface_default.xml")

def find_faces(pil_image):
    """
    Returns an array of identified faces.
    Each face is represented as an 48x48 array of 8-bit integers.
    """

    # convert from PIL to OpenCV
    img = cv.fromarray(cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR))
    #img = cv.fromarray(np.array(pil_image))
    #img = np.array(pil_image)
    #img = cv.LoadImage("../Desktop/IMG_4423-150x150.jpg", 1)

    # allocate temporary images
    gray = cv.CreateImage((img.width,img.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(img.width / imageScale), cv.Round(img.height / imageScale)), 8, 1)
    # convert color input image to grayscale
    cv.CvtColor(img, gray, cv.CV_BGR2GRAY)
    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)
    cv.EqualizeHist(small_img, small_img)
    faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0),haarScale, minNeighbors, haarFlags, minSize)

    face_array = []
    if faces:
        print "\tDetected ", len(faces), " object(s)"
        for ((x, y, w, h), n) in faces:
            #the input to cv.HaarDetectObjects was resized, scale the
            #bounding box of each face and convert it to two CvPoints
            pt1 = (int(x * imageScale), int(y * imageScale))
            pt2 = (int((x + w) * imageScale), int((y + h) * imageScale))
            cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
            
            face_img = small_img[y:y+h, x:x+w]
            #print face_img
            face_small = cv.CreateImage((48, 48), 8, 1)
            cv.Resize(face_img, face_small, cv.CV_INTER_LINEAR)
            #print face_small
            #print x, y, w, h, n

            #arr = np.fromstring( face_small.tostring(), dtype='c' ).reshape((48, 48))
            arr = np.fromstring( face_small.tostring(), dtype=np.uint8 ).reshape((48, 48))
            #print arr.shape
            #print arr
            face_array.append(arr)

#            plt.ion()
#            fig = plt.figure(figsize = (4, 3))
#            ax = fig.add_subplot(111)
#            ax.imshow(arr, cmap='gray')
            #ax.imshow(face_img, cmap='gray')
#            fig.canvas.draw()

    return face_array
