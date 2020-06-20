# -*- coding: utf-8 -*-
import sys, os, traceback, time
from functools import lru_cache
from math import sin, cos, sqrt, radians
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


org = tuple((0,0,0))
org_points = [[tuple((0, 0, 0)), tuple((3, 0, 0))],
              [tuple((0, 0, 0)), tuple((0, 3, 0))],
              [tuple((0, 0, 0)), tuple((0, 0, 3))]]

def drawEdge(points):
    glColor3f(0,0,0)
    glBegin(GL_LINE_STRIP)
    for point in points:
        glVertex3fv(point)
    glEnd()

def drawPolygon(points):
    glLineWidth(1.0)
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glColor3f(1,1,1)
    glBegin(GL_TRIANGLES)
    for point in points:
        glVertex3fv(point)
    glEnd()

def drawAxis():
    ## X
    glColor3f(1.0, 0.0, 0.0)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex3fv(org_points[0][0])
    glVertex3fv(org_points[0][1])
    glEnd()

    ## Y
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3fv(org_points[1][0])
    glVertex3fv(org_points[1][1])
    glEnd()

    ## Z
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3fv(org_points[2][0])
    glVertex3fv(org_points[2][1])
    glEnd()

def drawText(value, x, y, windowHeight, windowWidth):
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

def drawText_3D(value, x, y, z):
    glColor3f(1.0, 1.0, 1.0);
    cood = tuple((x, y, z))
    glRasterPos3f(x, y, z);
    lines = 0
    for character in value:
        if character == '\n':
            glRasterPos2i(x, y-(lines*18))
        else:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(character));

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

def create_vbo(buffers, vertices, colors, indices):
    buffers = glGenBuffers(3)
    glBindBuffer(GL_ARRAY_BUFFER, buffers[0])
    glBufferData(GL_ARRAY_BUFFER,
                 len(vertices)*4,  # byte size
                 (ctypes.c_float*len(vertices))(*vertices),
                 GL_STATIC_DRAW)

    glBindBuffer(GL_ARRAY_BUFFER, buffers[1])
    glBufferData(GL_ARRAY_BUFFER,
                 len(colors)*4, # byte size
                 (ctypes.c_float*len(colors))(*colors),
                 GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, buffers[2])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,
                 len(indices)*4, # byte size
                 (ctypes.c_uint*len(indices))(*indices),
                 GL_STATIC_DRAW)
    return buffers

def draw_vbo(buffers, indices, mode_front=GL_FILL, mode_back=GL_FILL):
    glEnable(GL_CULL_FACE)  # カリングを有効に
    glCullFace(GL_BACK)

    glPolygonMode(GL_FRONT, mode_front)
    glPolygonMode(GL_BACK,  mode_back)
    glLineWidth(1.5)

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
