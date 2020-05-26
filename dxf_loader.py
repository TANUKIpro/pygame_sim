
import dxfgrabber

dxf = dxfgrabber.readfile("test_extensor_hood_v1.dxf")
print(dxf.entities)

for i in dxf.entities:
    print(i)

cirs = [e for e in dxf.entities if e.dxftype == 'CIRCLE']
lines = [e for e in dxf.entities if e.dxftype == 'LINE']
all_arcs = [e for e in dxf.entities if entity.dxftype == 'ARC']

#print(cirs)
