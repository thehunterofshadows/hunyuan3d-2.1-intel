"""Read-only independent V1.8 exported-artifact audit. Prints JSON; writes no artifacts.
Run with ../.venv/bin/python independent_validate_v1_8.py.
Uses STL topology/coordinates, V1.7 byte comparisons, and re-imported STEP geometry.
It deliberately does not import build_cabinet.py or trust its validation flags.
"""
from pathlib import Path
from collections import defaultdict
import hashlib, json, math, struct
import numpy as np
import cadquery as cq

ROOT=Path(__file__).resolve().parent
NEW=ROOT/'exports'; OLD=ROOT.parent/'portable-pinball-v1_7'/'exports'
EXPECTED={'left_front_wall','right_front_wall','rear_vent_panel'}
manifest=json.loads((NEW/'parts_manifest.json').read_text())
previous=json.loads((OLD/'parts_manifest.json').read_text())
meshes={x['name']:x for x in json.loads((NEW/'preview_meshes.json').read_text())}
old_meshes={x['name']:x for x in json.loads((OLD/'preview_meshes.json').read_text())}
names=[p['name'] for p in manifest['parts']]
assert len(names)==45 and set(names)==set(old_meshes)==set(meshes)
assert len(manifest['tests'])==16
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
stl_changed=[n for n in names if sha(NEW/'enclosure_stl'/(n+'.stl'))!=sha(OLD/'enclosure_stl'/(n+'.stl'))]
mesh_changed=[n for n in names if meshes[n]!=old_meshes[n]]
assert set(stl_changed)==set(mesh_changed)==EXPECTED,(stl_changed,mesh_changed)
old_parts={p['name']:p for p in previous['parts']}
for p in manifest['parts']:
 if p['name'] not in EXPECTED:
  assert p==old_parts[p['name']],p['name']

def stl(path):
 d=path.read_bytes();count=struct.unpack_from('<I',d,80)[0]
 assert len(d)==84+50*count,(path,'binary STL length')
 return np.array([struct.unpack_from('<12fH',d,84+50*i)[3:12] for i in range(count)]).reshape(-1,3,3)

def topology(path):
 tri=stl(path)
 area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)/2
 assert area.min()>1e-10,(path,'degenerate triangle')
 vertices,indices=np.unique(np.round(tri.reshape(-1,3),5),axis=0,return_inverse=True)
 faces=indices.reshape(-1,3);edges=defaultdict(list)
 for i,face in enumerate(faces):
  for a,b in zip(face,np.roll(face,-1)):
   assert a!=b,(path,'collapsed edge')
   edges[tuple(sorted((int(a),int(b))))].append((i,1 if a<b else -1))
 assert all(len(e)==2 for e in edges.values()),(path,'nonmanifold/open edge')
 assert all(e[0][1]+e[1][1]==0 for e in edges.values()),(path,'inconsistent winding')
 parent=list(range(len(faces)))
 def root(a):
  while parent[a]!=a:
   parent[a]=parent[parent[a]];a=parent[a]
  return a
 for e in edges.values():
  a,b=root(e[0][0]),root(e[1][0]);parent[b]=a
 assert len({root(i) for i in range(len(faces))})==1,(path,'disconnected triangle shells')
 vol=float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6)
 assert vol>0,(path,'negative signed volume')
 lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));dims=hi-lo
 assert lo[2]>-1e-5,(path,'below print bed')
 assert dims[0]+16<325.001 and dims[1]+16<325.001 and dims[2]<315.001,(path,'printer envelope')
 return tri,{'file':str(path.relative_to(NEW)),'triangles':len(tri),'volume_mm3':round(vol,6),'bounds_mm':np.round(dims,6).tolist()}

files=sorted((NEW/'enclosure_stl').glob('*.stl'))+sorted((NEW/'print_first_tests').glob('*.stl'))
assert len(files)==61
triangles={};mesh_rows=[]
for path in files:
 tri,row=topology(path);triangles[path.stem]=tri;mesh_rows.append(row)

def flat_area(tri,axis,level):
 mask=np.all(abs(tri[:,:,axis]-level)<1e-5,axis=1)
 return float(np.linalg.norm(np.cross(tri[mask,1]-tri[mask,0],tri[mask,2]-tri[mask,0]),axis=1).sum()/2)

