from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

#file_name = "model/finger_bone_smooth_v1.stl"
file_name = "model/only_index.stl"

# 描画領域を新規作成
figure = pyplot.figure()
axes = mplot3d.Axes3D(figure)

# STLファイルを読み込み、メッシュデータからプロットデータに変換
your_mesh = mesh.Mesh.from_file(file_name)
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))

# 大きさを自動調整
scale = your_mesh.points.flatten('C')
axes.auto_scale_xyz(scale, scale, scale)

# 表示
pyplot.show()
