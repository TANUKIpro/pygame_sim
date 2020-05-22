#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame, sys, math

pygame.init()

FPS = 60
fpsClock = pygame.time.Clock()

WIDTH = 400
HEIGHT = 300
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Koike TEST')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

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

    def update(self, dt):
        if self.fixed == False:
            # Verlet Integration
            self.newx = 2.0 * self.x - self.oldx + self.ax * dt * dt
            self.newy = 2.0 * self.y - self.oldy + self.ay * dt * dt
            self.oldx = self.x
            self.oldy = self.y
            self.x = self.newx
            self.y = self.newy

            # Collision Process
            if self.x < 0 or self.x > WIDTH:
                self.x, self.oldx = self.oldx, self.x
            if self.y < 0 or self.y > HEIGHT:
                self.y, self.oldy = self.oldy, self.y

        if self.selected == True:
            pos = pygame.mouse.get_pos()
            self.x = pos[0]
            self.y = pos[1]
        if mouse == False:
            self.selected = False

    def draw(self, surf, size):
        if self.fixed == True:
            color = GREEN
        else:
            color = WHITE
        if self.selected == True:
            color = RED

        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), size)

# パーティクルへの制約
class Constraint:
    def __init__(self, index0, index1):
        self.index0 = index0
        self.index1 = index1
        dx = particles[index0].x - particles[index1].x
        dy = particles[index0].y - particles[index1].y
        self.restLength = math.sqrt(dx**2 + dy**2)

    def update(self):
        up_dx = particles[self.index1].x - particles[self.index0].x
        up_dy = particles[self.index1].y - particles[self.index0].y
        dLength = math.sqrt(up_dx**2 + up_dy**2)
        # 二点間の距離の比率
        diff = (dLength - self.restLength)/dLength

        if particles[self.index0].fixed == False:
            particles[self.index0].x += 0.5 * diff * up_dx
            particles[self.index0].y += 0.5 * diff * up_dy
        if particles[self.index1].fixed == False:
            particles[self.index1].x -= 0.5 * diff * up_dx
            particles[self.index1].y -= 0.5 * diff * up_dy

    def draw(self, surf, size):
        x0 = particles[self.index0].x
        y0 = particles[self.index0].y
        x1 = particles[self.index1].x
        y1 = particles[self.index1].y
        pygame.draw.line(surf, WHITE, (int(x0), int(y0)), (int(x1), int(y1)), size)


def find_particle(pos):
    for i in range(len(particles)):
        dx = particles[i].x - pos[0]
        dy = particles[i].y - pos[1]
        if (dx**2 + dy**2) < 400:
            particles[i].selected = True
            break

dt = 0.1
NUM_ITER = 10
mouse = False

# パーティクルの作成
NUM_X = 5
NUM_Y = 5
particles = []
for j in range(NUM_Y):
    for i in range(NUM_X):
        x = 100 + i * 20.0
        y = j * 20.0
        p = Particle(x, y+50)
        particles.append(p)

# パーティクルの固定
particles[0].fixed = True
particles[NUM_X-1].fixed = True
particles[-1].fixed = True
particles[-NUM_X].fixed = True

constraints = []
for j in range(NUM_Y):
    for i in range(NUM_X):
        if i < (NUM_X - 1):
            index0 = i + j * NUM_X
            index1 = (i + 1) + j * NUM_X
            c = Constraint(index0, index1)
            constraints.append(c)
        if j < (NUM_Y - 1):
            index0 = i + j * NUM_X
            index1 = i + (j + 1) * NUM_X
            c = Constraint(index0, index1)
            constraints.append(c)

while True:
    screen.fill(BLACK)
    # particles update
    for i in range(len(particles)):
        particles[i].update(dt)

    # constraints update
    for i in range(NUM_ITER):
        for cons in range(len(constraints)):
            constraints[cons].update()

    # particles draw
    for i in range(len(particles)):
        particles[i].draw(screen, 3)

    # constraints draw
    for i in range(len(constraints)):
        constraints[i].draw(screen, 1)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = True
        if event.type == pygame.MOUSEBUTTONUP:
            mouse = False

    if mouse:
        pos = pygame.mouse.get_pos()
        find_particle(pos)

    pygame.display.update()
    fpsClock.tick(FPS)
