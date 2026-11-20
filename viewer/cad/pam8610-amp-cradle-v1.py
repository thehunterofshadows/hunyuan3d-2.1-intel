#!/usr/bin/env python3
"""PAM8610 mini PCB glue-on cradle V1, user-measured outer hole spans, assumed diameter."""
from pathlib import Path
import cadquery as cq, trimesh, numpy as np, json, zipfile
ROOT=Path('/home/justin/projects/hunyuan3d-2.1-intel')
O=ROOT/'assets/pam8610-amp-cradle-v1'
O.mkdir(exist_ok=True)
# User caliper measurements: outermost edge of hole to outermost edge of hole.
# For equal circular mounting holes, outer-edge span = center span + hole diameter.
# HOLE_D is a provisional value. Measure on real PCB before committing mounting.
OUTER_SPAN_X=27.48; OUTER_SPAN_Y=22.93
HOLE_D=3.0
PITCH_X=OUTER_SPAN_X-HOLE_D; PITCH_Y=OUTER_SPAN_Y-HOLE_D
PCB_X=31.; PCB_Y=25.
BASE_X=39.; BASE_Y=33.; BASE_T=2.8; POST_TOP=11.1
INSERT_OD=5.; INSERT_LEN=6.; PILOT_D=4.3
# Printed flat underside down. Four corner posts and no side walls: all 4 wiring edges open.
def cyl(x,y,z,d,h):
 return cq.Workplane('XY').center(x,y).circle(d/2).extrude(h).translate((0,0,z))
base=cq.Workplane('XY').box(BASE_X,BASE_Y,BASE_T,centered=(True,True,False)).edges('|Z').fillet(2.2)
holes=[(x,y) for y in (-PITCH_Y/2,PITCH_Y/2) for x in (-PITCH_X/2,PITCH_X/2)]
for x,y in holes:
 base=base.union(cyl(x,y,BASE_T,7.4,POST_TOP-BASE_T))
 # Blind heat-set hole: insert from TOP, stop above cabinet-contact underside.
 base=base.cut(cyl(x,y,POST_TOP-6.65,PILOT_D,6.76))
 base=base.cut(cyl(x,y,POST_TOP-.5,4.7,.62)) # smaller mouth relief
base=base.clean()
# A fast, cheap 4-hole PCB drill pitch gauge; place against the real board before mounting.
gauge=cq.Workplane('XY').box(36,30,1.5,centered=(True,True,False)).edges('|Z').fillet(2.2)
for x,y in holes: gauge=gauge.cut(cyl(x,y,-.1,3.15,1.7))
gauge=gauge.clean()
# Fit coupon, 6.7 mm pilot depth, three diameters around requested 4.3 mm.
coupon=cq.Workplane('XY').box(42,13,9,centered=(True,True,False)).edges('|Z').fillet(1.2)
for x,d in [(-13,4.2),(0,4.3),(13,4.4)]:
 coupon=coupon.cut(cyl(x,0,2.3,d,6.9))
coupon=coupon.clean()
parts={'amp_cradle':base,'pcb_hole_pitch_gauge':gauge,'m3_insert_fit_coupon':coupon}
scene=trimesh.Scene(); report={}
colors={'amp_cradle':[47,92,97,255], 'pcb_reference':[36,41,47,150]}
for name,p in parts.items():
 assert len(p.solids().vals())==1 and p.val().isValid(),name
 cq.exporters.export(p,str(O/(name+'.stl')),tolerance=.032,angularTolerance=.095)
 cq.exporters.export(p,str(O/(name+'.step')))
 m=trimesh.load(O/(name+'.stl'),force='mesh')
 assert m.is_watertight and m.volume>0,(name,m.is_watertight,m.volume)
 report[name]={'size_mm':[round(float(v),3) for v in m.extents],
               'watertight':True,'solid':True,'volume_mm3':round(float(m.volume),1)}
 if name=='amp_cradle':
  m.visual.vertex_colors=colors[name]
  xyz=m.vertices.copy()
  m.vertices=np.stack([xyz[:,0],xyz[:,2],-xyz[:,1]],axis=1)*.001
  scene.add_geometry(m,geom_name='amp_cradle_printable',node_name='amp_cradle_printable')
# Honest illustrative PCB envelope, not the supplied board CAD or printed component.
board=cq.Workplane('XY').box(PCB_X,PCB_Y,2.5,centered=(True,True,False)).translate((0,0,POST_TOP+.35))
for x,y in holes: board=board.cut(cyl(x,y,POST_TOP+.2,3.2,2.9))
vv,ff=board.val().tessellate(.07,.15)
b=trimesh.Trimesh(vertices=np.array([v.toTuple() for v in vv]),faces=ff,process=False)
b.visual.vertex_colors=colors['pcb_reference']
coords=b.vertices.copy()
b.vertices=np.stack([coords[:,0],coords[:,2],-coords[:,1]],axis=1)*.001
scene.add_geometry(b,geom_name='pcb_31x25_reference_only',node_name='pcb_31x25_reference_only')
(O/'pam8610-amp-cradle-v1.glb').write_bytes(scene.export(file_type='glb'))
# Top-view SVG illustrates the dimensions; not a substitute for physical pitch measurement.
svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 560" width="800" height="560">
<rect width="800" height="560" fill="#14202a"/>
<rect x="154" y="96" width="492" height="369" rx="23" fill="#316568" stroke="#86c2be" stroke-width="5"/>
<rect x="201" y="142" width="398" height="276" rx="9" fill="#1b292e" stroke="#c5d8d5" stroke-dasharray="8 8" stroke-width="3"/>
<g fill="#c8b38b" stroke="#10222a" stroke-width="8">
<circle cx="229" cy="158" r="30"/><circle cx="571" cy="158" r="30"/>
<circle cx="229" cy="401" r="30"/><circle cx="571" cy="401" r="30"/></g>
<g fill="#19292a"><circle cx="229" cy="158" r="17"/><circle cx="571" cy="158" r="17"/><circle cx="229" cy="401" r="17"/><circle cx="571" cy="401" r="17"/></g>
<g stroke="#eef1e8" stroke-width="2"><path d="M229 61V121 M571 61V121 M229 77H571 M124 158H190 M124 401H190 M134 158V401" /></g>
<g fill="#e9f3ef" font-family="Arial,sans-serif" font-size="28" text-anchor="middle">
<text x="400" y="63">24.48 mm* hole centers</text><text transform="translate(116 280) rotate(-90)">19.93 mm* hole centers</text>
<text x="400" y="516" font-size="22">PAM8610 cradle · 31 × 25 mm PCB · pitch estimated for Ø3.0 holes</text></g>
</svg>'''
(O/'preview.svg').write_text(svg)
readme=f'''# PAM8610 mini amp glue-on cradle V1

