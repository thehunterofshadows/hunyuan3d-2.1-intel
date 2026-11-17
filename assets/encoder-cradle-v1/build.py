from pathlib import Path
import cadquery as cq, trimesh, numpy as np, json, zipfile
R=Path('/home/justin/projects/hunyuan3d-2.1-intel'); O=R/'assets/encoder-cradle-v1'; O.mkdir(exist_ok=True)
def box(x,y,z,a,b,c): return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))
def cyl(x,y,z,d,h): return cq.Workplane('XY').center(x,y).circle(d/2).extrude(h).translate((0,0,z))
holes=[(-52,-27),(52,-27),(-52,27),(52,27)]
# Design coordinates: cabinet at z=0, PCB underside at z=6.
base=box(-59,-34,0,118,68,3)
# Wide open top and bottom: two edge rails support PCB; USB ends remain open.
for y in [-18.5,15.5]: base=base.union(box(-43.5,y,3,87,3,3))
# Outer guides stop sideways movement without blocking connector row.
for x in [-43.5,40.5]:
 for y in [-22,19.5]: base=base.union(box(x,y,3,3,2.5,6))
for x,y in holes:
 base=base.union(cyl(x,y,0,13,10))
 # blind inserts enter from cabinet face; 2.8mm cap prevents screw reaching PCB.
 base=base.cut(cyl(x,y,-.01,4.5,7.21)).cut(cq.Workplane('XY').center(x,y).circle(2.6).workplane(offset=.6).circle(2.25).loft().translate((0,0,-.01)))
# Cable tie slots: secure the PCB only at bare edges, or use small glue dabs on edge rails.
for x in [-35,35]:
 for y in [-25,22]: base=base.cut(box(x-2,y,-1,4,2.5,5))
# USB cable tie anchoring slots at open end.
for y in [-5,5]: base=base.cut(box(-56,y-1.25,-1,4,2.5,5))
# Print flat base down; narrow annular bore shoulder bridges 0.55mm radially.
for x,y in holes: base=base.cut(cyl(x,y,7,3.4,4))
# Through screw relief has only 0.55mm annular bridge at z7.2, no supports required.
jig=box(-59,-34,0,118,68,2)
for x,y in holes: jig=jig.cut(cyl(x,y,-1,3.4,4))
# Window aligns jig to cradle outline, saves plastic.
jig=jig.cut(box(-43,-18,-1,86,36,4))
gauge=box(-46,-22,0,92,44,2).cut(box(-43,-18,-1,86,36,4))
coupon=box(0,0,0,48,15,10)
for x,d in [(8,4.3),(24,4.5),(40,4.7)]: coupon=coupon.cut(cyl(x,7.5,-1,d,12))
parts={'encoder_cradle':base.clean(),'drill_jig_104x54':jig.clean(),'pcb_fit_gauge_86x36':gauge.clean(),'insert_test_4p3_4p5_4p7':coupon.clean()}
assembly=cq.Assembly(); scene=trimesh.Scene(); report={}
for i,(name,p) in enumerate(parts.items()):
 assert p.val().isValid() and len(p.solids().vals())==1,name
 cq.exporters.export(p,str(O/(name+'.stl')),tolerance=.03,angularTolerance=.08)
 cq.exporters.export(p,str(O/(name+'.step')))
 m=trimesh.load(O/(name+'.stl'),force='mesh'); assert m.is_watertight,name
 assert m.volume>0
 report[name]={'watertight':True,'valid_solid':True,'bounds_mm':m.extents.tolist(),'volume_mm3':m.volume}
 assembly.add(p,name=name)
 if i<2:
  v,f=p.val().tessellate(.03,.08); mm=trimesh.Trimesh(vertices=[q.toTuple() for q in v],faces=f,process=False)
  # show jig beside cradle, exact mm geometry converted to meters, Y-up.
  if i: mm.apply_translation([0,85,0])
  mm.vertices=np.stack((mm.vertices[:,0],mm.vertices[:,2],-mm.vertices[:,1]),axis=1)/1000
  mm.visual=trimesh.visual.ColorVisuals(mm,vertex_colors=[55,170,155,255] if not i else [240,175,65,255])
  scene.add_geometry(mm,node_name=name,geom_name=name)
