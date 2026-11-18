"""Independent optional V1.20 printable M8 nut-fit coupon and centered pilot drill guide."""
from pathlib import Path
import json,math
import cadquery as cq
from cadquery import exporters
R=Path(__file__).resolve().parent
P=json.loads((R/'parameters.json').read_text())
OUT=R/'exports/fit_m8_front'
OUT.mkdir(parents=True,exist_ok=True)
# 28 x 28 x 10 mm sample: verify purchased M8 standard nut passes into hex,
# bottoms at 8mm depth and supports an M8 stud through the 9mm center.
coupon=cq.Workplane('XY').box(28,28,10,centered=(True,True,False))
pocket=cq.Workplane('XY').polygon(6,P['foot_m8_nut_across_corners_mm']).extrude(8.01).translate((0,0,2))
coupon=coupon.cut(pocket).cut(cq.Workplane('XY').circle(P['foot_front_m8_stud_clearance_mm']/2).extrude(10.1))
# The drilled original backing plate and floor are kept unchanged in CAD.
# This separate sacrificial 60mm guide registers with the ORIGINAL four
# M5 holes and has a 3mm center hole for a light pilot marking pass.
jig=cq.Workplane('XY').circle(30).extrude(4)
for dx in [-P['foot_fastener_offsets_mm'],P['foot_fastener_offsets_mm']]:
 for dy in [-P['foot_fastener_offsets_mm'],P['foot_fastener_offsets_mm']]:
  jig=jig.cut(cq.Workplane('XY').center(dx,dy).circle(P['foot_m5_clearance_mm']/2+.1).extrude(4.1))
jig=jig.cut(cq.Workplane('XY').circle(1.5).extrude(4.1))
for name,shape in [('m8_nut_fit_coupon',coupon),('front_m8_center_pilot_jig',jig)]:
 assert shape.val().isValid() and len(shape.solids().vals())==1,name
 # Orient in positive print-bed coordinates, matching all enclosure STLs.
 bb=shape.val().BoundingBox()
 shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin))
 exporters.export(shape,str(OUT/(name+'.stl')),tolerance=.04,angularTolerance=.08)
 print(name,'volume',round(shape.val().Volume(),2))
