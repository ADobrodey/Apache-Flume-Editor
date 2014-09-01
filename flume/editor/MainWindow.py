import os
import math
# noinspection PyUnresolvedReferences
import diagramscene_rc
from PyQt5.QtCore import (pyqtSignal, QLineF, QPointF, QRectF, QSize,
                          QSizeF, Qt, QRect)
from PyQt5.QtGui import (QFont, QIcon, QPainter, QPen, QPixmap, QPolygonF, QTransform, QColor,
                         QIntValidator)
# from PyQt5 import QPainterPath
from PyQt5.QtWidgets import (QAction, QApplication, QButtonGroup, QComboBox,
                             QGraphicsItem, QGraphicsLineItem, QGraphicsPolygonItem,
                             QGraphicsScene, QGraphicsView, QGridLayout,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox, QSizePolicy,
                             QToolBox, QToolButton, QWidget, QFileDialog, QGraphicsTextItem, QMenu, QFontComboBox)


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


class DiagramTextItem(QGraphicsTextItem):
    lostFocus = pyqtSignal(QGraphicsTextItem)
    selectedChange = pyqtSignal(QGraphicsItem)

    def __init__(self, parent=None, scene=None):
        super(DiagramTextItem, self).__init__(parent, scene)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            self.selectedChange.emit(self)
        return value

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.lostFocus.emit(self)
        super(DiagramTextItem, self).focusOutEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextEditorInteraction)
        super(DiagramTextItem, self).mouseDoubleClickEvent(event)


class DiagramItem(QGraphicsPolygonItem):
    Channel, Sink, Source, Agent = range(4)

    def __init__(self, diagram_type, context_menu, parent=None):
        super(DiagramItem, self).__init__(parent)

        self.arrows = []

        self.diagramType = diagram_type
        self.contextMenu = context_menu

        # path = QPainterPath()
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
        # TODO self.myContextMenu.exec_(event.screenPos())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_position()
        return value


class DiagramScene(QGraphicsScene):
    InsertItem, InsertLine, InsertText, MoveItem, DefaultMode = range(5)

    itemInserted = pyqtSignal(int)

    textInserted = pyqtSignal(QGraphicsTextItem)

    itemSelected = pyqtSignal(QGraphicsItem)

    def __init__(self, item_menu, parent=None):
        super(DiagramScene, self).__init__(parent)

        self.my_item_menu = item_menu
        self.my_mode = self.DefaultMode
        self.my_item_type = DiagramItem.Channel
        self.line = None
        self.text_item = None
        self.my_item_color = Qt.white
        self.my_text_color = Qt.black
        self.my_line_color = Qt.black
        self.my_font = QFont()
        self.m_drag_offset = 0
        self.m_dragged = None

    def set_line_color(self, color):
        self.my_line_color = color
        if self.is_item_changed(Arrow):
            item = self.selectedItems()[0]
            item.set_color(self.my_line_color)
            self.update()

    def set_text_color(self, color):
        self.my_text_color = color
        if self.is_item_changed(DiagramTextItem):
            item = self.selectedItems()[0]
            item.setDefaultTextColor(self.my_text_color)

    def set_item_color(self, color):
        self.my_item_color = color
        if self.is_item_changed(DiagramItem):
            item = self.selectedItems()[0]
            item.setBrush(self.my_item_color)

    def setFont(self, font):
        self.my_font = font
        if self.is_item_changed(DiagramTextItem):
            item = self.selectedItems()[0]
            item.setFont(self.my_font)

    def set_mode(self, mode):
        self.my_mode = mode

    def set_item_type(self, new_type):
        self.my_item_type = new_type

    def editor_lost_focus(self, item):
        if item:
            cursor = item.text_cursor()
            cursor.clearSelection()
            item.set_text_cursor(cursor)

            if item.to_plain_text():
                self.removeItem(item)
                item.delete_later()

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
        elif self.my_mode == self.InsertText:
            text_item = DiagramTextItem()
            text_item.setFont(self.my_font)
            text_item.setTextInteractionFlags(Qt.TextEditorInteraction)
            text_item.setZValue(1000.0)
            text_item.lostFocus.connect(self.editor_lost_focus)
            # text_item.selectedChange.connect(self.itemSelected)
            self.addItem(text_item)
            text_item.setDefaultTextColor(self.my_text_color)
            text_item.setPos(mouse_event.scenePos())
            self.textInserted.emit(text_item)
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
            if self.m_dragged:
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


