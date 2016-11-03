from picamera import PiCamera
from os import system
from time import sleep

camera = PiCamera()
camera.resolution = (1024, 768)
camera.hflip = True
camera.vflip = True

n = 60
for i in range(n):
    if i == 0:
        # The first picture usually does not have an optimal quality (let us take it two times)
        camera.capture('image{0:04d}.jpg'.format(i))
        sleep(1)
    else:
        sleep(60)
    print "Taking picture %d out of %d" % (i + 1, n)
    camera.capture('image{0:04d}.jpg'.format(i))

print "Converting to gif"
system('convert -delay 10 -loop 0 image*.jpg animation.gif')
