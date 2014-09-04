import math
from PyQt5.QtCore import QPointF, QLineF, Qt, QSizeF, QRectF
from PyQt5.QtGui import QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsLineItem, QGraphicsItem


class Arrow(QGraphicsLineItem):
    def __init__(self, start_item, end_item, parent=None):
        super(Arrow, self).__init__(parent)

        self.arrowHead = QPolygonF()

        self.my_start_item = start_item
        self.my_end_item = end_item
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.my_color = Qt.black
        self.setPen(QPen(self.my_color, 2, Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin))

    def set_color(self, color):
        self.my_color = color

    def start_item(self):
        return self.my_start_item

    def end_item(self):
        return self.my_end_item

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QRectF(p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra, extra, extra)

    def shape(self):
        path = super(Arrow, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def update_position(self):
        line = QLineF(self.mapFromItem(self.my_start_item, 0, 0), self.mapFromItem(self.my_end_item, 0, 0))
        self.setLine(line)

    def paint(self, painter, option, widget=None):
        if self.my_start_item.collidesWithItem(self.my_end_item):
            return

        my_start_item = self.my_start_item
        my_end_item = self.my_end_item
        my_color = self.my_color
        my_pen = self.pen()
        my_pen.setColor(self.my_color)
        arrow_size = 20.0
        painter.setPen(my_pen)
        painter.setBrush(my_color)

        center_line = QLineF(my_start_item.pos(), my_end_item.pos())
        end_polygon = my_end_item.polygon

        p1 = end_polygon.first() + my_end_item.pos()

        intersect_point = QPointF()
        for i in end_polygon:
            p2 = i + my_end_item.pos()
            poly_line = QLineF(p1, p2)
            intersect_type = poly_line.intersect(center_line, intersect_point)
            if intersect_type == QLineF.BoundedIntersection:
                break
            p1 = p2

        self.setLine(QLineF(intersect_point, my_start_item.pos()))
        line = self.line()

        angle = math.acos(line.dx() / line.length())

        if line.dy() >= 0:
            angle = (math.pi * 2) - angle

        arrow_p1 = line.p1() + QPointF(math.sin(angle + math.pi / 3.0) * arrow_size,
                                       math.cos(angle + math.pi / 3) * arrow_size)
        arrow_p2 = line.p1() + QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrow_size,
                                       math.cos(angle + math.pi - math.pi / 3.0) * arrow_size)

        self.arrowHead.clear()
        for point in [line.p1(), arrow_p1, arrow_p2]:
            self.arrowHead.append(point)

        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QPen(my_color, 1, Qt.DashLine))
            my_line = QLineF(line)
            my_line.translate(0, 4.0)
            painter.drawLine(my_line)
            my_line.translate(0, -8.0)
            painter.drawLine(my_line)