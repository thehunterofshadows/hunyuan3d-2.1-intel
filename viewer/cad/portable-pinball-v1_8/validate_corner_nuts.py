"""Check all eight exact STEP brackets, nominal M3 entry, spin resistance and unchanged parts."""
from pathlib import Path
import json,math
import cadquery as cq
R=Path(__file__).resolve().parent
P=json.loads((R/'parameters.json').read_text())
solids=cq.importers.importStep(str(R/'exports/mini_vpin_assembly.step')).solids().vals()
rows=[]
def vol(w):return sum(s.Volume() for s in w.solids().vals())
def nut(zz,offset=0,angle=30):
 r=5.5/math.sqrt(3)
 points=[(14+r*math.cos(math.radians(angle+60*i)),zz+offset+r*math.sin(math.radians(angle+60*i))) for i in range(6)]
 return cq.Workplane('YZ').polyline(points).close().extrude(2.4).translate((7.4,0,0))
for side in ['left','right']:
 for end in ['front','rear']:
  for zz in ([24,56] if end=='front' else [24,128]):
   name=f'corner_{side}_{end}_{zz}'
   bounds=[4,24,4,24,zz-8,zz+8]
   if side=='right':bounds[:2]=[236,256]
   if end=='rear':bounds[2:4]=[446,466]
   matches=[]
   for s in solids:
    b=s.BoundingBox()
    if all(abs(a-b)<1e-4 for a,b in zip([b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax],bounds)):matches.append(s)
   assert len(matches)==1,(name,len(matches))
   sh=cq.Workplane(obj=matches[0])
   if end=='rear':sh=sh.mirror('XZ',(0,235,0))
   if side=='right':sh=sh.mirror('YZ',(130,0,0))
   assert sh.val().isValid() and len(sh.solids().vals())==1
   for axis in ['x','y']:
    for i in range(33):
     n=nut(zz,i*.5)
     if axis=='y':n=n.mirror((1,-1,0))
     assert vol(sh.intersect(n))<1e-5,(name,axis,'entry collision',i)
    n=nut(zz,angle=0)
    if axis=='y':n=n.mirror((1,-1,0))
    assert vol(sh.intersect(n))>.01,(name,axis,'nut can spin')
    # Original screw axis remains clear through the thickened arm.
    pt=(-.1,14,zz) if axis=='x' else (14,-.1,zz)
    direction=(1,0,0) if axis=='x' else (0,1,0)
    screw=cq.Workplane(obj=cq.Solid.makeCylinder(1.6,13,cq.Vector(*pt),cq.Vector(*direction)))
    assert vol(sh.intersect(screw))<1e-5,(name,axis,'blocked screw')
   rows.append({'part':name,'valid_single_solid':True,'both_nut_entry_paths_clear':True,'both_nuts_resist_rotation':True,'original_screw_axes_clear':True})
a={p['name']:p for p in json.loads((R.parent/'portable-pinball-v1_4/exports/preview_meshes.json').read_text())}
b={p['name']:p for p in json.loads((R/'exports/preview_meshes.json').read_text())}
changed=sorted(n for n in a if a[n]!=b[n]);assert changed==sorted(r['part'] for r in rows),changed
geo=json.loads((R/'exports/geometry_checks.json').read_text());assert not geo['interferences'] and not geo['reserved_space_interferences'],geo
report={'changed_parts':changed,'other_37_printable_meshes_identical':True,'arm_mm':8,'bearing_wall_mm':3.2,'back_wall_mm':2,'nut_depth_mm':2.8,'nut_slot_width_mm':5.85,'nominal_nut_flats_mm':5.5,'nominal_nut_thickness_mm':2.4,'physical_fit_tested':False,'checks':rows}
(R/'exports/corner_nut_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: all 8 brackets, 16 nut entry paths, spin resistance, original screw bores; 37 other parts unchanged.')
