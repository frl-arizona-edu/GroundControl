from flask import Flask
from flask import make_response
from flask import abort
from flask import jsonify

from random import random
from psql_handle import PostgresHandle

import msgpack
import sys
import argparse

app = Flask(__name__)
app.debug = True

@app.route("/next", methods=[ "GET" ])
def nextImage():
    rhandle = PostgresHandle( args.psqlhost, args.psqlport )
    image = rhandle.getNextImage()
    data = None

    with open('tmp/{}.jpg'.format(image[0]), 'rb') as f:
        data = f.read()
        f.close()

    return msgpack.packb(data)

@app.route("/update/<filename>/<int:found>", methods=[ "PUT" ])
@app.route("/update/<filename>/<int:found>/<float:x>/<float:y>", methods=[ "PUT" ])
def updateImageData(filename, found, x=-1.0, y=-1.0):
    print("Updating image data [{}] [{}] [({}, {})]".format(filename, found, x, y))
    rhandle = PostgresHandle( args.psqlhost, args.psqlport )

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

    parser.add_argument("-s", "--psqlhost", help="Host address of the Postgres server")
    parser.add_argument("-p", "--psqlport", help="Port of the Postgres server")

    args = parser.parse_args()

    if not (args.psqlhost and args.psqlport):
        parser.error('Missing argument --psqlhost or --psqlport')

    app.run()