def near(a,b,tol=1e-4):
 assert abs(a-b)<tol,(a,b,tol)

walls=[]
for name in ['left_front_wall','right_front_wall']:
 v=np.array(meshes[name]['v']);old=np.array(old_meshes[name]['v'])
 ex=0 if name.startswith('left') else 260;sign=1 if ex==0 else -1
 depth=(v[:,0]-ex)*sign
 near(depth.min(),0);near(depth.max(),8)
 mask=(abs(depth)<1e-6)&(abs(v[:,1]-136)<10)&(abs(v[:,2]-30)<10)
 corners=np.unique(np.round(v[mask,1:],6),axis=0)
 assert len(corners)==4
 dims=np.ptp(corners,axis=0);center=(corners.max(axis=0)+corners.min(axis=0))/2
 near(dims[0],14.1);near(dims[1],14.1);near(center[0],136);near(center[1],30)
 pocket=v[(abs(depth-4)<1e-6)&(abs(v[:,1]-136)<9)&(abs(v[:,2]-30)<9),1:]
 near(np.ptp(pocket,axis=0)[0],16.6);near(np.ptp(pocket,axis=0)[1],16.6)
 local=(abs(v[:,1]-136)<9)&(abs(v[:,2]-30)<9)
 assert set(np.round(depth[local],5))=={0.,1.5,4.}
 circle=v[(abs(depth)<1e-6)&(abs(np.linalg.norm(v[:,1:]-[103,30],axis=1)-14)<.001),1:]
 fit=np.linalg.lstsq(np.c_[2*circle,np.ones(len(circle))],np.einsum('ij,ij->i',circle,circle),rcond=None)[0]
 cy,cz=fit[:2];radius=math.sqrt(fit[2]+cy*cy+cz*cz)
 near(cy,103);near(cz,30);near(radius,14);near(center[0]-cy,33);near(center[1]-cz,0)
 newtri=v[np.array(meshes[name]['f'])];oldtri=old[np.array(old_meshes[name]['f'])]
 outer_area=flat_area(newtri,0,ex);old_outer_area=flat_area(oldtri,0,ex)
 near(old_outer_area-outer_area,14.1**2,.01)
 tri=triangles[name];near(tri[:,:,2].min(),0);near(tri[:,:,2].max(),8)
 assert flat_area(tri,2,0)>21000 and flat_area(tri,2,8)>900
 near(flat_area(tri,2,1.5),16.6**2-14.1**2,.001)
 walls.append({'name':name,'flipper_center_yz_mm':[round(cy,6),round(cz,6)],'nudge_center_yz_mm':center.tolist(),'spacing_mm':round(center[0]-cy,6),'hole_mm':dims.tolist(),'inside_relief_mm':[16.6,16.6],'exterior_lip_mm':1.5,'print_exterior_z_mm':0,'print_inner_wall_z_mm':4,'print_collar_z_mm':8,'only_exterior_area_removed_mm2':round(old_outer_area-outer_area,6)})

coupons=[]
for label,d in [('nudge_mx_14p0',14.0),('nudge_mx_14p1',14.1),('nudge_mx_14p2',14.2)]:
 tri=triangles[label];near(tri[:,:,2].min(),0);near(tri[:,:,2].max(),4)
 near(flat_area(tri,2,0),900-d*d,.001)
 near(flat_area(tri,2,4),900-16.6**2,.001)
 near(flat_area(tri,2,1.5),16.6**2-d*d,.001)
 coupons.append(label)
tri=triangles['flipper_nudge_wall_sample']
near(tri[:,:,2].min(),0);near(tri[:,:,2].max(),8)
near(flat_area(tri,2,1.5),16.6**2-14.1**2,.001)
assert flat_area(tri,2,0)>3300 and flat_area(tri,2,8)>900
coupons.append('flipper_nudge_wall_sample')

# Re-import production STEP. The first 45 solids must match every named printed
# part's volume and assembled bounding extents before index/name mapping is used.
solids=cq.importers.importStep(str(NEW/'mini_vpin_assembly.step')).solids().vals()
assert len(solids)==64
parts={}
for i,p in enumerate(manifest['parts']):
 s=solids[i];assert s.isValid() and len(s.Solids())==1
 near(s.Volume(),p['volume'],.001)
 bb=s.BoundingBox();v=np.array(meshes[p['name']]['v'])
 actual=np.array([bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax])
 expected=np.r_[v.min(axis=0),v.max(axis=0)]
 assert np.max(abs(actual-expected))<.1,(p['name'],'STEP/mesh bounds')
 parts[p['name']]=s
