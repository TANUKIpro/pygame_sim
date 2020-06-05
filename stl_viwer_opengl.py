from stl import mesh
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys, os, traceback
from math import *
pygame.display.init()
pygame.font.init()

screen_size = [800,600]
multisample = 16
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption("STL VIEW")
if multisample:
    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS,1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES,multisample)
pygame.display.set_mode(screen_size,OPENGL|DOUBLEBUF)

glHint(GL_PERSPECTIVE_CORRECTION_HINT,GL_NICEST)
glEnable(GL_DEPTH_TEST)
glPointSize(4)

#file_name = "model/finger_bone_smooth_v1.stl"
file_name = "model/only_index.stl"

# STLファイルの読み込み
mesh = mesh.Mesh.from_file(file_name)
meshes = (mesh.vectors) / 30

triangle_mesh = []
quad_mesh     = []
for _mesh in meshes:
    if len(_mesh) == 3:
        triangle_mesh.append(_mesh)
    elif len(_mesh) == 4:
        quad_mesh.append(_mesh)
    else:
        print("ERROR")
        sys.exit()

all_mesh_particle = []
for _mesh in meshes:
    for particle in _mesh:
        all_mesh_particle.append(particle)

camera_rot = [70,23]
camera_radius = 2.5
camera_center = [0.5,0.5,0.5]
def get_input():
    global camera_rot, camera_radius
    keys_pressed = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_rel = pygame.mouse.get_rel()
    for event in pygame.event.get():
        if   event.type == QUIT: return False
        elif event.type == KEYDOWN:
            if   event.key == K_ESCAPE: return False
        elif event.type == MOUSEBUTTONDOWN:
            if   event.button == 4: camera_radius -= 0.5
            elif event.button == 5: camera_radius += 0.5
    if mouse_buttons[0]:
        camera_rot[0] += mouse_rel[0]
        camera_rot[1] += mouse_rel[1]
    return True

def edge_draw(points):
    glColor3f(0,0,0)
    glBegin(GL_LINE_STRIP)
    for point in points:
        glVertex3fv(point)
    glEnd()

def polygon_draw(points):
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glColor3f(1,1,1)
    glBegin(GL_TRIANGLES)
    for point in points:
        glVertex3fv(point)
    glEnd()


def draw():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glViewport(0,0,screen_size[0],screen_size[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(90,float(screen_size[0])/float(screen_size[1]), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    camera_pos = [camera_center[0] + camera_radius*cos(radians(camera_rot[0]))*cos(radians(camera_rot[1])),
                  camera_center[1] + camera_radius*sin(radians(camera_rot[1])),
                  camera_center[2] + camera_radius*sin(radians(camera_rot[0]))*cos(radians(camera_rot[1]))]

    ####  gluLookAt(カメラ座標(x,y,z), カメラ向き(x,y,z), カメラの上方向を表すベクトル(,,))
    gluLookAt(camera_pos[0],camera_pos[1],camera_pos[2],
              camera_center[0],camera_center[1],camera_center[2],0,1,0)
    """
    glColor3f(0,1,1)
    glBegin(GL_TRIANGLES)
    for mesh in meshes:
        glVertex3fv(mesh[0])  # X
        glVertex3fv(mesh[1])  # Y
        glVertex3fv(mesh[2])  # Z
    glEnd()
    """
    #glEnable(GL_CULL_FACE)
    #glCullFace(GL_BACK)

    for mesh in meshes:
        polygon_draw(mesh)

    """
    for mesh in meshes:
        edge_draw(mesh)
    """
    pygame.display.flip()

def main():
    target_fps = 60
    clock = pygame.time.Clock()
    while True:
        if not get_input(): break
        draw()
        clock.tick(target_fps)
    pygame.quit()

if __name__=="__main__":
    try:
        main()
    except:
        print("Error")
    finally:
        traceback.print_exc()
        pygame.quit()
        sys.exit()
