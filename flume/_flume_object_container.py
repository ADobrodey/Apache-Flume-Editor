import bisect


class FlumeObjectContainer(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FlumeObjectContainer, cls).__new__(cls, *args)
            return cls._instance

    def __init__(self):
        self.__objects = []
        self.__objects_ids = {}

    def __iter__(self):
        for flume_object in self.__objects:
            yield flume_object

    def __len__(self):
        return len(self.__objects)

    def clear(self):
        self.__objects = []
        self.__objects_ids = {}

    def add(self, flume_object):
        if id(flume_object) in self.__objects_ids:
            return False
        key = flume_object.name
        bisect.insort_left(self.__objects, [key, flume_object])
        self.__objects_ids[id(flume_object)] = flume_object
        return True

    def search(self, name):
        if name in self.__objects:
            return
