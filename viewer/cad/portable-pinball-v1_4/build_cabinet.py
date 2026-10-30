"""Mini VPin prototype, mm. Requires cadquery 2.7. Run: python build_cabinet.py.
All STL exports are individually oriented onto their intended print face.
The STEP assembly retains assembled positions. No hardware or reference envelope is printable.
"""
from pathlib import Path
import json, math, csv
import cadquery as cq
from cadquery import exporters
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
OUT=ROOT/'exports'; OUT.mkdir(exist_ok=True)
STL=OUT/'enclosure_stl'; STL.mkdir(exist_ok=True)
TEST=OUT/'print_first_tests'; TEST.mkdir(exist_ok=True)
W=P['width'];L=P['length'];T=P['wall'];A=P['slope_degrees']; S=math.tan(math.radians(A)); C=math.cos(math.radians(A))
H=P['front_height'];Y0=P['monitor_front_y'];Y1=Y0+P['monitor_length']*C;ML=(W-P['monitor_width'])/2;MR=W-ML
G=P['joint_gap']; SPLIT=L/2
parts=[]; assembly=cq.Assembly(name='Mini_VPin_Prototype_V1_4')
colors={'wall':(.17,.24,.31),'floor':(.30,.37,.43),'lid':(.36,.48,.57),'bezel':(.16,.21,.26),'support':(.88,.55,.20),'joint':(.25,.66,.55),'test':(.25,.65,.80)}
def z(y):return H+y*S
def box(x,y,z0,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z0))
def cyl(point,d,length,axis=(0,0,1)):return cq.Workplane(obj=cq.Solid.makeCylinder(d/2,length,cq.Vector(*point),cq.Vector(*axis)))
def xhole(y,zz):return cyl((-5,y,zz),3.4,W+10,(1,0,0))
def yhole(x,zz):return cyl((x,-5,zz),3.4,L+10,(0,1,0))
def wedge(x,y,dx,dy,low,top_offset=0):
 return cq.Workplane('YZ').polyline([(y,low),(y+dy,low),(y+dy,z(y+dy)+top_offset),(y,z(y)+top_offset)]).close().extrude(dx).translate((x,0,0))
def topplate(x,y,dx,dy,t=4):
 return box(x,y/C,0,dx,dy/C,t).rotate((0,0,0),(1,0,0),A).translate((0,0,H+1))
N=(0,-math.sin(math.radians(A)),C)
def topbore(x,y,d=3.4):
 point=(x,y,z(y)+1)
 return cyl(tuple(point[i]-25*N[i] for i in range(3)),d,50,N)
def nut_top(x,y,depth=3.0):
 # Hex pocket along the same normal as the top-cover screws; opens at top.
 return cq.Workplane('XY').center(x,y/C).polygon(6,6.6).extrude(-depth).rotate((0,0,0),(1,0,0),A).translate((0,0,H+1))
def orient(shape,mode):
 if mode=='side':shape=shape.rotate((0,0,0),(0,1,0),90)
 if mode=='end':shape=shape.rotate((0,0,0),(1,0,0),90)
 if mode in ('top','top_diagonal'):shape=shape.rotate((0,0,0),(1,0,0),180-A)
 if mode=='top_diagonal':shape=shape.rotate((0,0,0),(0,0,1),45) # Both long bezel rails print diagonally on 325 mm bed
 bb=shape.val().BoundingBox();return shape.translate((-bb.xmin,-bb.ymin,-bb.zmin))
def add(name,shape,kind='wall',mode='flat',qty=1,export=True):
 shape=shape.clean(); assert shape.val().isValid(),name
 assert len(shape.solids().vals())==1,(name,'disconnected solids')
 assembly.add(shape,name=name,color=cq.Color(*colors[kind]))
 printed=orient(shape,mode); bb=printed.val().BoundingBox()
 fits=bb.xlen+16<=325 and bb.ylen+16<=325 and bb.zlen<=315
 assert fits,(name,'too large for bed with 8 mm brim',bb.xlen,bb.ylen,bb.zlen)
 if export:exporters.export(printed,str(STL/(name+'.stl')),tolerance=.08,angularTolerance=.12)
 parts.append(dict(name=name,shape=shape,print_shape=printed,kind=kind,mode=mode,bounds=[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],volume=shape.val().Volume(),export=export))
