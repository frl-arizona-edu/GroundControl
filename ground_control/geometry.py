import math

from psycopg2.extensions import adapt, register_adapter, AsIs

class Box(object):

    def __init__(self, p1, p2):
        d1 = math.sqrt(p1.x ** 2 + p1.y ** 2)
        d2 = math.sqrt(p2.x ** 2 + p2.y ** 2)

        if d1 >= d2:
            self.p1 = p1
            self.p2 = p2
        else:
            self.p1 = p2
            self.p2 = p1

    def __repr__(self):
        return "{},{}".format(self.p1, self.p2)

    def adapt(box):
        return AsIs("'{}'".format(box.__repr__()))

class Point(object):

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return "({},{})".format(self.x, self.y)

    def adapt(point):
        return AsIs("'{}'".format(point.__repr__()))

register_adapter(Box, Box.adapt)
register_adapter(Point, Point.adapt)
