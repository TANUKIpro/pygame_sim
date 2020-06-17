# -*- coding: utf-8 -*-
import sys, os, traceback, time
from functools import lru_cache
from math import sin, cos, sqrt, radians
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QHBoxLayout, QFrame, QSplitter, QTabWidget
from PyQt5.QtWidgets import QRadioButton, QButtonGroup
from PyQt5 import QtCore as Qt
from PyQt5.QtCore import *
from PyQt5.QtOpenGL import *
from stl import mesh
from stl_load_class import STL_loader
from drawer_class import drawPolygon, drawText, drawText_3D, drawAxis, create_vbo, draw_vbo
import ctypes
import numpy as np
from math import sqrt, pi, exp

window_title = "Cloth SIM@PyQt5 v.0.3"
screen_size = [600, 500]

to_models = "/Users/ryotaro/py_projects/pygame_sim/model"
finger = "/Index"

names_list = ["/Metacarpal3_01.stl",
              "/Proximal_Phalanx3_01_org.stl",
              "/Middle_Phalanxh3_01_org.stl",
              "/Distal_Phalanxh3_01_org.stl"]

file_name = [to_models+finger+names_list[0],
             to_models+finger+names_list[1],
             to_models+finger+names_list[2],
             to_models+finger+names_list[3]]
size = 1/15
Metacarpal3       = STL_loader(file_name[0], size)
Proximal_Phalanx3 = STL_loader(file_name[1], size)
Middle_Phalanxh3  = STL_loader(file_name[2], size)
Distal_Phalanxh3  = STL_loader(file_name[3], size)

## 頂点座標, カラー, 構成インデックス
Meta_ver, Meta_col, Meta_ind = Metacarpal3.ver_col_ind()
ProP_ver, ProP_col, ProP_ind = Proximal_Phalanx3.ver_col_ind()
MidP_ver, MidP_col, MidP_ind = Middle_Phalanxh3.ver_col_ind()
DisP_ver, DisP_col, DisP_ind = Distal_Phalanxh3.ver_col_ind()

## フレーム用カラー
Meta_Frame_col = Metacarpal3.color(Meta_ver, _r=1, _g=1, _b=0)
ProP_Frame_col = Metacarpal3.color(ProP_ver, _r=1, _g=1, _b=0)
MidP_Frame_col = Metacarpal3.color(MidP_ver, _r=1, _g=1, _b=0)
DisP_Frame_col = Metacarpal3.color(DisP_ver, _r=1, _g=1, _b=0)

Meta_max_index = np.argmax(np.array(Metacarpal3.all_mesh_particle)[:,1])
Meta_max_cood = Metacarpal3.all_mesh_particle[Meta_max_index]
print("Metacarpal3 max coordinates : ", Meta_max_cood)

ProP_max_index = np.argmax(np.array(Proximal_Phalanx3.all_mesh_particle)[:,1])
ProP_max_cood = Metacarpal3.all_mesh_particle[ProP_max_index]
print("Proximal_Phalanx3 max coordinates : ", ProP_max_cood)

MidP_max_index = np.argmax(np.array(Middle_Phalanxh3.all_mesh_particle)[:,1])
MidP_max_cood = Metacarpal3.all_mesh_particle[MidP_max_index]
print("Metacarpal3 max coordinates : ", MidP_max_cood)

def gaussian_function(sigma, mu, x, A=1.25):
    return A*(1/sqrt(2*pi*sigma) * exp(-1/(2*sigma*sigma)*(x-mu)**2))

def super_gaussian_function(sigma, mu, lmd, x, A=1.25):
    return A*exp(-(1/2*sigma*sigma*(x-mu)**2)**lmd)

