#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://www.gpgstudy.com/gpgiki/GDC_2001:_Advanced_Character_Physics
import pygame
import numpy as np
import dxfgrabber
import sys
import math
import time

pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()
font = pygame.font.Font(None, 15)

WIDTH  = 800
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('EXTENSOR HOOD')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 負荷かかった時のヒートマップ表示
def rgb(value, minimum=30, maximum=45):
    minimum, maximum = float(minimum), float(maximum)
    ratio = 2 * (value-minimum) / (maximum - minimum)
    b = int(max(0, 255*(1 - ratio)))
    r = int(max(0, 255*(ratio - 1)))
    g = 255 - b - r
    if b > 255:b=255
    if b < 0  :b=0
    if r > 255:r=255
    if r < 0  :r=0
    if g > 255:g=255
    if g < 0  :g=0
    return r,g,b

class Particle:
    def __init__(self, x, y, m = 1.0):
        self.m = m
        self.init_x, self.init_y = x, y
        self.x = x
        self.y = y
        self.oldx = x
        self.oldy = y
        self.newx = x
        self.newy = y
        self.ax = 0
        self.ay = 9.8 #0

        self.fixed = False
        self.selected = False

    def update(self, delta_t):
        if self.fixed == False:
            # Verlet Integration
            # (https://www.watanabe-lab.jp/blog/archives/1993)
            self.newx = 2.0 * self.x - self.oldx + self.ax * delta_t**2
            self.newy = 2.0 * self.y - self.oldy + self.ay * delta_t**2
            self.oldx = self.x
            self.oldy = self.y
            self.x = self.newx
            self.y = self.newy

            # 壁の当たり判定
            if self.x < 0 or self.x > WIDTH:
                self.x, self.oldx = self.oldx, self.x
            if self.y < 0 or self.y > HEIGHT:
                self.y, self.oldy = self.oldy, self.y

        if mouse == False:
            self.selected = False

        if self.selected == True:
            self.x, self.y = pygame.mouse.get_pos()

    def set_pos(self, pos):
        self.x, self.y = pos

    def draw(self, surf, size):
        if self.fixed == True:
            color = GREEN
            moji = str(self.x)+", "+str(self.y)
            txt = font.render(moji, True, (0, 0, 0))
            screen.blit(txt, [self.x, self.y])
        else:
            color = BLACK
        if self.selected == True:
            color = RED

        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), size)

# パーティクルへの拘束条件
class Constraint:
    def __init__(self, index0, index1):
        self.index0 = index0
        self.index1 = index1
        delta_x = particles[index0].x - particles[index1].x
        delta_y = particles[index0].y - particles[index1].y
        self.restLength = math.sqrt(delta_x**2 + delta_y**2)

    def update(self):
        delta_x = particles[self.index1].x - particles[self.index0].x
        delta_y = particles[self.index1].y - particles[self.index0].y
        deltaLength = math.sqrt(delta_x**2 + delta_y**2)
        diff = (deltaLength - self.restLength)/(deltaLength+0.001)

        le = 0.5
        if particles[self.index0].fixed == False:
            particles[self.index0].x += le * diff * delta_x
            particles[self.index0].y += le * diff * delta_y
        if particles[self.index1].fixed == False:
            particles[self.index1].x -= le * diff * delta_x
            particles[self.index1].y -= le * diff * delta_y

    def draw(self, surf, size):
        ## 初期位置からパーティクル間の距離を計算
        f_x0 = particles[self.index0].init_x
        f_y0 = particles[self.index0].init_y
        f_x1 = particles[self.index1].init_x
        f_y1 = particles[self.index1].init_y
        init_d = math.sqrt((f_x0-f_x1)**2+(f_y0-f_y1)**2)

        x0 = particles[self.index0].x
        y0 = particles[self.index0].y
        x1 = particles[self.index1].x
        y1 = particles[self.index1].y
        d = math.sqrt((x0-x1)**2+(y0-y1)**2)

        pygame.draw.line(surf, rgb(d, minimum=init_d, maximum=init_d*1.25),
                         (int(x0), int(y0)), (int(x1), int(y1)), size)

def find_particle(pos):
    for i in range(len(particles)):
        dx = particles[i].x - pos[0]
        dy = particles[i].y - pos[1]
        if (dx*dx + dy*dy) < 300:
            particles[i].selected = True
            particles[i].set_pos(pos)
            break

# 重複要素の消去
def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]

delta_t = 0.1
NUM_ITER = 5       # 結束強度
mouse = False
mouse_pos = (0, 0)

