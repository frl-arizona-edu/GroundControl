import msgpack
import zmq
import Tkinter
import sys
import os
import argparse
import atexit

from PIL import Image, ImageTk

from redis_interface import RedisHandle

def request_images( host, rhandle ):
    addr = "tcp://%s" % host

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect( addr )

    print 'Opening TCP Connection [%s]' % addr

    def teardown_connection():
        socket.disconnect( addr )
        socket.close()

    atexit.register( teardown_connection )

    imageNumber = 0

    while True:
        socket.send( "Hello" )

        try:
            message = socket.recv()
        except KeyboardInterrupt:
            print "+ Connection terminated"
            return

        (width, height, image) = msgpack.unpackb( message )
        image = bytearray( image )

        imageNumber += 1

        print '+ Message Received [%d] (%s x %s)' % (len( image ), width, height)

        path = 'tmp/image%04d.jpg' % imageNumber

        with open( path, 'a' ) as f:
            f.write( image )

        print '+ Saved image to [%s]' % path

        if rhandle:
            rhandle.addNewImage( path, { 'width': width, 'height': height } )


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
    parser.add_argument("-s", "--redishost", help="Host address of the Redis server")
    parser.add_argument("-p", "--redisport", help="Port of the Redis server")
    parser.add_argument("--flush",           help="Flushes all keys from the Redis server", action="store_true")
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
            except Exception, e:
                print e

    if args.redishost and args.redisport:
        rhandle = RedisHandle( args.redishost, args.redisport )

        if args.flush:
            rhandle.emptyDatabase()

    """
    rhandle.addNewImage( 'test.jpg1', { 'x': 100, 'y': 100 } )
    rhandle.addNewImage( 'test.jpg2', { 'x': 100, 'y': 100 } )
    rhandle.addNewImage( 'test.jpg3', { 'x': 100, 'y': 100 } )
    rhandle.addNewImage( 'test.jpg4', { 'x': 100, 'y': 100 } )


    rhandle.getNextImage()
    rhandle.getNextImage()
    rhandle.getNextImage()
    rhandle.getNextImage()

    rhandle.detectedImage( 'test.jpg1', {} )
    rhandle.detectedImage( 'test.jpg2', {} )
    rhandle.detectedImage( 'test.jpg3', {} )
    rhandle.detectedImage( 'test.jpg4', {} )
    """

    if args.dimage:
        show_image( 'test.jpg' )

    if args.airplane:
        request_images( args.airplane, rhandle )
