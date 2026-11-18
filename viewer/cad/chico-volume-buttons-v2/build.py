#!/usr/bin/env python3
"""Chico Volume Control V2: parametric PETG enclosure, captive button caps."""
from pathlib import Path
import cadquery as cq
import trimesh, numpy as np, json, zipfile, math
R=Path('/home/justin/projects/hunyuan3d-2.1-intel')
OUT=R/'assets/chico-volume-buttons-v2'
OUT.mkdir(parents=True,exist_ok=True)
SWITCHES=(-13.0,13.0)
W,H=78.,32.
def block(x,y,z,dx,dy,dz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=(True,True,False)).translate((x,y,z))
def cyl(x,y,z,r,h):
    return cq.Workplane('XY').center(x,y).circle(r).extrude(h).translate((0,0,z))
def roundbox(w,h,d,z,r):
    return cq.Workplane('XY').box(w,h,d,centered=(True,True,False)).edges('|Z').fillet(r).translate((0,0,z))
# Back tray, open upward; faceplate fixes with two heatset inserts in solid end pillars.
body=roundbox(W,H,15,0,5.0)
body=body.cut(roundbox(72.,26.,13.2,2.8,3.0))
for x in [-33.1,33.1]:
    body=body.union(cyl(x,0,2.8,5.15,12.2))
    # 5mm OD x6mm M3 insert, fitted from FRONT, leaves 2.4mm below 6.7mm bore
    body=body.cut(cyl(x,0,8.1,2.25,7.01))
    body=body.cut(cyl(x,0,14.4,2.55,.7)) # entry chamfer-ish lead in
# Dual 12.7mm clearance seats, guide rails capture y edges without blocking leg soldering.
for x in SWITCHES:
    # two shortened ribs preserve switch location but clear the full-width button pad
    for sign in [-1,1]:
        body=body.union(block(x,sign*7.55,2.8,15.8,2.1,5.6))
    # tiny central spacer island under switch; switch legs remain unobstructed
    body=body.union(block(x,0,2.8,8,8,.8))
    # wire lead reliefs in base rear within shell, not through the cabinet back
    body=body.cut(block(x,0,2.65,3.0,10.4,.7))
# rear cable notch cuts through long wall at +Y, leaving external bottom surface intact
body=body.cut(block(0,15.2,4.1,9.0,6.0,6.8))
# two optional inside-access mounting holes in bottom floor (under cover, not in switch wells)
for x,y in [(-26,-10.2),(26,10.2)]:
    body=body.cut(cyl(x,y,-.2,1.75,3.3))
    body=body.cut(cyl(x,y,1.1,3.0,1.8))
# Cover: round rectangle, two cap clearance holes and countersunk screw entries.
cover=roundbox(W,H,2.8,0,5.0)
for x in SWITCHES:
    cover=cover.cut(cyl(x,0,-.1,8.05,3.0)) # cap head Ø15.3 with 0.4 radial clearance
for x in (-33.1,33.1):
    cover=cover.cut(cyl(x,0,-.1,1.75,3.1))
    cover=cover.cut(cyl(x,0,1.1,3.05,1.8))
# Clear bottom of cover around button flange; do not cut all the way through
for x in SWITCHES:
    cover=cover.cut(cyl(x,0,-.01,10.5,.51))
# Front face engraving for model aesthetic: shallow line to denote compact panel
# Faceplate printing: outside/front face upward; cap separate.
def cap(symbol,stem):
    # V2 button PRINTS BROAD BACK FACE DOWN, with no narrow central tip.
    # The Ø20.3mm retaining lip continues at full diameter to the switch actuator.
    # Ø15.3mm front face sits above full-width lower section; no unsupported overhangs.
    rear_height=1.5+stem
    p=cyl(0,0,0,10.15,rear_height)
    p=p.union(cyl(0,0,rear_height,7.65,4.5))
    # engraved characters face UP in slicer for cleaner detail.
    face_z=rear_height+4.5
    p=p.cut(block(0,0,face_z-.72,7.2,1.3,.82))
    if symbol=='plus':
        p=p.cut(block(0,0,face_z-.72,1.3,7.2,.82))
    return p.clean()
parts={'enclosure_back':body.clean(),'front_faceplate':cover.clean()}
for sym in ['minus','plus']:
    for label,stem in [('short',1.9),('standard',3.4),('long',4.9)]:
        parts[f'{sym}_cap_{label}']=cap(sym,stem)
# switch-fit gauge verifies a real switch footprint BEFORE printing full housing.
gauge=block(0,0,0,25,25,2.8)
for side in [-1,1]:
    gauge=gauge.union(block(0,side*7.55,2.8,15.8,2.1,5.6))
