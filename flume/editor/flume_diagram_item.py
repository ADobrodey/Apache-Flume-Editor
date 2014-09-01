from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPolygonF, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsItem
from flume.editor import FlumeObject


class FlumeDiagramItem(QGraphicsPolygonItem):
    def __init__(self, flume_component, parent=None):
        super(FlumeDiagramItem, self).__init__(parent)

        self.flume_component = flume_component

        if flume_component == FlumeObject.channel:
            self.polygon = QPolygonF([QPointF(-100, -50), QPointF(100, -50),
                                      QPointF(100, 50), QPointF(-100, 50),
                                      QPointF(-100, -50)])
        elif flume_component == FlumeObject.source:
            self.polygon = QPolygonF([QPointF(-100, -100), QPointF(100, -50),
                                      QPointF(100, 50), QPointF(-100, 100),
                                      QPointF(-100, -100)])
        elif flume_component == FlumeObject.sink:
            self.polygon = QPolygonF([QPointF(-100, -50), QPointF(100, -100),
                                      QPointF(100, 100), QPointF(-100, 50),
                                      QPointF(-100, -50)])

        self.setPolygon(self.polygon)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def image(self):
        pixmap = QPixmap(250, 250)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.polygon)
        return pixmap
