from flask import Flask
from flask import make_response
from flask import abort
from flask import jsonify

from random import random
from redis_interface import RedisHandle

import msgpack
import sys

app = Flask(__name__)
app.debug = True
global rhandle

@app.route("/next", methods=[ "GET" ])
def nextImage():
    data = {}
    data['uuid'] = random() * 1000000
    data['telemetry'] = { 'x': 1.0, 'y': 1.0, 'z': 1.0 }
    data['width'] = 100.0
    data['height'] = 80.0

    imagePath = rhandle.getNextImage()

    print imagePath

    with open('test.jpg', 'rb') as f:
        data['image'] = f.read()
        f.close()

    return msgpack.packb(data)

@app.route("/update", methods=[ "POST" ])
def updateImageData():
    pass

@app.route("/")
@app.errorhandler(404)
def handle_404(error = None):
    return make_response( jsonify( { "success": 0, "error": "404 - Not Found" } ), 404 )

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'Usage: python rest_server [REDIS HOST] [REDIS PORT]'
        sys.exit(0)

    global rhandle

    rhandle = RedisHandle( sys.argv[1], sys.argv[2] )
    app.run()