(O/'encoder-cradle-v1.glb').write_bytes(scene.export(file_type='glb'))
assembly.save(str(O/'encoder-cradle-v1.step'))
report.update({'hole_pattern_mm':[104,54],'insert_nominal_mm':[3,5,6],'insert_bore_mm':4.5,'pcb_nominal_mm':[85,35],'pcb_gauge_opening_mm':[86,36],'physical_fit_tested':False})
(O/'validation.json').write_text(json.dumps(report,indent=2))
(O/'README.md').write_text('''# Encoder cradle V1 — separate printable model
Print encoder_cradle.stl and drill_jig_104x54.stl flat as supplied, 100% scale in millimeters.
PETG, 0.2mm layers, 4 walls, 5 top/bottom layers, 25–35% infill. No supports required;
the insert bore shoulder has a short 0.55mm radial bridge. No printed threads or snap hooks.
Cradle 118 x 68 x 10mm. Four M3 mounting axes: 104 x 54mm rectangular centers.
PCB assumption from prior discussion: 85 x 35mm, NOT measured. Print the 86 x 36mm
open fit gauge first. Board must fit with plugs attached and bare underside edges
must land on the two raised rails without solder/component contact. If not, stop and
provide actual board dimensions for revision. No exact board-hole pattern assumed.
Board underside sits 6mm above cabinet, 3mm above tray floor. Open ends clear USB.
Secure board using tiny hot glue dabs on bare supported edges, or loose nonconductive
ties through outer slots where connectors/components permit. Do not clamp components.
USB cable ties go through the pair of slots at the left end to remove plug strain.
Heat-set inserts: user M3, nominal 5mm OD x 6mm long. Insert from FLAT CABINET FACE
(underside), small smooth end first. Four 4.5mm bores, 7.2mm depth plus 3.4mm screw relief.
Test coupon holes left-to-right 4.3 / 4.5 / 4.7mm; test actual insert first.
Inserts flush with flat cabinet-contact face; cool before mounting. Remove any first-layer
elephant foot at bore entries. Screw tips must stay inside the 10mm boss envelope.
Choose screw length = actual floor + washer thickness + 4–5mm thread engagement;
e.g. 4mm floor + 1mm washer + 5mm engagement = M3x10. Verify, do not bottom out.
JIG: check printed center spacing with ruler (104 x 54mm). Tape flat to UNDERSIDE
at intended location. Check clearance above all four locations first. Mark centers
through the four 3.4mm holes, remove jig, drill 3.4mm clearance with a backing block.
The symmetric pattern works from below; no mirrored template needed.
The jig is a marking guide, not a precision metal drill bushing. Do not heat it with a drill.
Mount screws upward into cradle inserts. Fit and hardware retention need physical testing.
Editable STEP, reproducible build source and mesh validation included. Cabinet untouched.
''')
# 1:1 paper SVG is optional; printed plastic jig is primary.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="158mm" height="108mm" viewBox="-79 -54 158 108"><rect x="-59" y="-34" width="118" height="68" fill="none" stroke="black" stroke-width=".3"/>']
for x,y in holes: svg.append(f'<circle cx="{x}" cy="{y}" r="1.7" fill="none" stroke="black" stroke-width=".2"/><path d="M{x-4},{y}h8 M{x},{y-4}v8" stroke="black" stroke-width=".2"/>')
svg.append('<text x="-55" y="45" font-size="3">100% actual size. Centers 104 x 54 mm. Check scale.</text></svg>')
(O/'paper-template-1to1.svg').write_text(''.join(svg))
(O/'build.py').write_text(Path(__file__).read_text())
with zipfile.ZipFile(O/'encoder-cradle-v1-print-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in O.iterdir():
  if f.suffix in ['.stl','.step','.md','.json','.svg','.py']: z.write(f,f.name)
print(json.dumps(report))

