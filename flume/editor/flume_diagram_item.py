from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPolygonF, QPixmap, QPainter, QPen, QFont
from PyQt5.QtWidgets import QGraphicsPolygonItem, QGraphicsItem
from flume.editor.manage_properties import ManageProperties


class FlumeDiagramItem(QGraphicsPolygonItem):
    def __init__(self, flume_object, parent=None):
        super(FlumeDiagramItem, self).__init__(parent)

        self.flume_object = flume_object
        self.flume_component = self.flume_object.component

        if self.flume_component == "channel":
            self.polygon = QPolygonF([QPointF(-100, -50), QPointF(100, -50),
                                      QPointF(100, 50), QPointF(-100, 50),
                                      QPointF(-100, -50)])
        elif self.flume_component == "source":
            self.polygon = QPolygonF([QPointF(-100, -100), QPointF(100, -50),
                                      QPointF(100, 50), QPointF(-100, 100),
                                      QPointF(-100, -100)])
        elif self.flume_component == "sink":
            self.polygon = QPolygonF([QPointF(-100, -50), QPointF(100, -100),
                                      QPointF(100, 100), QPointF(-100, 50),
                                      QPointF(-100, -50)])

        self.setPolygon(self.polygon)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.name = flume_object.name
        self._text = self.name

        self.arrows = []

    def image(self):
        pixmap = QPixmap(250, 250)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.polygon)
        return pixmap

    def remove_arrow(self, arrow):
        try:
            self.arrows.remove(arrow)
        except ValueError:
            pass


    def remove_arrows(self):
        for arrow in self.arrows:
            arrow.start_item().remove_arrow(arrow)
            arrow.end_item().remove_arrow(arrow)
            self.scene().removeItem(arrow)

    def add_arrow(self, arrow):
        self.arrows.append(arrow)

    def paint(self, painter, option, widget=None):
        super(FlumeDiagramItem, self).paint(painter, option, widget)

        painter.setFont(QFont('Arial', 15))
        if 'type' in self.flume_object.properties.keys():
            self.text = self.name + "(" + self.flume_object.properties['type']['value'] + ")"
        painter.drawText(-50, -50, 100, 100, Qt.AlignCenter, self.text)

    def mouseDoubleClickEvent(self, mouse_event):
        if ManageProperties(self.flume_object).exec_():
            self.update()
        super().mouseDoubleClickEvent(mouse_event)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_position()
        return value
