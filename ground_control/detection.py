import re

from ground_control.geometry import Point
from ground_control.geometry import Box

class ImageDetection(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        if 'bounds' in kwargs.keys():
            coords = re.findall(r'[-+]?\d*\.\d+|\d+', self.bounds)
            self.bounds = Box(Point(coords[0], coords[1]), Point(coords[2], coords[3]))

