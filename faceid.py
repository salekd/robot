import os, sys, time
import cv2.cv as cv
import cv2
import numpy as np
import logging
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import time
import re
import os
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib



minSize = (20, 20)
imageScale = 1
haarScale = 2
minNeighbors = 3
haarFlags = cv.CV_HAAR_DO_CANNY_PRUNING

cdir = "/usr/share/opencv/haarcascades/"
cascade = cv.Load(cdir + "haarcascade_frontalface_default.xml")



def find_faces(pil_image, save=False):
    """
    Returns an array of identified faces.
    Each face is represented as an 48x48 array of 8-bit integers.

    It is possible to save the identified faces as png images.
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

    # save the faces
    if save:
        for array in face_array:
            s = int(time.time())
            mpimg.imsave('faces/img%4d.png'%s, array, cmap="gray")

    return face_array



def read_faces():
    """
    Returns image data of all faces stored in individual directories for each person.
    Each face is represented as an 48x48 array of 8-bit integers and a string label.
    """

    # initialize arrays for image data and labels
    X = np.empty((0,2304), dtype=np.uint8)
    y = np.empty((0), dtype=np.uint8)

    #subfolders = [f.path for f in os.scandir(os.curdir) if f.is_dir() ]
    subfolders = filter(os.path.isdir, os.listdir(os.curdir))
    tag_directories = filter(lambda x: re.match("tag_.*", x), subfolders)

    for d in tag_directories:
        tag = d[4:]

        #files = filter(os.path.isfile, os.listdir(d))
        files = os.listdir(d)
        for f in files:
            img = mpimg.imread(d + '/' + f)
            lum_img = img[:,:,0]
            arr = np.array( lum_img*256, dtype=np.uint8 )

            X = np.append(X, np.array([arr.flatten()]), axis=0)
            y = np.append(y, tag)

    return X, y



def train_classifier(X, y):
    """
    Returns a trained classifier
    """

    clf = LogisticRegression()
    clf.fit(X, y)

    return clf



def save_classifier(filename='clf.pkl'):
    joblib.dump(clf, filename)



def read_classifier(filename='clf.pkl'):
    return joblib.load(filename)



def identify_faces(faces, clf):
    """
    Identifies persons using a trained classifier
    """

    X = np.empty((0,2304), dtype=np.uint8)
    for face in faces:
        X = np.append(X, np.array([face.flatten()]), axis=0)

    print clf.predict(X)
    print clf.predict_proba(X)