# dxf analysation
#file_name="model/extensor_hood_test001.dxf"
file_name="model/extensor_hood_test002.dxf"
dxf = dxfgrabber.readfile(file_name)

for i, layer in enumerate(dxf.layers):
    print("Layer {0} : {1}".format(i, layer.name))

all_stop_points_en      = [e for e in dxf.entities if e.layer == 'stop_points']     ##  only CIRCLE
all_polly_lines_en      = [e for e in dxf.entities if e.layer == 'polly_lines']     ##  only LWPOLYLINE
all_particle_points_en  = [e for e in dxf.entities if e.layer == 'particle_points'] ##  only CIRCLE

size_vias = 1/18
inversion = -1
x_vias = 70#-100
y_vias = 740#880

## 固定パーティクルの座標が格納
stop_points = []
for circle in all_stop_points_en:
    x = int(round(circle.center[0] * size_vias + x_vias, 1))
    y = int(round(circle.center[1] * size_vias * inversion + y_vias, 1))
    stop_points.append([x, y])

## ポリラインの頂点座標が格納
poly_lines = []
for lw_polyline in all_polly_lines_en:
    lump = []
    for cood in lw_polyline.points:
        x = int(round(cood[0] * size_vias + x_vias, 1))
        y = int(round(cood[1] * size_vias * inversion + y_vias, 1))
        lump.append([x, y])
    poly_lines.append(lump)

## パーティクルの座標が格納
particle_points = []
for circle in all_particle_points_en:
    x = int(round(circle.center[0] * size_vias + x_vias, 1))
    y = int(round(circle.center[1] * size_vias * inversion + y_vias, 1))
    particle_points.append([x, y])

## パーティクルの重複座標を消去
print("Clearing duplicate particles : ", len(particle_points), "-->",
                                         len(get_unique_list(particle_points)))
particle_points = get_unique_list(particle_points)

particles = []
for p_point in particle_points:
    p = Particle(int(p_point[0]), int(p_point[1]))
    particles.append(p)

for s_point in stop_points:
    try:
        anc_idx = particle_points.index(s_point)
        particles[anc_idx].fixed = True
    except:pass

constraints = []
for lines in poly_lines:
    top_count = len(lines)
    for i in range(top_count-1):
        try:
            index0 = particle_points.index(lines[i])
            index1 = particle_points.index(lines[i+1])
            c = Constraint(index0, index1)
            constraints.append(c)
        except:
            print(lines[i])

Running = True
while Running:
    start_time = time.time()
    screen.fill(WHITE)
    # particles update
    particles_update_time_s = time.time()
    for i in range(len(particles)):
        particles[i].update(delta_t)
    particles_update_time = time.time() - particles_update_time_s

    # constraints update
    constraints_update_time_s = time.time()
    for i in range(NUM_ITER):
        for ii in range(len(constraints)):
            constraints[ii].update()
    constraints_update_time = time.time() - constraints_update_time_s

    # particles draw
    particles_draw_time_s = time.time()
    for i in range(len(particles)):
        particles[i].draw(screen, 3)
    particles_draw_time = time.time() - particles_draw_time_s

    # constraints draw
    constraints_draw_time_s = time.time()
    for i in range(len(constraints)):
        constraints[i].draw(screen, 1)
    constraints_draw_time = time.time() - constraints_draw_time_s

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = True
        if event.type == pygame.MOUSEBUTTONUP:
            mouse = False
        if event.type == pygame.MOUSEMOTION and mouse == True:
            find_particle(pygame.mouse.get_pos())

    ## particles_update_time  : 4th
    ## constraints_update_time: 1st
    ## particles_draw_time    : 3rd
    ## constraints_draw_time  : 2nd
    print("\
           1. particles_update_time   : {0}s \n\
           2. constraints_update_time : {1}s \n\
           3. particles_draw_time     : {2}s \n\
           4. constraints_draw_time   : {3}s \n\
       TOTAL.                         : {4}s \n"
           .format(particles_update_time,
                   constraints_update_time,
                   particles_draw_time,
                   constraints_draw_time,
                   particles_update_time+constraints_update_time+particles_draw_time+constraints_draw_time))

    past_time = time.time() - start_time
    delay = past_time/delta_t

    color = GREEN
    moji = "FPS:"+str(round(FPS*delay, 2))
    txt = font.render(moji, True, (0, 0, 0))
    screen.blit(txt, [0, 0])

    pygame.display.update()
    fpsClock.tick(FPS)

pygame.quit()