# Seam splice and wall holes; no permanent bonding.
splice_holes=[(215,25),(215,50),(255,25),(255,50)]
shelf_ys=[28,218,252,442]
mount_ys=[25,50,140,330,450]
saddle_ys=[180,360]
corner_ys=[14,L-14];corner_zs={14:[24,56],L-14:[24,128]}
for side in ['left','right']:
 x=0 if side=='left' else W-T
 for region in ['front','rear']:
  ya=0 if region=='front' else SPLIT+G/2
  yb=SPLIT-G/2 if region=='front' else L
  sh=wedge(x,ya,T,yb-ya,0)
  # In-plane tongue, printed flat; 0.3 mm clearance each non-contact edge.
  if region=='front':sh=sh.union(box(x,SPLIT-G/2,70,T,6+G/2,8))
  else:sh=sh.cut(box(x-1,SPLIT-G/2,69.7,T+2,6.3+G/2,8.6))
  for yy,zz in splice_holes:sh=sh.cut(xhole(yy,zz))
  for yy in shelf_ys:sh=sh.cut(xhole(yy-4,8))
  for yy in mount_ys:sh=sh.cut(xhole(yy+6,z(yy)-8))
  for yy in saddle_ys:sh=sh.cut(xhole(yy,z(yy)-20))
  for yy in corner_ys:
   for zz in corner_zs[yy]:sh=sh.cut(xhole(yy,zz))
  # Flipper hole at 103 from front, 30 above bottom.
  sh=sh.cut(cyl((-5,103,30),P['button_hole'],W+10,(1,0,0)))
  if region=='rear':
   for yy in range(275,416,20):sh=sh.cut(box(x-1,yy,20,T+2,7,18))
  add(side+'_'+region+'_wall',sh,'wall','side')
# End plates sit between side walls.
front=wedge(T,0,W-2*T,T,0)
for xx in [110,160,210]:front=front.cut(cyl((xx,-1,26),P['button_hole'],T+2,(0,1,0)))
for xx in [14,W-14]:
 for zz in [24,56]:front=front.cut(yhole(xx,zz))
add('front_button_panel',front,'wall','end')
rear=wedge(T,L-T,W-2*T,T,0)
for xx in [14,W-14]:
 for zz in [24,128]:rear=rear.cut(yhole(xx,zz))
# Rear PC/USB/power pass-through plus exhaust slots. PC ports face the front.
rear=rear.cut(box(100,L-T-1,16,60,T+2,25))
for xx in range(50,211,20):rear=rear.cut(box(xx,L-T-1,80,7,T+2,36))
add('rear_vent_panel',rear,'wall','end')
# Internal L brackets: two per corner. Print upright on L-shaped foot.
for side in ['left','right']:
 for end,yy in [('front',14),('rear',L-14)]:
  for zz in corner_zs[yy]:
   a=box(4,4,zz-8,4,20,16).union(box(4,4,zz-8,20,4,16))
   a=a.cut(xhole(14,zz)).cut(yhole(14,zz))
   if side=='right':a=a.mirror('YZ',(W/2,0,0))
   if end=='rear':a=a.mirror('XZ',(0,L/2,0))
   add(f'corner_{side}_{end}_{zz}',a,'joint')
# Side splice plates bridge the middle seam, one plate each side.
for side in ['left','right']:
 x=4 if side=='left' else W-8
 sp=box(x,203,12,4,64,48)
 for yy,zz in splice_holes:sp=sp.cut(xhole(yy,zz))
 add('splice_'+side,sp,'joint','side')
# Eight floor shelf blocks. Bolt to wall, then screw removable floor upward into top-loaded M3 nuts.
for side in ['left','right']:
 for yy in shelf_ys:
  x=4 if side=='left' else W-20;cx=x+8
  sh=box(x,yy-8,4,16,16,8).cut(xhole(yy-4,8))
  sh=sh.cut(cyl((cx,yy,0),3.4,20))
  sh=sh.cut(cq.Workplane('XY').center(cx,yy).polygon(6,6.6).extrude(3.1).translate((0,0,8.9)))
  add(f'floor_block_{side}_{yy}',sh,'joint')
