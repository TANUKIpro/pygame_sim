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
from dxf_loader import DXF_Loader
from stl_loader import STL_loader
from drawer import drawPolygon, drawText, drawText_3D, drawAxis, create_vbo, draw_vbo
import ctypes
import numpy as np
from math import sqrt, pi, exp

window_title = "Cloth SIM@PyQt5 v.0.5"
screen_size = [600, 500]
to_models = "/Users/ryotaro/py_projects/pygame_sim/model"

##################### DXF ANALYSATION #####################
extensor = "model/extensor_hood_test002.dxf"
## スケーリング済
extensor_reduced_scale = 1/1500
Extensor = DXF_Loader(extensor, extensor_reduced_scale, -0.65, 2, -1.)
stop_points_3d, particle_points_3d, poly_lines_3d = Extensor.ver_col_ind()
## オリジナルスケール
orgExtensor = DXF_Loader(extensor, 1, 0, 0, 0, integer=True)
org_sp_3d, org_pp_3d, org_pl_3d = orgExtensor.ver_col_ind()

const_set = []
for set in poly_lines_3d:
    for i in range(len(set)-1):
        const_set.append([set[i].tolist(), set[i+1].tolist()])

#####################  LOAD 3D MODEL  #####################
finger = "/Index"
names_list = ["/Metacarpal3_01.stl",
              "/Proximal_Phalanx3_01_org.stl",
              "/Middle_Phalanxh3_01_org.stl",
              "/Distal_Phalanxh3_01_org.stl"]

file_name = [to_models+finger+names_list[0],
             to_models+finger+names_list[1],
             to_models+finger+names_list[2],
             to_models+finger+names_list[3]]
bone_reduced_scale = 1/15
Metacarpal3       = STL_loader(file_name[0], bone_reduced_scale)
Proximal_Phalanx3 = STL_loader(file_name[1], bone_reduced_scale)
Middle_Phalanxh3  = STL_loader(file_name[2], bone_reduced_scale)
Distal_Phalanxh3  = STL_loader(file_name[3], bone_reduced_scale)

## 頂点座標, カラー, 構成インデックス
Meta_ver, Meta_col, Meta_ind = Metacarpal3.ver_col_ind()
ProP_ver, ProP_col, ProP_ind = Proximal_Phalanx3.ver_col_ind()
MidP_ver, MidP_col, MidP_ind = Middle_Phalanxh3.ver_col_ind()
DisP_ver, DisP_col, DisP_ind = Distal_Phalanxh3.ver_col_ind()

## フレーム用カラー
Meta_Frame_col = Metacarpal3.color(Meta_ver, _r=0, _g=0, _b=0)
ProP_Frame_col = Metacarpal3.color(ProP_ver, _r=0, _g=0, _b=0)
MidP_Frame_col = Metacarpal3.color(MidP_ver, _r=0, _g=0, _b=0)
DisP_Frame_col = Metacarpal3.color(DisP_ver, _r=0, _g=0, _b=0)

""" 各モデルの座標の最大値(Y軸) """
Meta_max_index = np.argmax(np.array(Metacarpal3.all_mesh_particle)[:,1])
Meta_max_cood = Metacarpal3.all_mesh_particle[Meta_max_index]
ProP_max_index = np.argmax(np.array(Proximal_Phalanx3.all_mesh_particle)[:,1])
ProP_max_cood = Metacarpal3.all_mesh_particle[ProP_max_index]
MidP_max_index = np.argmax(np.array(Middle_Phalanxh3.all_mesh_particle)[:,1])
MidP_max_cood = Metacarpal3.all_mesh_particle[MidP_max_index]

###############################################################

def gaussian_function(sigma, mu, x, A=1.25):
    return A*(1/sqrt(2*pi*sigma) * exp(-1/(2*sigma*sigma)*(x-mu)**2))

def super_gaussian_function(sigma, mu, lmd, x, A=1.25):
    return A*exp(-(1/2*sigma*sigma*(x-mu)**2)**lmd)

def subtract(vec1,vec2):
    return [vec1[i]-vec2[i] for i in [0,1,2]]

def get_length(vec):
    return sum([vec[i]*vec[i] for i in [0,1,2]])**0.5

BLACK = (0, 0, 0)
WHITE = (1, 1, 1)
RED   = (1, 0, 0)
GREEN = (0, 1, 0)

