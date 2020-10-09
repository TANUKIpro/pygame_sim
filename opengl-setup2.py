#!/usr/bin/python
# -*- coding: utf-8 -*-

from ctypes import c_int
from ctypes import c_uint
from ctypes import c_float
from ctypes import c_void_p
from ctypes import c_char
from ctypes import POINTER
from ctypes import CDLL
from ctypes import CFUNCTYPE
from ctypes import byref
from ctypes.util import find_library
from functools import partial
from numpy import zeros
from numpy import uint8
from numpy import array

EGLNativeDisplayType = c_void_p
EGLDisplay = c_void_p
EGL_DEFAULT_DISPLAY = EGLNativeDisplayType(0)
EGLBoolean = c_uint
EGLint = c_int
EGL_OPENGL_API = 0x30A2
EGLenum = c_uint
EGL_BLUE_SIZE = 0x3022
EGL_GREEN_SIZE = 0x3023
EGL_RED_SIZE = 0x3024
EGL_DEPTH_SIZE = 0x3025
EGL_SURFACE_TYPE = 0x3033
EGL_NONE = 0x3038
EGL_PBUFFER_BIT = 0x01
EGLConfig = c_void_p
EGL_HEIGHT = 0x3056
EGL_WIDTH = 0x3057
EGLSurface = c_void_p
EGL_CONTEXT_CLIENT_VERSION = 0x3098
EGLContext = c_void_p
EGL_NO_CONTEXT = EGLContext(0)
EGL_NO_SURFACE = EGLSurface(0)

GL_NO_ERROR = 0
GLenum = c_uint
GLuint = c_uint
GLsizei = c_int
GL_RENDERBUFFER = 0x8D41
GL_RGB8 = 0x8051
GL_RGBA8 = 0x8058
GL_RGB32F = 0x8815
GL_RGBA32F = 0x8814
GL_FRAMEBUFFER = 0x8D40
GL_COLOR_ATTACHMENT0 = 0x8CE0
GL_COLOR_ATTACHMENT1 = 0x8CE1
GL_COLOR_ATTACHMENT2 = 0x8CE2
GL_COLOR_ATTACHMENT3 = 0x8CE3
GL_COLOR_ATTACHMENT4 = 0x8CE4
GL_FRAMEBUFFER_COMPLETE = 0x8CD5
GL_FRAGMENT_SHADER = 0x8B30
GL_VERTEX_SHADER = 0x8B31
GLchar = c_char
GLint = c_int
GLfloat = c_float
GLbitfield = c_uint
GLint = c_int
GLsizei = c_int
GLvoid_p = c_void_p
GL_FALSE = 0
GL_TRUE = 1
GL_COMPILE_STATUS = 0x8B81
GL_INFO_LOG_LENGTH = 0x8B84
GL_COLOR_BUFFER_BIT = 0x00004000
GL_DEPTH_BUFFER_BIT = 0x00000100
GL_RGB = 0x1907
GL_UNSIGNED_BYTE = 0x1401

eglLib = CDLL(find_library('EGL'))
glLib = CDLL(find_library('GL'))

def load(lib, name, restype, *args):
    return (CFUNCTYPE(restype, *args))((name, lib))

def makeCtypeArray(ctype, contents):
    arrayType = ctype * len(contents)
    return arrayType(*contents)

loadEgl = partial(load, eglLib)
eglGetDisplay = loadEgl('eglGetDisplay', EGLDisplay, EGLNativeDisplayType)
eglInitialize = loadEgl('eglInitialize', EGLBoolean, EGLDisplay , POINTER(EGLint), POINTER(EGLint))
eglBindAPI = loadEgl('eglBindAPI', EGLBoolean, EGLenum)
eglChooseConfig = loadEgl('eglChooseConfig', EGLBoolean, EGLDisplay, POINTER(EGLint), POINTER(EGLConfig), EGLint, POINTER(EGLint))
eglCreatePbufferSurface = loadEgl('eglCreatePbufferSurface', EGLSurface, EGLDisplay, EGLConfig, POINTER(EGLint))
eglCreateContext = loadEgl('eglCreateContext', EGLContext, EGLDisplay, EGLConfig, EGLContext, POINTER(EGLint))
eglMakeCurrent = loadEgl('eglMakeCurrent', EGLBoolean, EGLDisplay, EGLSurface, EGLSurface, EGLContext)
eglDestroySurface = loadEgl('eglDestroySurface', EGLBoolean, EGLDisplay, EGLSurface)
eglDestroyContext = loadEgl('eglDestroyContext', EGLBoolean, EGLDisplay, EGLContext)
eglTerminate = loadEgl('eglTerminate', EGLBoolean, EGLDisplay)

