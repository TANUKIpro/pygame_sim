import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget
from PyQt5.QtCore import Qt


class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMouseTracking(True)

        self.setWindowTitle("mouse")
        self.resize(320, 240)
        self.show()

    def mouseButtonKind(self, buttons):
        if buttons & Qt.LeftButton:
            print("LEFT")
        if buttons & Qt.MidButton:
            print("MIDDLE")
        if buttons & Qt.RightButton:
            print("RIGHT")

    def mousePressEvent(self, e):
        print("BUTTON PRESS")
        self.mouseButtonKind(e.buttons())

    def mouseReleaseEvent(self, e):
        print("BUTTON RELEASE")
        self.mouseButtonKind(e.buttons())

    def wheelEvent(self, e):
        print("wheel")
        print("(%d %d)" % (e.angleDelta().x(), e.angleDelta().y()))

    def mouseMoveEvent(self, e):
        print("(%d %d)" % (e.x(), e.y()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Main()
    sys.exit(app.exec_())
