from camera import *
from led import *
import time
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import logging, sys

from pydrive.drive import GoogleDrive

from pydrive.auth import GoogleAuth
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



logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

camera = Camera()
led = Led()

prior_image = None
prior_timestamp = long(time.time())

time_delay = 15
threshold = 1000

plt.ion()
fig = plt.figure(figsize = (8, 6))
ax = fig.add_subplot(111)

try:
    while True:
        current_timestamp = long(time.time())
        logging.debug(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))

        current_image = camera.capture()
        if not prior_image: prior_image = current_image

        # Mean squared error
        img1 = PIL2array(current_image)
        img2 = PIL2array(prior_image)
        mse = np.sum(img1 - img2)
        mse /= img1.shape[0] * img1.shape[1]
        logging.debug("Mean squared error between the two images: %d" % mse)

        if mse > threshold:
            filename = time.strftime("%Y_%m_%d_%H_%M_%S.jpg", time.localtime())
            current_image.save("motiondetect/"+filename, "JPEG", quality=80, optimize=True, progressive=True)

            #drive = GoogleDrive(gauth)

            #f = drive.CreateFile()
            f = drive.CreateFile({'title': filename, "parents":  [{"kind": "drive#fileLink","id": gid}]})
            f.SetContentFile("motiondetect/"+filename)
            f.Upload()

        try:
            ax.imshow(current_image)
            fig.canvas.draw()
        except:
            logging.debug("Cannot show image, no figure is defined.")

        logging.debug("Elapsed time %ds, waiting additional %ds."%(
            current_timestamp - prior_timestamp,
            max(0, time_delay + prior_timestamp - current_timestamp)))
        time.sleep(max(0, time_delay + prior_timestamp - current_timestamp))
        prior_image = current_image
        prior_timestamp = current_timestamp

# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    print("Bye!")
