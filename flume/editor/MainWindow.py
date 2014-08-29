import os
from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRectF, QSize,
                          QSizeF, Qt)
from PyQt5.QtGui import (QFont, QIcon, QPainter, QPen, QPixmap, QPolygonF, QTransform)
from PyQt5.QtWidgets import (QAction, QApplication, QButtonGroup, QComboBox,
                             QGraphicsItem, QGraphicsLineItem, QGraphicsPolygonItem,
                             QGraphicsScene, QGraphicsView, QGridLayout,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox, QSizePolicy,
                             QToolBox, QToolButton, QWidget, QFileDialog)

import diagramscene_rc
import math


class Arrow(QGraphicsLineItem):
    def __init__(self, start_item, end_item, parent=None):
        super(Arrow, self).__init__(parent)

        self.arrowHead = QPolygonF()

        self.myStartItem = start_item
        self.myEndItem = end_item
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.myColor = Qt.black
        self.setPen(QPen(self.myColor, 2, Qt.SolidLine, Qt.RoundCap,
                         Qt.RoundJoin))

    def set_color(self, color):
        self.myColor = color

    def start_item(self):
        return self.myStartItem

    def end_item(self):
        return self.myEndItem

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
        line = QLineF(self.mapFromItem(self.myStartItem, 0, 0), self.mapFromItem(self.myEndItem, 0, 0))
        self.setLine(line)

    def paint(self, painter, option, widget=None):
        if self.myStartItem.collidesWithItem(self.myEndItem):
            return

        my_start_item = self.myStartItem
        my_end_item = self.myEndItem
        my_color = self.myColor
        my_pen = self.pen()
        my_pen.setColor(self.myColor)
        arrow_size = 20.0
        painter.setPen(my_pen)
        painter.setBrush(my_color)

        center_line = QLineF(my_start_item.pos(), my_end_item.pos())
        end_polygon = my_end_item.polygon()

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


class DiagramItem(QGraphicsPolygonItem):
    Channel, Sink, Source = range(3)

    def __init__(self, diagram_type, context_menu, parent=None):
        super(DiagramItem, self).__init__(parent)

        self.arrows = []

        self.diagramType = diagram_type
        self.contextMenu = context_menu

        # FIXME path = QPainterPath()
        if self.diagramType == self.Channel:
            self.myPolygon = QPolygonF([
                QPointF(-100, -50), QPointF(100, -50),
                QPointF(100, 50), QPointF(-100, 50),
                QPointF(-100, -50)])

        elif self.diagramType == self.Source:
            self.myPolygon = QPolygonF([
                QPointF(-100, -100), QPointF(100, -50),
                QPointF(100, 50), QPointF(-100, 100),
                QPointF(-100, -100)])
        elif self.diagramType == self.Sink:
            self.myPolygon = QPolygonF([
                QPointF(-100, -50), QPointF(100, -100),
                QPointF(100, 100), QPointF(-100, 50),
                QPointF(-100, -50)])

        self.setPolygon(self.myPolygon)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def remove_arrow(self, arrow):
        try:
            self.arrows.remove(arrow)
        except ValueError:
            print("Value error on arrow removement n 139")

    def remove_arrows(self):
        for arrow in self.arrows:
            arrow.start_item().remove_arrow(arrow)
            arrow.end_item().remove_arrow(arrow)
            self.scene().removeItem(arrow)

    def add_arrow(self, arrow):
        self.arrows.append(arrow)

    def image(self):
        pixmap = QPixmap(250, 250)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.black, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.myPolygon)
        return pixmap

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        # FIXME self.myContextMenu.exec_(event.screenPos())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_position()
        return value


