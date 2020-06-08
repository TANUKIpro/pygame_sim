# -*- coding: utf-8 -*-
import sys, os, traceback, time
from functools import lru_cache
from math import sin, cos, sqrt, radians

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from stl import mesh
import ctypes


screen_size = [800,600]
multisample = 16
window_title = "STL VIEW"

pygame.display.init()
pygame.font.init()
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption(window_title)
if multisample:
    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS,1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES,multisample)
screen = pygame.display.set_mode(screen_size,OPENGL|DOUBLEBUF)

glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST)
glEnable(GL_DEPTH_TEST)
glPointSize(4)

class STL_loader:
    def __init__(self, file_name, size):
        self.file_name = file_name
        self.size = size
        self.triangle_mesh = []
        self.quad_mesh     = []
        self.all_mesh_particle = []

    def load(self):
        # STLファイルの読み込み
        __mesh = mesh.Mesh.from_file(self.file_name)
        meshes = (__mesh.vectors) * self.size

        for m in meshes:
            if len(m) == 3:
                self.triangle_mesh.append(m)
            elif len(m) == 4:
                self.quad_mesh.append(m)
            else:
                print("ERROR")
                sys.exit()

        for _m in meshes:
            for particle in _m:
                self.all_mesh_particle.append(particle)

        return self.triangle_mesh, self.quad_mesh, self.all_mesh_particle


class OpenGL_sim:
    ## 描画するのに必要最低限の機能と表示
    def __init__(self):
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

    def get_input(self):
        keys_pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_rel = pygame.mouse.get_rel()
        key = pygame.key.get_pressed()
        move_pix = 0.5
        if key[K_LSHIFT]:
            if   key[K_x] : self.camera_cood[0][0] -= 0.1
            elif key[K_y] : self.camera_cood[1][0] -= 0.1
            elif key[K_z] : self.camera_cood[2][0] -= 0.1

            elif key[K_UP]  : self.angle_x += move_pix
            elif key[K_DOWN]: self.angle_x -= move_pix

        elif key[K_x] : self.camera_cood[0][0] += 0.1
        elif key[K_y] : self.camera_cood[1][0] += 0.1
        elif key[K_z] : self.camera_cood[2][0] += 0.1
        elif key[K_ESCAPE] : self.camera_cood = [[0.],[0.],[0.]]

        elif key[K_LEFT]  : self.angle_y += move_pix
        elif key[K_RIGHT] : self.angle_y -= move_pix
        elif key[K_UP]    : self.angle_z += move_pix
        elif key[K_DOWN]  : self.angle_z -= move_pix

        for event in pygame.event.get():
            if   event.type == QUIT:
                return False
            #elif event.type == KEYDOWN:
            #    if event.key == K_ESCAPE:
            #        return False
            elif event.type == MOUSEBUTTONDOWN:
                if   event.button == 4: self.camera_radius -= move_pix
                elif event.button == 5: self.camera_radius += move_pix

        if mouse_buttons[0]:
            self.camera_rot[0] += mouse_rel[0]
            self.camera_rot[1] += mouse_rel[1]
        return True

    def drawEdge(self, points):
        glColor3f(0,0,0)
        glBegin(GL_LINE_STRIP)
        for point in points:
            glVertex3fv(point)
        glEnd()

    #@lru_cache()
    def drawPolygon(self, points):
        glLineWidth(1.0)
        glPolygonMode(GL_FRONT, GL_LINE)
        glPolygonMode(GL_BACK, GL_LINE)
        glColor3f(1,1,1)
        glBegin(GL_TRIANGLES)
        for point in points:
            glVertex3fv(point)
        glEnd()

    #@lru_cache()
    def drawAxis(self):
        ## X
        glColor3f(1.0, 0.0, 0.0)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex3fv(self.org_points[0][0])
        glVertex3fv(self.org_points[0][1])
        glEnd()

        ## Y
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3fv(self.org_points[1][0])
        glVertex3fv(self.org_points[1][1])
        glEnd()

        ## Z
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3fv(self.org_points[2][0])
        glVertex3fv(self.org_points[2][1])
        glEnd()

    def drawText(self, value, x, y,
                 windowHeight=screen_size[0], windowWidth=screen_size[1]):
        ## 文字列をビットマップフォントで描画
        glMatrixMode(GL_PROJECTION);
        matrix = glGetDouble( GL_PROJECTION_MATRIX )

        glLoadIdentity();
        glOrtho(0.0, windowHeight, 0.0, windowWidth, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW);
        glPushMatrix();
        glLoadIdentity();

        glColor3f(1.0, 1.0, 1.0);
        glRasterPos2i(x, y);
        lines = 0
        for character in value:
            if character == '\n':
                glRasterPos2i(x, y-(lines*18))
            else:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character));
        glPopMatrix();
        glMatrixMode(GL_PROJECTION);
        glLoadMatrixd(matrix)
        glMatrixMode(GL_MODELVIEW);

    def drawText_3D(self, value, x, y, z):
        glColor3f(1.0, 1.0, 1.0);
        cood = tuple((x, y, z))
        glRasterPos3f(x, y, z);
        lines = 0
        for character in value:
            if character == '\n':
                glRasterPos2i(x, y-(lines*18))
            else:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character));

    def set_AxisViw_and_CameraAngle(self,org_point=True, axis=True):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glViewport(0,0,screen_size[0],screen_size[1])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera_wide_angle,float(screen_size[0])/float(screen_size[1]), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        camera_pos = [self.camera_center[0] + self.camera_radius*cos(radians(self.camera_rot[0]))*cos(radians(self.camera_rot[1])),
                      self.camera_center[1] + self.camera_radius*sin(radians(self.camera_rot[1])),
                      self.camera_center[2] + self.camera_radius*sin(radians(self.camera_rot[0]))*cos(radians(self.camera_rot[1]))]

        ####  gluLookAt(視点の位置(x,y,z), 目標の位置(x,y,z), 法線ベクトル(,,))
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
                  self.camera_center[0], self.camera_center[1], self.camera_center[2], 0,1,0)

        ## 指定軸に対して回転
        glRotated(self.angle_x, 1.0, 0.0, 0.0)
        glRotated(self.angle_y, 0.0, 1.0, 0.0)
        glRotated(self.angle_z, 0.0, 0.0, 1.0)
        ## 指定軸に対して平行移動
        glTranslatef(-self.camera_cood[0][0], -self.camera_cood[1][0], -self.camera_cood[2][0])

        if org_point:
            glColor3f(1, 1, 0)
            glPointSize(15)
            glBegin(GL_POINTS)
            glVertex3fv(self.org)
            glEnd()
        if axis:
            self.drawText_3D("X", 5., 0., 0.)
            self.drawText_3D("Y", 0., 5., 0.)
            self.drawText_3D("Z", 0., 0., 5.)
            self.drawAxis()

