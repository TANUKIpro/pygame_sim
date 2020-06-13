# -*- coding: utf-8 -*-
import sys, os, traceback, time
from functools import lru_cache
from math import sin, cos, sqrt, radians
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore as Qt
from PyQt5.QtCore import *
from PyQt5.QtOpenGL import *
from stl import mesh
from stl_load_class import STL_loader
from drawer_class import drawPolygon, drawText, drawText_3D, drawAxis
import ctypes

window_title = "Cloth SIM@PyQt5 v.0.3"
screen_size = [700, 600]

to_models = "/Users/ryotaro/py_projects/pygame_sim/model"
finger = "/Index"

names_list = ["/Metacarpal3_01.stl",
              "/Proximal_Phalanx3_01.stl",
              "/Middle_Phalanxh3_01.stl",
              "/Distal_Phalanxh3_01.stl"]

file_name = [to_models+finger+names_list[0],
             to_models+finger+names_list[1],
             to_models+finger+names_list[2],
             to_models+finger+names_list[3]]
size = 1/15
Metacarpal3,       _, _ = STL_loader(file_name[0], size).load()
Proximal_Phalanx3, _, _ = STL_loader(file_name[1], size).load()
Middle_Phalanxh3,  _, _ = STL_loader(file_name[2], size).load()
Distal_Phalanxh3,  _, _ = STL_loader(file_name[3], size).load()

