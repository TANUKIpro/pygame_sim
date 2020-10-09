# パーティクルへの拘束条件
class Constraint:
    def __init__(self, index0, index1):
        self.index0 = index0
        self.index1 = index1
        delta_x = particles[index0].x - particles[index1].x
        delta_y = particles[index0].y - particles[index1].y
        delta_z = particles[index0].z - particles[index1].z
        self.restLength = sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        self.init_d = 0
        self.d      = 0

    def update(self):
        delta_x = particles[self.index1].x - particles[self.index0].x
        delta_y = particles[self.index1].y - particles[self.index0].y
        delta_z = particles[self.index1].z - particles[self.index0].z
        deltaLength = sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        diff = (deltaLength - self.restLength)/(deltaLength+0.001)

        le = 0.5
        if particles[self.index0].fixed == False:
            particles[self.index0].x += le * diff * delta_x
            particles[self.index0].y += le * diff * delta_y
            particles[self.index0].z += le * diff * delta_z
        if particles[self.index1].fixed == False:
            particles[self.index1].x -= le * diff * delta_x
            particles[self.index1].y -= le * diff * delta_y
            particles[self.index1].z -= le * diff * delta_z

    def draw(self):
        ## 初期位置からパーティクル間の距離を計算
        f_x0 = particles[self.index0].init_x
        f_y0 = particles[self.index0].init_y
        f_z0 = particles[self.index0].init_z
        f_x1 = particles[self.index1].init_x
        f_y1 = particles[self.index1].init_y
        f_z1 = particles[self.index1].init_z
        self.init_d = sqrt((f_x0-f_x1)**2+(f_y0-f_y1)**2+(f_z0-f_z1)**2)

        x0 = particles[self.index0].x
        y0 = particles[self.index0].y
        z0 = particles[self.index0].z
        x1 = particles[self.index1].x
        y1 = particles[self.index1].y
        z1 = particles[self.index1].z
        self.d = sqrt((x0-x1)**2+(y0-y1)**2++(z0-z1)**2)

        #pygame.draw.line(surf, rgb(d, minimum=init_d, maximum=init_d*1.25),
        #                 (int(x0), int(y0)), (int(x1), int(y1)), size)
        glColor3f(1, 0, 1)
        glBegin(GL_LINES)
        glVertex3fv(tuple((x0, y0, z0)))
        glVertex3fv(tuple((x1, y1, z1)))
        glEnd()
