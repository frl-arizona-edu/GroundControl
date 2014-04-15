import atexit
import msgpack
import zmq
import os

from ground_control.telemetry import TelemetryData
from ground_control.psql_handle import PostgresHandle

class PlaneQueue(object):

    def __init__(self, host, rhandle):
        self.host = host
        self.rhandle = rhandle

    def run_forever(self):
        addr = "tcp://{}".format(self.host)

        socket = zmq.Context().socket(zmq.REQ)
        socket.connect(addr)

        def teardown_connection():
            socket.disconnect(addr)
            socket.close()

        atexit.register(teardown_connection)

        imagePrefix = "image"
        imageNumber = 0

        # Get last image name
        for f in os.listdir('tmp/'):
            number = int(f[len(imagePrefix):-4])
            imageNumber = max(imageNumber, number)

        while True:
            socket.send_string("ping")

            try:
                message = socket.recv()
                (width, height, image) = msgpack.unpackb(message)
            except KeyboardInterrupt:
                print("+ Connection terminated")
                return

            image = bytearray(image)
            imageNumber += 1

            print('+ Message Received [{}] ({} x {})'.format(len(image), width, height))

            name = "image{0:0>4}".format(imageNumber)
            path = "tmp/{}.jpg".format(name)

            with open(path, 'wb') as f:
                f.write( image )

            print('+ Saved image to [{}]'.format(path))

            if self.rhandle:
                self.rhandle.add_image(name, TelemetryData(**{ 'width': width, 'height': height }))