# noinspection PyAttributeOutsideInit
class MainWindow(QMainWindow):
    InsertTextButton = 10

    def __init__(self):
        super(MainWindow, self).__init__()

        self.create_actions()
        self.create_menus()
        self.create_tool_box()

        self.scene = DiagramScene(self.item_menu)
        self.scene.setSceneRect(QRectF(0, 0, 1000, 1000))

        self.scene.itemInserted.connect(self.item_inserted)
        self.scene.textInserted.connect(self.text_inserted)
        self.scene.itemSelected.connect(self.item_selected)

        self.create_tool_bars()
        # self.scene.enable_grid()

        layout = QHBoxLayout()
        layout.addWidget(self.tool_box)
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
        self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # FIXME doesn't work as needed

        self.widget = QWidget()
        self.widget.setLayout(layout)

        self.setCentralWidget(self.widget)
        self.setWindowTitle("The Flume Illustrator")

    # noinspection PyAttributeOutsideInit,PyArgumentList
    def create_actions(self):

        self.to_front_action = QAction(QIcon(':/images/bringtofront.png'),
                                       "Bring to &Front", self, shortcut="Ctrl+F",
                                       statusTip="Bring item to front", triggered=self.bring_to_front)
        self.send_back_action = QAction(QIcon(':/images/sendtoback.png'),
                                        "Send to &Back", self, shortcut="Ctrl+B",
                                        statusTip="Send item to back", triggered=self.send_to_back)
        self.bold_action = QAction(QIcon(':/images/bold.png'),
                                   "Bold", self, checkable=True, shortcut="Ctrl+B",
                                   triggered=self.handle_font_change)
        self.italic_action = QAction(QIcon(':/images/italic.png'),
                                     "Italic", self, checkable=True, shortcut="Ctrl+I",
                                     triggered=self.handle_font_change)
        self.underline_action = QAction(QIcon(':/images/underline.png'),
                                        "Underline", self, checkable=True, shortcut="Ctrl+U",
                                        triggered=self.handle_font_change)

        self.delete_action = QAction(QIcon(':/images/delete.png'),
                                     "Delete", self, shortcut="Delete", statusTip='Delete item from diagram',
                                     triggered=self.delete_item)
        self.exit_action = QAction("Exit", self, shortcut="Ctrl+X",
                                   statusTip="Quit program", triggered=self.close)
        self.about_action = QAction("About", self, shortcut="Ctrl+B",
                                    triggered=self.about)
        self.load_config_action = QAction("Load", self, shortcut="Ctrl+O",
                                          statusTip="Load config file", triggered=self.load_config)

        self.enable_grid_action = QAction("Enable grid", self, triggered=self.enable_grid)

    # noinspection PyAttributeOutsideInit
    def create_menus(self):
        self.file_menu = self.menuBar().addMenu("File")
        self.file_menu.addAction(self.exit_action)

        self.item_menu = self.menuBar().addMenu("Item")
        self.item_menu.addAction(self.delete_action)
        self.item_menu.addSeparator()
        self.item_menu.addAction(self.to_front_action)
        self.item_menu.addAction(self.send_back_action)

        self.about_menu = self.menuBar().addMenu("Help")
        self.about_menu.addAction(self.about_action)

    # noinspection PyAttributeOutsideInit,PyUnresolvedReferences
    def create_tool_box(self):
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(False)
        self.button_group.buttonClicked[int].connect(self.button_group_clicked)

        layout = QGridLayout()
        layout.addWidget(self.create_cell_widget("Source", DiagramItem.Source), 0, 0)
        layout.addWidget(self.create_cell_widget("Channel", DiagramItem.Channel), 0, 1)
        layout.addWidget(self.create_cell_widget("Sink", DiagramItem.Sink), 1, 0)

        text_button = QToolButton()
        text_button.setCheckable(True)
        self.button_group.addButton(text_button, self.InsertTextButton)
        text_button.setIcon(QIcon(QPixmap(':/images/textpointer.png').scaled(30, 30)))
        text_button.setIconSize(QSize(50, 50))

        text_layout = QGridLayout()
        text_layout.addWidget(text_button, 0, 0, Qt.AlignHCenter)
        text_layout.addWidget(QLabel("Text"), 1, 0, Qt.AlignCenter)
        text_widget = QWidget()
        text_widget.setLayout(text_layout)
        layout.addWidget(text_widget, 1, 1)

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

        self.edit_tool_bar = self.addToolBar("Edit")
        self.edit_tool_bar.addAction(self.delete_action)
        self.edit_tool_bar.addAction(self.to_front_action)
        self.edit_tool_bar.addAction(self.send_back_action)
        self.edit_tool_bar.addAction(self.enable_grid_action)

        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.current_font_changed)

        self.font_size_combo = QComboBox()
        self.font_size_combo.setEditable(True)
        for i in range(8, 30, 2):
            self.font_size_combo.addItem(str(i))
        validator = QIntValidator(2, 64, self)
        self.font_size_combo.setValidator(validator)
        self.font_size_combo.currentIndexChanged.connect(self.font_size_changed)

        self.font_color_tool_button = QToolButton()
        self.font_color_tool_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.font_color_tool_button.setMenu(
            self.create_color_menu(self.text_color_changed, Qt.black))
        self.text_action = self.font_color_tool_button.menu().defaultAction()
        self.font_color_tool_button.setIcon(
            self.create_color_tool_button_icon(':/images/textpointer.png',
                                               Qt.black))
        self.font_color_tool_button.setAutoFillBackground(True)
        self.font_color_tool_button.clicked.connect(self.text_button_triggered)

        self.fill_color_tool_button = QToolButton()
        self.fill_color_tool_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.fill_color_tool_button.setMenu(
            self.create_color_menu(self.item_color_changed, Qt.white))
        self.fillAction = self.fill_color_tool_button.menu().defaultAction()
        self.fill_color_tool_button.setIcon(
            self.create_color_tool_button_icon(':/images/floodfill.png',
                                               Qt.white))
        self.fill_color_tool_button.clicked.connect(self.fill_button_triggered)

        self.line_color_tool_button = QToolButton()
        self.line_color_tool_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.line_color_tool_button.setMenu(
            self.create_color_menu(self.line_color_changed, Qt.black))
        self.lineAction = self.line_color_tool_button.menu().defaultAction()
        self.line_color_tool_button.setIcon(
            self.create_color_tool_button_icon(':/images/linecolor.png',
                                               Qt.black))
        self.line_color_tool_button.clicked.connect(self.line_button_triggered)

        self.text_tool_bar = self.addToolBar("Font")
        self.text_tool_bar.addWidget(self.font_combo)
        self.text_tool_bar.addWidget(self.font_size_combo)
        self.text_tool_bar.addAction(self.bold_action)
        self.text_tool_bar.addAction(self.italic_action)
        self.text_tool_bar.addAction(self.underline_action)

        self.color_tool_bar = self.addToolBar("Color")
        self.color_tool_bar.addWidget(self.font_color_tool_button)
        self.color_tool_bar.addWidget(self.fill_color_tool_button)
        self.color_tool_bar.addWidget(self.line_color_tool_button)

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
        buttons = self.button_group.buttons()
        for button in buttons:
            if self.button_group.button(button_id) != button:
                button.setChecked(False)
        if button_id == self.InsertTextButton:
            self.scene.set_mode(DiagramScene.InsertText)
        else:
            self.scene.set_item_type(button_id)
            self.scene.set_mode(DiagramScene.InsertItem)

    def delete_item(self):
        for item in self.scene.selectedItems():
            if isinstance(item, DiagramItem):
                item.remove_arrows()
            self.scene.removeItem(item)

    # noinspection PyTypeChecker,PyCallByClass
    def about(self):

        # noinspection PyArgumentList
        QMessageBox.about(self, "About Flume Illustrator", "The Flume illustrator shows config-file details")

    def pointer_group_clicked(self):  # FIXME deleted i
        self.scene.set_mode(self.pointer_type_group.checkedId())

    def bring_to_front(self):
        if not self.scene.selectedItems():
            return

        selected_item = self.scene.selectedItems()[0]
        overlap_items = selected_item.collidingItems()

        z_value = 0
        for item in overlap_items:
            if (item.zValue() >= z_value and isinstance(item, DiagramItem)):
                z_value = item.zValue() + 0.1
        selected_item.setZValue(z_value)

    def send_to_back(self):
        if not self.scene.selectedItems():
            return

        selected_item = self.scene.selectedItems()[0]
        overlap_items = selected_item.collidingItems()

        z_value = 0
        for item in overlap_items:
            if (item.zValue() <= z_value and isinstance(item, DiagramItem)):
                z_value = item.zValue() - 0.1
        selected_item.setZValue(z_value)

    def scene_scale_changed(self, scale):
        new_scale = float(scale[:scale.index("%")]) / 100
        old_transform = self.view.transform()
        self.view.resetTransform()
        self.view.translate(old_transform.dx(), old_transform.dy())
        self.view.scale(new_scale, new_scale)

    def item_inserted(self, diagram_type):
        self.pointer_type_group.button(DiagramScene.MoveItem).setChecked(True)
        self.scene.set_mode(self.scene.DefaultMode)  # FIXME self.pointerTypeGroup.checkedId()
        self.button_group.button(diagram_type).setChecked(False)

    def text_inserted(self, item):
        self.button_group.button(self.InsertTextButton).setChecked(False)
        self.scene.set_mode(self.pointer_type_group.checkedId())

    def current_font_changed(self, font):
        self.handle_font_change()

    def font_size_changed(self, font=None):
        self.handle_font_change()

    def text_color_changed(self):
        self.text_action = self.sender()
        self.font_color_tool_button.setIcon(
            self.create_color_tool_button_icon(':/images/textpointer.png',
                                               QColor(self.text_action.data())))
        self.text_button_triggered()

    def item_color_changed(self):
        self.fillAction = self.sender()
        self.fill_color_tool_button.setIcon(
            self.create_color_tool_button_icon(':/images/floodfill.png',
                                               QColor(self.fillAction.data())))
        self.fill_button_triggered()

    def line_color_changed(self):
        self.lineAction = self.sender()
        self.line_color_tool_button.setIcon(
            self.create_color_tool_button_icon(':/images/linecolor.png',
                                               QColor(self.lineAction.data())))
        self.line_button_triggered()

    def text_button_triggered(self):
        self.scene.set_text_color(QColor(self.text_action.data()))

    def fill_button_triggered(self):
        self.scene.set_item_color(QColor(self.fillAction.data()))

    def line_button_triggered(self):
        self.scene.set_line_color(QColor(self.lineAction.data()))

    def handle_font_change(self):
        font = self.font_combo.currentFont()
        font.setPointSize(int(self.font_size_combo.currentText()))
        if self.bold_action.isChecked():
            font.setWeight(QFont.Bold)
        else:
            font.setWeight(QFont.Normal)
        font.setItalic(self.italic_action.isChecked())
        font.setUnderline(self.underline_action.isChecked())

        self.scene.setFont(font)

    def item_selected(self, item):
        print(item)
        font = item.font()
        self.font_combo.setCurrentFont(font)
        self.font_size_combo.setEditText(str(font.pointSize()))
        self.bold_action.setChecked(font.weight() == QFont.Bold)
        self.italic_action.setChecked(font.italic())
        self.underline_action.setChecked(font.underline())

    def create_cell_widget(self, text, diagram_type):
        item = DiagramItem(diagram_type, self.item_menu)
        icon = QIcon(item.image())

        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.button_group.addButton(button, diagram_type)

        layout = QGridLayout()
        layout.addWidget(button, 0, 0, Qt.AlignHCenter)
        layout.addWidget(QLabel(text), 1, 0, Qt.AlignHCenter)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    # noinspection PyArgumentList
    def create_color_menu(self, slot, default_color):
        colors = [Qt.black, Qt.white, Qt.red, Qt.blue, Qt.yellow]
        names = ["black", "white", "red", "blue", "yellow"]

        color_menu = QMenu(self)
        for color, name in zip(colors, names):
            action = QAction(self.create_color_icon(color), name, self,
                             triggered=slot)
            action.setData(QColor(color))
            color_menu.addAction(action)
            if color == default_color:
                color_menu.setDefaultAction(action)
        return color_menu

    @staticmethod
    def create_color_tool_button_icon(image_file, color):
        pixmap = QPixmap(50, 80)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        image = QPixmap(image_file)
        target = QRect(0, 0, 50, 60)
        source = QRect(0, 0, 42, 42)
        painter.fillRect(QRect(0, 60, 50, 80), color)
        painter.drawPixmap(target, image, source)
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def create_color_icon(color):
        pixmap = QPixmap(20, 20)
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)
        painter.fillRect(QRect(0, 0, 20, 20), color)
        painter.end()

        return QIcon(pixmap)

    def enable_grid(self):
        for i in range(50):
            for j in range(50):
                self.scene.addEllipse(i * 100, j * 100, 2, 2)


    # ########################################################################

    def load_config(self):
        # noinspection PyCallByClass
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
                                                      x=300 * items[component][1], y=400)
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