gl_set = OpenGL_sim()
file_name = ["../model/Index/Metacarpal3_01.stl",
             "../model/Index/Proximal_Phalanx3_01.stl",
             "../model/Index/Middle_Phalanxh3_01.stl",
             "../model/Index/Distal_Phalanxh3_01.stl"]
size = 1/15
Metacarpal3, _, _       = STL_loader(file_name[0], size).load()
Proximal_Phalanx3, _, _ = STL_loader(file_name[1], size).load()
Middle_Phalanxh3,  _, _ = STL_loader(file_name[2], size).load()
Distal_Phalanxh3,  _, _ = STL_loader(file_name[3], size).load()

def draw():
    gl_set.set_AxisViw_and_CameraAngle(org_point=True, axis=True)
    gl_set.drawText("TEST", 5, 580)

    for idx_Meta in Metacarpal3:
        gl_set.drawPolygon(idx_Meta)
    for idx_PrxPh in Proximal_Phalanx3:
        gl_set.drawPolygon(idx_PrxPh)
    for idx_MddPh in Middle_Phalanxh3:
        gl_set.drawPolygon(idx_MddPh)
    for idx_DisPh in Distal_Phalanxh3:
        gl_set.drawPolygon(idx_DisPh)

    glFlush()
    glutSwapBuffers()
    pygame.display.flip()

def main():
    target_fps = 60
    clock = pygame.time.Clock()

    while True:
        if not gl_set.get_input(): break
        draw()
        clock.tick(target_fps)
    pygame.quit()

if __name__=="__main__":
    try:
        main()
    except:
        traceback.print_exc()
        pygame.quit()
        sys.exit()