delta_t = 0.1
NUM_ITER = 3

class Particle:
    def __init__(self, x, y, z, m=1.0):
        self.m = m
        self.init_x, self.init_y, self.init_z = x, y, z
        self.x, self.y, self.z = x, y, z
        self.oldx, self.oldy, self.oldz = x, y, z
        self.newx, self.newy, self.newz = x, y, z
        self.ax = 0
        self.ay = 0#-9.8 #0
        self.az = 0

        self.fixed = False
        self.selected = False

    def update(self, delta_t):
        if self.fixed == False:
            # Verlet Integration
            # (https://www.watanabe-lab.jp/blog/archives/1993)
            self.newx = 2.0 * self.x - self.oldx + self.ax * delta_t**2
            self.newy = 2.0 * self.y - self.oldy + self.ay * delta_t**2
            self.newz = 2.0 * self.z - self.oldz + self.az * delta_t**2
            self.oldx = self.x
            self.oldy = self.y
            self.oldz = self.z
            self.x = self.newx
            self.y = self.newy
            self.z = self.newz

    def set_pos(self, pos):
        self.x, self.y, self.z = pos

    def draw(self):
        if self.fixed == True:
            color = GREEN
            moji = str(self.x)+", "+str(self.y)+", "+str(self.z)
            #t_xt = font.render(moji, True, (0, 0, 0))
            #screen.blit(txt, [self.x, self.y])
        else:
            color = BLACK
        if self.selected == True:
            color = RED

        glColor3f(1, 0, 0);
        glPointSize(10);
        glBegin(GL_POINTS);
        glVertex3fv(tuple((self.x, self.y, self.z)));
        glEnd();

# パーティクルへの拘束条件
class Constraint:
    def __init__(self, index0, index1):
        self.index0 = index0
        self.index1 = index1
        delta_x = particles[index0].x - particles[index1].x
        delta_y = particles[index0].y - particles[index1].y
        delta_z = particles[index0].z - particles[index1].z
        self.restLength = sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        self.init_d = 0
        self.d      = 0

    def update(self):
        delta_x = particles[self.index1].x - particles[self.index0].x
        delta_y = particles[self.index1].y - particles[self.index0].y
        delta_z = particles[self.index1].z - particles[self.index0].z
        deltaLength = sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        diff = (deltaLength - self.restLength)/(deltaLength+0.001)

        le = 0.5
        if particles[self.index0].fixed == False:
            particles[self.index0].x += le * diff * delta_x
            particles[self.index0].y += le * diff * delta_y
            particles[self.index0].z += le * diff * delta_z
        if particles[self.index1].fixed == False:
            particles[self.index1].x -= le * diff * delta_x
            particles[self.index1].y -= le * diff * delta_y
            particles[self.index1].z += le * diff * delta_z

    def draw(self):
        ## 初期位置からパーティクル間の距離を計算
        f_x0 = particles[self.index0].init_x
        f_y0 = particles[self.index0].init_y
        f_z0 = particles[self.index0].init_z
        f_x1 = particles[self.index1].init_x
        f_y1 = particles[self.index1].init_y
        f_z1 = particles[self.index1].init_z
        self.init_d = sqrt((f_x0-f_x1)**2+(f_y0-f_y1)**2+(f_z0-f_z1)**2)

        x0 = particles[self.index0].x
        y0 = particles[self.index0].y
        z0 = particles[self.index0].z
        x1 = particles[self.index1].x
        y1 = particles[self.index1].y
        z1 = particles[self.index1].z
        self.d = sqrt((x0-x1)**2+(y0-y1)**2++(z0-z1)**2)

        #pygame.draw.line(surf, rgb(d, minimum=init_d, maximum=init_d*1.25),
        #                 (int(x0), int(y0)), (int(x1), int(y1)), size)
        glColor3f(1, 0, 1)
        glBegin(GL_LINES)
        glVertex3fv(tuple((x0, y0, z0)))
        glVertex3fv(tuple((x1, y1, z1)))
        glEnd()
###
###stop_points_3d, particle_points_3d, poly_lines_3d
particles = []
for p_point in particle_points_3d:
    p = Particle(p_point[0], p_point[1], p_point[2])
    particles.append(p)

for sp in stop_points_3d:
    try:
        anc_idx = particle_points_3d.tolist().index(sp.tolist())
        particles[anc_idx].fixed = True
    except:
        print("sp error : ", sp)

