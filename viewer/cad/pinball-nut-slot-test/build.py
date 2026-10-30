"""Exact V1.3 top_block_left_140 with side-entry M3 nut pocket; units mm."""
from pathlib import Path
import json, math, struct
from collections import Counter
import cadquery as cq
from cadquery import exporters
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'assets/pinball-nut-slot-test'; OUT.mkdir(parents=True,exist_ok=True)
P=json.loads((ROOT/'viewer/cad/portable-pinball-v1_3/parameters.json').read_text())
A=P['slope_degrees']; C=math.cos(math.radians(A)); S=math.tan(math.radians(A))
H=P['front_height']; W=P['width']; yy=140; cx=10; U=yy/C
z=lambda y:H+y*S
def box(x,y,z0,dx,dy,dz):
 return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z0))
def cyl(pt,d,length,axis=(0,0,1)):
 return cq.Workplane(obj=cq.Solid.makeCylinder(d/2,length,cq.Vector(*pt),cq.Vector(*axis)))
def top(shape):
 return shape.rotate((0,0,0),(1,0,0),A).translate((0,0,H+1))
base=cq.Workplane('YZ').polyline([(130,z(140)-13),(150,z(140)-13),(150,z(150)+1),(130,z(130)+1)]).close().extrude(12).translate((4,0,0))
N=(0,-math.sin(math.radians(A)),C); pt=(cx,yy,z(yy)+1)
screw=cyl(tuple(pt[i]-25*N[i] for i in range(3)),3.4,50,N)
mount=cyl((-5,yy+6,z(yy)-8),3.4,W+10,(1,0,0))
old=base.cut(mount).cut(screw).cut(top(cq.Workplane('XY').center(cx,U).polygon(6,6.6).extrude(-3))).clean()
original=cq.importers.importStep(str(ROOT/'assets/portable-pinball/cabinet-v1_3.step'))
matches=[]
for solid in original.solids().vals():
 b=solid.BoundingBox()
 if abs(b.xmin-4)<.001 and abs(b.xmax-16)<.001 and abs(b.ymin-130)<.001 and abs(b.ymax-150)<.001:matches.append(cq.Workplane(obj=solid))
assert len(matches)==1,len(matches)
assert old.cut(matches[0]).val().Volume()<1e-5
assert matches[0].cut(old).val().Volume()<1e-5
roof=3.2; height=2.8; tunnel=5.85
hexcut=cq.Workplane('XY').center(cx,U).polygon(6,6.7).extrude(height).translate((0,0,-roof-height))
channel=box(cx,U-tunnel/2,-roof-height,7,tunnel,height)
flare=cq.Workplane('XY').polyline([(14.5,U-tunnel/2),(17,U-3.6),(17,U+3.6),(14.5,U+tunnel/2)]).close().extrude(height).translate((0,0,-roof-height))
pocket=top(hexcut.union(channel).union(flare))
block=base.cut(mount).cut(screw).cut(pocket).clean()
assert block.val().isValid() and len(block.solids().vals())==1
assert pocket.intersect(mount).val().Volume()<1e-6
for x in np.linspace(20,10,41):
 nut=cq.Workplane('XY').center(float(x),U).polygon(6,5.5/math.cos(math.pi/6)).extrude(2.4).translate((0,0,-5.8))
 assert block.intersect(top(nut)).val().Volume()<1e-6,('nut collision',float(x))
printed=block.rotate((0,0,0),(1,0,0),180-A)
b=printed.val().BoundingBox(); printed=printed.translate((-b.xmin,-b.ymin,-b.zmin))
exporters.export(printed,str(OUT/'top_block_left_140_side_slot.stl'),tolerance=.025,angularTolerance=.08)
exporters.export(block,str(OUT/'top_block_left_140_side_slot.step'))
b=printed.val().BoundingBox(); assert b.xlen+16<325 and b.ylen+16<325 and b.zlen<315
data=(OUT/'top_block_left_140_side_slot.stl').read_bytes()
count=struct.unpack_from('<I',data,80)[0]; edges=Counter(); assert len(data)==84+50*count
for i in range(count):
 f=struct.unpack_from('<12fH',data,84+50*i)
 vs=[tuple(round(c,5) for c in f[j:j+3]) for j in (3,6,9)]
 assert len(set(vs))==3
 for a,bb in ((vs[0],vs[1]),(vs[1],vs[2]),(vs[2],vs[0])):edges[tuple(sorted((a,bb)))]+=1
assert all(n==2 for n in edges.values())
verts,faces=block.val().tessellate(.025,.08)
v=np.array([p.toTuple() for p in verts]);v-=v.min(axis=0)
v=np.stack((v[:,0],v[:,2],-v[:,1]),axis=1)/1000
positions=v[np.array(faces)].reshape(-1,3).astype('<f4')
norm=np.cross(positions[1::3]-positions[0::3],positions[2::3]-positions[0::3]);norm/=np.linalg.norm(norm,axis=1)[:,None]
norm=np.repeat(norm,3,axis=0).astype('<f4');blob=positions.tobytes()+norm.tobytes()
g={'asset':{'version':'2.0','generator':'CadQuery 2.7 exact CAD'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'top_block_left_140_side_slot','mesh':0}],'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1},'material':0}]}],'materials':[{'name':'Test block teal','pbrMetallicRoughness':{'baseColorFactor':[.25,.66,.55,1],'metallicFactor':0,'roughnessFactor':.65}}],'buffers':[{'byteLength':len(blob)}],'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':positions.nbytes,'target':34962},{'buffer':0,'byteOffset':positions.nbytes,'byteLength':norm.nbytes,'target':34962}],'accessors':[{'bufferView':0,'componentType':5126,'count':len(positions),'type':'VEC3','min':positions.min(axis=0).tolist(),'max':positions.max(axis=0).tolist()},{'bufferView':1,'componentType':5126,'count':len(norm),'type':'VEC3'}]}
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
(OUT/'nut-slot-v1.glb').write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
report={'source':'V1.3 top_block_left_140','original_exact_match':True,'solid_valid':True,'single_solid':True,'stl_closed_manifold':True,'nominal_nut_insertion_clear':True,'wall_mount_bore_clear_of_pocket':True,'roof_normal_mm':roof,'pocket_height_mm':height,'tunnel_width_mm':tunnel,'hex_corner_diameter_mm':6.7,'print_bounds_mm':[b.xlen,b.ylen,b.zlen],'triangles':len(faces),'physical_fit_tested':False}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'README.md').write_text("""# Side-entry nut block — test V1
One replacement for V1.3 top_block_left_140. Cabinet assembly unchanged.
Slide a standard M3 hex nut (nominal 5.5 mm flats, 2.4 mm thickness) into the +X inside face.
Pocket: 6.7 mm corner diameter; slot 5.85 mm wide and 2.8 mm tall; roof 3.2 mm thick.
Back hex faces resist spinning. Entry is flared. No plug included.
Optional tiny hot-glue dab at entrance retains loose nut. Keep glue off threads and bearing faces.
Original outer envelope, screw axis and side mounting bore preserved.
Lower nut position reduces screw engagement by 3.2 mm; check screw length, longer may be needed.
Print supplied STL top-face-down (already on Z=0) with calibrated PETG settings.
Test insertion, retention, screw reach and strength before duplicating. Do not overtighten.
Exact CAD, closed STL and nominal nut insertion checks passed. Physical fit/strength untested.
Source: viewer/cad/pinball-nut-slot-test/build.py; Python 3.12, CadQuery 2.7, numpy.
""")
print(json.dumps(report))
