import io
import socket
import struct
from PIL import Image
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
host = socket.gethostname() #Get the local machine name
port = 8000 # Reserve a port for your service
server_socket.bind((host, port))
server_socket.listen(0)

# Prepare canvas
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')
try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        print('Image is %dx%d' % image.size)
        #image.verify()
        #print('Image is verified')
        
        # Draw image
        ax.imshow(image)
        fig.canvas.draw()
        
finally:
    connection.close()
    server_socket.close()