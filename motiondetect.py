import picamera
import picamera.array
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import logging, sys
import time



# Logging
logging.basicConfig( stream=sys.stderr, level=logging.DEBUG )



prior_image = None
prior_timestamp = time.time()

threshold = 100

img_array = []
filename_array = []



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
        gid = file1['id']

try:
    gid
except:
    file1 = drive.CreateFile({'title': "motiondetect", "mimeType": "application/vnd.google-apps.folder"})
    file1.Upload()
    gid = file1['id']



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
        img1 = current_image
        img2 = prior_image
        mse = np.sum((img1 - img2)**2)
        mse /= img1.shape[0] * img1.shape[1]

        logging.debug( "Mean squared error between the two images: %d" % mse )

        # Is motion detected?
        if mse > threshold:
            timestr = time.strftime("%Y_%m_%d_%H_%M_%S.{}".format(mlsec), time.localtime(current_timestamp))
            filename = timestr + "_mse%d.jpg"%mse
            filename_array.append(filename)

            img = Image.fromarray(current_image)
            img_array.append(img)

            logging.debug( "Motion detected, filename = %s" % filename )

        # Save the images after motion is no longer detected:
        elif len(filename_array):
            for img, filename in zip(img_array, filename_array):
                img.save("motiondetect/"+filename, "JPEG", quality=80, optimize=True, progressive=True)

                f = drive.CreateFile({'title': filename, "parents":  [{"kind": "drive#fileLink","id": gid}]})
                f.SetContentFile("motiondetect/"+filename)
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
            logging.debug( "Cannot show image, no figure is defined." )

        logging.debug( "Elapsed time: %.3fs" % (current_timestamp - prior_timestamp) )

        prior_image = current_image
        prior_timestamp = current_timestamp



# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    print("Bye!")