Independent 3D-printable mounting accessory for Chico pinball.
Source board is the photographed PAM8610 V0.0.4 mini stereo amplifier.

## Dimensions — IMPORTANT ACCURACY NOTE
* Published board size: **31 x 25 x 2.5 mm** (module, NOT the IC).
* **27.48 x 22.93 mm outside-to-outside hole spans were measured by user with calipers.**
* Assuming PCB mounting holes Ø3.00 mm: pitch **24.48 x 19.93 mm center-to-center**.
  Formula center pitch = outside-edge span - one hole diameter.
* Ø3.00 mm is a DESIGN ASSUMPTION, not yet measured; exact pitch remains unverified.
* Measure the real PCB mounting-hole diameter to calculate the final center pitch.
  If not 3.00 mm, change HOLE_D and regenerate before using this cradle.
  Test the gauge against all four real holes BEFORE installing any inserts or gluing.
* Base outer size: 39 x 33 x 11.1 mm overall (including standoffs); flat bottom.
* Four Ø7.4 mm standoffs at +/−12.24 mm X, +/−9.965 mm Y (provisional).
* PCB nominal underside = z11.1 mm, giving 8.3 mm gap above the base.
* Four **M3 heat-set inserts**, user's nominal 5 mm OD by 6 mm length.
* **4.3 mm Ø insert pilots** (versus 4.5 mm on Chico volume box), 6.65 mm deep,
  installed FROM TOP; tiny 4.7 mm mouth relief. Blind, bottom remains unbroken.
* Cradle open on all sides for speaker, power and input wires.
* Suggested PCB mounting screws: M3x8, verify screw/board/insert clearance and don't
  force a screw against the blind pocket bottom.

## Print & mount
1. Measure PCB mounting-hole diameter, then print `pcb_hole_pitch_gauge.stl`
   (1.5 mm thick) and test against all four PCB holes. If even one misses, DO NOT force the screws or glue the cradle.
2. Print `m3_insert_fit_coupon.stl`: 4.2, 4.3 and 4.4 mm test pockets.
   Use 4.3mm production cradle only if the real inserts fit with secure plastic.
3. Print `amp_cradle.stl` flat on its bottom in PETG, 0.2 mm layers, 4 walls,
   30% infill recommended, no supports required.
4. Seat heat inserts from the TOP with a controlled soldering iron, square, away
   from electronics. Allow to cool completely. Never drive screws to bottom.
5. Screw PCB to posts, keeping all pads and exposed contacts clear of screw heads.
   Use gentle torque; check board flex and clear solder joints.
6. Test powered operation and thermal behavior BEFORE gluing down. Disconnect.
7. Roughen and clean the smooth underside of the cradle and cabinet bonding area.
   Use an adhesive suitable for PETG and the chosen cabinet surface (e.g., appropriate
   2-part epoxy); clamp and allow full cure. Hot glue alone may soften near heat.
   Keep the amp ventilated and wires strain-relieved.
8. Keep glue away from the board, standoffs and insert mouths.

The viewer shows a dark **nominal PCB envelope for fit illustration only**;
no physical board, PCB trace, or mounting CAD drawing was supplied.
All fit measurements are provisional until physical gauge test.
'''
(O/'README.md').write_text(readme)
report['assumptions']={'board_mm':[31,25,2.5],'user_measured_outer_hole_span_mm':[OUTER_SPAN_X,OUTER_SPAN_Y],
                      'assumed_mount_hole_diameter_mm':HOLE_D,
                      'hole_pitch_mm':[PITCH_X,PITCH_Y],
                      'pitch_verified':False,'insert_od_mm':5.,'insert_length_mm':6.,
                      'pilot_mm':4.3,'volume_pilot_mm':4.5,'base_mm':[39,33,11.1]}
(O/'validation.json').write_text(json.dumps(report,indent=2))
# Full editable STEP assembly with print parts
assembly=cq.Assembly(name='pam8610_adhesive_cradle_v1')
for name,p in parts.items():
 assembly.add(p,name=name,loc=cq.Location(cq.Vector(0,45 if name=='pcb_hole_pitch_gauge' else -45 if name=='m3_insert_fit_coupon' else 0,0)))
assembly.save(str(O/'pam8610-amp-cradle-v1.step'))
with zipfile.ZipFile(O/'pam8610-amp-cradle-v1-print-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in O.iterdir():
  if f.suffix in ['.stl','.step','.svg','.py','.md','.json']:
   z.write(f,f.name)
print(json.dumps(report))
