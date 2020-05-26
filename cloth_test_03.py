#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://www.gpgstudy.com/gpgiki/GDC_2001:_Advanced_Character_Physics
import pygame
import dxfgrabber
import sys
import math

pygame.init()

FPS = 60
fpsClock = pygame.time.Clock()

WIDTH = 600
HEIGHT = 300
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('EXTENSOR HOOD TEST 01')

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
        self.x = x
        self.y = y
        self.oldx = x
        self.oldy = y
        self.newx = x
        self.newy = y
        self.ax = 0
        self.ay = 9.8

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
        else:
            color = WHITE
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
        x0 = particles[self.index0].x
        y0 = particles[self.index0].y
        x1 = particles[self.index1].x
        y1 = particles[self.index1].y

        d = math.sqrt((x0-x1)**2+(y0-y1)**2)
        pygame.draw.line(surf, rgb(d), (int(x0), int(y0)), (int(x1), int(y1)), size)

def find_particle(pos):
    for i in range(len(particles)):
        dx = particles[i].x - pos[0]
        dy = particles[i].y - pos[1]
        if (dx*dx + dy*dy) < 300:
            particles[i].selected = True
            particles[i].set_pos(pos)
            break

delta_t = 0.1
NUM_ITER = 10       # 結束強度
mouse = False
mouse_pos = (0, 0)

##    =================================================================    ##
file_name="test_extensor_hood_v2.dxf"
dxf = dxfgrabber.readfile(file_name)

circles = [e for e in dxf.entities if e.dxftype == 'CIRCLE']
lines   = [e for e in dxf.entities if e.dxftype == 'LINE']
points  = [e for e in dxf.entities if e.dxftype == 'POINT']

all_cood = []
particles = []
anchors = []
for circle in circles:
    x = circle.center[0]*10 +10
    y = circle.center[1]*10 +50
    x, y = int(round(x, 3)), int(round(y, 3))
    all_cood.append([x, y])
    if x == -7+10 or x == 96+10:
        anchors.append([x, y])

for line in lines:
    ls_x, ls_y = -1*line.start[0]*10+10, line.start[2]*10+50
    le_x, le_y = -1*line.end[0]  *10+10, line.end[2]  *10+50

    ls_x, ls_y = round(ls_x, 3), round(ls_y, 3)
    le_x, le_y = round(le_x, 3), round(le_y, 3)
    all_cood.append([int(ls_x), int(ls_y)])
    all_cood.append([int(le_x), int(le_y)])

# 重複要素の消去
def get_unique_list(seq):
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]

clear_cood = get_unique_list(all_cood)
for cood in clear_cood:
    p = Particle(cood[0], cood[1])
    particles.append(p)

# particle fix
for anchor in get_unique_list(anchors):
    anc_idx = clear_cood.index(anchor)
    particles[anc_idx].fixed = True

sys.exit()
##    =================================================================    ##

constraints = []

# 縦、横への拘束
for j in range(NUM_Y):
    for i in range(NUM_X):
        if i < (NUM_X - 1):
            index0 = i + j * NUM_X
            index1 = (i + 1) + j * NUM_X
            #print("idx0:{0}, idx1:{1}".format(index0, index1))
            c = Constraint(index0, index1)
            constraints.append(c)
        if j < (NUM_Y - 1):
            index0 = i + j * NUM_X
            index1 = i + (j + 1) * NUM_X
            c = Constraint(index0, index1)
            constraints.append(c)


Running = True
while Running:
    screen.fill(BLACK)
    # particles update
    for i in range(len(particles)):
        particles[i].update(delta_t)

    # constraints update
    for i in range(NUM_ITER):
        for ii in range(len(constraints)):
            constraints[ii].update()

    # particles draw
    for i in range(len(particles)):
        particles[i].draw(screen, 3)

    # constraints draw
    for i in range(len(constraints)):
        constraints[i].draw(screen, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = True
        if event.type == pygame.MOUSEBUTTONUP:
            mouse = False
        if event.type == pygame.MOUSEMOTION and mouse == True:
            find_particle(pygame.mouse.get_pos())

    pygame.display.update()
    fpsClock.tick(FPS)

pygame.quit()
