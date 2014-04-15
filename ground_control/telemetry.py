import json

class TelemetryData(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return json.dumps(self.__dict__)
