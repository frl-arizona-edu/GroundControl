import threading
import time
import atexit
import json
import psycopg2 as psql
import psycopg2.extras

from ground_control.setint import setInterval
from ground_control.image import ImageData
from ground_control.detection import ImageDetection
from ground_control.geometry import Box
from ground_control.geometry import Point

UNPROCESSED = 'unprocessed'
PROCESSING = 'processing'
PROCESS_ERROR = 'process_error'
REPROCESS = 'reprocess'
ACKNOWLEDGED = 'ack'

class PostgresHandle(object):

    def __init__(self, host, port, timeout_interval=30.0):
        self.host = host
        self.port = port
        self.timeout = timeout_interval

        self._check_processing()

    def _get_connection(self):
        args = { 'host': self.host,
                 'port': self.port,
                 'database': 'auvsi',
                 'user': 'auvsi_owner',
                 'password': 'auvsi' }
        return psql.connect(**args)

    def _change_image_status(self, name, status, senttime=None):
        connection = self._get_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""UPDATE images
                                SET status = %s, sentTime = %s
                                WHERE name = %s""", (status, senttime, name,))
            connection.commit()

    """
    Periodically checks to see if any of the images that should be in the process
    of undergoing image analysis have taken too long and should be readded to the
    queue.
    """
    @setInterval(1.0)
    def _check_processing(self):
        with self._get_connection().cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""SELECT name
                                FROM images
                                WHERE status='processing' AND sentTime < %s""",
                                (time.time() - self.timeout,))
            results = cursor.fetchall()

            for result in results:
                self._change_image_status(result[0], PROCESS_ERROR)

    """
    Empties out the entire Postgres database -- mostly just for debugging.
    """
    def empty_database(self):
        connection = self._get_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""DELETE FROM images_cvresults""")
            cursor.execute("""DELETE FROM images""")
            cursor.execute("""DELETE FROM cvresults""")

            connection.commit()

    def ack_image(self, image_name):
        connection = self._get_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""UPDATE images SET status='ack' WHERE name=%s""", (image_name,))
            connection.commit()

    def add_cvresult(self, image_name, box, results):
        connection = self._get_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""INSERT INTO cvresults(bounds, results) VALUES (%s,%s)""", (box, json.dumps(results),))
            connection.commit()

            cursor.execute("""SELECT id FROM cvresults ORDER BY id DESC LIMIT 1""")
            cursor.execute("""INSERT INTO images_cvresults(name, result_id)
                                VALUES(%s, %s)""", (image_name, cursor.fetchone()[0]))
            connection.commit()

    def get_image_detections(self, image_name):
        with self._get_connection().cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""SELECT name AS name, bounds, results
                                FROM images_cvresults AS ic
                                    JOIN cvresults AS cv ON ic.result_id=cv.id
                                WHERE ic.name=%s""", (image_name,))
            return [ImageDetection(**x) for x in cursor.fetchall()]

    """
    Adds image data and marks it as unchecked
    """
    def add_image(self, image_name, telemetry, priority=100):
        connection = self._get_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # TODO: Get actual telemetry data format
            cursor.execute("""INSERT INTO images(name, center, priority)
                            VALUES(%s,POINT(%s,%s),%s)""", (image_name, 1.0, 1.0, priority))
            connection.commit()

    def get_image(self, image_name):
        connection = self._get_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""SELECT name, center, priority, recvTime, sentTime, status
                                FROM images WHERE name=%s""", (image_name,))

            return ImageData(**cursor.fetchone())

    def get_all_images(self):
        connection = self._get_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""SELECT name, center, priority, recvTime, sentTime, status
                                FROM images ORDER BY priority, recvTime""")

            return [ImageData(**x) for x in cursor.fetchall()]

    """
    Returns the image with the highest priority that has not been processed
    for image analysis successfully yet.  This will move it from the 'unchecked'
    list to the 'processing' list.
    """
    def get_next_image(self):
        with self._get_connection().cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""SELECT name, center, priority, recvTime, sentTime, status
                                FROM images
                                WHERE status = 'unprocessed'
                                ORDER BY priority DESC, recvTime LIMIT 1""")

            result = cursor.fetchone()

            if result is not None:
                image = ImageData(**result)
                self._change_image_status(image.name, PROCESSING, senttime=time.time())

                return image

            return None
