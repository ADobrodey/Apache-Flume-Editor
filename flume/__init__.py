__version__ = "0.1.0"


class Error(Exception):
    def __init__(self, kind, msg="", info=""):
        self.kind = kind
        self.msg = msg
        self.info = info

    def __str__(self):
        s = "%s%s" % (self.info, self.kind)
        if self.msg:
            s += ": %s" % self.msg
        return s


from _arrow import Arrow
from _config_maintenance import FlumeConfig
from _diagram_scene import DiagramScene
from _diagram_text_item import DiagramTextItem
from _flume_diagram_item import FlumeDiagramItem
from _flume_object import FlumeObject
from _flume_object_container import FlumeObjectContainer
from MainWindow import MainWindow
from _manage_properties import ManageProperties

__all__ = ["Arrow",
           "FlumeConfig",
           "DiagramScene",
           "DiagramTextItem",
           "FlumeDiagramItem",
           "FlumeObject",
           "FlumeObjectContainer",
           "MainWindow",
           "ManageProperties"
]