Meta_angle, ProP_angle, MidP_angle, DisP_angle = 0., 0., 0., 0.
Meta, PrxPh, MddPh, DisPh = False, False, False, False
class QTGLWidget2(QGLWidget):
    Meta_buff=np.array([None])
    ProP_buff=np.array([None])
    MidP_buff=np.array([None])
    DisP_buff=np.array([None])

    outMeta_buff=np.array([None])
    outProP_buff=np.array([None])
    outMidP_buff=np.array([None])
    outDisP_buff=np.array([None])
    #Meta_angle, ProP_angle, MidP_angle, DisP_angle = 0., 0., 0., 0.
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
        #self.Meta_angle, self.ProP_angle, self.MidP_angle, self.DisP_angle = 0., 0., 0., 0.

    def joint_listener(self, typ, val):
        global Meta_angle, ProP_angle, MidP_angle, DisP_angle
        if   typ=="Meta":Meta_angle=val
        elif typ=="ProP":ProP_angle=val
        elif typ=="MidP":MidP_angle=val
        elif typ=="DisP":DisP_angle=val

    def box_listener(self, bool_list):
        global Meta, PrxPh, MddPh, DisPh
        Meta, PrxPh, MddPh, DisPh = bool_list

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
        if type == 'WHEEL':
            if   event.angleDelta().y() == 120  : self.camera_radius -= move_pix
            elif event.angleDelta().y() == -120 : self.camera_radius += move_pix

    def paintGL(self):
        glClearColor(self.br, self.bg, self.bb, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        camera_pos = [self.camera_center[0]+self.camera_radius*cos(radians(self.camera_rot[0]))*cos(radians(self.camera_rot[1])),
                      self.camera_center[1]+self.camera_radius*sin(radians(self.camera_rot[1])),
                      self.camera_center[2]+self.camera_radius*sin(radians(self.camera_rot[0]))*cos(radians(self.camera_rot[1]))]
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

        if not Meta:
            global Meta_buff, outMeta_buff
            if self.Meta_buff.all()==None:
                Meta_buff    = create_vbo(self.Meta_buff, Meta_ver, Meta_col, Meta_ind)
                outMeta_buff = create_vbo(self.outMeta_buff, Meta_ver, Meta_Frame_col, Meta_ind)
            #glPolygonMode(GL_FRONT, GL_FILL)
            draw_vbo(outMeta_buff, Meta_ind)
            draw_vbo(Meta_buff, Meta_ind, mode_front=GL_FILL)

            #glPolygonMode(GL_FRONT, GL_LINE)
            #glPolygonMode(GL_BACK, GL_LINE)

        if not PrxPh:
            global ProP_buff
            glTranslatef(0, (Meta_max_cood[1]-0.2)-Meta_angle*0.01, Meta_angle*0.002)
            if self.ProP_buff.all()==None:
                ProP_buff = create_vbo(self.ProP_buff, ProP_ver, ProP_col, ProP_ind)
            glRotatef(Meta_angle, 1, 0, 0)
            draw_vbo(ProP_buff, ProP_ind)

        if not MddPh:
            global MidP_buff
            mddp_vias = gaussian_function(sigma=20, mu=60, x=ProP_angle, A=1.7)
            glTranslatef(0, (ProP_max_cood[1]+1.8)-ProP_angle*0.008, -ProP_angle*0.001+mddp_vias)
            if self.MidP_buff.all()==None:
                MidP_buff = create_vbo(self.MidP_buff, MidP_ver, MidP_col, MidP_ind)
            glRotatef(ProP_angle+3, 1, 0, 0)
            draw_vbo(MidP_buff, MidP_ind)

        if not DisPh:
            global DisP_buff
            disp_vias = gaussian_function(sigma=25, mu=70, x=MidP_angle, A=1.9)
            glTranslatef(0, (MidP_max_cood[1]-0.95)-MidP_angle*0.009, -MidP_angle*0.005+disp_vias)
            if self.DisP_buff.all()==None:
                DisP_buff = create_vbo(self.DisP_buff, DisP_ver, DisP_col, DisP_ind)
            glRotatef(MidP_angle+3, 1, 0, 0)
            draw_vbo(DisP_buff, DisP_ind)

        ## 座標の表示    -self.camera_cood[0][0], -self.camera_cood[1][0], -self.camera_cood[2][0]
        drawText("Camera Pos : "+str(round(camera_pos[0], 2))+", "\
                                +str(round(camera_pos[1], 2))+", "\
                                +str(round(camera_pos[2], 2)), 2, 12, *screen_size)

        drawText("Camera Axe : "+str(round(self.camera_cood[0][0], 2))+", "\
                                +str(round(self.camera_cood[1][0], 2))+", "\
                                +str(round(self.camera_cood[2][0], 2)), 2, 2,  *screen_size)
        ## 関節角度の表示
        drawText("Meta Angle : "  + str(float(Meta_angle)), 2, screen_size[1]-10, *screen_size)
        drawText("ProP Angle : "  + str(float(ProP_angle)), 2, screen_size[1]-20, *screen_size)
        drawText("MidP Angle : "  + str(float(MidP_angle)), 2, screen_size[1]-30, *screen_size)
        drawText("DisP Angle  : " + str(float(DisP_angle)), 2, screen_size[1]-40, *screen_size)

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
        gluPerspective(40.0, 1.0, .1, 100.0)

#####    http://penguinitis.g1.xrea.com/computer/programming/Python/PyQt5/PyQt5-memo/PyQt5-memo.html
class Joint_Slider(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.gl = QTGLWidget2(self)
        self.Meta_lab = QLabel("0")
        self.ProP_lab = QLabel("0")
        self.MidP_lab = QLabel("0")
        self.DisP_lab = QLabel("0")

        self.Meta_lab.setFont(QtGui.QFont("Sanserif", 10))
        self.ProP_lab.setFont(QtGui.QFont("Sanserif", 10))
        self.MidP_lab.setFont(QtGui.QFont("Sanserif", 10))
        self.DisP_lab.setFont(QtGui.QFont("Sanserif", 10))

        self.initUI()

    def initUI(self):
        ## Meta,ProP,MidP,DisP
        Meta_slider = QSlider(Qt.Horizontal)
        ProP_slider = QSlider(Qt.Horizontal)
        MidP_slider = QSlider(Qt.Horizontal)
        DisP_slider = QSlider(Qt.Horizontal)

        Meta_slider.setMinimum(-10)
        Meta_slider.setMaximum(90)
        Meta_slider.valueChanged.connect(lambda val: self.gl.joint_listener("Meta", val))

        ProP_slider.setMinimum(-10)
        ProP_slider.setMaximum(90)
        ProP_slider.valueChanged.connect(lambda val: self.gl.joint_listener("ProP",val))

        MidP_slider.setMinimum(-10)
        MidP_slider.setMaximum(90)
        MidP_slider.valueChanged.connect(lambda val: self.gl.joint_listener("MidP",val))

        layout = QVBoxLayout()
        layout.addWidget(Meta_slider)
        layout.addWidget(ProP_slider)
        layout.addWidget(MidP_slider)

        self.setLayout(layout)

class Bone_CheckBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bool_list = [True, True, True, True]
        self.listCheckBox = names_list
        self.listLabel = []
        for label in range(len(self.listCheckBox)):
            self.listLabel.append("")
        self.gl = QTGLWidget2(self)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        for i, v in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QCheckBox(v)
            self.listLabel[i] = QLabel()
            layout.addWidget(self.listCheckBox[i], i+10, 0)
            layout.addWidget(self.listLabel[i],    i+10, 1)

        sc_button = QPushButton("Show / Clear")
        sc_button.clicked.connect(self.check_checkbox)
        layout.addWidget(sc_button, 20, 0)

        rst_button = QPushButton("RESER CAMERA VIEW")
        rst_button.clicked.connect(self.gl.cameraRESET)
        layout.addWidget(rst_button, 30, 0)

        self.setLayout(layout)

    def check_checkbox(self):
        for i, v in enumerate(self.listCheckBox):
            if v.checkState():
                self.bool_list[i]=True
            else:
                self.bool_list[i]=False
        self.gl.box_listener(self.bool_list)

class QTWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.clicked_points = [0, 0]

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

        widget1 = Joint_Slider(self)
        widget2 = Bone_CheckBox(self)

        tab = QTabWidget()
        tab.addTab(widget1, "Joint slider")
        tab.addTab(widget2, "Check Box (Bone)")

        gui_layout.addWidget(tab)

        self.setLayout(gui_layout)

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

if __name__=='__main__':
    app = QApplication(sys.argv)
    w = QTWidget()
    w.setWindowTitle(window_title)
    w.show()

    sys.exit(app.exec_())
