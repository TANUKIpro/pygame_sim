import cython
import math
import pygame

cdef constraints_update(particles, int index0, int index1, float restLength):
    cdef:
      int delta_x, delta_y
      float deltaLength, diff

    delta_x = particles[index1].x - particles[index0].x
    delta_y = particles[index1].y - particles[index0].y
    deltaLength = math.sqrt(delta_x*delta_x + delta_y*delta_y)
    diff = (deltaLength - restLength)/(deltaLength+0.001)

    if particles[index0].fixed == False:
        particles[index0].x += 0.5 * diff * delta_x
        particles[index0].y += 0.5 * diff * delta_y
    if particles[index1].fixed == False:
        particles[index1].x -= 0.5 * diff * delta_x
        particles[index1].y -= 0.5 * diff * delta_y

# 負荷かかった時のヒートマップ表示
cdef rgb(float value,  float minimum, float maximum):
      cdef:
          float ratio
          int r, g, b
      ratio = 0.
      r = 0
      g = 0
      b = 0

      ratio = 2 * (value-minimum) / ((maximum - minimum) + 0.0001)
      #ratio = 2 * (value-minimum) / (maximum - minimum)
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

cdef constraint_draw(surf, int size, particles, int index0, int index1):
    cdef:
        int f_x0, f_y0, f_x1, f_y1, x0, y0, x1, y1
        float init_d, d

    ## 初期位置からパーティクル間の距離を計算
    f_x0 = particles[index0].init_x
    f_y0 = particles[index0].init_y
    f_x1 = particles[index1].init_x
    f_y1 = particles[index1].init_y
    init_d = math.sqrt((f_x0-f_x1)*(f_x0-f_x1)+(f_y0-f_y1)*(f_y0-f_y1))

    x0 = particles[index0].x
    y0 = particles[index0].y
    x1 = particles[index1].x
    y1 = particles[index1].y
    d = math.sqrt((x0-x1)*(x0-x1)+(y0-y1)*(y0-y1))

    pygame.draw.line(surf, rgb(d, init_d, init_d*1.25),
                     (int(x0), int(y0)), (int(x1), int(y1)), size)

def constraints_update_cython(int NUM_ITER, constraints, particles):
    cdef:
        int i, ii, CON_ITER
        int delta_x, delta_y
        float deltaLength, diff
    i = 0
    ii = 0
    CON_ITER = len(constraints)
    delta_x = 0
    delta_y = 0
    deltaLength = 0.0
    diff = 0.0

    for i in range(NUM_ITER):
        for ii in range(CON_ITER):
            constraints_update(particles,
                               constraints[ii].index0, constraints[ii].index1,
                               constraints[ii].restLength)

def constraints_draw_cython(constraints, particles, screen):
    cdef:
      int i, CON_ITER
    i = 0
    CON_ITER = len(constraints)

    for i in range(CON_ITER):
        #constraints[i].draw(screen, 1)
        constraint_draw(screen, 1, particles, constraints[i].index0, constraints[i].index1)