parts['switch_12mm_fit_gauge']=gauge.clean()
# Insert coupon three bore sizes, 7.1mm deep
coupon=block(0,0,0,49,14,9)
for x,r in [(-15,2.15),(0,2.25),(15,2.35)]:
    coupon=coupon.cut(cyl(x,0,2.0,r,7.2))
parts['m3_insert_fit_coupon']=coupon.clean()
result={}
scene=trimesh.Scene()
COL={'enclosure_back':[37,44,52,255],'front_faceplate':[64,73,81,255],
     'minus_cap_standard':[20,22,25,255],'plus_cap_standard':[20,22,25,255],
     'switch_reference':[162,166,170,255]}
def addmesh(name,p,color,translate=(0,0,0),flip_cap=False):
    vs,faces=p.val().tessellate(.09,.14)
    m=trimesh.Trimesh(vertices=np.array([v.toTuple() for v in vs]),
      faces=faces,process=False)
    if flip_cap: m.apply_transform([[1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,1]])
    m.apply_translation(translate)
    arr=m.vertices.copy()
    m.vertices=np.stack([arr[:,0],arr[:,2],-arr[:,1]],axis=-1)*.001
    m.visual.vertex_colors=np.tile(np.array(color,dtype=np.uint8),(len(m.vertices),1))
    scene.add_geometry(m,node_name=name,geom_name=name)
for name,p in parts.items():
    assert len(p.solids().vals())==1 and p.val().isValid(),name
    path=OUT/(name+'.stl')
    cq.exporters.export(p,str(path),tolerance=.045,angularTolerance=.11)
    mesh=trimesh.load(path,force='mesh')
    assert mesh.is_watertight and mesh.volume>0,(name,mesh.is_watertight,mesh.volume)
    result[name]={'bounds_mm':[round(float(i),3) for i in mesh.extents], 'watertight':True,'solid':True}
    cq.exporters.export(p,str(OUT/(name+'.step')))
# In the 3D viewer, keep cover slightly raised and switches visible for inspectable construction.
addmesh('enclosure_back',body,COL['enclosure_back'])
addmesh('front_faceplate',cover,COL['front_faceplate'],(0,0,19))
for x,sym in zip(SWITCHES,['minus','plus']):
    sw=block(x,0,3.6,12,12,4.2).union(cyl(x,0,7.8,2.8,2.3))
    addmesh(f'{sym}_12mm_tactile_switch_illustration',sw,COL['switch_reference'])
    # Front face at z23.5, rear disk at z14.1; cover exploded at z19.
    # In the fully assembled unit (cover down 4mm), rear disk touches switch actuator.
    addmesh(f'{sym}_retained_button',parts[f'{sym}_cap_standard'],COL[f'{sym}_cap_standard'],(x,0,14.1))