# Two lift-out bottom panels; rear panel also acts as the PC tray.
for region in ['front','rear']:
 ya=4.3 if region=='front' else SPLIT+G/2
 yb=SPLIT-G/2 if region=='front' else L-4.3
 sh=box(4.3,ya,0,W-8.6,yb-ya,4)
 for xx in [12,W-12]:
  for yy in shelf_ys:sh=sh.cut(cyl((xx,yy,-1),3.4,6))
 if region=='rear':
  for xx in [25,230]:
   for yy in [250,400]:sh=sh.cut(box(xx,yy,-1,6,20,6))
 add('bottom_'+region,sh,'floor')
# Top fastening blocks. Top-loaded hex nuts are captured by installed covers.
for side in ['left','right']:
 for yy in mount_ys:
  x=4 if side=='left' else W-16;cx=x+6
  sh=wedge(x,yy-10,12,20,z(yy)-13,1).cut(xhole(yy+6,z(yy)-8))
  sh=sh.cut(topbore(cx,yy)).cut(nut_top(cx,yy))
  add(f'top_block_{side}_{yy}',sh,'joint')
# Four padded edge saddles. Housing contact must be confirmed with the fit coupon.
for side in ['left','right']:
 for yy in saddle_ys:
  x=4 if side=='left' else MR-5
  width=ML+5-4
  shelf_raise=P['right_saddle_raise_mm'] if side=='right' else 0
  sh=wedge(x,yy-10,width,20,z(yy)-32,-14+shelf_raise)
  stop_x=ML-3.5 if side=='left' else MR+.5
  # Preserve the monitor-facing stop face; add 3 mm toward the wall.
  reinforced_x=stop_x-3 if side=='left' else stop_x
  sh=sh.union(wedge(reinforced_x,yy-10,6,20,z(yy)-28,.5))
  # External triangular root brace. No new material enters the monitor pocket.
  if side=='left':profile=[(reinforced_x-4,z(yy-10)-14),(reinforced_x,z(yy-10)-14),(reinforced_x,z(yy-10)-6)]
  else:profile=[(reinforced_x+6+4,z(yy-10)-14),(reinforced_x+6,z(yy-10)-14),(reinforced_x+6,z(yy-10)-6)]
  brace=cq.Workplane('XZ').polyline(profile).close().extrude(-20).translate((0,yy-10,0))
  sh=sh.union(brace).cut(xhole(yy,z(yy)-20))
  add(f'monitor_saddle_{side}_{yy}',sh,'support','end')
# Both side bezels are continuous: right A1+A2 retained from V1.2,
# and left front+rear joined in V1.3. Same monitor overlap, screw holes, clearance.
# Length ~351.35 mm: print each rail at 45 degrees across QIDI X-Max 3 bed.
for side in ['left','right']:
 x=0 if side=='left' else MR-1
 width=ML+1
 sh=topplate(x,Y0+1,width,Y1-Y0-2)
 for yy in [140,330]:sh=sh.cut(topbore(x+10 if side=='left' else W-10,yy))
 add('bezel_left_one_piece' if side=='left' else 'bezel_right_a1_a2',sh,'bezel','top_diagonal')
# Full-width front cable lid includes 1 mm housing overlap. No glue or permanent monitor change.
sh=topplate(0,0,W,Y0+1)
# Front-right housing stop, clear of the front-left connectors.
sh=sh.union(wedge(MR-12,Y0-4.5,12,4,z(Y0)-18,2))
for xx in [10,W-10]:
 for yy in [25,50]:sh=sh.cut(topbore(xx,yy))
add('front_cable_lid',sh,'lid','top')
# Rear deck includes removable control hatch. Small underside nut pockets retain hatch nuts.
hy=Y1+4; hx=18;hw=80;hd=35
sh=topplate(0,Y1-1,W,L-Y1+1)
# Cut opening with a generously tall normal prism.
cut=box(hx,hy/C,-3,hw,hd/C,12).rotate((0,0,0),(1,0,0),A).translate((0,0,H+1))
sh=sh.cut(cut)
sh=sh.union(wedge(MR-12,Y1+.5,12,4,z(Y1)-18,2))
for xx in [10,W-10]:sh=sh.cut(topbore(xx,450))
# Hatch bolt positions: clear of main deck fasteners and the aperture.
for xx in [12,104]:
 yy=hy+hd/2
 sh=sh.cut(topbore(xx,yy))
 # nut pocket below deck, same normal, leaving 1.4 mm roof below hatch.
 pocket=cq.Workplane('XY').center(xx,yy/C).polygon(6,6.6).extrude(2.6).rotate((0,0,0),(1,0,0),A).translate((0,0,H+1))
 sh=sh.cut(pocket)