class DiagramScene(QGraphicsScene):
    InsertItem, InsertLine, MoveItem, DefaultMode = range(4)

    itemInserted = pyqtSignal(int)

    itemSelected = pyqtSignal(QGraphicsItem)

    def __init__(self, item_menu, parent=None):
        super(DiagramScene, self).__init__(parent)

        self.my_item_menu = item_menu
        self.my_mode = self.DefaultMode
        self.my_item_type = DiagramItem.Channel
        self.line = None
        self.my_item_color = Qt.white
        self.my_line_color = Qt.black
        self.my_font = QFont()
        self.m_drag_offset = 0
        self.m_dragged = None

        self.enable_grid()

    def set_line_color(self, color):
        self.my_line_color = color
        if self.is_item_changed(Arrow):
            item = self.selectedItems()[0]
            item.setColor(self.my_line_color)
            self.update()

    def set_item_color(self, color):
        self.my_item_color = color
        if self.is_item_changed(DiagramItem):
            item = self.selectedItems()[0]
            item.setBrush(self.my_item_color)

    def set_mode(self, mode):
        self.my_mode = mode

    def enable_grid(self):
        for i in range(50):
            for j in range(50):
                self.addEllipse(i * 100, j * 100, 2, 2)

    def set_item_type(self, new_type):
        self.my_item_type = new_type

    def insert_item(self, item_type=None, x=None, y=None):
        item = DiagramItem(item_type, self.my_item_menu)
        item.setBrush(self.my_item_color)
        self.addItem(item)
        item.setPos(x, y)
        return item

    def mousePressEvent(self, mouse_event):

        if mouse_event.button() != Qt.LeftButton:
            return

        if self.my_mode == self.InsertItem:
            x = mouse_event.scenePos().x() // 50 * 50
            y = mouse_event.scenePos().y() // 50 * 50
            item = self.insert_item(self.my_item_type, x, y)
            self.itemInserted.emit(item.diagramType)
        elif self.my_mode == self.InsertLine:
            self.line = QGraphicsLineItem(QLineF(mouse_event.scenePos(),
                                                 mouse_event.scenePos()))
            self.line.setPen(QPen(self.my_line_color, 2))
            self.addItem(self.line)
        else:
            self.m_dragged = QGraphicsScene.itemAt(self, mouse_event.scenePos(), QTransform())
            if self.m_dragged:
                self.my_mode = self.MoveItem
                self.m_drag_offset = mouse_event.scenePos() - self.m_dragged.pos()

        super(DiagramScene, self).mousePressEvent(mouse_event)

    def mouseMoveEvent(self, mouse_event):
        if self.my_mode == self.InsertLine and self.line:
            new_line = QLineF(self.line.line().p1(), mouse_event.scenePos())
            self.line.setLine(new_line)
        elif self.my_mode == self.MoveItem:
            self.m_dragged.setPos(mouse_event.scenePos() - self.m_drag_offset)
            super(DiagramScene, self).mouseMoveEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):

        if self.line and self.my_mode == self.InsertLine:
            start_items = self.items(self.line.line().p1())
            if len(start_items) and start_items[0] == self.line:
                start_items.pop(0)
            end_items = self.items(self.line.line().p2())
            if len(end_items) and end_items[0] == self.line:
                end_items.pop(0)

            self.removeItem(self.line)
            self.line = None

            if len(start_items) and len(end_items) and isinstance(start_items[0], DiagramItem) and \
                    isinstance(end_items[0], DiagramItem) and start_items[0] != end_items[0]:
                start_item = start_items[0]
                end_item = end_items[0]

                self.add_arrow(start_item, end_item)

        self.line = None

        if self.m_dragged:
            x = mouse_event.scenePos().x() // 50 * 50
            y = mouse_event.scenePos().y() // 50 * 50
            self.m_dragged.setPos(x, y)
            self.m_dragged = None
            self.my_mode = self.DefaultMode

        super(DiagramScene, self).mouseReleaseEvent(mouse_event)

    def add_arrow(self, start_item, end_item):
        arrow = Arrow(start_item, end_item)
        arrow.set_color(self.my_line_color)
        start_item.add_arrow(arrow)
        end_item.add_arrow(arrow)
        arrow.setZValue(-1000.0)
        self.addItem(arrow)
        arrow.update_position()

    def is_item_changed(self, new_type):
        for item in self.selectedItems():
            if isinstance(item, new_type):
                return True
        return False


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.create_actions()
        self.create_menus()
        self.create_tool_box()

        self.scene = DiagramScene(self.itemMenu)
        self.scene.setSceneRect(QRectF(0, 0, 5000, 5000))

        self.scene.itemInserted.connect(self.item_inserted)
        self.scene.itemSelected.connect(self.item_selected)

        self.create_tool_bars()

        layout = QHBoxLayout()
        layout.addWidget(self.tool_box)
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
        self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # FIXME doesn't work as needed

        self.widget = QWidget()
        self.widget.setLayout(layout)

        self.setCentralWidget(self.widget)
        self.setWindowTitle("The Flume Illustrator")

    # noinspection PyAttributeOutsideInit
    def create_actions(self):
        self.deleteAction = QAction(QIcon(''),
                                    "Delete", self, shortcut="Delete", statusTip="Delete item from diagram",
                                    triggered=self.delete_item)
        self.exitAction = QAction("Exit", self, shortcut="Ctrl+X",
                                  statusTip="Quit program", triggered=self.close)
        self.aboutAction = QAction("About", self, shortcut="Ctrl+B",
                                   triggered=self.about)
        self.load_config_action = QAction("Load", self, shortcut="Ctrl+O",
                                          statusTip="Load config file", triggered=self.load_config)

    # noinspection PyAttributeOutsideInit
    def create_menus(self):
        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.exitAction)

        self.itemMenu = self.menuBar().addMenu("Item")
        self.itemMenu.addAction(self.deleteAction)

        self.aboutMenu = self.menuBar().addMenu("Help")
        self.aboutMenu.addAction(self.aboutAction)

    # noinspection PyAttributeOutsideInit,PyUnresolvedReferences
    def create_tool_box(self):
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked[int].connect(self.button_group_clicked)

        layout = QGridLayout()
        layout.addWidget(self.create_cell_widget("Source", DiagramItem.Source), 0, 0)
        layout.addWidget(self.create_cell_widget("Channel", DiagramItem.Channel), 0, 1)
        layout.addWidget(self.create_cell_widget("Sink", DiagramItem.Sink), 1, 0)

        layout.setRowStretch(3, 10)
        layout.setColumnStretch(2, 10)

        item_widget = QWidget()
        item_widget.setLayout(layout)

        self.tool_box = QToolBox()
        self.tool_box.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored))
        self.tool_box.setMinimumWidth(item_widget.sizeHint().width())
        self.tool_box.addItem(item_widget, "Basic Flume Items")

    # noinspection PyAttributeOutsideInit,PyUnresolvedReferences
    def create_tool_bars(self):
        self.loading_tool_bar = self.addToolBar("Load")
        self.loading_tool_bar.addAction(self.load_config_action)

        pointer_button = QToolButton()
        pointer_button.setCheckable(True)
        pointer_button.setChecked(True)
        pointer_button.setIcon(QIcon(":/images/pointer.png"))
        line_pointer_button = QToolButton()
        line_pointer_button.setCheckable(True)
        line_pointer_button.setIcon(QIcon(":/images/linepointer.png"))

        self.pointer_type_group = QButtonGroup()
        self.pointer_type_group.addButton(pointer_button, DiagramScene.MoveItem)
        self.pointer_type_group.addButton(line_pointer_button, DiagramScene.InsertLine)
        self.pointer_type_group.buttonClicked[int].connect(self.pointer_group_clicked)

        self.scene_scale_combo = QComboBox()
        self.scene_scale_combo.addItems(["50%", "75%", "100%", "125%", "150%"])
        self.scene_scale_combo.setCurrentIndex(2)
        self.scene_scale_combo.currentIndexChanged[str].connect(self.scene_scale_changed)

        self.pointer_tool_bar = self.addToolBar("Pointer type")
        self.pointer_tool_bar.addWidget(pointer_button)
        self.pointer_tool_bar.addWidget(line_pointer_button)
        self.pointer_tool_bar.addWidget(self.scene_scale_combo)

    def button_group_clicked(self, button_id):
        buttons = self.buttonGroup.buttons()
        for button in buttons:
            if self.buttonGroup.button(button_id) != button:
                button.setChecked(False)
        self.scene.set_item_type(button_id)
        self.scene.set_mode(DiagramScene.InsertItem)

    def delete_item(self):
        for item in self.scene.selectedItems():
            if isinstance(item, DiagramItem):
                item.remove_arrows()
            self.scene.removeItem(item)

    # noinspection PyTypeChecker,PyCallByClass
    def about(self):

        QMessageBox.about(self, "About Flume Illustrator",
                          "The Flume illustrator shows config-file details")

    def pointer_group_clicked(self):  # FIXME deleted i
        self.scene.set_mode(self.pointer_type_group.checkedId())

    def scene_scale_changed(self, scale):
        new_scale = float(scale[:scale.index("%")]) / 100
        old_transform = self.view.transform()
        self.view.resetTransform()
        self.view.translate(old_transform.dx(), old_transform.dy())
        self.view.scale(new_scale, new_scale)

    def item_inserted(self, diagram_type):
        self.pointer_type_group.button(DiagramScene.MoveItem).setChecked(True)
        self.scene.set_mode(self.scene.DefaultMode)  # FIXME self.pointerTypeGroup.checkedId()
        self.buttonGroup.button(diagram_type).setChecked(False)

    def item_selected(self, item):
        pass

    def create_cell_widget(self, text, diagram_type):
        item = DiagramItem(diagram_type, self.itemMenu)
        icon = QIcon(item.image())

        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.buttonGroup.addButton(button, diagram_type)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def load_config(self):
        filename = QFileDialog.getOpenFileName(self, "Open config file", os.getenv('Home'))
        with open(filename[0], "r") as config_file:
            config = self.parse_config(config_file)
            # TODO print(config)
            self.procedure_config(config)

    def parse_config(self, config_file):
        comment_char = '#'
        option_char = '='
        agents = {}
        for line in config_file:
            if comment_char in line:
                line, comment = line.split(comment_char, 1)
            if option_char in line:
                option, values = line.split(option_char, 1)
                option = option.strip()
                values = values.strip()

                def rpad(length, seq, padding=None):
                    return tuple(seq) + tuple((length - len(seq)) * [padding])

                (agent, component, name, flume_property) = rpad(4, option.split("."))
                if not agent in agents.keys():
                    agents[agent] = {"sources": {}, "channels": {}, "sinks": {}, "connections": {}}

                if not name:
                    for value in values.split():
                        agents[agent][component][value] = {}
                else:
                    if flume_property == 'channel' or flume_property == 'channels':
                        if value not in agents[agent]["connections"].keys():
                            agents[agent]["connections"][value] = (name,)
                        else:
                            agents[agent]["connections"][value] += (
                                name,)  # agents[agent]["connections"][value].extend(name)
                    else:
                        agents[agent][component][name][flume_property] = values

        return agents

    def procedure_config(self, config):
        items = {"channels": [DiagramItem.Channel, 1], "sinks": [DiagramItem.Sink, 2],
                 "sources": [DiagramItem.Source, 0]}
        for agent in config.keys():
            components = {}
            for component in config[agent].keys():
                if component != "connections":
                    new_item = self.scene.insert_item(item_type=items[component][0],
                                                      x=2200 + 300 * items[component][1], y=2400)
                    for name in config[agent][component].keys():
                        components[name] = (new_item, items[component][1])
            for connection in config[agent]["connections"]:
                for connector in config[agent]["connections"][connection]:

                    if components[connector][1] < components[connection][1]:
                        start_item = components[connector][0]
                        end_item = components[connection][0]
                    else:
                        start_item = components[connection][0]
                        end_item = components[connector][0]

                    self.scene.add_arrow(start_item, end_item)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = MainWindow()
    screen.show()

    sys.exit(app.exec_())