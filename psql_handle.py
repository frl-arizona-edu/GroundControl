import random
import time
import threading
import atexit
import psycopg2 as psql

from enum import Enum
from setint import setInterval

UNPROCESSED = 'unprocessed'
PROCESSING = 'processing'
POSITIVE = 'positive'
NEGATIVE = 'negative'

class PostgresHandle(object):

    def __init__( self, host, port ):
        self.host = host
        self.port = port

        self.checkProcessing()

    def getConnection( self ):
        args = { 'host': self.host,
                 'port': self.port,
                 'user': 'auvsi_owner',
                 'password': 'auvsi' }
        return psql.connect(**args)

    """
    Empties out the entire Postgres database -- mostly just for debugging.
    """
    def emptyDatabase( self ):
        conn = self.getConnection()
        cursor = conn.cursor()

        cursor.execute("""DELETE FROM images""")
        conn.commit()

    def changeImageStatus( self, name, status ):
        conn = self.getConnection()
        cursor = conn.cursor()

        cursor.execute("""UPDATE images
                            SET status = ?
                            WHERE name = ?""", (status, name, ))
        conn.commit()

    """
    Adds image data and marks it as unchecked
    """
    def addNewImage( self, imagePath, data ):
        conn = self.getConnection()
        cursor = conn.cursor()
        score = random.randint(1, 100)

        print('+ Adding "{}" ({})'.format(imagePath, score))

        cursor.execute("""INSERT INTO images(name, center, priority)
                          VALUES(?,?,?)""", (imagePath, (1.0, 1.0), score))
        conn.commit()

    """
    Returns the image with the highest priority that has not been processed
    for image analysis successfully yet.  This will move it from the 'unchecked'
    list to the 'processing' list.
    """
    def getNextImage( self ):
        conn = self.getConnection()
        results = conn.execute("""SELECT name, center, priority
                                    FROM images
                                    ORDER BY score, recvTime LIMIT 1""")

        if len(results) > 0:
            next_image = results[0]

            self.changeImageStatus(next_image[0], PROCESSING)

            return next_image

        return None

    """
    Marks an image as positively detected and stamps it with the time it was
    added to the database so it can be referenced later.
    """
    def detectedImage( self, name, data ):
        self.changeImageStatus(name, POSITIVE)

    """
    Marks an image as empty so that it won't be rescanned but it does not remove
    any data so its record can still be referenced in the future.
    """
    def emptyImage( self, name ):
        self.changeImageStatus(name, NEGATIVE)

    """
    Periodically checks to see if any of the images that should be in the process
    of undergoing image analysis have taken too long and should be readded to the
    queue.
    """
    @setInterval(1.0)
    def checkProcessing( self ):
        conn = self.getConnection()

        results = conn.execute("""SELECT name FROM images WHERE sentTime < ?""", (time.time() - 30))

        for result in results:
            self.changeImageStatus(result[0], UNPROCESSED)