loadGl = partial(load, glLib)
glGetError = loadGl('glGetError', GLenum)
glGenRenderbuffers = loadGl('glGenRenderbuffers', None, GLsizei, POINTER(GLuint))
glBindRenderbuffer = loadGl('glBindRenderbuffer', None, GLenum, GLuint)
glRenderbufferStorage = loadGl('glRenderbufferStorage', None, GLenum, GLenum, GLsizei, GLsizei)
glGenFramebuffers = loadGl('glGenFramebuffers', None, GLsizei, POINTER(GLuint))
glBindFramebuffer = loadGl('glBindFramebuffer', None, GLenum, GLuint)
glFramebufferRenderbuffer = loadGl('glFramebufferRenderbuffer', None, GLenum, GLenum, GLenum, GLuint)
glDrawBuffers = loadGl('glDrawBuffers', None, GLsizei, POINTER(GLenum))
glCheckFramebufferStatus = loadGl('glCheckFramebufferStatus', GLenum, GLenum)
glCreateShader = loadGl('glCreateShader', GLuint, GLenum)
glShaderSource = loadGl('glShaderSource', None, GLuint, GLsizei, POINTER(POINTER(GLchar)), POINTER(GLint))
glCompileShader = loadGl('glCompileShader', None, GLuint)
glGetShaderiv = loadGl('glGetShaderiv', None, GLuint, GLenum, POINTER(GLint))
glGetShaderInfoLog = loadGl('glGetShaderInfoLog', None, GLuint, GLsizei, POINTER(GLsizei), POINTER(GLchar))
glCreateProgram = loadGl('glCreateProgram', GLuint)
glClearColor = loadGl('glClearColor', None, GLfloat, GLfloat, GLfloat, GLfloat)
glClear = loadGl('glClear', None, GLbitfield)
glAttachShader = loadGl('glAttachShader', None, GLuint, GLuint)
glDeleteShader = loadGl('glDeleteShader', None, GLuint)
glBindAttribLocation = loadGl('glBindAttribLocation', None, GLuint, GLuint, POINTER(GLchar))
glBindFragDataLocation = loadGl('glBindFragDataLocation', None, GLuint, GLuint, POINTER(GLchar))
glLinkProgram = loadGl('glLinkProgram', None, GLuint)
glUseProgram = loadGl('glUseProgram', None, GLuint)
glReadBuffer = loadGl('glReadBuffer', None, GLenum)
glReadPixels = loadGl('glReadPixels', None, GLint, GLint, GLsizei, GLsizei, GLenum, GLenum, GLvoid_p)

# EGL Display
display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
if not display:
    raise Exception('no EGL display')

# EGL Initialize
major = EGLint(0)
minor = EGLint(0)
if not eglInitialize(display, byref(major), byref(minor)):
    raise Exception('cannot initialize EGL display')

# EGL BindAPI
if not eglBindAPI(EGLenum(EGL_OPENGL_API)):
    raise Exception('cannot bind API')

# EGL ChooseConfig
attribList = makeCtypeArray(EGLint, [
    EGL_BLUE_SIZE, 8,
    EGL_GREEN_SIZE, 8,
    EGL_RED_SIZE, 8,
    EGL_DEPTH_SIZE, 24,
    EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
    EGL_NONE])

config = EGLConfig()
configSize = EGLint(1)
numConfig = EGLint(0)
if not eglChooseConfig(display, attribList, byref(config), configSize, byref(numConfig)):
    raise Exception('no suitable configs available on display')

