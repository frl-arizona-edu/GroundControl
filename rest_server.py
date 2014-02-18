from flask import Flask
from flask import make_response
from flask import abort
from flask import jsonify

from random import random
from redis_interface import RedisHandle

import msgpack
import sys
import argparse

app = Flask(__name__)
app.debug = True

@app.route("/next", methods=[ "GET" ])
def nextImage():
    rhandle = RedisHandle( args.redishost, args.redisport )
    imagePath = rhandle.getNextImage()
    data = None

    with open(imagePath, 'rb') as f:
        data = f.read()
        f.close()

    return msgpack.packb(data)

@app.route("/update/<filename>/<int:found>", methods=[ "PUT" ])
@app.route("/update/<filename>/<int:found>/<float:x>/<float:y>", methods=[ "PUT" ])
def updateImageData(filename, found, x=-1.0, y=-1.0):
    print("Updating image data [{}] [{}] [({}, {})]".format(filename, found, latitude, longitude))
    rhandle = RedisHandle( args.redishost, args.redisport )

    if found == 1:
        rhandle.detectedImage(filename, { 'x': x, 'y': y })
    else:
        rhandle.emptyImage(filename)

    return "hi"

@app.route("/")
@app.errorhandler(404)
def handle_404(error = None):
    return make_response( jsonify( { "success": 0, "error": "404 - Not Found" } ), 404 )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--redishost", help="Host address of the Redis server")
    parser.add_argument("-p", "--redisport", help="Port of the Redis server")

    args = parser.parse_args()

    if not (args.redishost and args.redisport):
        parser.error('Missing argument --redishost or --redisport')

    app.run()
