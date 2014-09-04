import pickle
from flume._flume_diagram_item import FlumeDiagramItem


class UnknownPropertyError(KeyError):
    pass


class FlumeObject(object):
    components = {"source": 0, "channel": 1, "sink": 2}
    statuses = {"active": 0, "ready": 1, "error": -1}

    def __init__(self, component, name):
        self._component = component
        self.status = self.statuses["error"]  # {"error":2, "defined":1, "active":0}
        self._name = name  # s1, k5
        self.properties = {}
        self.managed = False
        self.pictogram = FlumeDiagramItem(self)
        # FlumeObjectContainer().add(self)  #TODO

    def set_pic(self):
        # QPoligonItem
        pass

    @property
    def component(self):
        return self._component

    @property
    def name(self):
        return self._name

    def set_property(self, new_property, value):
        if self.properties[new_property]:
            self.properties[new_property]["value"] = value
            self.properties[new_property]["default"] = False
        else:
            raise UnknownPropertyError

    def load_default_properties(self, component_type):
        path = 'properties/' + self.component + '/' + component_type + '.dat'
        with open(path, 'rb') as property_file:
            loaded_properties = pickle.load(property_file)
            self.properties = loaded_properties


class SourceObject(FlumeObject):
    pass


class SinkObject(FlumeObject):
    pass


class ChannelObject(FlumeObject):
    pass
