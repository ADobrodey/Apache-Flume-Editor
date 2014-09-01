import pickle
from flume.editor import flume_diagram_item
from flume.editor.flume_diagram_item import FlumeDiagramItem


class FlumeObject(object):
    source, channel, sink = range(3)

    def __init__(self, component):
        self.component = component  # source sink channel
        self.pictogram = FlumeDiagramItem(component)  # QPoligonItem
        self.status = 2  # {"error":2, "defined":1, "active":0}
        self.properties = {}

    def set_property(self, new_property, value):
        self.properties[new_property]["value"] = value
        self.properties[new_property]["default"] = False

    def activate(self):
        if self.is_defined():
            self.status = 0
            return True
        self.status = 2
        return False

    def is_defined(self):
        # if properties loaded
        if self.properties:
            for prop in self.properties.keys():
                # if property required and is None:
                if prop["required"] and prop["default"]:
                    return False
            return True
        return False

    def load_default_properties(self, source_type):
        path = ':/properties/' + self.component + '/' + source_type + '.dat'
        with open(path, 'rb') as property_file:
            loaded_properties = pickle.load(property_file)

            for component_property in loaded_properties:
                self.properties[component_property["name"]] = {"value": component_property["default"],
                                                               "required": component_property["required"],
                                                               "default": True,
                                                               "description": component_property["description"]}


class SourceObject(FlumeObject):
    def __init__(self, component, name, source_type):
        super(SourceObject, self).__init__(component)
        self.name = name  # s1
        self.source_type = source_type  # "avro" "thrift"
        self.load_default_properties(self.source_type)