constraints = []
for pl in poly_lines_3d:
    top_count = len(pl)
    pl = pl.tolist()
    for i in range(top_count-1):
        try:
            index0 = particle_points_3d.tolist().index(pl[i])
            index1 = particle_points_3d.tolist().index(pl[i+1])
            c = Constraint(index0, index1)
            constraints.append(c)
        except:
            print("pl error : ",pl[i])

#print(constraints)
#sys.exit()

Meta_angle, Meta_AbdAdd_angle, ProP_angle, MidP_angle, DisP_angle = 0., 0., 0., 0., 0.
Meta, PrxPh, MddPh, DisPh = False, False, False, False
DisP_1, DisP_2, DisP_3 = [0,0,0], [0,0,0], [0,0,0]
MidP_1, MidP_2, MidP_3 = [0,0,0], [0,0,0], [0,0,0]
serect = None
class DrawWidget(QGLWidget):
    Meta_buff=np.array([None])
    ProP_buff=np.array([None])
    MidP_buff=np.array([None])
    DisP_buff=np.array([None])

    outMeta_buff=np.array([None])
    outProP_buff=np.array([None])
    outMidP_buff=np.array([None])
    outDisP_buff=np.array([None])
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
        self.bRGB = [.0, .0, .0]
        self.Meta, self.PrxPh, self.MddPh, self.DisPh = False, False, False, False
        self.keys_list = []
        self.all_camera_status = []
        #self.Meta_angle, self.ProP_angle, self.MidP_angle, self.DisP_angle = 0., 0., 0., 0.

    def mode_sp(self, mode):
        global serect
        if   mode==0:serect="DisP_1";
        elif mode==1:serect="DisP_2";
        elif mode==2:serect="DisP_3";
        elif mode==3:serect="MidP_1";
        elif mode==4:serect="MidP_2";
        elif mode==5:serect="MidP_3";

    def sp_slide_listener(self, axis, val):
        global DisP_1, DisP_2, DisP_3, MidP_1, MidP_2, MidP_3
        if   serect=="DisP_1":
            if   axis=="X":DisP_1[0]=val
            elif axis=="Y":DisP_1[1]=val
            elif axis=="Z":DisP_1[2]=val
            print(serect, DisP_1)
        elif serect=="DisP_2":
            if   axis=="X":DisP_2[0]=val
            elif axis=="Y":DisP_2[1]=val
            elif axis=="Z":DisP_2[2]=val
            print(serect, DisP_2)
        elif serect=="DisP_3":
            if   axis=="X":DisP_3[0]=val
            elif axis=="Y":DisP_3[1]=val
            elif axis=="Z":DisP_3[2]=val
            print(serect, DisP_3)
        elif serect=="MidP_1":
            if   axis=="X":MidP_1[0]=val
            elif axis=="Y":MidP_1[1]=val
            elif axis=="Z":MidP_1[2]=val
            print(serect, MidP_1)
        elif serect=="MidP_2":
            if   axis=="X":MidP_2[0]=val
            elif axis=="Y":MidP_2[1]=val
            elif axis=="Z":MidP_2[2]=val
            print(serect, MidP_2)
        elif serect=="MidP_3":
            if   axis=="X":MidP_3[0]=val
            elif axis=="Y":MidP_3[1]=val
            elif axis=="Z":MidP_3[2]=val
            print(serect, MidP_3)
        else:print("serect is None")

    def joint_listener(self, typ, val):
        global Meta_angle, Meta_AbdAdd_angle, ProP_angle, MidP_angle, DisP_angle
        if   typ=="Meta":Meta_angle=val
        elif typ=="Meta_AbdAdd":Meta_AbdAdd_angle=val
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

    def mouse_listener(self, type, event, mv_cood=[0, 0]):
        ## LEFT, MIDDLE, RIGHT, WHEEL, MOVE
        move_pix = 0.5
        if type == 'MOVE':
            self.camera_rot[0] += mv_cood[0]
            self.camera_rot[1] += mv_cood[1]
        if type == 'WHEEL':
            if   event.angleDelta().y() == 120  : self.camera_radius -= move_pix
            elif event.angleDelta().y() == -120 : self.camera_radius += move_pix

    def cameraRESET(self):
        self.camera_rot = [70,23]
        self.camera_radius = 2.5
        self.camera_center = [0.5,0.5,0.5]
        self.camera_cood = [[0.],[0.],[0.]]
        self.angle_x, self.angle_y, self.angle_z = 0., 0., 0.
        self.vias_x, self.vias_y, self.vias_z = 0.,0.,0.

    def paintGL(self):
        glClearColor(*self.bRGB, 0.0)
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

        drawText_3D("X", 3., 0., 0.)
        drawText_3D("Y", 0., 3., 0.)
        drawText_3D("Z", 0., 0., 3.)
        drawAxis()

        ##############################  DRAW BONES  ##############################
        glPushMatrix();
        ## 中手骨の描画
        if not Meta:
            global Meta_buff, outMeta_buff
            if self.Meta_buff.all()==None:
                Meta_buff    = create_vbo(self.Meta_buff, Meta_ver, Meta_col, Meta_ind)
                outMeta_buff = create_vbo(self.outMeta_buff, Meta_ver, Meta_Frame_col, Meta_ind)
            draw_vbo(Meta_buff, Meta_ind)
            draw_vbo(outMeta_buff, Meta_ind, mode_front=GL_LINE, mode_back=GL_LINE)

        ## 基節骨の描画
        glTranslatef(2.4, (Meta_max_cood[1]-0.2)-Meta_angle*0.01, Meta_angle*0.002)
        if not PrxPh:
            global ProP_buff, outProP_buff
            if self.ProP_buff.all()==None:
                ProP_buff    = create_vbo(self.ProP_buff, ProP_ver, ProP_col, ProP_ind)
                outProP_buff = create_vbo(self.outProP_buff, ProP_ver, ProP_Frame_col, ProP_ind)
            glRotatef(Meta_angle, 1, 0, 0)
            glTranslatef(-1.2,0,0)
            glRotated(Meta_AbdAdd_angle, 0, 0, 1)
            glTranslatef(-1.2-Meta_AbdAdd_angle*0.003,0,0)
            draw_vbo(ProP_buff, ProP_ind)
            draw_vbo(outProP_buff, ProP_ind, mode_front=GL_LINE)

        ## 中節骨の描画
        mddp_vias = gaussian_function(sigma=20, mu=60, x=ProP_angle, A=1.7)
        glTranslatef(0, (1.462+1.8)-ProP_angle*0.008, -ProP_angle*0.001+mddp_vias)
        if not MddPh:
            global MidP_buff, outMidP_buff
            if self.MidP_buff.all()==None:
                MidP_buff    = create_vbo(self.MidP_buff, MidP_ver, MidP_col, MidP_ind)
                outMidP_buff = create_vbo(self.outMidP_buff, MidP_ver, MidP_Frame_col, MidP_ind)
            glRotatef(ProP_angle+3, 1, 0, 0)
            draw_vbo(MidP_buff, MidP_ind)
            draw_vbo(outMidP_buff, MidP_ind, mode_front=GL_LINE)

        ## 末節骨の描画
        disp_vias = gaussian_function(sigma=25, mu=70, x=MidP_angle, A=1.9)
        glTranslatef(0, (2.906-0.95)-MidP_angle*0.009, -MidP_angle*0.005+disp_vias)
        if not DisPh:
            global DisP_buff, outDisP_buff
            if self.DisP_buff.all()==None:
                DisP_buff    = create_vbo(self.DisP_buff, DisP_ver, DisP_col, DisP_ind)
                outDisP_buff = create_vbo(self.outDisP_buff, DisP_ver, DisP_Frame_col, DisP_ind)
            glRotatef(MidP_angle+3, 1, 0, 0)
            draw_vbo(DisP_buff, DisP_ind)
            draw_vbo(outDisP_buff, DisP_ind, mode_front=GL_LINE)
        glPopMatrix();
        ##########################################################################

        ## 座標の表示    -self.camera_cood[0][0], -self.camera_cood[1][0], -self.camera_cood[2][0]
        drawText("Camera Pos : "+str(round(camera_pos[0], 2))+", "\
                                +str(round(camera_pos[1], 2))+", "\
                                +str(round(camera_pos[2], 2)), 2, 12, *screen_size)

        drawText("Camera Axe : "+str(round(self.camera_cood[0][0], 2))+", "\
                                +str(round(self.camera_cood[1][0], 2))+", "\
                                +str(round(self.camera_cood[2][0], 2)), 2, 2,  *screen_size)
        ## 関節角度の表示
        drawText("Meta Angle : " +str(float(Meta_angle))+"°"+"   |   "
                +"Meta Abd & Add Angle : "+str(float(Meta_AbdAdd_angle))+"°",2, screen_size[1]-10, *screen_size)
        drawText("ProP Angle : " +str(float(ProP_angle))+"°", 2, screen_size[1]-20, *screen_size)
        drawText("MidP Angle : " +str(float(MidP_angle))+"°", 2, screen_size[1]-30, *screen_size)
        drawText("DisP Angle  : "+str(float(DisP_angle))+"°", 2, screen_size[1]-40, *screen_size)

        ##########################  DRAW EXTENSOR HOOD  ##########################
        for i in range(len(particles)):
            particles[i].update(delta_t)

        for i in range(NUM_ITER):
            for ii in range(len(constraints)):
                constraints[ii].update()

        for i in range(len(particles)):
            particles[i].draw()

        for i in range(len(constraints)):
            constraints[i].draw()
        """
        glPushMatrix();
        glColor3f(1, 0, 1)
        #glTranslatef(*DisP_1)
        glTranslatef(2.4, 9, 0.7)
        glLineWidth(5.0)
        for line_clump in poly_lines_3d:
            glBegin(GL_LINE_STRIP)
            for poly in line_clump:
                glVertex3fv(poly)
            glEnd()
        glPopMatrix();

        glPushMatrix();
        glColor3f(0, 1, 0)
        glTranslatef(2.4, 9, 0.7)
        glPointSize(15)
        glBegin(GL_POINTS)
        for sp in stop_points_3d:
            glVertex3fv(sp)
        glEnd()
        glPopMatrix();
        """

        ##########################################################################

        ## 原点の描画
        glColor3f(1, 1, 0)
        glPointSize(30)
        glBegin(GL_POINTS)
        glVertex3fv(self.org)
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

        glClearColor(*self.bRGB, 1.0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, 1.0, .1, 100.0)

