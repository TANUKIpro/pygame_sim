# -*- coding: utf-8 -*-
import sys, os, traceback, time
from functools import lru_cache
from math import sin, cos, sqrt, radians

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo

from PyQt5.QtWidgets import *
from PyQt5 import QtCore as Qt
from PyQt5.QtCore import *
from PyQt5.QtOpenGL import *

from stl import mesh
from stl_load_class import STL_loader
from drawer_class import drawPolygon, drawText, drawText_3D, drawAxis
import ctypes

import numpy as np
########   https://nrotella.github.io/journal/first-steps-python-qt-opengl.html   ########

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
size = 1/30
"""
Metacarpal3,       _, _ = STL_loader(file_name[0], size).load()
Proximal_Phalanx3, _, _ = STL_loader(file_name[1], size).load()
Middle_Phalanxh3,  _, _ = STL_loader(file_name[2], size).load()
Distal_Phalanxh3,  _, _ = STL_loader(file_name[3], size).load()
"""
##########    https://qiita.com/ousttrue/items/e343baabdbdd6b7891c4    ##########

Metacarpal3 = STL_loader(to_models+"/only_index.stl", size)
vertices, colors, indices = Metacarpal3.ver_col_ind()

#
# 描画関数 glBegin
#
##################    Normal    ##################
def draw_cube0():
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glBegin(GL_TRIANGLES)
    for i in range(0, len(indices), 3):
        index=indices[i]*3
        glColor3f(*colors[index:index+3])
        glVertex3f(*vertices[index:index+3])

        index=indices[i+1]*3
        glColor3f(*colors[index:index+3])
        glVertex3f(*vertices[index:index+3])

        index=indices[i+2]*3
        glColor3f(*colors[index:index+3])
        glVertex3f(*vertices[index:index+3])
    glEnd()

##################    glVertexPointer without VBO    ##################
def draw_cube1():
    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_COLOR_ARRAY);
    glVertexPointer(3, GL_FLOAT, 0, vertices);
    glColorPointer(3, GL_FLOAT, 0, colors)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices);
    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY);

##################    glVertexPointer with VBO without Shader    ##################
buffers=np.array([None])
def create_vbo():
    buffers = glGenBuffers(3)
    glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
    glBufferData(GL_ARRAY_BUFFER,
            len(vertices)*4,  # byte size
            (ctypes.c_float*len(vertices))(*vertices), # 謎のctypes
            GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
    glBufferData(GL_ARRAY_BUFFER,
            len(colors)*4, # byte size
            (ctypes.c_float*len(colors))(*colors),  # 謎のctypes
            GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
            len(indices)*4, # byte size
            (ctypes.c_uint*len(indices))(*indices),  # 謎のctypes
            GL_STATIC_DRAW)
    return buffers

def draw_vbo():
    glEnableClientState(GL_VERTEX_ARRAY);
    glEnableClientState(GL_COLOR_ARRAY);
    glBindBuffer(GL_ARRAY_BUFFER, buffers[0]);
    glVertexPointer(3, GL_FLOAT, 0, None);
    glBindBuffer(GL_ARRAY_BUFFER, buffers[1]);
    glColorPointer(3, GL_FLOAT, 0, None);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2]);
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None);
    glDisableClientState(GL_COLOR_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY);

def draw_cube2():
    global buffers
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    if buffers.all()==None:
        buffers=create_vbo()
    draw_vbo()

###################################################################################

def initialize():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)

def resize(Width, Height):
    # viewport
    if Height == 0:
        Height = 1
    glViewport(0, 0, Width, Height)
    # projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(Width)/float(Height), 0.1, 100.0)


yaw=0
pitch=0
def draw():
    global yaw, pitch
    # clear
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # view
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    yaw+=0.39
    pitch+=0.27
    glTranslatef(0.0, 0.0, -2.0)
    glRotatef(yaw, 0, 1, 0)
    glRotatef(pitch, 1, 0, 0)

    # cube
    draw_cube2()

    glFlush()


##############################################################################
# glut driver
##############################################################################

def reshape_func(w, h):
    resize(w, h == 0 and 1 or h)

def disp_func():
    draw()
    glutSwapBuffers()

if __name__=="__main__":
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(500, 500)
    glutCreateWindow(b"vbo")
    glutDisplayFunc(disp_func)
    glutIdleFunc(disp_func)
    glutReshapeFunc(reshape_func)

    initialize()

    glutMainLoop()
