class ImageData(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return "[{}] at point ({}) with priority ({}) status ({})".format(self.name, self.center, self.priority, self.status)