#####    http://penguinitis.g1.xrea.com/computer/programming/Python/PyQt5/PyQt5-memo/PyQt5-memo.html
class Joint_Slider(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.gl = DrawWidget(self)
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
        splitter1 = QSplitter(Qt.Vertical)
        splitter2 = QSplitter(Qt.Vertical)
        splitter3 = QSplitter(Qt.Vertical)
        ## Meta,ProP,MidP,DisP
        Meta_slider = QSlider(Qt.Horizontal)
        Meta_AbdAdd_slider = QSlider(Qt.Horizontal)
        ProP_slider = QSlider(Qt.Horizontal)
        MidP_slider = QSlider(Qt.Horizontal)
        DisP_slider = QSlider(Qt.Horizontal)

        label_Meta = QLabel("Angle of the Meta (Flexion / extension)　/ (abduction / adduction)")
        label_ProP = QLabel("Angle of the ProP (Flexion / extension)")
        label_MidP = QLabel("Angle of the MidP (Flexion / extension)")
        ## 屈曲 / 伸展
        Meta_slider.setMinimum(-10)
        Meta_slider.setMaximum(90)
        Meta_slider.valueChanged.connect(lambda val: self.gl.joint_listener("Meta", val))
        ## 外転 / 内転
        Meta_AbdAdd_slider.setMinimum(-20)
        Meta_AbdAdd_slider.setMaximum(20)
        Meta_AbdAdd_slider.valueChanged.connect(lambda val: self.gl.joint_listener("Meta_AbdAdd",val))
        splitter1.addWidget(label_Meta)
        splitter1.addWidget(Meta_slider)
        splitter1.addWidget(Meta_AbdAdd_slider)
        splitter1.setFrameShape(QFrame.Panel)

        ## 屈曲 / 伸展
        ProP_slider.setMinimum(-10)
        ProP_slider.setMaximum(90)
        ProP_slider.valueChanged.connect(lambda val: self.gl.joint_listener("ProP",val))
        splitter2.addWidget(label_ProP)
        splitter2.addWidget(ProP_slider)
        splitter2.setFrameShape(QFrame.Panel)

        ## 屈曲 / 伸展
        MidP_slider.setMinimum(-10)
        MidP_slider.setMaximum(90)
        MidP_slider.valueChanged.connect(lambda val: self.gl.joint_listener("MidP",val))
        splitter3.addWidget(label_MidP)
        splitter3.addWidget(MidP_slider)
        splitter3.setFrameShape(QFrame.Panel)

        layout   = QVBoxLayout()
        layout.addWidget(splitter1)
        layout.addWidget(splitter2)
        layout.addWidget(splitter3)

        self.setLayout(layout)

class Coordination_slider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gl = DrawWidget(self)
        ## パーティクルの移動
        slider_x = QSlider(Qt.Horizontal)
        slider_x.setMinimum(-10)
        slider_x.setMaximum(10)
        slider_x.setTickInterval(.1)
        slider_x.valueChanged.connect(lambda val: self.gl.sp_slide_listener("X", val))

        slider_y = QSlider(Qt.Horizontal)
        slider_y.setMinimum(-10)
        slider_y.setMaximum(10)
        slider_y.setTickInterval(.1)
        slider_y.valueChanged.connect(lambda val: self.gl.sp_slide_listener("Y", val))

        slider_z = QSlider(Qt.Horizontal)
        slider_z.setMinimum(-10)
        slider_z.setMaximum(10)
        slider_z.setTickInterval(.1)
        slider_z.valueChanged.connect(lambda val: self.gl.sp_slide_listener("Z", val))

        label_x = QLabel("Coordination X")
        label_y = QLabel("Coordination Y")
        label_z = QLabel("Coordination Z")

        layout = QVBoxLayout()

        layout.addWidget(label_x)
        layout.addWidget(slider_x)
        layout.addWidget(label_y)
        layout.addWidget(slider_y)
        layout.addWidget(label_z)
        layout.addWidget(slider_z)

        self.setLayout(layout)

class Particle_cBox(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gl = DrawWidget(self)
        ## パーティクルの選択
        cBox_label = QLabel("Select Stop Particle")
        self.combo = QComboBox(self)
        self.combo.addItem("DisP_1")
        self.combo.addItem("DisP_2")
        self.combo.addItem("DisP_3")
        self.combo.addItem("MidP_1")
        self.combo.addItem("MidP_2")
        self.combo.addItem("MidP_3")

        button = QPushButton("Check")
        button.clicked.connect(self.buttonClicked)

        layout = QVBoxLayout()
        layout.addWidget(cBox_label)
        layout.addWidget(self.combo)
        layout.addWidget(button)

        self.setLayout(layout)

    def buttonClicked(self):
        self.gl.mode_sp(self.combo.currentIndex())

class AnchorPoint_Slider(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gl = DrawWidget(self)

        self.initUI()

    def initUI(self):
        frame1 = Particle_cBox(self)
        frame1.setFrameShape(QFrame.Panel)

        frame2 = Coordination_slider(self)
        frame2.setFrameShape(QFrame.Panel)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(frame1)
        splitter.addWidget(frame2)
        splitter.setHandleWidth(10)

        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

class Bone_CheckBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bool_list = [True, True, True, True]
        self.listCheckBox = names_list
        self.listLabel = []
        self.layout = QGridLayout()
        for label in range(len(self.listCheckBox)):
            self.listLabel.append("")
        self.gl = DrawWidget(self)
        self.initUI()

    def initUI(self):
        for i, v in enumerate(self.listCheckBox):
            self.listCheckBox[i] = QCheckBox(v)
            self.listLabel[i] = QLabel()
            self.layout.addWidget(self.listCheckBox[i], i+10, 0)
            self.layout.addWidget(self.listLabel[i],    i+10, 1)

        sc_button = QPushButton("Show / Clear")
        sc_button.clicked.connect(self.check_checkbox)
        self.layout.addWidget(sc_button, 20, 0)

        #rst_button = QPushButton("RESER CAMERA VIEW")
        #rst_button.clicked.connect(self.gl.cameraRESET)
        #layout.addWidget(rst_button, 30, 0)
        self.setLayout(self.layout)

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
        self.gl = DrawWidget(self)
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
        widget3 = AnchorPoint_Slider(self)

        tab = QTabWidget()
        tab.addTab(widget1, "Joint slider")
        tab.addTab(widget2, "Check Box (Bone)")
        tab.addTab(widget3, "Stop Particle slider")

        rst_button = QPushButton("RESER CAMERA VIEW")
        rst_button.clicked.connect(self.gl.cameraRESET)
        widget2.layout.addWidget(rst_button, 30, 0)

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
