import msgpack
import zmq
import tkinter
import sys
import os
import argparse
import atexit

from PIL import Image, ImageTk

from psql_handle import PostgresHandle

def request_images( host, rhandle ):
    addr = "tcp://%s" % host

    socket = zmq.Context().socket(zmq.REQ)
    socket.connect( addr )

    def teardown_connection():
        socket.disconnect( addr )
        socket.close()

    atexit.register( teardown_connection )

    imagePrefix = "image"
    imageNumber = 0

    # Get last image name
    for f in os.listdir('tmp/'):
        number = int(f[len(imagePrefix):-4])
        imageNumber = max( imageNumber, number )

    while True:
        socket.send_string( "Hello" )

        try:
            message = socket.recv()
            (width, height, image) = msgpack.unpackb( message )
        except KeyboardInterrupt:
            print("+ Connection terminated")
            return

        image = bytearray( image )

        imageNumber += 1

        print('+ Message Received [{}] ({} x {})'.format(len( image ), width, height))

        name = "image%04d" % imageNumber
        path = "tmp/%s.jpg" % name

        with open( path, 'wb' ) as f:
            f.write( image )

        print('+ Saved image to [{}]'.format(path))

        if rhandle:
            rhandle.addNewImage( name, { 'width': width, 'height': height } )


def show_image( imagePath ):
    tk = Tkinter.Tk()

    can = Tkinter.Canvas(tk)
    can.pack()
    image = Image.open( imagePath )
    img = ImageTk.PhotoImage( image )
    can.create_image((100, 100), image=img)

    tk.mainloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--airplane",  help="[HOST:PORT]")
    parser.add_argument("-s", "--psqlhost", help="Host address of the Postgres server")
    parser.add_argument("-p", "--psqlport", help="Port of the Postgres server")
    parser.add_argument("--flush",           help="Flushes all keys from the Postgres server", action="store_true")
    parser.add_argument("-i", "--dimage",    help="Launch GUI", action="store_true")
    parser.add_argument("--deltmp",          help="Deletes the contents of the image directory", action="store_true")

    args = parser.parse_args()

    rhandle = None

    if args.deltmp:
        for f in os.listdir('tmp/'):
            path = os.path.join('tmp/', f)

            try:
                if os.path.isfile(path):
                    os.unlink(path)
            except Exception:
                print(e)

    if args.psqlhost and args.psqlport:
        rhandle = PostgresHandle( args.psqlhost, args.psqlport )

        if args.flush:
            rhandle.emptyDatabase()

    if args.dimage:
        show_image( 'test.jpg' )

    if args.airplane:
        request_images( args.airplane, rhandle )
