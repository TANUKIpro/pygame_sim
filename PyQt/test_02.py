#!env python
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
#from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QSlider, QLabel, QMainWindow
from PyQt5.QtOpenGL import *


#app = QApplication(sys.argv)

class QTGLWidget1(QGLWidget):
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

    def paintGL(self):
        glClearColor(0.0, 0.0, 1.0, 0.0)
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

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, 1.0, 1.0, 30.0)



class QTGLSample(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        widget = QTGLWidget1(self)
        self.setCentralWidget(widget)


app = QApplication(sys.argv)
window = QTGLSample()
window.setWindowTitle('PyQt OpenGL 1')
window.show()
sys.exit(app.exec_())
