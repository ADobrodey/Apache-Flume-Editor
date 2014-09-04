from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QHBoxLayout, QGraphicsView, QWidget
from flume.editor import FlumeObject


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(QRectF(0, 0, 1000, 1000))

        item = FlumeObject("source", "r1")
        self.scene.addItem(item.pictogram)
        item.pictogram.setPos(200, 200)

        layout = QHBoxLayout()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)
        self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # FIXME doesn't work as needed

        self.widget = QWidget()
        self.widget.setLayout(layout)

        self.setCentralWidget(self.widget)
        self.setWindowTitle("The Flume Illustrator")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = MainWindow()
    screen.show()

    sys.exit(app.exec_())