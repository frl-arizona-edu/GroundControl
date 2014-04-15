import unittest
import time

from pprint import pprint
from ground_control.psql_handle import PostgresHandle
from ground_control.telemetry import TelemetryData
from ground_control.geometry import Box
from ground_control.geometry import Point

class PostgresHandleTest(unittest.TestCase):

    def setUp(self):
        self.psql = PostgresHandle('localhost', 5432, timeout_interval=1.5)
        self.psql.empty_database()

        self.psql.add_image('image001', TelemetryData(), 80)
        self.psql.add_image('image002', TelemetryData(), 90)
        self.psql.add_image('image003', TelemetryData(), 100)
        self.psql.add_image('image004', TelemetryData(), 20)
        self.psql.add_image('image005', TelemetryData(), 100)

    def test_get_next(self):
        next = self.psql.get_next_image()
        self.assertEqual(next.name, 'image003')
        self.assertEqual(next.status, 'unprocessed')

        next = self.psql.get_next_image()
        self.assertEqual(next.name, 'image005')
        self.assertEqual(next.status, 'unprocessed')

        next = self.psql.get_next_image()
        self.assertEqual(next.name, 'image002')
        self.assertEqual(next.status, 'unprocessed')

        next = self.psql.get_next_image()
        self.assertEqual(next.name, 'image001')
        self.assertEqual(next.status, 'unprocessed')

        next = self.psql.get_next_image()
        self.assertEqual(next.name, 'image004')
        self.assertEqual(next.status, 'unprocessed')

        images = self.psql.get_all_images()

        self.assertEqual(len(images), 5)

        for image in images:
            self.assertEqual(image.status, 'processing')

        self.psql.ack_image('image001')
        self.psql.ack_image('image002')
        self.psql.ack_image('image003')

        image1 = self.psql.get_image('image001')
        image2 = self.psql.get_image('image002')
        image3 = self.psql.get_image('image003')
        image4 = self.psql.get_image('image004')
        image5 = self.psql.get_image('image005')

        self.assertEqual(image1.status, 'ack')
        self.assertEqual(image2.status, 'ack')
        self.assertEqual(image3.status, 'ack')
        self.assertEqual(image4.status, 'processing')
        self.assertEqual(image5.status, 'processing')

        # We wait here long enough for a self-check to happen and check for any
        # request that might have timed out to have their status' changed.
        time.sleep(2)

        image1 = self.psql.get_image('image001')
        image2 = self.psql.get_image('image002')
        image3 = self.psql.get_image('image003')
        image4 = self.psql.get_image('image004')
        image5 = self.psql.get_image('image005')

        self.assertEqual(image1.status, 'ack')
        self.assertEqual(image2.status, 'ack')
        self.assertEqual(image3.status, 'ack')
        self.assertEqual(image4.status, 'process_error')
        self.assertEqual(image5.status, 'process_error')

        self.psql.add_cvresult('image001', Box(Point(1,1),Point(4,4)), {})
        self.psql.add_cvresult('image002', Box(Point(2,2),Point(7,5)), {})
        self.psql.add_cvresult('image002', Box(Point(3,3),Point(6,6)), {})
        self.psql.add_cvresult('image002', Box(Point(1,1),Point(1,2)), {})

        detect1 = self.psql.get_image_detections('image001')
        detect2 = self.psql.get_image_detections('image002')

        self.assertEqual(len(detect2), 3)

        boxs1 = [x.bounds.__repr__() for x in detect1]
        boxs2 = [x.bounds.__repr__() for x in detect2]

        self.assertTrue('(4.0,4.0),(1.0,1.0)' in boxs1)
        self.assertTrue('(7.0,5.0),(2.0,2.0)' in boxs2)
        self.assertTrue('(6.0,6.0),(3.0,3.0)' in boxs2)
        self.assertTrue('(1.0,2.0),(1.0,1.0)' in boxs2)
