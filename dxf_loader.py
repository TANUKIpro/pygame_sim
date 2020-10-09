import numpy as np
import dxfgrabber
from math import floor
import sys

class DXF_Loader:
    def __init__(self, file_name, extensor_reduced_scale, x_vias, y_vias, z_vias, inversion=1, integer=False):
        self.file_name = file_name
        self.reduced_scale = extensor_reduced_scale
        self.x_vias = x_vias#-100
        self.y_vias = y_vias#880
        self.z_vias = z_vias
        self.inversion = inversion  ## 反転操作(-1or1)
        self.round_quality = 5

        self.stop_points = []      ## 固定パーティクルの座標が格納
        self.poly_lines = []       ## ポリラインの頂点座標が格納
        self.particle_points = []  ## パーティクルの座標が格納
        self.integer = integer
        self.load_dxf()

    def get_unique_list(self, seq):
        seen=[];return [x for x in seq if x not in seen and not seen.append(x)]

    def load_dxf(self):
        n=12
        dxf = dxfgrabber.readfile(self.file_name)
        for i, layer in enumerate(dxf.layers):
            print("Layer {0} : {1}".format(i, layer.name))

        all_stop_points_en      = [e for e in dxf.entities if e.layer == 'stop_points']     ##  only CIRCLE
        all_polly_lines_en      = [e for e in dxf.entities if e.layer == 'polly_lines']     ##  only LWPOLYLINE
        all_particle_points_en  = [e for e in dxf.entities if e.layer == 'particle_points'] ##  only CIRCLE

        for circle in all_stop_points_en:
            if not self.integer:
                x = floor((circle.center[0] * self.reduced_scale + self.x_vias)*10**n) / (10**n)
                y = floor((circle.center[1] * self.reduced_scale * self.inversion + self.y_vias)*10**n) / (10**n)
                x, y = round(x, self.round_quality), round(y, self.round_quality)
            else:
                x = int(circle.center[0] * self.reduced_scale + self.x_vias)
                y = int(circle.center[1] * self.reduced_scale * self.inversion + self.y_vias)
            self.stop_points.append([x, y])

        for lw_polyline in all_polly_lines_en:
            lump = []
            for cood in lw_polyline.points:
                if not self.integer:
                    x = floor((cood[0] * self.reduced_scale + self.x_vias)*10**n) / (10**n)
                    y = floor((cood[1] * self.reduced_scale * self.inversion + self.y_vias)*10**n) / (10**n)
                    x, y = round(x, self.round_quality), round(y, self.round_quality)
                else:
                    x = int(cood[0] * self.reduced_scale + self.x_vias)
                    y = int(cood[1] * self.reduced_scale * self.inversion + self.y_vias)
                lump.append([x, y])
            self.poly_lines.append(lump)

        for circle in all_particle_points_en:
            if not self.integer:
                x = floor((circle.center[0] * self.reduced_scale + self.x_vias)*10**n) / (10**n)
                y = floor((circle.center[1] * self.reduced_scale * self.inversion + self.y_vias)*10**n) / (10**n)
                x, y = round(x, self.round_quality), round(y, self.round_quality)
            else:
                x = int(circle.center[0] * self.reduced_scale + self.x_vias)
                y = int(circle.center[1] * self.reduced_scale * self.inversion + self.y_vias)
            self.particle_points.append([x, y])

        print("Clearing duplicate particles : ", len(self.particle_points), "-->",
                                                 len(self.get_unique_list(self.particle_points)))
        self.particle_points = self.get_unique_list(self.particle_points)

    def ver_col_ind(self):
        """  2次元座標 --> 3次元座標　へ変換  """
        stop_points_2d = np.array(self.stop_points)
        stop_points_3d = np.zeros((stop_points_2d.shape[0], 3))+self.z_vias
        stop_points_3d[:,0]=stop_points_2d[:,0]
        stop_points_3d[:,1]=stop_points_2d[:,1]

        particle_points_2d = np.array(self.particle_points)
        particle_points_3d = np.zeros((particle_points_2d.shape[0], 3))+self.z_vias
        particle_points_3d[:,0]=particle_points_2d[:,0]
        particle_points_3d[:,1]=particle_points_2d[:,1]

        poly_lines_2d = np.array(self.poly_lines)
        poly_lines_3d = []
        for i, line_clump in enumerate(poly_lines_2d):
            line_clump = np.array(line_clump)
            z_zeros = np.zeros((line_clump.shape[0], 1))+self.z_vias
            poly_lines_3d.append(np.hstack((line_clump, z_zeros)))

        return stop_points_3d, particle_points_3d, poly_lines_3d

    def color(self, ver, _r=1, _g=1, _b=1):
        col = np.zeros_like(ver).tolist()
        for i, idx in enumerate(col):
            amari = i%3
            if   amari == 0:
                col[i] = _r
            elif amari == 1:
                col[i] = _g
            elif amari == 2:
                col[i] = _b
        return col
