import sys
import random
import math
from math import sin, cos, pi

import pygame as pg

#pg.init()
FPS = 60
fpsClock = pg.time.Clock()

background_color = (255,255,255)
line_color       = (0, 255, 0)
(width, height) = (400, 400)

drag = 0.999                   # 空気抵抗
elasticity = 0.75              # 反発係数
#gravity = (pi, 0.002)          # 重力
gravity = (pi, 0.2)

def addVectors(angle1, length1, angle2, length2):
    x  = sin(angle1) * length1 + sin(angle2) * length2
    y  = cos(angle1) * length1 + cos(angle2) * length2

    angle = 0.5 * pi - math.atan2(y, x)
    length  = math.hypot(x, y)
    return (angle, length)

def findParticle(particles, x, y):
    for p in particles:
        if math.hypot(p.x-x, p.y-y) <= p.size:
            return p
    return None

def collide(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y

    distance = math.hypot(dx, dy)
    if distance < p1.size + p2.size:
        angle = math.atan2(dy, dx) + 0.5 * pi
        total_mass = p1.mass + p2.mass

        vecp1_x = (p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass)
        vecp1_y = (angle, 2*p2.speed*p2.mass/total_mass)
        vecp2_x = (p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass)
        vecp2_y = (angle+pi, 2*p1.speed*p1.mass/total_mass)
        p1.angle, p1.speed = addVectors(*vecp1_x, *vecp1_y)
        p2.angle, p2.speed = addVectors(*vecp2_x, *vecp2_y)
        p1.speed *= elasticity
        p2.speed *= elasticity

        overlap = 0.5*(p1.size + p2.size - distance+1)
        p1.x += sin(angle)*overlap
        p1.y -= cos(angle)*overlap
        p2.x -= sin(angle)*overlap
        p2.y += cos(angle)*overlap

class Particle:
    def __init__(self, x, y, size, mass=1):
        self.x = x
        self.y = y
        self.size = size                 # 半径
        self.mass = mass                 # 質量
        self.circle_color = (0, 0, 255)
        self.line_color = (0, 0, 0)
        self.thickness = 0               # 埋率, 0で全て塗り潰し
        self.speed = 0
        self.angle = 0

    def display(self):
        pg.draw.circle(screen, self.circle_color, (int(self.x), int(self.y)), self.size, self.thickness)

    def move(self):
        (self.angle, self.speed) = addVectors(*(self.angle, self.speed), *gravity)
        self.x += sin(self.angle) * self.speed
        self.y -= cos(self.angle) * self.speed
        self.speed *= drag

    def bounce(self):
        if self.x > width - self.size:
            self.x = 2*(width - self.size) - self.x
            self.angle = - self.angle
            self.speed *= elasticity

        elif self.x < self.size:
            self.x = 2*self.size - self.x
            self.angle = - self.angle
            self.speed *= elasticity

        if self.y > height - self.size:
            self.y = 2*(height - self.size) - self.y
            self.angle = pi - self.angle
            self.speed *= elasticity

        elif self.y < self.size:
            self.y = 2*self.size - self.y
            self.angle = pi - self.angle
            self.speed *= elasticity

screen = pg.display.set_mode((width, height))
pg.display.set_caption('Tutorial 1')
screen.fill(background_color)

particle_num = 3
my_particles = []

for n in range(particle_num):
    #size = random.randint(10, 20)
    size = 10
    density = random.randint(1, 20)     # 密度
    x = random.randint(size, width-size)
    y = random.randint(size, height-size)

    particle = Particle(x, y, size, density*size**2)
    #particle.color = (200-density*10, 200-density*10, 255)
    particle.speed = random.random()
    particle.angle = random.uniform(0, pi*2)

    my_particles.append(particle)

selected_particle = None
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            (mouseX, mouseY) = pg.mouse.get_pos()
            selected_particle = findParticle(my_particles, mouseX, mouseY)
        elif event.type == pg.MOUSEBUTTONUP:
            #"""
            try:
                selected_particle.circle_color = (0,0,255)
            except:
                pass
            #"""
            selected_particle = None

    if selected_particle:
        selected_particle.circle_color = (255,0,0)
        (mouseX, mouseY) = pg.mouse.get_pos()
        dx = mouseX - selected_particle.x
        dy = mouseY - selected_particle.y
        selected_particle.angle = 0.5*pi + math.atan2(dy, dx)
        selected_particle.speed = math.hypot(dx, dy) * 0.1

    screen.fill(background_color)

    circle_points = []
    for i, particle in enumerate(my_particles):
        particle.move()
        particle.bounce()
        for particle2 in my_particles[i+1:]:
            collide(particle, particle2)
        particle.display()
        circle_points.append((particle.x, particle.y))
    pg.draw.lines(screen, line_color, True, circle_points)
    pg.display.flip()

    fpsClock.tick(FPS)

pg.quit()
sys.exit()
