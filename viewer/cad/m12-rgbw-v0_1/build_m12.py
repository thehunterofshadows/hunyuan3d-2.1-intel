"""M12 lantern RGBW electronics carrier and two-button rocker replacement; v0.1.
Source/donor attribution: ksuszka https://www.printables.com/model/96307-milwaukee-m12-lanterntorch
This is an unverified accessory-only CAD prototype; original donor geometry remains unchanged.
"""
from pathlib import Path
import cadquery as cq
import trimesh, numpy as np, json, zipfile
P=Path(__file__).resolve().parent
A=P.parents[2]/'assets'/'m12-rgbw-v0_1'
A.mkdir(parents=True,exist_ok=True)
STL=A/'stl'
STL.mkdir(exist_ok=True)
# 21x15mm nominal donor rectangular rocker switch cutout.
plug=cq.Workplane('XY').box(20.55,14.55,3.2).translate((0,0,-1.6))
flange=cq.Workplane('XY').box(24,18,1.7).translate((0,0,.85)).edges('|Z').fillet(1.5)
panel=plug.union(flange)
for x in (-5.3,5.3):
 panel=panel.cut(cq.Workplane('XY').center(x,0).circle(1.95).extrude(7).translate((0,0,-3.6)))
for x in (-8.25,8.25):
 for y in (-5.15,5.15):
  panel=panel.cut(cq.Workplane('XY').center(x,y).circle(.7).extrude(2.8).translate((0,0,-3.6)))
button=cq.Workplane('XY').circle(1.72).extrude(4.15).union(cq.Workplane('XY').circle(2.95).extrude(1.25).translate((0,0,4.15))).edges('>Z').fillet(.45)
spine=cq.Workplane('XY').box(26.5,2.8,84,centered=(True,True,False))
for z in (0,81.6):
 spine=spine.union(cq.Workplane('XY').circle(15.2).circle(12.2).extrude(2.4).translate((0,0,z)))
for z in (17,39,61):
 for x in (-8.6,8.6):
  spine=spine.cut(cq.Workplane('XY').box(3,6,5).translate((x,0,z)))
for z in (10,74):
 spine=spine.cut(cq.Workplane('XZ').center(0,z).circle(2.7).extrude(6,both=True))
gauge=cq.Workplane('XY').circle(15.2).circle(12.2).extrude(3)
parts={'rocker-slot_two-button_bezel':panel.val(),'mode_and_brightness_button_cap':button.val(),'esp32_cutoff_electronics_spine':spine.val(),'electronics_spine_diameter_fit_gauge':gauge.val()}
for name,obj in parts.items():cq.exporters.export(obj,str(STL/(name+'.stl')))
asm=cq.Assembly(name='M12 RGBW v0.1 accessory prototype')
for name,obj in parts.items():asm.add(obj,name=name)
asm.save(str(A/'m12-accessories-v0_1.step'))
# Exploded parts viewer layout, converting STL Z-up to web GLB Y-up.
scene=trimesh.Scene()
r=trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0])
for name,xyz,c in [
 ('esp32_cutoff_electronics_spine',(28,0,0),[26,147,137,255]),
 ('rocker-slot_two-button_bezel',(-34,28,0),[65,72,85,255]),
 ('mode_and_brightness_button_cap',(-39,28,9),[44,130,223,255]),
 ('electronics_spine_diameter_fit_gauge',(28,-7,0),[234,163,68,255])]:
 m=trimesh.load(STL/(name+'.stl'),force='mesh');m.apply_transform(r);m.apply_translation(xyz)
 m.visual.vertex_colors=np.tile(c,(len(m.vertices),1))
 scene.add_geometry(m,geom_name=name)
m=trimesh.load(STL/'mode_and_brightness_button_cap.stl',force='mesh')
m.apply_transform(r);m.apply_translation([-29,28,9]);m.visual.vertex_colors=np.tile([244,168,43,255],(len(m.vertices),1));scene.add_geometry(m,geom_name='brightness_button_cap')
scene.export(A/'m12-rgbw-lantern-v0_1.glb')
report={}
for n in parts:
 m=trimesh.load(STL/(n+'.stl'),force='mesh')
 report[n]={'watertight':bool(m.is_watertight),'extents_mm':list(map(lambda x:round(float(x),2),m.extents))}
(A/'validation.json').write_text(json.dumps(report,indent=2))
(A/'README.md').write_text("""# M12 RGBW lantern v0.1 — printable accessory concept
Original lantern by ksuszka, Printables #96307: https://www.printables.com/model/96307-milwaukee-m12-lanterntorch
This v0.1 viewer previews ONLY the newly designed parts, in an exploded layout; original battery housing, LED spiral holder, and diffuser are NOT included as files in this public deployment. The original donor geometry is not altered. The new insert nominally uses the original 21x15 mm rocker cutout to provide MODE and BRIGHTNESS tactile switches. This replaces the rocker; the eventual build still needs a physical power cutoff, real tact PCB mounting dimensions, and electronics-board fitting. The LED carrier is an 84mm universal cable-tie accessory that fits only if the donor inner tube measures >=30.4 mm. Print the 3mm diameter-fit ring first, then bezel fit coupon, then only print the full spine after physical trial assembly.
## Electronics requirements
M12 -> inline fuse -> independent, correctly configured 3S low-voltage disconnect with hysteresis -> regulated 5V DC/DC -> ESP32 and SK6812 RGBW LEDs. WLED mode and brightness mapping requires actual firmware configuration, not included in this mechanical CAD release. Battery voltage sensing, logic level shifter, capacitor, insulation, low battery cutoff, thermal control and master battery disconnect must be validated on the bench. Don't charge via this lantern. Actual LED strip and controller choice might require redesign.
## Current files
- stl/rocker-slot_two-button_bezel.stl
- stl/mode_and_brightness_button_cap.stl (print TWO)
- stl/esp32_cutoff_electronics_spine.stl
- stl/electronics_spine_diameter_fit_gauge.stl
- m12-accessories-v0_1.step
## Safety/status
Mechanical geometry passes watertight mesh checks only. NO print fit checks, electrical tests, thermal validation, or battery-pack cutoff testing have occurred. Keep original battery contacts and slide geometry unchanged. Confirm the original author's redistribution license before publishing their source models.
""")
with zipfile.ZipFile(A/'m12-rgbw-v0_1-print-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in [*STL.glob('*.stl'),A/'m12-accessories-v0_1.step',A/'README.md',A/'validation.json']:
  z.write(f,f.relative_to(A))
print(json.dumps({'outputs':sorted(p.name for p in A.iterdir()),'validation':report},indent=2))
