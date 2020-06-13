from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
#from PyQt4 import QtGui
#from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QLabel, QMainWindow, QPushButton
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtOpenGL import *


class QTGLWidget2(QGLWidget):
    vertex = [
        [ 0.0, 0.0, 0.0 ],
        [ 1.0, 0.0, 0.0 ],
        [ 1.0, 1.0, 0.0 ],
        [ 0.0, 1.0, 0.0 ],
        [ 0.0, 0.0, 1.0 ],
        [ 1.0, 0.0, 1.0 ],
        [ 1.0, 1.0, 1.0 ],
        [ 0.0, 1.0, 1.0 ]]

    edge = [
        [ 0, 1 ],
        [ 1, 2 ],
        [ 2, 3 ],
        [ 3, 0 ],
        [ 4, 5 ],
        [ 5, 6 ],
        [ 6, 7 ],
        [ 7, 4 ],
        [ 0, 4 ],
        [ 1, 5 ],
        [ 2, 6 ],
        [ 3, 7 ]]

    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(300, 300)
        self.br = 0.0
        self.bg = 0.0
        self.bb = 1.0

    def paintGL(self):
        glClearColor(self.br, self.bg, self.bb, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        gluLookAt(3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        glBegin(GL_LINES)
        for i in range(0, 12):
            glVertex(self.vertex[self.edge[i][0]])
            glVertex(self.vertex[self.edge[i][1]])
        glEnd()

        glFlush()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(30.0, w/h, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def initializeGL(self):
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glClearColor(self.br, self.bg, self.bb, 1.0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, 1.0, 1.0, 30.0)

    def changeBackColor(self):
        c = self.br
        self.br = self.bg
        self.bg = self.bb
        self.bb = c
        self.updateGL()

class QTWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.gl = QTGLWidget2(self)
        bb = QPushButton('Back Color', self)
        bb.clicked.connect(self.gl.changeBackColor)
        cb = QPushButton('Close', self)
        cb.clicked.connect(qApp.quit)

        hbox = QHBoxLayout()
        hbox.addWidget(bb)
        hbox.addWidget(cb)

        vbox = QVBoxLayout()
        vbox.addWidget(self.gl)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.resize(300, 350)


app = QApplication(sys.argv)
w = QTWidget()
w.setWindowTitle('PyQt OpenGL 2')
w.show()
sys.exit(app.exec_())