rear=parts['rear_vent_panel'];rearv=np.array(meshes['rear_vent_panel']['v'])
near(rearv[:,1].min(),466);near(rearv[:,1].max(),470)
near(triangles['rear_vent_panel'][:,:,2].min(),0);near(triangles['rear_vent_panel'][:,:,2].max(),4)
face=[f for f in rear.Faces() if abs(f.BoundingBox().ymin-470)<1e-5 and abs(f.BoundingBox().ymax-470)<1e-5]
assert len(face)==1 and len(face[0].innerWires())==17
slots=[w for w in face[0].innerWires() if 800<cq.Face.makeFromWires(w).Area()<1000]
assert len(slots)==8
open_area=sum(cq.Face.makeFromWires(w).Area() for w in slots)
web=min(a.distance(b) for i,a in enumerate(slots) for b in slots[i+1:])
assert web>4
assert rear.isInside(cq.Vector(136,468,88))
assert all(rear.isInside(cq.Vector(136+58*math.cos(a),468,88+58*math.sin(a))) for a in np.linspace(0,2*math.pi,129)[:-1])
# Identify reference boxes from bounds, independently of their STEP index.
def box_ref(bounds):
 matches=[]
 for s in solids[45:]:
  b=s.BoundingBox();got=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
  if np.max(abs(np.array(got)-bounds))<1e-5:matches.append(s)
 assert len(matches)==1,bounds
 return matches[0]
pc=box_ref([35,240,13,225,430,58]);fan25=box_ref([76,441,28,196,466,148]);fan27=box_ref([76,439,28,196,466,148])
clearances=[]
for label,fan in [('25mm case',fan25),('27mm installed depth',fan27)]:
 d={'reference':label,'to_pc_mm':fan.distance(pc),'to_rear_deck_mm':fan.distance(parts['rear_control_deck']),'to_hatch_mm':fan.distance(parts['control_hatch'])}
 assert d['to_pc_mm']>=9 and d['to_rear_deck_mm']>5 and d['to_hatch_mm']>7
 clearances.append({k:round(v,6) if isinstance(v,float) else v for k,v in d.items()})
# Cable exit is an actual 60x25 wire at the intended location.
cables=[w for w in face[0].innerWires() if abs(cq.Face.makeFromWires(w).Area()-1500)<.001]
assert len(cables)==1
cb=cables[0].BoundingBox()
for a,b in zip([cb.xmin,cb.xmax,cb.zmin,cb.zmax],[10,70,50,75]):near(a,b)
near(76-cb.xmax,6)

report={
 'status':'PASS',
 'evidence':'Independent read-only audit of production STL, preview meshes, and re-imported STEP; no builder module imported.',
 'printed_parts':45,'fit_coupons':16,
 'only_changed_parts':stl_changed,'unchanged_parts_with_identical_stl_bytes_and_preview_geometry':42,
 'unchanged_part_manifest_records':42,
 'mesh_topology':{'checked':61,'closed_edge_manifold':61,'consistent_winding':61,'single_connected_triangle_shell':61,'positive_volume':61,'nondegenerate':61,'within_printer_envelope_with_8mm_brim':61},
 'walls':walls,'new_coupons_outside_down':coupons,
 'rear':{'thickness_mm':4,'closed_curved_openings':8,'minimum_exact_web_mm':round(web,6),'open_area_mm2':round(open_area,6),'open_fraction_of_112mm_circle':round(open_area/(math.pi*56**2),6),'continuous_hub_and_rim':True,'cable_cutout_xz_mm':[10,70,50,75],'cable_to_fan_frame_gap_mm':6},
 'reference_hardware_clearance':clearances,
 'physical_limits':['Actual switch clips, keycap/body and flipper nut/thread fit require supplied coupons.','Reference fan clearances do not verify wiring bends, blade clearance, cooling, or complete hand access through the hatch.']}
print(json.dumps(report,indent=2))
