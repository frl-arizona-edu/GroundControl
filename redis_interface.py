import redis
import random
import time
import threading
import atexit

from setint import setInterval

BASE_KEY = 'flightimage'
KEY_PROCESSING = '%s:processing' % BASE_KEY
KEY_UNCHECKED = '%s:unchecked' % BASE_KEY
KEY_DETECTED = '%s:detected' % BASE_KEY
KEY_EMPTY = '%s:empty' % BASE_KEY
KEY_IMAGE_DATA = '%s:image:' % BASE_KEY

class RedisHandle(object):

    _instance = None

    pool = None
    host = None
    port = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RedisHandle, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__( self, host, port ):
        super( RedisHandle, self ).__init__( self )

        self.host = host
        self.port = port

        if self.pool is None:
            self.pool = redis.ConnectionPool( host=self.host, port=self.port, db=0 )
            print "+ Connected to Redis at [%s:%s]" % (host, port)

        atexit.register( self.cleanUp )

        self.checkProcessing()

    """
    Terminates the Redis connection on exit of the application.
    """
    def cleanUp( self ):
        print "+ Closing Redis connection "
        self.pool.disconnect()

    """
    Empties out the entire Redis database -- mostly just for debugging.
    """
    def emptyDatabase( self ):
        conn = redis.Redis( connection_pool=self.pool )
        conn.flushdb()

    """
    Constructs the key used to store telemetry data for an image in the database.
    """
    def imageKey( self, imagePath ):
        return KEY_IMAGE_DATA + imagePath.split('/')[-1]

    """
    Adds image data to the 'unchecked' list.
    """
    def addNewImage( self, imagePath, data ):
        conn = redis.Redis( connection_pool=self.pool )
        score = random.randint(1, 100)

        print 'Adding "%s" (%d)' % (imagePath, score)

        conn.set( self.imageKey( imagePath ), data )
        conn.zadd( KEY_UNCHECKED, imagePath, score )

    """
    Returns the image with the highest priority that has not been processed
    for image analysis successfully yet.  This will move it from the 'unchecked'
    list to the 'processing' list.
    """
    def getNextImage( self ):
        conn = redis.Redis( connection_pool=self.pool )
        results = conn.zrangebyscore( KEY_UNCHECKED, 0, 100, start=0, num=1 )

        if len(results) > 0:
            next_image = results[0]

            conn.zrem( KEY_UNCHECKED, next_image )
            conn.zadd( KEY_PROCESSING, next_image, time.time() )

            return next_image

        return None

    """
    Marks an image as positively detected and stamps it with the time it was
    added to the database so it can be referenced later.
    """
    def detectedImage( self, imagePath, data ):
        conn = redis.Redis( connection_pool=self.pool )

        conn.zrem( KEY_PROCESSING, imagePath )
        conn.zadd( KEY_DETECTED, imagePath, time.time() )

    """
    Marks an image as empty so that it won't be rescanned but it does not remove
    any data so its record can still be referenced in the future.
    """
    def emptyImage( self, imagePath, data ):
        conn = redis.Redis( connection_pool=self.pool )

        conn.zrem( KEY_PROCESSING, imagePath )
        conn.zadd( KEY_EMPTY, imagePath, time.time() )

    """
    Periodically checks to see if any of the images that should be in the process
    of undergoing image analysis have taken too long and should be readded to the
    queue.
    """
    @setInterval(1.0)
    def checkProcessing( self ):
        conn = redis.Redis( connection_pool=self.pool )

        results = conn.zrangebyscore( KEY_PROCESSING, 0, time.time() - 30, )

        for result in results:
            conn.zrem( KEY_PROCESSING, result )
            conn.zadd( KEY_UNCHECKED, result, 100 )