add('rear_control_deck',sh,'lid','top')
# Hatch sits on top of rear deck. 100 × ~49 projected footprint; screws retain it for transport.
sh=topplate(8,hy-7,100,hd+14,3).translate((0,-4*math.sin(math.radians(A)),4*C))
for xx in [12,104]:sh=sh.cut(topbore(xx,hy+hd/2))
# Main left deck screw is under the hatch footprint: add head clearance on its underside.
sh=sh.cut(topbore(10,450,7))
add('control_hatch',sh,'lid','top')
# Dedicated tests. Small samples are supplied separately from full enclosure STLs.
tests=[]
def test(name,shape,mode='flat',note=''):
 shape=orient(shape.clean(),mode);assert shape.val().isValid() and len(shape.solids().vals())==1,name
 exporters.export(shape,str(TEST/(name+'.stl')),tolerance=.05,angularTolerance=.1)
 bb=shape.val().BoundingBox();tests.append({'name':name,'bounds':[round(bb.xlen,2),round(bb.ylen,2),round(bb.zlen,2)],'note':note,'shape':shape})
# 28.0 / 28.2 / 28.4 holes account for real printer dimensional behavior.
for d in [28,28.2,28.4]:
 sh=box(0,0,0,52,52,4).cut(cyl((26,26,-1),d,6))
 test('button_hole_'+str(d).replace('.','p'),sh,note=f'{d} mm modeled hole, 4 mm panel; fit actual threaded barrel and nut.')
# Monitor edge test leaves open space under the housing for the attached cover.
# 2 mm pad +12 mm housing => screen top51; retention underside52 gives 1 mm gap.
base=box(0,0,0,30,50,5).union(box(0,0,0,8,50,52))
base=base.union(box(8,0,32,6,50,5))
gusset=cq.Workplane('XZ').polyline([(8,26),(14,32),(8,32)]).close().extrude(-50)
base=base.union(gusset)
for yy in [10,40]:base=base.cut(cyl((-1,yy,46),2.8,7,(1,0,0)))
test('monitor_edge_cradle_12mm',base,note='2 mm padding on narrow shelf; 12 mm housing screen top51. Cover gets open space underneath. Retainer underside52.')
bar=box(-4,0,52,14,50,3).union(box(-4,0,40,4,50,15))
for yy in [10,40]:bar=bar.cut(cyl((-5,yy,46),3.4,6,(1,0,0)))
# Rotate top of cap onto bed; upright skirt prints upward without support.
test('monitor_retaining_bar',bar.rotate((0,0,0),(1,0,0),180),note='Install with two M3 ×10 screws lightly into the coupon pilot holes. Only ~1 mm housing overlap; no screen pressure.')
shim=box(0,0,0,6,50,5)
test('monitor_5mm_shim_for_7mm_housing',shim,note='On narrow shelf only, add under 7 mm housing with 2 mm pad. Same top51 target.')
test('optional_saddle_shim_5mm',box(0,0,0,5,20,5),note='Optional full-cabinet shim; print four if all saddles land on 7 mm housing. Tape to saddle, never monitor.')
# Exact wall seam geometry extracted from the design, with assembly holes at same coordinates.
for region in ['front','rear']:
 sh=next(p['shape'] for p in parts if p['name']=='left_'+region+'_wall')
 clip=box(-1,203,12,6,64,92)
 test('joint_'+region+'_wall',sh.intersect(clip),'side',note='Print with outer wall face down; slide tongue into slot, attach splice with M3 bolts.')