# EGL Surface
surfaceAttribList = makeCtypeArray(EGLint, [
    EGL_WIDTH, 100,
    EGL_HEIGHT, 100,
    EGL_NONE])

surface = eglCreatePbufferSurface(display, config, surfaceAttribList)
if not surface:
    raise Exception('cannot create pbuffer surface')

# EGL Context
contextAttribList = makeCtypeArray(EGLint, [EGL_NONE])
context = eglCreateContext(display, config, EGL_NO_CONTEXT, contextAttribList)
if not context:
    raise Exception('cannot create GL context')

# EGL MakeCurrent
if not eglMakeCurrent(display, surface, surface, context):
    raise Exception('cannot make GL context current')

# Generate render buffer
n = 1
renderbuffers = zeros(n, dtype=GLuint)
glGenRenderbuffers(GLsizei(n), renderbuffers.ctypes.data_as(POINTER(GLuint)))
if not glGetError() == GL_NO_ERROR:
    raise Exception('glGenRenderbuffers failed')

# Bind render buffer
glBindRenderbuffer(GL_RENDERBUFFER, GLuint(renderbuffers[0]))
if not glGetError() == GL_NO_ERROR:
    raise Exception('glBindRenderbuffer failed')

# Create buffer storage for render buffer
width,height = 100,100
glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8, GLsizei(width), GLsizei(height))
if not glGetError() == GL_NO_ERROR:
    raise Exception('glRenderbufferStorage failed')

# Unbind render buffer
glBindRenderbuffer(GL_RENDERBUFFER, GLuint(0))
if not glGetError() == GL_NO_ERROR:
    raise Exception('glBindRenderbuffer failed')

# Generate frame buffer
n = 1
ids = zeros(n, dtype=GLuint)
glGenFramebuffers(GLsizei(n), ids.ctypes.data_as(POINTER(GLuint)))
if not glGetError() == GL_NO_ERROR:
    raise Exception('glGenFramebuffers failed')

# Bind frame buffer
glBindFramebuffer(GL_FRAMEBUFFER, ids[0])
if not glGetError() == GL_NO_ERROR:
    raise Exception('glBindFramebuffer failed')

# Attach render buffer
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, renderbuffers[0])
if not glGetError() == GL_NO_ERROR:
    raise Exception('glFramebufferRenderbuffer failed')

# Set as color buffer
bufs = array([GL_COLOR_ATTACHMENT0], dtype=GLenum)
glDrawBuffers(GLsizei(1), bufs.ctypes.data_as(POINTER(GLenum)))
if not glGetError() == GL_NO_ERROR:
    raise Exception('glDrawBuffers failed')

# Verify frame buffer
status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
if not glGetError() == GL_NO_ERROR:
    raise Exception('glCheckFramebufferStatus failed')
if not status == GL_FRAMEBUFFER_COMPLETE:
    raise Exception('framebuffer not completed')

# Clear render buffer
glClearColor(GLfloat(1.0), GLfloat(1.0), GLfloat(1.0), GLfloat(1.0))
if not glGetError() == GL_NO_ERROR:
    raise Exception('glClearColor failed')

glClear(GLbitfield(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT))
if not glGetError() == GL_NO_ERROR:
    raise Exception('glClear failed')

# Create shader object
vobj = glCreateShader(GL_VERTEX_SHADER)
if not glGetError() == GL_NO_ERROR:
    raise Exception('glCreateShader failed')
fobj = glCreateShader(GL_FRAGMENT_SHADER)
if not glGetError() == GL_NO_ERROR:
    raise Exception('glCreateShader failed')

# Load shader related functions

# Create program
program = glCreateProgram()
if not glGetError() == GL_NO_ERROR:
    raise Exception('glCreateProgram failed')

# Load program related functions

# IPython
import IPython
IPython.embed()

# EGL Destroy
if not eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT):
    print('eglMakeCurrent failed')

if not eglDestroySurface(display, surface):
    print('eglDestroySurface failed')

if not eglDestroyContext(display, context):
    print('eglDestroyContext failed')

if not eglTerminate(display):
    print('eglTerminate failed')
