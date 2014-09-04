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

from arrow import Arrow
from config_maintenance import FlumeConfig
from diagram_scene import DiagramScene
from diagram_text_item import DiagramTextItem
from flume_diagram_item import FlumeDiagramItem
from flume_object import FlumeObject
from flume_object_container import FlumeObjectContainer
from MainWindow import MainWindow
from manage_properties import ManageProperties

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