class QTGLWidget2(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setMinimumSize(*screen_size)
        self.camera_rot = [70,23]
        self.camera_radius = 2.5
        self.camera_center = [0.5,0.5,0.5]
        self.camera_cood = [[0.],[0.],[0.]]
        self.camera_wide_angle = 60
        self.angle_x, self.angle_y, self.angle_z = 0., 0., 0.
        self.vias_x, self.vias_y, self.vias_z = 0.,0.,0.

        self.bool_vias_x, self.bool_vias_y, self.bool_vias_z = False, False, False
        self.org = tuple((0,0,0))
        self.org_points = [[tuple((0, 0, 0)), tuple((5, 0, 0))],
                           [tuple((0, 0, 0)), tuple((0, 5, 0))],
                           [tuple((0, 0, 0)), tuple((0, 0, 5))]]
        self.br = 0.0
        self.bg = 0.0
        self.bb = 0.0
        self.Meta, self.PrxPh, self.MddPh, self.DisPh = False, False, False, False
        self.keys_list = []
        self.all_camera_status = []


    def listener(self, bool_list):
        self.Meta, self.PrxPh, self.MddPh, self.DisPh = bool_list

    def key_listener(self, event):
        key = event.key()
        move_pix = 0.5
        if event.modifiers() & Qt.ShiftModifier:
            if   key==Qt.Key_X : self.camera_cood[0][0] -= 0.05
            elif key==Qt.Key_Y : self.camera_cood[1][0] -= 0.05
            elif key==Qt.Key_Z : self.camera_cood[2][0] -= 0.05

            elif key == Qt.Key_Up : self.angle_x += move_pix
            elif key == Qt.Key_Down : self.angle_x -= move_pix

        elif key==Qt.Key_X : self.camera_cood[0][0] += 0.05
        elif key==Qt.Key_Y : self.camera_cood[1][0] += 0.05
        elif key==Qt.Key_Z : self.camera_cood[2][0] += 0.05

        elif key==Qt.Key_Left  : self.angle_y += move_pix
        elif key==Qt.Key_Right : self.angle_y -= move_pix
        elif key==Qt.Key_Up    : self.angle_z += move_pix
        elif key==Qt.Key_Down  : self.angle_z -= move_pix

    def cameraRESET(self):
        self.camera_rot = [70,23]
        self.camera_radius = 2.5
        self.camera_center = [0.5,0.5,0.5]
        self.camera_cood = [[0.],[0.],[0.]]
        self.angle_x, self.angle_y, self.angle_z = 0., 0., 0.
        self.vias_x, self.vias_y, self.vias_z = 0.,0.,0.

    def mouse_listener(self, type, event, mv_cood=[0, 0]):
        ## LEFT, MIDDLE, RIGHT, WHEEL, MOVE
        move_pix = 0.5
        if type == 'MOVE':
            self.camera_rot[0] += mv_cood[0]
            self.camera_rot[1] += mv_cood[1]
            #self.update()
        if type == 'WHEEL':
            if   event.angleDelta().y() == 120  : self.camera_radius -= move_pix
            elif event.angleDelta().y() == -120 : self.camera_radius += move_pix

    def paintGL(self):
        glClearColor(self.br, self.bg, self.bb, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        camera_pos = [self.camera_center[0] + self.camera_radius*cos(radians(self.camera_rot[0]))*cos(radians(self.camera_rot[1])),
                      self.camera_center[1] + self.camera_radius*sin(radians(self.camera_rot[1])),
                      self.camera_center[2] + self.camera_radius*sin(radians(self.camera_rot[0]))*cos(radians(self.camera_rot[1]))]
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
                  self.camera_center[0], self.camera_center[1], self.camera_center[2], 0,1,0)

        ## 指定軸に対して回転
        glRotated(self.angle_x, 1.0, 0.0, 0.0)
        glRotated(self.angle_y, 0.0, 1.0, 0.0)
        glRotated(self.angle_z, 0.0, 0.0, 1.0)
        ## 指定軸に対して平行移動
        glTranslatef(-self.camera_cood[0][0], -self.camera_cood[1][0], -self.camera_cood[2][0])

        glColor3f(1, 1, 0)
        glPointSize(30)
        glBegin(GL_POINTS)
        glVertex3fv(self.org)
        glEnd()

        drawText_3D("X", 3., 0., 0.)
        drawText_3D("Y", 0., 3., 0.)
        drawText_3D("Z", 0., 0., 3.)
        drawAxis()

        if not self.Meta:
            for idx_Meta in Metacarpal3:
                drawPolygon(idx_Meta)
        if not self.PrxPh:
            for idx_PrxPh in Proximal_Phalanx3:
                drawPolygon(idx_PrxPh)
        if not self.MddPh:
            for idx_MddPh in Middle_Phalanxh3:
                drawPolygon(idx_MddPh)
        if not self.DisPh:
            for idx_DisPh in Distal_Phalanxh3:
                drawPolygon(idx_DisPh)
        glFlush()
        #self.updateGL()

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
        gluPerspective(40.0, 1.0, .1, 100.0)

class QTWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.clicked_points = [0, 0]
        self.bool_list = [True, True, True, True]
        self.listCheckBox = names_list
        self.listLabel = []
        for label in range(len(self.listCheckBox)):
            self.listLabel.append("")
        self.gl = QTGLWidget2(self)
        self.initUI()

        timer = QTimer(self)
        timer.setInterval(20)   # period, in milliseconds
        timer.timeout.connect(self.gl.updateGL)
        timer.start()

    def initUI(self):
        gui_layout = QGridLayout()
        self.setLayout(gui_layout)
        gui_layout.addWidget(self.gl)

        for i, v in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QCheckBox(v)
            self.listLabel[i] = QLabel()
            gui_layout.addWidget(self.listCheckBox[i], i+10, 0)
            gui_layout.addWidget(self.listLabel[i],    i+10, 1)

        self.sc_button = QPushButton("Show / Clear")
        self.sc_button.clicked.connect(self.check_checkbox)
        # (ウェジット、行、列)
        gui_layout.addWidget(self.sc_button, 20, 0)

        self.rst_button = QPushButton("RESER CAMERA VIEW")
        self.rst_button.clicked.connect(self.gl.cameraRESET)
        gui_layout.addWidget(self.rst_button, 30, 0)

    def check_checkbox(self):
        for i, v in enumerate(self.listCheckBox):
            if v.checkState():
                self.bool_list[i]=True
            else:
                self.bool_list[i]=False
        self.gl.listener(self.bool_list)

    def keyPressEvent(self, event):
        self.gl.key_listener(event)

    ## LEFT, MIDDLE, RIGHT, WHEEL, MOVE
    def mouseButtonKind(self, buttons):
        if buttons & Qt.LeftButton  : self.gl.mouse_listener("LEFT",   None)
        if buttons & Qt.MidButton   : self.gl.mouse_listener("MIDDLE", None)
        if buttons & Qt.RightButton : self.gl.mouse_listener("RIGHT",  None)

    def mousePressEvent(self, e):
        self.mouseButtonKind(e.buttons())
        self.clicked_points = [e.pos().x(), e.pos().y()]

    def mouseReleaseEvent(self, e):
        self.mouseButtonKind(e.buttons())

    def wheelEvent(self, e):
        self.gl.mouse_listener("WHEEL", e)

    def mouseMoveEvent(self, e):
        # マウスの相対移動座標
        mvX, mvY = self.clicked_points[0]-e.x(), self.clicked_points[1]-e.y()
        self.gl.mouse_listener("MOVE", e, mv_cood=[-mvX*0.2, -mvY*0.2])
        self.update()

def main():
    app = QApplication(sys.argv)
    w = QTWidget()
    w.setWindowTitle(window_title)
    w.show()

    sys.exit(app.exec_())


if __name__=='__main__':
    main()
