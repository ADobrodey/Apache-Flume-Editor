from PyQt5.QtCore import (QRectF, QSize,
                          Qt, QRect)
from PyQt5.QtGui import (QFont, QIcon, QPainter, QPen, QPixmap, QColor,
                         QIntValidator)

from PyQt5.QtWidgets import (QAction, QApplication, QButtonGroup, QComboBox,
                             QGraphicsView, QGridLayout,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox, QSizePolicy,
                             QToolBox, QToolButton, QWidget, QMenu, QFontComboBox)


# noinspection PyAttributeOutsideInit
from flume import FlumeConfig, DiagramScene, FlumeDiagramItem, FlumeObject
from properties import properties_generator


# noinspection PyAttributeOutsideInit,PyUnusedLocal,PyUnresolvedReferences
class MainWindow(QMainWindow):
    InsertTextButton = 10
    items = {-2: "source", -3: "channel", -4: "sink"}

    def __init__(self):
        import _diagramscene_rc

        super(MainWindow, self).__init__()

        self.config_manipulations = FlumeConfig(self)
        properties_generator.dump_props()

        self.create_actions()
        self.create_menus()
        self.create_tool_box()
        self.clicked_button_id = 0

        self.scene = DiagramScene(self.item_menu)
        self.scene.setSceneRect(QRectF(0, 0, 5000, 5000))

        self.scene.itemInserted.connect(self.item_inserted)
        self.scene.textInserted.connect(self.text_inserted)
        self.scene.itemSelected.connect(self.item_selected)

        self.create_tool_bars()
        # self.scene.enable_grid()

        layout = QHBoxLayout()
        layout.addWidget(self.tool_box)
        self.view = QGraphicsView(self.scene)
        self.view.centerOn(0, 0)
        layout.addWidget(self.view)

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
                                          statusTip="Load config file", triggered=self.config_manipulations.load_config)

        self.enable_grid_action = QAction("Enable grid", self, checkable=True, triggered=self.enable_grid)

    # noinspection PyAttributeOutsideInit
    def create_menus(self):
        self.file_menu = self.menuBar().addMenu("File")
        self.file_menu.addAction(self.load_config_action)
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
        layout.addWidget(self.create_cell_widget("Source", "source"), 0, 0)
        layout.addWidget(self.create_cell_widget("Channel", "channel"), 0, 1)
        layout.addWidget(self.create_cell_widget("Sink", "sink"), 1, 0)

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
        self.clicked_button_id = button_id
        for button in buttons:
            if self.button_group.button(button_id) != button:
                button.setChecked(False)
        if button_id == self.InsertTextButton:
            self.scene.set_mode(DiagramScene.InsertText)
        else:
            self.scene.set_item_type(self.items[button_id])
            self.scene.set_mode(DiagramScene.InsertItem)

    def delete_item(self):
        for item in self.scene.selectedItems():
            if isinstance(item, FlumeDiagramItem):
                item.remove_arrows()
            self.scene.removeItem(item)

    # noinspection PyTypeChecker,PyCallByClass
    def about(self):

        # noinspection PyArgumentList
        QMessageBox.about(self, "About Flume Illustrator", "The Flume illustrator shows config-file details")

    def pointer_group_clicked(self):
        self.scene.set_mode(self.pointer_type_group.checkedId())

    def bring_to_front(self):
        if not self.scene.selectedItems():
            return

        selected_item = self.scene.selectedItems()[0]
        overlap_items = selected_item.collidingItems()

        z_value = 0
        for item in overlap_items:
            if item.zValue() >= z_value and isinstance(item, FlumeDiagramItem):
                z_value = item.zValue() + 0.1
        selected_item.setZValue(z_value)

    def send_to_back(self):
        if not self.scene.selectedItems():
            return

        selected_item = self.scene.selectedItems()[0]
        overlap_items = selected_item.collidingItems()

        z_value = 0
        for item in overlap_items:
            if item.zValue() <= z_value and isinstance(item, FlumeDiagramItem):
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
        self.scene.set_mode(self.scene.DefaultMode)
        self.button_group.button(self.clicked_button_id).setChecked(False)

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
        font = item.font()
        self.font_combo.setCurrentFont(font)
        self.font_size_combo.setEditText(str(font.pointSize()))
        self.bold_action.setChecked(font.weight() == QFont.Bold)
        self.italic_action.setChecked(font.italic())
        self.underline_action.setChecked(font.underline())

    def create_cell_widget(self, text, diagram_type):
        item = FlumeObject(diagram_type, "")
        icon = QIcon(item.pictogram.image())

        button = QToolButton()
        button.setIcon(icon)
        button.setIconSize(QSize(50, 50))
        button.setCheckable(True)
        self.button_group.addButton(button)  # , diagram_type

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
        if self.enable_grid_action.isChecked():
            color = Qt.black
        else:
            color = Qt.white
        for i in range(50):
            for j in range(50):
                self.scene.addEllipse(i * 100, j * 100, 2, 2, QPen(color))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = MainWindow()
    screen.show()

    sys.exit(app.exec_())