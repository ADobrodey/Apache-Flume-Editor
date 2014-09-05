from PyQt5.QtCore import pyqtSignal, Qt, QLineF
from PyQt5.QtGui import QFont, QPen, QTransform
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsItem, QGraphicsLineItem, QInputDialog
from flume import Arrow
from flume._flume_object import FlumeObject
from flume._diagram_text_item import DiagramTextItem
from flume._flume_diagram_item import FlumeDiagramItem


class DiagramScene(QGraphicsScene):
    InsertItem, InsertLine, InsertText, MoveItem, DefaultMode = range(5)

    itemInserted = pyqtSignal(int)

    textInserted = pyqtSignal(QGraphicsTextItem)

    itemSelected = pyqtSignal(QGraphicsItem)

    def __init__(self, item_menu, parent=None):
        super(DiagramScene, self).__init__(parent)

        self.my_item_menu = item_menu
        self.my_mode = self.DefaultMode
        self.my_item_type = "channel"
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
        if self.is_item_changed(DiagramTextItem):
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

    # noinspection PyArgumentList
    def insert_item(self, item_type=None, x=None, y=None, text=None):
        if not text:
            text, ok = QInputDialog.getText(QInputDialog(), 'Insert name', 'Enter new object name:')
            if not ok:  # TODO
                return
        item = FlumeObject(item_type, text).pictogram
        item.setBrush(self.my_item_color)
        self.addItem(item)
        item.setPos(x, y)
        return item

    def mousePressEvent(self, mouse_event):

        if mouse_event.button() != Qt.LeftButton:
            return
        if self.my_mode == self.InsertItem:
            x = mouse_event.scenePos().x()  # // 50 * 50
            y = mouse_event.scenePos().y()  # // 50 * 50
            item = self.insert_item(self.my_item_type, x, y)
            self.itemInserted.emit(item.flume_component)
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

            if len(start_items) and len(end_items) and isinstance(start_items[0], FlumeDiagramItem) and \
                    isinstance(end_items[0], FlumeDiagramItem) and start_items[0] != end_items[0]:
                start_item = start_items[0]
                end_item = end_items[0]

                self.add_arrow(start_item, end_item)

        self.line = None

        if self.m_dragged:
            x = mouse_event.scenePos().x()  # // 50 * 50
            y = mouse_event.scenePos().y()  # // 50 * 50
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
