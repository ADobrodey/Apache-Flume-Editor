from flume.editor.flume_object import SourceObject

try:
    import cPickle as pickle
except:
    import pickle


class AvroSource(SourceObject):
    def __init__(self, component=*args):
        self.properties = args
        self.status = 0


class elementBase(object):
    path = ":/base.dat"

    def load_data(self):
        data_file = open(self.path, 'rb')
        try:
            while True:
                try:
                    o = pickle.load(data_file)
                except EOFError:
                    break
                else:
                    print('Read data from file')
        finally:
            data_file.close()

    def add_data(self):
