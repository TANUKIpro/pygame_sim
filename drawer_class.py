# -*- coding: utf-8 -*-
import sys, os, traceback, time
from functools import lru_cache
from math import sin, cos, sqrt, radians
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


org = tuple((0,0,0))
org_points = [[tuple((0, 0, 0)), tuple((5, 0, 0))],
              [tuple((0, 0, 0)), tuple((0, 5, 0))],
              [tuple((0, 0, 0)), tuple((0, 0, 5))]]

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
