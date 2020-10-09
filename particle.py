class Particle:
    def __init__(self, x, y, z, m=1.0):
        self.m = m
        self.init_x, self.init_y, self.init_z = x, y, z
        self.x, self.y, self.z = x, y, z
        self.oldx, self.oldy, self.oldz = x, y, z
        self.newx, self.newy, self.newz = x, y, z
        self.ax = 0
        self.ay = 0#-9.8 #0
        self.az = 0

        self.fixed = False

    def when_move(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def update(self, delta_t):
        if self.fixed == False:
            # Verlet Integration
            # (https://www.watanabe-lab.jp/blog/archives/1993)
            self.newx = 2.0 * self.x - self.oldx + self.ax * delta_t**2
            self.newy = 2.0 * self.y - self.oldy + self.ay * delta_t**2
            self.newz = 2.0 * self.z - self.oldz + self.az * delta_t**2
            self.oldx = self.x
            self.oldy = self.y
            self.oldz = self.z
            self.x = self.newx
            self.y = self.newy
            self.z = self.newz

    def set_pos(self, pos):
        self.x, self.y, self.z = pos

    def draw_sp(self):
        color = GREEN
        glColor3f(*color);
        glPointSize(10);
        glBegin(GL_POINTS);
        glVertex3fv(tuple((self.x, self.y, self.z)));
        glEnd();

        drawText_3D(str(self.x)+", "+str(self.y)+", "+str(self.z),
                    self.x, self.y, self.z)

    def draw(self):
        DisP_cood_y = 10.61333
        MidP_cood_y = 8.88667
        color = RED
        glColor3f(*color);
        glPointSize(10);
        glBegin(GL_POINTS);
        glVertex3fv(tuple((self.x, self.y, self.z)));
        glEnd();
