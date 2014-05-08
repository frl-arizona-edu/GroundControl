import zmq
import msgpack
import os

def run( port=10101 ):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:{}".format(port))

    for fname in os.listdir('dummy/'):
        path = 'dummy/{}'.format(fname)

        with open(path, 'rb') as file:
            message = file.read()

        packed = msgpack.packb((100, 100, message))

        client_message = socket.recv()

        print("Client message: {}".format(client_message))

        socket.send(packed)

    while True:
        pass

if __name__ == '__main__':
    run()
