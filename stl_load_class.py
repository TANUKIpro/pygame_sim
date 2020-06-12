from stl import mesh

class STL_loader:
    def __init__(self, file_name, size):
        self.file_name = file_name
        self.size = size
        self.triangle_mesh = []
        self.quad_mesh     = []
        self.all_mesh_particle = []

    def load(self):
        # STLファイルの読み込み
        __mesh = mesh.Mesh.from_file(self.file_name)
        meshes = (__mesh.vectors) * self.size

        for m in meshes:
            if len(m) == 3:
                self.triangle_mesh.append(m)
            elif len(m) == 4:
                self.quad_mesh.append(m)
            else:
                print("ERROR")
                sys.exit()

        for _m in meshes:
            for particle in _m:
                self.all_mesh_particle.append(particle)

        return self.triangle_mesh, self.quad_mesh, self.all_mesh_particle
