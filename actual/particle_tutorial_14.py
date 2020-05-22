from math import pi
import sys
import random
import pygame
import PyParticles4

pygame.init()
width, height = (400, 400)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Springs')

universe = PyParticles4.Environment(width, height)
universe.colour = (255,255,255)
universe.addFunctions(['move', 'bounce', 'collide', 'drag', 'accelerate'])
universe.acceleration = (pi, 0.2)
universe.mass_of_air = 0.02

circle_width = 1
font = pygame.font.Font(None, 30)

"""
for p in range(3):
    universe.addParticles(mass=20, size=6, speed=2, elasticity=0.005, colour=(20,40,200))
"""
universe.addParticles(mass=50, size=6, speed=0, elasticity=0.5, colour=(20,40,200))
universe.addParticles(mass=50, size=6, speed=0, elasticity=0.5, colour=(20,40,200))
universe.addParticles(mass=50, size=6, speed=0, elasticity=0.5, colour=(20,40,200))

universe.addSpring(0,1, length=50, strength=15.)
universe.addSpring(1,2, length=50, strength=15.)
universe.addSpring(2,0, length=50, strength=15.)
#universe.addSpring(3,4, length=50, strength=0.5)
#universe.addSpring(4,0, length=50, strength=0.5)

selected_particle = None
paused = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = (True, False)[paused]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle = universe.findParticle(mouseX, mouseY)
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_particle = None

    if selected_particle:
        (mouseX, mouseY) = pygame.mouse.get_pos()
        selected_particle.mouseMove(mouseX, mouseY)
    if not paused:
        universe.update()

    screen.fill(universe.colour)

    for i, p in enumerate(universe.particles):
        pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, circle_width)
        # 番号表示
        txt = font.render(str(i), True, (0, 0, 0))
        screen.blit(txt, [int(p.x), int(p.y)])

    for s in universe.springs:
        pygame.draw.aaline(screen, (0,0,0), (int(s.p1.x), int(s.p1.y)), (int(s.p2.x), int(s.p2.y)))

    pygame.display.flip()
