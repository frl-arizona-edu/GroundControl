import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379

def ImageSource():
    pool = None

    def __init__(cls, host=REDIS_HOST, port=REDIS_PORT):
        pool = redis.ConnectionPool(host, port)

    def addImageData(uuid, telemetry, imagePath):
        pass
