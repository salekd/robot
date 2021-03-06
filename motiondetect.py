import picamera
import picamera.array
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import urllib
import logging, sys
import time
import os



# Logging
logging.basicConfig( stream=sys.stderr, level=logging.DEBUG )



# Threshold for the mean-squared error (expected value witout motion is around 10)
threshold1 = 15
# Threshold for coutning the number of pixels that changed
threshold2 = 50
# Threshold for the fraction of pixels that changed (in percent) 
threshold3 = 8.3

prior_image = None
prior_timestamp = time.time()
daydir = time.strftime("%Y_%m_%d", time.localtime(prior_timestamp))

img_array = []
filename_array = []

buff = np.empty(shape=[0, 1])
index = 0



########
# GoogleDrive authorisation 
########

gauth = GoogleAuth()
#gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.

# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")


drive = GoogleDrive(gauth)



########
# Create directory "motiondetect" in case it does not exist
########

# Auto-iterate through all files that matches this query
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
    print('title: %s, id: %s' % (file1['title'], file1['id']))
    if file1['title'] == "motiondetect":
        gid0 = file1['id']

try:
    gid0
except:
    file1 = drive.CreateFile({'title': "motiondetect", "mimeType": "application/vnd.google-apps.folder"})
    file1.Upload()
    gid0 = file1['id']

# Auto-iterate through all files that matches this query
file_list = drive.ListFile({'q': "'%s' in parents and trashed=false"%gid0}).GetList()
for file1 in file_list:
    print('title: %s, id: %s' % (file1['title'], file1['id']))
    if file1['title'] == daydir:
        gid = file1['id']

try:
    gid
except:
    file1 = drive.CreateFile({'title': daydir, "mimeType": "application/vnd.google-apps.folder", "parents": [{"kind": "drive#fileLink","id": gid0}]})
    file1.Upload()
    gid = file1['id']

os.system("mkdir motiondetect/%s"%daydir)
    


########
# Camera settings
########

camera = picamera.PiCamera()
camera.resolution = (1640, 1232)
#camera.resolution = (640, 480)
camera.vflip = True
camera.hflip = True
camera.start_preview()

stream = picamera.array.PiRGBArray(camera)


#plt.ion()
#fig = plt.figure(figsize = (8, 6))
#ax = fig.add_subplot(111)



try:
    while True:

        # Timestamp
        current_timestamp = time.time()
        mlsec = repr(current_timestamp).split('.')[1][:3]
        timestr = time.strftime("%a, %Y-%m-%d %H:%M:%S.{} %Z".format(mlsec), time.localtime(current_timestamp))
        logging.debug(timestr)

        # Capture an image in the RGB format
        camera.capture(stream, 'rgb')
        current_image = stream.array
        stream.seek(0)
        stream.truncate()
        if prior_image is None: prior_image = current_image

        # Mean squared error
        img1 = np.array(current_image).flatten()
        img2 = np.array(prior_image).flatten()
        diff2 = (img1 - img2)**2
        mse = float(np.sum(diff2)) / len(diff2)
        #mse = np.sum(diff2)
        #mse /= img1.shape[0] * img1.shape[1]

        #frac = float(np.sum(diff2 > threshold2)) / len(diff2) * 100.
        ##frac = np.sum(diff2 > threshold2) / len(diff2)

        #motion = mse > threshold1
        #motion = frac > threshold3

        logging.debug( "Mean squared error between the two images: %.4f" % mse )
        #logging.debug( "Fraction of pixels with squared difference above threshold: %.1f%%" % frac )

        if buff.shape[0] < 100:
            buff = np.append(buff, mse)
        else:
            buff[index] = mse
        m = np.mean(buff)
        s = np.std(buff)
        mse_scaled = (mse - m) / s

        logging.debug( "Mean and std of the last %d MSE: %.4f, %.4f" % (buff.shape[0], m, s) )
        logging.debug( "Rescaled MSE: %.4f" % mse_scaled )

        index = index + 1
        if index == 100: index = 0

        motion = abs(mse_scaled) > 5.

        # Is motion detected?
        if motion:
            #timestr = time.strftime("%Y_%m_%d_%H_%M_%S.{}".format(mlsec), time.localtime(current_timestamp))
            timestr = time.strftime("%H_%M_%S.{}".format(mlsec), time.localtime(current_timestamp))
            #filename = timestr + "_mse%.1f_frac%.1f.jpg"%(mse, frac)
            filename = timestr + "_mse%.1f.jpg"%(mse_scaled)
            filename_array.append(filename)

            img = Image.fromarray(current_image)
            img_array.append(img)

            logging.debug( "Motion detected, filename: %s" % filename )

        # Send message to Triggi once motion is no longer detected:
        if not motion and len(filename_array):
            timestr = time.strftime("%H:%M:%S", time.localtime(current_timestamp))
            params = urllib.urlencode({'value': 'motion detected at %s'%timestr})
            urllib.urlopen("https://connect.triggi.com/c/BByu1SmuHezfDWheA0WR?%s"%params)

            logging.debug( "Sending message to Triggi" )

        # Save the images once motion is no longer detected:
        #elif len(filename_array):
        if (not motion and len(filename_array)) or len(filename_array) > 10:
            for img, filename in zip(img_array, filename_array):
                img.save("motiondetect/"+daydir+"/"+filename, "JPEG", quality=80, optimize=True, progressive=True)

                f = drive.CreateFile({'title': filename, "parents":  [{"kind": "drive#fileLink","id": gid}]})
                f.SetContentFile("motiondetect/"+daydir+"/"+filename)
                f.Upload()

                logging.debug( "Saved file %s" % filename )

            # Empy the arrays
            del img_array[:]
            del filename_array[:]

        # Show image in case a figure is defined
        try:
            ax.imshow(current_image)
            fig.canvas.draw()
        except:
            pass

        logging.debug( "Elapsed time: %.3fs" % (current_timestamp - prior_timestamp) )

        prior_image = current_image
        prior_timestamp = current_timestamp



# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    print("Bye!")
