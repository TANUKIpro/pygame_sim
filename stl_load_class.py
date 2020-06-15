from stl import mesh
import numpy as np

class STL_loader:
    def __init__(self, file_name, size):
        self.file_name = file_name
        self.size = size
        self.triangle_mesh = []
        #self.quad_mesh     = []
        self.all_mesh_particle = []
        self.load()

    def load(self):
        # STLファイルの読み込み
        __mesh = mesh.Mesh.from_file(self.file_name)
        meshes = (__mesh.vectors) * self.size

        for m in meshes:
            if len(m) == 3:
                self.triangle_mesh.append(m)
            elif len(m) == 4:
                print("Quad mesh is not support.")
                sys.exit()
                #self.quad_mesh.append(m)
            else:
                print("ERROR")
                sys.exit()

        for _m in meshes:
            for particle in _m:
                self.all_mesh_particle.append(particle)

    def ver_and_ind(self):
        # 頂点座標
        target = np.array(self.all_mesh_particle)
        datanum, corner = target.shape
        ver = np.zeros((datanum*corner, 1)).tolist()
        ind = np.zeros((datanum, 1)).tolist()
        i = 0

        for one_tri, tri_mesh in enumerate(target):
            for top_cood in tri_mesh:
                ver[i] = top_cood.tolist()
                i += 1
            ind[one_tri] = one_tri
        return ver, ind

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
