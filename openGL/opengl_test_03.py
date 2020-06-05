from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


vertex = [
    [ -1.0, -1.0, 1.0 ],
    [ 1.0, -1.0, 1.0 ],
    [ -1.0, 1.0, 1.0 ],
    [ 1.0, 1.0, 1.0 ],
    [ -1.0, 1.0, -1.0 ],
    [ 1.0, 1.0, -1.0 ],
    [ -1.0, -1.0, -1.0 ],
    [ 1.0, -1.0, -1.0 ]]

face = [
    [ 0, 1, 3, 2 ],
    [ 2, 3, 5, 4 ],
    [ 4, 5, 7, 6 ],
    [ 6, 7, 1, 0 ],
    [ 1, 7, 5, 3 ],
    [ 6, 0, 2, 4 ]]

color = [
    [ 1.0, 0.0, 0.0 ],
    [ 0.0, 1.0, 0.0 ],
    [ 0.0, 0.5, 0.5 ],
    [ 1.0, 1.0, 0.0 ],
    [ 1.0, 0.0, 1.0 ],
    [ 0.0, 1.0, 1.0 ]]

angleX = 0.0
angleY = 0.0


def resize(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, w/h, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)


def draw():
    global angleX, angleY

    glClearColor(0.0, 0.0, 1.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    gluLookAt(3.0, 4.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    glRotated(angleX, 1.0, 0.0, 0.0);
    glRotated(angleY, 0.0, 1.0, 0.0);

    glBegin(GL_QUADS)
    for j in range(0, len(face)):
        glColor3dv(color[j])
        for i in range(0, 4):
            glVertex(vertex[face[j][i]])
    glEnd()

    glFlush()
    glutSwapBuffers()


def keyboard(key, x, y):
    global angleX, angleY
    if key=='q':
        sys.exit()
    elif key=='h':
        angleY += 1.0
        glutPostRedisplay()
    elif key=='j':
        angleX += 1.0
        glutPostRedisplay()

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
glutInitWindowSize(320, 320)
glutCreateWindow("PyOpenGL 11")
glutDisplayFunc(draw)
glutReshapeFunc(resize)
glutKeyboardFunc(keyboard)

glClearColor(0.0, 0.0, 1.0, 0.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_CULL_FACE)
glCullFace(GL_BACK)

glutMainLoop()