(OUT/'chico-volume-buttons-v2.glb').write_bytes(scene.export(file_type='glb'))
readme="""# Chico volume buttons V2 — standalone 3D printable model

Two independent momentary volume controls using the user's BLACK, nominal 12x12mm tactile switches.
Not part of the large pinball cabinet model.

## Construction and retention
- Rounded case 78 x 32 x 17.8mm total (back 15mm, front 2.8mm).
- Two 15.3mm printed button heads slide in Ø16.1mm faceplate bores.
- The rear of EACH cap is a solid **Ø20.3mm-wide cylindrical pad** extending to
  the tactile switch contact (no skinny plunger). Its diameter is larger than the
  Ø16.1mm faceplate opening: insert from the inside before closing. It cannot fall out.
- The tactile spring returns each cap, and the flange stops against the underside of cover.
- Two front M3 screws secure into heat-set inserts in rear pillars x +/- 33.1mm.
- User's nominal M3 5mm OD x 6mm inserts: 4.5mm pilot pocket, 6.9mm usable depth,
  insert from open front of rear shell, not through its back. Check real insert size.
- 9 x 6.8mm cable notch in rear shell's side (+Y), with a covered rear floor.
- Two optional rear mounting holes accept 3mm screws through the tray floor before assembly.
- Switch pockets assume **12 x 12mm body**. Both sides remain accessible for wiring.
  Secure each switch to its support with a small removable glue bead or suitable thin PCB,
  not on metal/switch actuator. Never pull on bare solder legs.
- Faceplate prevents button escape; faceplate is removable to replace a switch or cap.
- The prior Ø4.8mm narrow plunger has been removed on both + and - buttons.
  The **Ø20.3mm retaining lip now continues all the way to the flat switch-contact face**.
  This makes each cap printable with its full-width 20.3mm back on the build plate.
  Cap head remains Ø15.3mm, moves freely inside the Ø16.1mm faceplate opening.
- Three full-width back lengths: 3.4 / 4.9 / 6.4mm total below head (short,
  standard, long). Use ONE minus and ONE plus cap of the same selected length.
  The standard cap is engineered to touch the illustrated switch at rest:
  nominal 0.5-1mm compression travel available before adjacent pocket ribs,
  but **actual switch height/throw are unmeasured**. Try before mounting.
- PETG suggested, 0.2mm layers, 4 walls, 25-35% infill.
  Print caps **large flat underside DOWN**, symbols UP; body base DOWN,
  faceplate outer face DOWN. Letter marks recessed 0.7mm.
  The large button base removes the fragile small-foot print orientation.
- Print switch_12mm_fit_gauge and m3_insert_fit_coupon **first**. Coupon bores:
  4.3 / 4.5 / 4.7mm nominal; 5mm inserts must be tested with your actual printer.

## Wiring
- Black 4-leg switch normally has 2 legs on each electrically common side. Verify with
  a multimeter: use one pin from each opposite side for a normally-open button.
- Route both switch wires through side notch; strain relieve them to the cabinet.
- Connect to TWO spare, separate USB encoder inputs and GND if available.
  Map encoder key outputs to Windows system Volume Up / Volume Down (software mapping may
  be necessary; keyboard HID codes depend on the encoder). Do not apply amp power to switch.

## CAD and status
- Exact CAD generated in CadQuery; STL / STEP for each part in ZIP.
- GLB preview has illustrated switch bodies and the cover **exploded upward** so rear
  flanges and heat-set bosses are visible. Printed STL files are NOT exploded.
- Computer-validated manifold meshes and nominal assembled-fit check only.
  Actual switch geometry, actuation, insert heating and fit remain to be tested.
- V1 is preserved unchanged. V2 is a separate selectable studio model.
"""
(OUT/'README.md').write_text(readme)
result.update({'outer_dimensions_mm':[W,H,17.8],
 'cap_hole_diameter_mm':16.1,'cap_flange_diameter_mm':20.3,
 'underside_full_width_mm':20.3, 'narrow_plunger_removed':True,
 'cap_print_orientation':'flat full-width back face on build plate; lettered head up',
 'switch_illustration_contact_gap_standard_mm':0,
 'm3_insert_nominal_mm':[3,5,6],
 'm3_insert_pocket_diameter_mm':4.5,
 'rear_cable_notch_mm':[9,6.8],
 'physical_fit_tested':False})
(OUT/'validation.json').write_text(json.dumps(result,indent=2))
(OUT/'build.py').write_text(Path(__file__).read_text())
# SVG preview with perspective-free illustrations (not a generated concept drawing).
svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 520">
<rect width="980" height="520" fill="#121b23"/>
<text x="58" y="70" fill="#e5f0f5" font-size="34" font-family="sans-serif" font-weight="bold">CHICO · VOLUME BUTTONS</text>
<text x="58" y="106" fill="#86a9b5" font-size="20" font-family="sans-serif">V2 · wide-base captured-cap case / M3 inserts</text>
<rect x="70" y="170" width="510" height="225" rx="44" fill="#56616d" stroke="#8393a0" stroke-width="9"/>
<circle cx="240" cy="282" r="86" fill="#1c242b" stroke="#929da6" stroke-width="5"/>
<circle cx="418" cy="282" r="86" fill="#1c242b" stroke="#929da6" stroke-width="5"/>
<path d="M197 283 h85" stroke="#dce3e7" stroke-width="17" stroke-linecap="round"/>
<path d="M377 283 h85 M420 240 v85" stroke="#dce3e7" stroke-width="17" stroke-linecap="round"/>
<circle cx="112" cy="282" r="13" fill="#27303a" stroke="#a9b3bc" stroke-width="4"/>
<circle cx="538" cy="282" r="13" fill="#27303a" stroke="#a9b3bc" stroke-width="4"/>
<text x="625" y="220" fill="#e5f0f5" font-size="25" font-family="sans-serif">78 × 32 × 17.8 mm</text>
<text x="625" y="268" fill="#9bafbc" font-size="19" font-family="sans-serif">Ø20.3 full-width button backs</text>
<text x="625" y="305" fill="#9bafbc" font-size="19" font-family="sans-serif">2 × M3 heat-set inserts</text>
<text x="625" y="342" fill="#9bafbc" font-size="19" font-family="sans-serif">Back cable notch</text>
<text x="70" y="460" fill="#7c96a7" font-size="17" font-family="sans-serif">Actual CAD STL and STEP available. Physical switch-fit test required.</text>
</svg>'''
(OUT/'preview.svg').write_text(svg)
with zipfile.ZipFile(OUT/'chico-volume-buttons-v2-print-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(OUT.iterdir()):
        if f.suffix in ('.stl','.step','.md','.json','.py'): z.write(f,f.name)
print(json.dumps({'ok':True,'parts':list(parts),'geometry':result,'pack_bytes':(OUT/'chico-volume-buttons-v2-print-pack.zip').stat().st_size}))