sh=next(p['shape'] for p in parts if p['name']=='splice_left')
test('joint_splice_plate',sh,'side',note='Use four M3 × 12 screws and M3 nuts with joint samples.')
# Monitor-reference envelopes, for review only. No active-screen dimensions are assumed.
reference=wedge(ML,Y0,P['monitor_width'],Y1-Y0,z(Y0)-12,0) # use uniform 12 mm envelope following slope instead below
reference=cq.Workplane('YZ').polyline([(Y0,z(Y0)-12),(Y1,z(Y1)-12),(Y1,z(Y1)),(Y0,z(Y0))]).close().extrude(P['monitor_width']).translate((ML,0,0))
assembly.add(reference,name='REFERENCE_monitor_12mm_envelope',color=cq.Color(.2,.65,.85,.22))
pc=box(35,240,13,190,190,45)
assembly.add(pc,name='REFERENCE_PC_allowance_ports_face_front',color=cq.Color(.25,.75,.5,.25))
# Reserved spaces are separate reference solids and are checked against printed geometry.
keepouts=[('PC allowance',pc)]
for xx in [110,160,210]:keepouts.append((f'front button {xx}',box(xx-20,4.2,6,40,P['button_inward_clearance'],40)))
keepouts.append(('left flipper',box(4.2,83,10,P['button_inward_clearance'],40,40)))
keepouts.append(('right flipper',box(W-4.2-P['button_inward_clearance'],83,10,P['button_inward_clearance'],40,40)))
cover=cq.Workplane('YZ').polyline([(Y0,z(Y0)-P['cover_total_depth_allowance']),(Y1,z(Y1)-P['cover_total_depth_allowance']),(Y1,z(Y1)-7),(Y0,z(Y0)-7)]).close().extrude(P['monitor_width']-10).translate((ML+5,0,0))
keepouts.append(('central folded cover reserve',cover))
keepouts.append(('USB encoder allowance',box(100,140,13,70,50,12)))
for idx,(label,sh) in enumerate(keepouts[1:]):assembly.add(sh,name='REFERENCE_'+str(idx)+'_'+label.replace(' ','_'),color=cq.Color(.95,.60,.15,.2))
# Do not export reference objects as STLs.
assembly.save(str(OUT/'mini_vpin_assembly.step'))
# Mesh source retained for exact CAD previews.
manifest={'revision':'Prototype V1.4','units':'mm','printer_build_mm':[325,325,315],'brim_margin_each_side_mm':8,'parameters':P,'parts':[{k:v for k,v in p.items() if k not in ['shape','print_shape']} for p in parts],'tests':[{k:v for k,v in t.items() if k!='shape'} for t in tests]}
(OUT/'parts_manifest.json').write_text(json.dumps(manifest,indent=2))
with (OUT/'print_inventory.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['part','print_x_mm','print_y_mm','print_z_mm','orientation','status'])
 for p in parts:w.writerow([p['name'],*p['bounds'],p['mode'],'PROTOTYPE - FIT TEST FIRST'])
# Save assembly placement and meshes for renderer, plus test geometry.
mesh=[]
for p in parts:
 verts,faces=p['shape'].val().tessellate(.3,.2)
 mesh.append({'name':p['name'],'kind':p['kind'],'v':[[v.x,v.y,v.z] for v in verts],'f':[list(f) for f in faces]})
(OUT/'preview_meshes.json').write_text(json.dumps(mesh))
# Pairwise solid interference: shared faces excluded. Report before issuing package.
issues=[]
keepout_issues=[]
for label,sh in keepouts:
 for p in parts:
  hit=sh.intersect(p['shape'])
  vol=sum(v.Volume() for v in hit.solids().vals())
  if vol>.05:keepout_issues.append({'reserve':label,'part':p['name'],'volume_mm3':round(vol,4)})
for i,p in enumerate(parts):
 for q in parts[i+1:]:
  a=p['shape'].val().BoundingBox();b=q['shape'].val().BoundingBox()
  if min(a.xmax,b.xmax)-max(a.xmin,b.xmin)<.001 or min(a.ymax,b.ymax)-max(a.ymin,b.ymin)<.001 or min(a.zmax,b.zmax)-max(a.zmin,b.zmin)<.001:continue
  v=p['shape'].intersect(q['shape']).val().Volume() if p['shape'].intersect(q['shape']).vals() else 0
  if v>.05:issues.append({'a':p['name'],'b':q['name'],'intersection_mm3':round(v,4)})
(OUT/'geometry_checks.json').write_text(json.dumps({'all_parts_valid':True,'all_parts_single_solid':True,'all_parts_fit_with_8mm_brim':True,'interferences':issues,'reserved_space_interferences':keepout_issues},indent=2))
print(json.dumps({'parts':len(parts),'tests':len(tests),'interferences':issues,'reserved_space_interferences':keepout_issues},indent=2),flush=True)
