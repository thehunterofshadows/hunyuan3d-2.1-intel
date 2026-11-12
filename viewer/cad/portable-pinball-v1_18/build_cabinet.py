"""Mini VPin prototype, mm. Requires cadquery 2.7. Run: python build_cabinet.py.
All STL exports are individually oriented onto their intended print face.
The STEP assembly retains assembled positions. No hardware or reference envelope is printable.
"""
from pathlib import Path
import json, math, csv, hashlib
import cadquery as cq
from cadquery import exporters
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
OUT=ROOT/'exports'; OUT.mkdir(exist_ok=True)
STL=OUT/'enclosure_stl'; STL.mkdir(exist_ok=True)
TEST=OUT/'print_first_tests'; TEST.mkdir(exist_ok=True)
# Remove a stale pre-V1.18 coupon filename if this output directory was previously generated.
( TEST/'flipper_floor_notch_sample.stl' ).unlink(missing_ok=True)
W=P['width'];L=P['length'];T=P['wall'];A=P['slope_degrees']; S=math.tan(math.radians(A)); C=math.cos(math.radians(A))
H=P['front_height'];Y0=P['monitor_front_y'];Y1=Y0+P['monitor_length']*C;ML=(W-P['monitor_width'])/2;MR=W-ML
G=P['joint_gap']; SPLIT=L/2
parts=[]; assembly=cq.Assembly(name='Mini_VPin_Prototype_V1_16')
colors={'wall':(.17,.24,.31),'floor':(.30,.37,.43),'lid':(.36,.48,.57),'bezel':(.16,.21,.26),'support':(.88,.55,.20),'joint':(.25,.66,.55),'test':(.25,.65,.80),'feet':(.26,.33,.40),'mount':(.36,.45,.48)}
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
 if mode=='flip':shape=shape.rotate((0,0,0),(1,0,0),180)
 if mode=='side':shape=shape.rotate((0,0,0),(0,1,0),90)
 if mode=='side_outer_left':shape=shape.rotate((0,0,0),(0,1,0),-90)
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

# V1.18 selective front edge treatment. All coordinates are assembly millimetres.
EDGE_D=P['front_edge_depth_mm']; EDGE_R=P['front_edge_blend_radius_mm']
LID_D=P['lid_edge_depth_mm']; LID_R=P['lid_edge_blend_radius_mm']
SIN=math.sin(math.radians(A)); SQRT2=math.sqrt(2)
EDGE_A=EDGE_D+EDGE_R-SQRT2*EDGE_R
LID_A=LID_D+LID_R-SQRT2*LID_R
front_before={}
def corner_plan_cut(yscale=1.0,height=200,zbase=-1):
 # Hybrid outside corner in XY: 45 degree line then a true radius1 arc.
 # The elliptic variant scales only Y to compensate the lid's10 degree plane.
 # Explicit ellipse keeps endpoint tangency; transformGeometry would spline
 # the straight segment and can destabilize the later perimeter blend.
 d=EDGE_D;r=EDGE_R;t=d-r/SQRT2
 pts=[(-1,-1,0),(d,-1,0),(d,0,0),(t,(r-r/SQRT2)*yscale,0),(0,EDGE_A*yscale,0),(-1,(EDGE_A+1)*yscale,0)]
 edges=[cq.Edge.makeLine(cq.Vector(*pts[0]),cq.Vector(*pts[1])),cq.Edge.makeLine(cq.Vector(*pts[1]),cq.Vector(*pts[2]))]
 edges.append(cq.Edge.makeEllipse(r*yscale,r,(d,r*yscale,0),(0,0,1),(0,1,0),135,180))
 edges += [cq.Edge.makeLine(cq.Vector(*pts[i]),cq.Vector(*pts[(i+1)%len(pts)])) for i in [3,4,5]]
 wire=cq.Wire.assembleEdges(edges)
 return cq.Workplane('XY').newObject([wire]).toPending().extrude(height).translate((0,0,zbase))
vertical_front_cut=corner_plan_cut(height=z(L)+10)
# Shared cut across the front face. The first segment has actual dZ/dY=1
# in the panel's print axes, then R1 blends tangent to the 10 degree top.
# Defining a45-degree profile relative to the sloped top would exceed45.
LIP_CY=EDGE_D+EDGE_R*SIN
LIP_CZ=H+S*EDGE_D-EDGE_R*C
LIP_TY=LIP_CY-EDGE_R/SQRT2
LIP_TZ=LIP_CZ+EDGE_R/SQRT2
LIP_START_Z=LIP_TZ-LIP_TY
mid=math.radians((135+90+A)/2)
front_lip_cut=(cq.Workplane('YZ').moveTo(-1,H+6).lineTo(EDGE_D,H+6)
 .lineTo(EDGE_D,H+S*EDGE_D)
 .threePointArc((LIP_CY+EDGE_R*math.cos(mid),LIP_CZ+EDGE_R*math.sin(mid)),(LIP_TY,LIP_TZ))
 .lineTo(-1,LIP_START_Z-1).close().extrude(W+2).translate((-1,0,0)))
def rounded_lid_blank():
 # Work in the unrotated lid plane. Constant-through-thickness plan cuts
 # match the walls at the underside; their top retains the original tilt
 # projection. The upper rim follows the entire rounded corner.
 depth=(Y0+1)/C
 plan_cut=corner_plan_cut(1/C,T+2,-1)
 original=box(0,0,0,W,depth,T)
 plan=original.cut(plan_cut).cut(plan_cut.mirror('YZ',(W/2,0,0)))
 perimeter=[e for e in plan.val().Edges() if all(abs(v.Z-T)<1e-6 for v in e.Vertices()) and e.Center().y<depth-1e-5]
 chamfered=plan.newObject(perimeter).chamfer(LID_A)
 blend=[e for e in chamfered.val().Edges() if all(abs(v.Z-(T-LID_A))<1e-6 for v in e.Vertices()) and e.Center().y<depth-1e-5]
 softened=chamfered.newObject(blend).fillet(LID_R)
 assert softened.val().isValid() and len(softened.solids().vals())==1,'lid perimeter blend'
 # Fade the side rim to zero at Y = 60; the rear 5 mm at the bezel seam remains
 # exact. This mask is vertical in print axes and adds no downward overhang.
 fade0=P['lid_side_fade_start_y_mm']/C;fade1=P['lid_side_fade_end_y_mm']/C
 mask=box(-1,-1,-1,W+2,fade0+1,T+2)
 taper=(cq.Workplane('XY').polyline([(-1,fade0),(LID_A,fade0),(0,fade1),(-1,fade1)])
        .close().extrude(T+2).translate((0,0,-1)))
 mask=mask.union(taper).union(taper.mirror('YZ',(W/2,0,0)))
 removed=plan.cut(softened).intersect(mask)
 result=plan.cut(removed)
 assert result.val().isValid() and len(result.solids().vals())==1,'lid fade'
 return result
lid_local_rounded=rounded_lid_blank()

# V1.18 controls: floor-seated, screw-anchored flipper reinforcement.
FY=P['flipper_y_mm']; BZ=P['button_center_z_mm']; NY=FY+P['nudge_center_spacing_mm']
COLLAR_R=P['flipper_reinforcement_diameter_mm']/2
LOCAL_T=P['flipper_total_local_thickness_mm']
PEDESTAL_Z=P['flipper_pedestal_bottom_z_mm']; FLOOR_CLEAR=P['flipper_floor_notch_clearance_mm']
FLOOR_H=4; FAST_X=P['flipper_anchor_x_mm']; FAST_Y=FY+P['flipper_anchor_y_offset_mm']; FAST_NUT_Z=P['flipper_anchor_nut_bottom_z_mm']
RECESS=P['nudge_recess_depth_mm']; WELL_FLOOR=P['nudge_well_floor_mm']; WELL_MOUTH=P['nudge_well_mouth_mm']
UPPER_HOUSING=P['nudge_upper_housing_mm']
assert abs(RECESS+P['nudge_snap_plate_mm']-T)<1e-9
assert abs(WELL_MOUTH-WELL_FLOOR-2*RECESS)<1e-9
def mirror_side(shape,side):
 return shape if side=='left' else shape.mirror('YZ',(W/2,0,0))
def collar(side):
 # Retain the V1.8 analytic cone and flat nut seat. A matching tapered stem
 # fills its lower half down to the intact floor top at Z=4.
 # Together they form a broad D-shaped reinforcement on the inside wall, with a separate floor-fastening lug.
 flat_r=P['flipper_reinforcement_flat_diameter_mm']/2
 co=cq.Workplane(obj=cq.Solid.makeCone(COLLAR_R,flat_r,LOCAL_T-T+.02,cq.Vector(T-.02,FY,BZ),cq.Vector(1,0,0)))
 stem=cq.Workplane('XY').polyline([(T-.02,FY-COLLAR_R),(LOCAL_T,FY-flat_r),(LOCAL_T,FY+flat_r),(T-.02,FY+COLLAR_R)]).close().extrude(BZ-FLOOR_H).translate((0,0,FLOOR_H))
 # The *original* D-shaped flipper reinforcement is retained. The V1.13
 # rectangular offset block/heel is removed entirely. Slightly flare the
 # existing pedestal's foot toward the inside from X8 to X11.5 for an M3 nut.
 # This is one continuous tapered root under the button, NOT a separate box.
 foot_flare=(cq.Workplane('XZ').polyline([(T-.05,FLOOR_H),(11.5,FLOOR_H),
                    (11.5,11.5),(LOCAL_T,13.9),(T-.05,13.9)]).close()
             .extrude(-9).translate((0,FY-21,0)))
 # Standard metal M3 hex nut lies flat inside the original rib footprint.
 # The inside-facing slot opens in +X: slide the nut sideways before
 # inserting the removable bottom panel and fastening from underneath.
 nut=(cq.Workplane('XY').center(FAST_X,FAST_Y)
      .polygon(6,P['flipper_anchor_hex_diameter_mm'])
      .extrude(P['flipper_anchor_nut_height_mm']).translate((0,0,FAST_NUT_Z)))
 access=box(FAST_X,FAST_Y-P['flipper_anchor_slot_width_mm']/2,FAST_NUT_Z,
            17-FAST_X,P['flipper_anchor_slot_width_mm'],P['flipper_anchor_nut_height_mm'])
 screw=cyl((FAST_X,FAST_Y,FLOOR_H-.1),P['flipper_anchor_bore_mm'],
           FAST_NUT_Z+P['flipper_anchor_nut_height_mm']-FLOOR_H+.2)
 return mirror_side(co.union(stem).union(foot_flare).cut(nut).cut(access).cut(screw),side)

def nudge_well(side):
 # Intersect two planar trapezoid prisms to form the square frustum.
 # This preserves exact planar bounds and print-bed placement; a generic
 # loft may create spline faces with conservative OCC bounding boxes.
 # At X=0 the mouth is23 mm, narrowing to18 mm at X=2.5 (45 degrees).
 reach=WELL_MOUTH+.2
 profile_y=[(-.1,NY-reach/2),(RECESS,NY-WELL_FLOOR/2),(RECESS,NY+WELL_FLOOR/2),(-.1,NY+reach/2)]
 profile_z=[(-.1,BZ-reach/2),(RECESS,BZ-WELL_FLOOR/2),(RECESS,BZ+WELL_FLOOR/2),(-.1,BZ+reach/2)]
 taper_y=cq.Workplane('XY').polyline(profile_y).close().extrude(reach).translate((0,0,BZ-reach/2))
 taper_z=cq.Workplane('XZ').polyline(profile_z).close().extrude(-reach).translate((0,NY-reach/2,0))
 return mirror_side(taper_y.intersect(taper_z),side)
def nudge_cuts(side,cutout=None):
 d=P['nudge_cutout_mm'] if cutout is None else cutout
 relief=P['nudge_relief_mm']; lip=P['nudge_snap_plate_mm']
 through=box(-1,NY-d/2,BZ-d/2,LOCAL_T+2,d,d)
 # Backside clip/body clearance now begins behind the recessed 1.5 mm plate.
 # At the default 2.5 mm setback this is X=4, the existing inside wall face.
 pocket=box(RECESS+lip,NY-relief/2,BZ-relief/2,LOCAL_T+1-RECESS-lip,relief,relief)
 return mirror_side(through.union(pocket),side).union(nudge_well(side))
# Seam splice and wall holes; no permanent bonding.
splice_holes=[(215,25),(215,50),(215,85),(255,25),(255,50),(255,85)]
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
  # Reinforce both front walls inward only; keep the original flipper bore/axis.
  if region=='front':sh=sh.union(collar(side)).cut(nudge_cuts(side))
  sh=sh.cut(cyl((-5,FY,BZ),P['button_hole'],W+10,(1,0,0)))
  if region=='rear':
   for yy in range(275,416,20):sh=sh.cut(box(x-1,yy,20,T+2,7,18))
  mode='side_outer_left' if side=='left' and region=='front' else 'side'
  if region=='front':
   front_before[side+'_front_wall']=sh
   sh=sh.cut(mirror_side(vertical_front_cut,side)).cut(front_lip_cut)
  add(side+'_'+region+'_wall',sh,'wall',mode)
# End plates sit between side walls.
front=wedge(T,0,W-2*T,T,0)
for xx in [110,160,210]:front=front.cut(cyl((xx,-1,26),P['button_hole'],T+2,(0,1,0)))
for xx in [14,W-14]:
 for zz in [24,56]:front=front.cut(yhole(xx,zz))
front_before['front_button_panel']=front
front=front.cut(front_lip_cut)
add('front_button_panel',front,'wall','end')
rear=wedge(T,L-T,W-2*T,T,0)
for xx in [14,W-14]:
 for zz in [24,128]:rear=rear.cut(yhole(xx,zz))
# V1.9 integrated spiral grille. Four mounting regions retain the full 4 mm wall.
# Eight spline-sided openings leave broad curved spokes and a continuous outer rim.
FX=P['fan_center_x_mm']; FZ=P['fan_center_z_mm']
R0=P['fan_grille_hub_radius_mm']; R1=P['fan_grille_radius_mm']
SPOKES=P['fan_grille_spokes']; SW=P['fan_grille_spoke_width_mm']; TW=math.radians(P['fan_grille_twist_degrees'])
def slot_point(r,i,side):
 phi=i*2*math.pi/SPOKES+TW*(r-R0)/(R1-R0)
 a=phi+side*(math.pi/SPOKES-SW/(2*r))
 return (FX+r*math.cos(a),FZ+r*math.sin(a))
fan_slots=[]
for i in range(SPOKES):
 radii=[R0+(R1-R0)*j/24 for j in range(25)]
 lo=[slot_point(r,i,-1) for r in radii]; hi=[slot_point(r,i,1) for r in radii]
 outer_mid=(FX+R1*math.cos(i*2*math.pi/SPOKES+TW),FZ+R1*math.sin(i*2*math.pi/SPOKES+TW))
 inner_mid=(FX+R0*math.cos(i*2*math.pi/SPOKES),FZ+R0*math.sin(i*2*math.pi/SPOKES))
 slot=cq.Workplane('XZ').moveTo(*lo[0]).spline(lo[1:],includeCurrent=True).threePointArc(outer_mid,hi[-1]).spline(list(reversed(hi[:-1])),includeCurrent=True).threePointArc(inner_mid,lo[0]).close().extrude(T+2).translate((0,L+1,0))
 fan_slots.append(slot); rear=rear.cut(slot)
fan_mount_centers=[]
for sx in [-1,1]:
 for sz in [-1,1]:
  xx=FX+sx*P['fan_mount_spacing_mm']/2; zz=FZ+sz*P['fan_mount_spacing_mm']/2
  fan_mount_centers.append((xx,zz))
  rear=rear.cut(cyl((xx,L-T-1,zz),P['fan_mount_hole_mm'],T+2,(0,1,0)))
cable_cut=box(P['rear_cable_x_mm'],L-T-1,P['rear_cable_z_mm'],P['rear_cable_width_mm'],T+2,P['rear_cable_height_mm'])
rear=rear.cut(cable_cut)
add('rear_vent_panel',rear,'wall','end')
# Internal L brackets: two per corner. Print upright on L-shaped foot.
for side in ['left','right']:
 for end,yy in [('front',14),('rear',L-14)]:
  for zz in corner_zs[yy]:
   # Thicker inward arms, unchanged wall contact planes and mounting axes.
   arm=P['corner_arm_mm']; depth=P['corner_nut_depth_mm']
   bearing=P['corner_nut_bearing_mm']; slot=P['corner_nut_slot_width_mm']
   a=box(4,4,zz-8,arm,20,16).union(box(4,4,zz-8,20,arm,16))
   # X-axis screw nut: top-loading YZ hex slot, with flats parallel to entry.
   radius=P['corner_nut_hex_diameter_mm']/2
   profile=[(14+radius*math.cos(math.radians(30+60*i)),zz+radius*math.sin(math.radians(30+60*i))) for i in range(6)]
   pocket=cq.Workplane('YZ').polyline(profile).close().extrude(depth).translate((4+bearing,0,0))
   pocket=pocket.union(box(4+bearing,14-slot/2,zz,depth,slot,8.5))
   flare=[(14-slot/2,zz+6.5),(14+slot/2,zz+6.5),(14+3.6,zz+8.5),(14-3.6,zz+8.5)]
   pocket=pocket.union(cq.Workplane('YZ').polyline(flare).close().extrude(depth).translate((4+bearing,0,0)))
   # Rotate the second slot about the corner diagonal: x/y swap.
   pocket_y=pocket.mirror((1,-1,0),(0,0,0))
   a=a.cut(pocket).cut(pocket_y).cut(xhole(14,zz)).cut(yhole(14,zz))
   if side=='right':a=a.mirror('YZ',(W/2,0,0))
   if end=='rear':a=a.mirror('XZ',(0,L/2,0))
   add(f'corner_{side}_{end}_{zz}',a,'joint')
# V1.6: both splice plates bridge the seam with 6 mm thickness and 83 mm height.
# Three fastener rows, each on either side of seam. Outer wall faces and mating seams unchanged.
for side in ['left','right']:
 x=T if side=='left' else W-T-P['splice_thickness_mm']
 sp=box(x,203,12,P['splice_thickness_mm'],64,83)
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
# Four independent modular foot stations: two in each removable bottom panel.
# M4 through-bolts clamp a 50 mm external mounting disc to a 50 mm internal
# load-spreading plate. No fastener relies on tapping the 4 mm floor plastic.
FOOT_X=P['foot_centers_x_mm']; FOOT_Y={'front':P['foot_front_y_mm'],'rear':P['foot_rear_y_mm']}
FOOT_OFF=P['foot_fastener_offsets_mm']; FOOT_BOLT_D=P['foot_m4_clearance_mm']
FOOT_STATIONS=[(side,region,xx,FOOT_Y[region]) for side,xx in [('left',FOOT_X[0]),('right',FOOT_X[1])] for region in ['front','rear']]
foot_refs=[]
def foot_bolts(xx,yy,zmin,zlen):
 return [cyl((xx+dx,yy+dy,zmin),FOOT_BOLT_D,zlen) for dx in [-FOOT_OFF,FOOT_OFF] for dy in [-FOOT_OFF,FOOT_OFF]]
# V1.18: centered tool-free M6x30 joining sections.  Each 45 mm module
# contains a metal M6x30 bolt pointing UP and a captive M6 hex nut underneath.
# The bolt enters from the +X SIDE through a temporary keyway. A torque-keyed
# hexagonal locking sleeve then closes the entire opening and snaps to the core.
# No tools are needed to join/remove modules once their bolt/sleeve are fitted.
M6_D=P['foot_m6_bore_mm']
M6_SLOT_W=P['foot_m6_nut_slot_width_mm'];M6_SLOT_H=P['foot_m6_nut_slot_height_mm']
M6_NUT_D=P['foot_m6_nut_across_corners_mm'];M6_HEAD_D=P['foot_m6_bolt_head_clearance_mm']
M6_WEB=P['foot_m6_nut_bottom_web_mm'];SEC_H=P['foot_section_height_mm']
BODY_D=P['foot_section_body_diameter_mm'];SLEEVE_IN=P['foot_section_sleeve_inner_diameter_mm']
SLEEVE_OUT=P['foot_section_outer_diameter_mm'];RIM_H=P['foot_section_rim_height_mm']
HEAD_BASE=P['foot_m6_head_pocket_base_mm'];HEAD_H=P['foot_m6_head_pocket_height_mm']
HEAD_ENTRY_W=P['foot_m6_head_side_entry_width_mm']
def hex_prism(cx,cy,diam,z0,height,phase_deg=0):
 r=diam/2
 profile=[(cx+r*math.cos(math.radians(phase_deg+60*i)),cy+r*math.sin(math.radians(phase_deg+60*i))) for i in range(6)]
 return cq.Workplane('XY').polyline(profile).close().extrude(height).translate((0,0,z0))
def m6_hex(cx,cy,z0,h=M6_SLOT_H,direction='y'):
 return hex_prism(cx,cy,M6_NUT_D,z0,h,30 if direction=='y' else 0)
def capture_m6(sh,cx,cy,base,sign=-1,direction='y'):
 """Standard M6 horizontal hex pocket; separate press-in keeper closes its mouth."""
 z0=base+M6_WEB
 if direction=='x':
  channel=box(cx,cy-M6_SLOT_W/2,z0,36,M6_SLOT_W,M6_SLOT_H)
 else:
  channel=box(cx-M6_SLOT_W/2,cy if sign==1 else cy-36,z0,M6_SLOT_W,36,M6_SLOT_H)
 return sh.cut(m6_hex(cx,cy,z0,direction=direction)).cut(channel)

def keeper_with_catches(sh,cx,cy,bottom,metric):
 """An optional removable PETG nut-door with two cantilever catches.

 Spring barbs snap into matching side pockets; the metal nut carries the
 fastener load, not the printed keeper. All keepers insert along +Y and
 can be removed at a fingernail relief in the outside face.
 """
 assert metric in ('m6','m8')
 w=M6_SLOT_W if metric=='m6' else P['foot_m8_slot_width_mm']
 h=M6_SLOT_H if metric=='m6' else P['foot_m8_nut_height_mm']
 z0=bottom+(M6_WEB if metric=='m6' else P['foot_m8_nut_base_web_mm'])
 # Align with cylindrical 54 mm base, leaving 0.3 mm horizontal/0.25 vertical
 # clearance. The nose rests ~0.35 mm from the edge of the seated metal nut.
 tail=-26.25 if metric=='m6' else -26.0
 nose=-6.45 if metric=='m6' else -8.1
 width=w-P['foot_m6_keeper_clearance_width_mm']
 height=h-P['foot_m6_keeper_clearance_height_mm']
 zplug=z0+P['foot_m6_keeper_clearance_height_mm']/2
 keeper=box(cx-width/2,cy+tail,zplug,width,nose-tail,height)
 # Two long slits make the last 1.35 mm of each side into a compliant beam.
 beam=P['foot_keeper_spring_beam_width_mm']; slit=P['foot_keeper_spring_slot_width_mm']
 for sign in (-1,1):
  slit_cx=cx+sign*(width/2-beam-slit/2)
  keeper=keeper.cut(box(slit_cx-slit/2,cy+tail-.1,zplug-.1,slit,14.0,height+.2))
 # Matching pockets set BARB clearance when the plug reaches final position.
 # They lie behind the circular outer wall and don't contact the seated nut.
 catch_y=cy-23.25;length=P['foot_keeper_barb_length_mm']
 for sign in (-1,1):
  wall_x=cx+sign*w/2
  depth=P['foot_m6_keeper_recess_depth_mm'] if metric=='m6' else P['foot_m8_keeper_recess_depth_mm']
  pocket_x=wall_x-.06 if sign>0 else wall_x-depth+.06
  recess=box(pocket_x,catch_y-length/2-.35,z0+.55,depth,length+.7,h-1.1)
  sh=sh.cut(recess)
  projection=P['foot_keeper_barb_projection_mm']
  # Actual installed barb is entirely in the recess, NOT interpenetrating.
  v=[(cx+sign*(width/2-.12),catch_y-length/2),
     (cx+sign*(w/2+projection),catch_y-length/4),
     (cx+sign*(w/2+projection),catch_y+length/4),
     (cx+sign*(width/2-.12),catch_y+length/2)]
  barb=cq.Workplane('XY').polyline(v).close().extrude(min(h-1.5,2.2)).translate((0,0,z0+(h-min(h-1.5,2.2))/2))
  keeper=keeper.union(barb)
 # Small outer-edge fingernail relief, within the exposed plug face.
 keeper=keeper.cut(box(cx-1.1,cy+tail-.1,zplug+height-1.2,2.2,2.3,1.3))
 return sh,keeper

def m6_shaft(sh,cx,cy,zmin,length):return sh.cut(cyl((cx,cy,zmin-.1),M6_D,length+.2))
def bolt_core_and_sleeve(cx,cy,bottom,terminal=False):
 """Two interlocked prints. Bolt is inserted from the side, sleeve traps head.
 Hex outside/inside interface transmits turning torque without relying on glue.
 Retention nibs with sleeve relief slots must be PETG-fit-tested physically.
 """
 h=P['foot_terminal_height_mm'] if terminal else SEC_H
 head_base=HEAD_BASE+(h-SEC_H)
 top=bottom+h
 core=cyl((cx,cy,bottom),SLEEVE_OUT,RIM_H).union(hex_prism(cx,cy,BODY_D,bottom+RIM_H,h-RIM_H))
 # Head socket 18.5..24.5 above bottom, with a full-depth +X loading path.
 # An M6x30 bolt seats against the roof and extends 9.5 mm above the top.
 core=core.cut(hex_prism(cx,cy,12.6,bottom+head_base,HEAD_H,0))
 core=m6_shaft(core,cx,cy,bottom+head_base,h-head_base)
 core=core.cut(box(cx,cy-HEAD_ENTRY_W/2,bottom+head_base,30,HEAD_ENTRY_W,HEAD_H+.02))
 core=core.cut(box(cx,cy-M6_D/2-.15,bottom+head_base+HEAD_H-.01,30,M6_D+.3,h-head_base-HEAD_H+.2))
 # Lower M6 metal nut receives the next screw-on unit or the swivel pad.
 if terminal:
  # M8 foot male stud fits the captive M8 female nut at the BOTTOM ONLY.
  # A blind 21 mm bore prevents a long M8 stud from approaching the M6 head.
  m8_z=bottom+P['foot_m8_nut_base_web_mm']
  m8_nut=hex_prism(cx,cy,P['foot_m8_nut_across_corners_mm'],m8_z,P['foot_m8_nut_height_mm'],30)
  m8_slot=box(cx-P['foot_m8_slot_width_mm']/2,cy-36,m8_z,P['foot_m8_slot_width_mm'],36,P['foot_m8_nut_height_mm'])
  m8_bore=cyl((cx,cy,bottom-.1),P['foot_m8_bore_diameter_mm'],P['foot_m8_stud_max_insertion_mm']+.1)
  core=core.cut(m8_nut).cut(m8_slot).cut(m8_bore)
 else:
  core=capture_m6(core,cx,cy,bottom,-1)
  # Fix V1.17: the M6 female pocket had no entry bore through its 3 mm base.
  # Bore now runs up through the 6 mm nut and stops below the bolt head.
  core=m6_shaft(core,cx,cy,bottom,P['foot_m6_entry_bore_depth_mm'])
 core,nut_keeper=keeper_with_catches(core,cx,cy,bottom,'m8' if terminal else 'm6')
 # A thin snap tooth on both opposing hexagonal flats retains the sleeve.
 r_flat=BODY_D*math.cos(math.pi/6)/2
 nib_rad=P['foot_sleeve_snap_nib_radial_mm']
 for sign in (-1,1):
  start_y=cy+sign*(r_flat-.1)
  nib_y=start_y if sign==1 else start_y-(nib_rad+.2)
  core=core.union(box(cx-3,nib_y,bottom+12,6,nib_rad+.2,3))
 # Sleeve is a single annular print with matching hexagonal torque key.
 sleeve=cyl((cx,cy,bottom+RIM_H),SLEEVE_OUT,h-RIM_H)
 sleeve=sleeve.cut(hex_prism(cx,cy,SLEEVE_IN,bottom+RIM_H-.1,h-RIM_H+.2))
 for sign in (-1,1):
  # No interference at the resting position: local recess captures snap nib.
  if sign==1:yg=cy+SLEEVE_IN*math.cos(math.pi/6)/2-.02
  else:yg=cy-SLEEVE_IN*math.cos(math.pi/6)/2-1.6
  sleeve=sleeve.cut(box(cx-3.3,yg,bottom+11.9,6.6,1.7,3.3))
  # Two relief kerfs allow the little locking tongue to deflect on assembly.
  for sx in (-5.7,5.7):
   yy=cy+16.5 if sign==1 else cy-28
   sleeve=sleeve.cut(box(cx+sx-.45,yy,bottom+RIM_H-.1,.9,11.5,8.5))
 # The head's side channel must be CLOSED also near its axis: otherwise
 # a bolt head can slide sideways within a wide slot and start spinning.
 # A removable, full-height stepped key fills the opening after loading.
 # The snap sleeve traps the key; this is a one-time tool-free preload.
 # V1.18: user printed V1.17 and confirmed the stepped insert sits too far
 # from the metal bolt head, letting the bolt wobble unless hand-pushed.
 # Advance only the HEAD-contact face 0.55 mm (6.65 -> 6.10 mm from axis).
 # This leaves ~0.33 mm clearance to a nominal M6 10 mm AF hex head's
 # 5.77 mm circumradius; exact head dimensions require print-first testing.
 head_contact=P['foot_m6_key_head_face_offset_mm']
 head_polygon=[(cx+head_contact,cy-6.1),(cx+18.3,cy-6.1),(cx+21.8,cy),(cx+18.3,cy+6.1),(cx+head_contact,cy+6.1)]
 shaft_polygon=[(cx+3.6,cy-3.25),(cx+19.95,cy-3.25),(cx+21.8,cy),(cx+19.95,cy+3.25),(cx+3.6,cy+3.25)]
 head_key=cq.Workplane('XY').polyline(head_polygon).close().extrude(HEAD_H).translate((0,0,bottom+head_base))
 shaft_key=cq.Workplane('XY').polyline(shaft_polygon).close().extrude(h-head_base-HEAD_H).translate((0,0,bottom+head_base+HEAD_H))
 keeper=head_key.union(shaft_key)
 return core,sleeve,keeper,nut_keeper
# Two lift-out bottom panels; rear panel also acts as the PC tray.
# V1.18: original D-shaped ribs bear on intact floor with no separate lug.
# A pair of through-holes accepts removable M3 screws from the underside.
for region in ['front','rear']:
 ya=4.3 if region=='front' else SPLIT+G/2
 yb=SPLIT-G/2 if region=='front' else L-4.3
 sh=box(4.3,ya,0,W-8.6,yb-ya,4)
 for xx in [12,W-12]:
  for yy in shelf_ys:sh=sh.cut(cyl((xx,yy,-1),3.4,6))
 if region=='front':
  for side in ['left','right']:
   xx=FAST_X if side=='left' else W-FAST_X
   sh=sh.cut(cyl((xx,FAST_Y,-1),P['flipper_anchor_bore_mm'],6))
 for _,station_region,xx,yy in FOOT_STATIONS:
  if station_region==region:
   for bore in foot_bolts(xx,yy,-1,6):sh=sh.cut(bore)
 if region=='rear':
  for xx in [25,230]:
   for yy in [250,400]:sh=sh.cut(box(xx,yy,-1,6,20,6))
 add('bottom_'+region,sh,'floor')
# V1.18: keep all four existing M4 load-spreading receiver mounts.
# Center the receiver M6 nut so round sections can actually be twisted onto it.
for side,region,xx,yy in FOOT_STATIONS:
 label=f'{side}_{region}'
 backing=cyl((xx,yy,4),50,5)
 for hole in foot_bolts(xx,yy,3.5,6):backing=backing.cut(hole)
 for dx in [-FOOT_OFF,FOOT_OFF]:
  for dy in [-FOOT_OFF,FOOT_OFF]:
   backing=backing.cut(cq.Workplane('XY').center(xx+dx,yy+dy).polygon(6,8.4).extrude(3.4).translate((0,0,5.65)))
 add('foot_backing_'+label,backing,'mount','flat')
 boss_bottom=-20
 receiver=cyl((xx,yy,-8),50,8).union(cyl((xx,yy,boss_bottom),P['foot_mount_boss_diameter_mm'],12))
 for hole in foot_bolts(xx,yy,-8.1,8.2):receiver=receiver.cut(hole)
 for dx in [-FOOT_OFF,FOOT_OFF]:
  for dy in [-FOOT_OFF,FOOT_OFF]:
   bx,by=xx+dx,yy+dy
   receiver=receiver.cut(cyl((bx,by,-8.01),8.4,4.6))
   receiver=receiver.cut(cyl((bx,by,boss_bottom-.1),P['foot_m4_boss_access_mm'],12.2))
 receiver=m6_shaft(receiver,xx,yy,boss_bottom,12)
 receiver=capture_m6(receiver,xx,yy,boss_bottom,-1)
 receiver,nut_keeper=keeper_with_catches(receiver,xx,yy,boss_bottom,'m6')
 add('foot_receiver_'+label,receiver,'mount','flip')
 add('foot_m6_nut_clip_receiver_'+label,nut_keeper,'joint','flat')
 current_bottom=boss_bottom
 heights=P['foot_front_extension_mm'] if region=='front' else P['foot_rear_extension_mm']
 for i,section in enumerate(heights):
  # Only the final, lowest section has an M8 female nut for the rubber foot.
  is_terminal=i==len(heights)-1
  h=P['foot_terminal_height_mm'] if is_terminal else SEC_H
  assert section==SEC_H,('logical step remains 45 mm',label,section)
  bottom=current_bottom-h
  core,sleeve,keeper,nut_keeper=bolt_core_and_sleeve(xx,yy,bottom,terminal=is_terminal)
  if is_terminal:
   add(f'foot_m8_terminal_core_{label}_55mm',core,'feet','flat')
   add(f'foot_m8_terminal_sleeve_{label}_55mm',sleeve,'mount','flat')
   add(f'foot_m8_terminal_bolt_key_{label}_55mm',keeper,'joint','side')
   add(f'foot_m8_nut_clip_terminal_{label}',nut_keeper,'joint','flat')
  else:
   add(f'foot_twist_core_{label}_{i+1}_45mm',core,'feet','flat')
   add(f'foot_lock_sleeve_{label}_{i+1}_45mm',sleeve,'mount','flat')
   add(f'foot_bolt_key_{label}_{i+1}_45mm',keeper,'joint','side')
   add(f'foot_m6_nut_clip_upper_{label}_{i+1}_45mm',nut_keeper,'joint','flat')
  current_bottom=bottom
 # Purchased M8 swivel pad: visual reference only, 20 mm stem engagement.
 # Its actual stem length must be checked against the 21 mm blind M8 bore.
 bottom=current_bottom
 stem=cyl((xx,yy,bottom-20),P['foot_rubber_stem_diameter_mm'],40)
 pivot=cyl((xx,yy,bottom-22),12,6)
 pad=cyl((xx,yy,bottom-26),P['foot_rubber_reference_diameter_mm'],7)
 foot_refs.append((f'REFERENCE_swivel_rubber_pad_{label}',stem.union(pivot).union(pad)))
 assembly.add(foot_refs[-1][1],name=foot_refs[-1][0],color=cq.Color(.06,.07,.08,.7))
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
# Keep an exact before-shape for local difference and fit checks.
sh=sh.union(wedge(MR-12,Y0-4.5,12,4,z(Y0)-18,2))
for xx in [10,W-10]:
 for yy in [25,50]:sh=sh.cut(topbore(xx,yy))
front_before['front_cable_lid']=sh
sh=lid_local_rounded.rotate((0,0,0),(1,0,0),A).translate((0,0,H+1))
sh=sh.union(wedge(MR-12,Y0-4.5,12,4,z(Y0)-18,2))
for xx in [10,W-10]:
 for yy in [25,50]:sh=sh.cut(topbore(xx,yy))
add('front_cable_lid',sh,'lid','top')
# Rear access hatch V1.7: lift-off cover, two plain cylindrical locating pegs.
# Existing screw positions become clearance holes (Ø6.4) instead of M3 bores.
# Preserve the original B1 outline to clear the left top fastener block.
hy=Y1+4; hx=18; hw=80; hd=35
peg_xs=[12,104]; peg_y=hy+8
peg_d=6.0; hole_d=6.4; peg_depth=4.4
sh=topplate(0,Y1-1,W,L-Y1+1)
cut=box(hx,hy/C,-3,hw,hd/C,12).rotate((0,0,0),(1,0,0),A).translate((0,0,H+1))
sh=sh.cut(cut)
sh=sh.union(wedge(MR-12,Y1+.5,12,4,z(Y1)-18,2))
for xx in [10,W-10]:sh=sh.cut(topbore(xx,450))
for xx in peg_xs:sh=sh.cut(topbore(xx,peg_y,hole_d))
add('rear_control_deck',sh,'lid','top')

# Hatch lies flat on the 4 mm deck; unlatched pegs simply locate it, not lock it.
# Exposed front edge has a small semicircular finger notch for tool-free removal.
sh=topplate(8,hy-7,100,hd+14,3).translate((0,-4*math.sin(math.radians(A)),4*C))
# Notch cut along the panel normal; center on the forward edge (radius 5 mm).
front_y=hy-7
sh=sh.cut(cyl((58,front_y-8*S,z(front_y)+1+8*C),10,16,(0,S,-C)))
# Leave head clearance for the existing left deck fastener beneath the cover.
sh=sh.cut(topbore(10,450,7))
for xx in peg_xs:
 base=(xx,peg_y-4*S,z(peg_y)+1+4*C)
 # Short round posts, extending below the deck by only 0.4 mm.
 sh=sh.union(cyl(base,peg_d,peg_depth,(0,S,-C)))
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
 sh=front_before['left_front_wall'] if region=='front' else next(p['shape'] for p in parts if p['name']=='left_'+region+'_wall')
 clip=box(-1,203,12,6,64,92)
 test('joint_'+region+'_wall',sh.intersect(clip),'side',note='Print with outer wall face down; slide tongue into slot, attach splice with M3 bolts.')
sh=next(p['shape'] for p in parts if p['name']=='splice_left')
test('joint_splice_plate',sh,'side',note='Use six M3 × 16 screws and M3 nuts with joint samples; verify washer stack and through-thread engagement.')
# Small print-first coupons for checking two-peg friction and actual printed tolerances.
# These match the full panel's extrusion/normal direction without modifying it.
fit_hole=box(0,0,0,22,22,4).cut(cyl((11,11,-1),hole_d,6))
test('hatch_hole_6p4mm',fit_hole,note='Ø6.4 mm through-hole. Pair with the Ø6.0 mm peg sample; 0.2 mm radial clearance.')
fit_peg=box(0,0,0,22,22,3).union(cyl((11,11,3),peg_d,peg_depth))
test('hatch_peg_6mm',fit_peg.rotate((0,0,0),(1,0,0),180),note='Ø6.0 mm x 4.4 mm straight peg, printed protrusion up. Test repeatedly for easy insertion/removal.')
# V1.18 switch-only coupons reproduce the wall's exact well and clip plate.
# Keep the wall's outside-down orientation so this also tests recess bridging.
nudge_samples={}
for d in [14.0,14.1,14.2]:
 sample=box(0,NY-15,BZ-15,T,30,30).cut(nudge_cuts('left',d))
 nudge_samples[d]=sample
 name='nudge_switch_fit' if abs(d-P['nudge_cutout_mm'])<.001 else 'nudge_mx_'+format(d,'.1f').replace('.','p')
 test(name,sample,'side_outer_left',note=f'30 x 30 x 4 mm switch-only sample: {d:.1f} mm aperture, 2.5 mm recessed mounting face, 1.5 mm snap plate, 18 mm floor / 23 mm outer mouth. Same cut geometry and outside-down orientation as the full wall. Test actual switch clips and full keycap travel; the {(WELL_FLOOR-d)/2:.2f} mm mounting ledge may need tuned bridging or local support.')
left_front=next(p['shape'] for p in parts if p['name']=='left_front_wall')
sample=left_front.intersect(box(-.1,76,0,14,78,57))
test('flipper_nudge_wall_sample',sample,'side_outer_left',note='Exact left wall section including the V1.18 floor-seated M3 flipper anchor: 28 mm flipper bore, 8 mm total thickness; nudge remains 33 mm rearward at the same height, now with 2.5 mm recessed seat / 1.5 mm plate / 14.1 mm aperture / 18-to-23 mm tapered well. Pair with the unchanged V1.9 floor sample; verify barrel thread, retaining nut, switch clips, full cap travel, body and wiring.')
front_floor=next(p['shape'] for p in parts if p['name']=='bottom_front')
floor_sample=front_floor.intersect(box(4.3,76,0,20,78,4))
test('flipper_floor_anchor_sample',floor_sample,note='Exact 4 mm front-floor section with underside M3 screw access. Pair with flipper_nudge_wall_sample in assembled orientation; the rib rests on top without floor relief. Test the M3 metal nut in side slot before full-size printing.')

# V1.18 exact corner crops. These three skin samples reuse two unchanged
# mounting parts so the 1 mm lid gap is registered by real support geometry.
CORNER_MIN=[0,-1,P['front_corner_sample_bottom_z_mm']]
CORNER_MAX=[P['front_corner_sample_span_mm'],P['front_corner_sample_span_mm'],100]
corner_clip=box(*CORNER_MIN,*[b-a for a,b in zip(CORNER_MIN,CORNER_MAX)])
corner_specs=[
 ('front_corner_wall_fit','left_front_wall','side_outer_left'),
 ('front_corner_panel_fit','front_button_panel','end'),
 ('front_corner_lid_fit','front_cable_lid','top')]
corner_samples={};corner_before_samples={}
for sample_name,part_name,mode in corner_specs:
 sh=next(p['shape'] for p in parts if p['name']==part_name).intersect(corner_clip)
 corner_samples[sample_name]=sh
 corner_before_samples[sample_name]=front_before[part_name].intersect(corner_clip)
 test(sample_name,sh,mode,note='Exact front-left corner crop of '+part_name+'. Assemble with the other two corner samples, original corner_left_front_56 and top_block_left_25. Align crop bottoms on a flat surface, fasten the corner bracket and top block, then screw the lid to the top block. The original 1 mm lid-to-wall vertical clearance is retained. Outside/show face prints down; artificial crop edges are not comfort edges.')
 tests[-1].update(source_part=part_name,assembly_crop_mm={'min':CORNER_MIN,'max':CORNER_MAX})
corner_mount_names=['corner_left_front_56','top_block_left_25']
def corner_mesh_payload(before=False):
 rows=[]
 for sample_name,part_name,mode in corner_specs:
  sh=(corner_before_samples if before else corner_samples)[sample_name]
  vv,ff=sh.val().copy().tessellate(.02,.07)
  rows.append({'name':sample_name,'source_part':part_name,'kind':'lid' if part_name=='front_cable_lid' else 'wall','v':[[v.x,v.y,v.z] for v in vv],'f':[list(f) for f in ff]})
 for name in corner_mount_names:
  p=next(p for p in parts if p['name']==name);vv,ff=p['shape'].val().copy().tessellate(.03,.08)
  rows.append({'name':name,'source_part':name,'kind':p['kind'],'v':[[v.x,v.y,v.z] for v in vv],'f':[list(f) for f in ff]})
 return rows
(OUT/'front_corner_preview_meshes.json').write_text(json.dumps(corner_mesh_payload()))
(OUT/'front_corner_before_meshes.json').write_text(json.dumps(corner_mesh_payload(True)))
corner_kit={
 'revision':'Prototype V1.18','units':'mm',
 'new_sample_count':3,'kit_stl_count_including_reused_mounts':5,
 'samples':[{'file':n+'.stl','source_part':p,'print_mode':m,'crop_min_mm':CORNER_MIN,'crop_max_mm':CORNER_MAX} for n,p,m in corner_specs],
 'reused_mounts':[n+'.stl' for n in corner_mount_names],
 'lid_vertical_clearance_mm':1.0,
 'print_orientation':'All three skin samples outside/show face down, as exported. Reused mounting parts retain their original print orientations.',
 'assembly':['Stand the wall and front-panel crops with their Z40 crop bottoms on the same flat surface. The front-panel crop goes inside the wall at X = 4; the front faces meet flush.',
 'Install corner_left_front_56 at the inside corner with the two original M3 holes at Y14/Z56 in the wall and X14/Z56 in the front panel. Use the same captive nuts and suitable original M3 fasteners.',
 'Attach top_block_left_25 to the side-wall sample through its Y31/Z71.408 hole. Its sloping top establishes the original lid height.',
 'Lay the lid on the top block and fasten through the X10/Y25 hole. Hold it aligned to the original outside outline while tightening gently. Do not force the lid down onto the wall/panel tops; the design has 1 mm vertical clearance.',
 'Feel the real exterior front corner and check the printed bevel/curve and alignment. The sample cut boundaries are artificial and remain square. Physical fit and comfort are not yet verified.'],
 'edge_treatment':{
 'maximum_treatment_depth_mm':EDGE_D,'blend_radius_mm':EDGE_R,
 'wall_front_corner':{'inward_depth_mm':EDGE_D,'outer_face_offset_mm':EDGE_A,'blend_radius_mm':EDGE_R,'first_segment_degrees_from_print_vertical':45},
 'front_panel_upper_edge':{'inward_y_depth_mm':EDGE_D,'front_face_vertical_offset_mm':H-LIP_START_Z,'blend_radius_mm':EDGE_R,'initial_dZ_dY':1,'final_dZ_dY':S},
 'lid_upper_rim':{'inward_normal_depth_mm':LID_D,'top_face_offset_mm':LID_A,'blend_radius_mm':LID_R,'side_fade_start_y_mm':P['lid_side_fade_start_y_mm'],'side_fade_end_y_mm':P['lid_side_fade_end_y_mm']},
 'changed_parts':['left_front_wall','right_front_wall','front_button_panel','front_cable_lid'],
 'flat_joint_planes_and_mounting_axes_retained':True,
 'new_edge_treatment_support_free_printing_physically_verified':False},
 'preview_meshes_assembly_coordinates':'front_corner_preview_meshes.json','before_preview_meshes_assembly_coordinates':'front_corner_before_meshes.json'}
(OUT/'front_corner_kit.json').write_text(json.dumps(corner_kit,indent=2))

# Monitor-reference envelopes, for review only. No active-screen dimensions are assumed.
reference=wedge(ML,Y0,P['monitor_width'],Y1-Y0,z(Y0)-12,0) # use uniform 12 mm envelope following slope instead below
reference=cq.Workplane('YZ').polyline([(Y0,z(Y0)-12),(Y1,z(Y1)-12),(Y1,z(Y1)),(Y0,z(Y0))]).close().extrude(P['monitor_width']).translate((ML,0,0))
assembly.add(reference,name='REFERENCE_monitor_12mm_envelope',color=cq.Color(.2,.65,.85,.22))
pc=box(35,240,13,190,190,45)
assembly.add(pc,name='REFERENCE_PC_allowance_ports_face_front',color=cq.Color(.25,.75,.5,.25))
# Reserved spaces are separate reference solids and are checked against printed geometry.
keepouts=[('PC allowance',pc)]
for xx in [110,160,210]:keepouts.append((f'front button {xx}',box(xx-20,4.2,6,40,P['button_inward_clearance'],40)))
# Replace V1.7's 40x40 box beginning at x4.2: its first 4 mm intentionally
# becomes reinforcement. Explicit barrel / nut / rear-body allowances are checked.
# These are assumed hardware dimensions, not measured manufacturer geometry.
control_hardware={}
for side in ['left','right']:
 barrel=cyl((-.1,FY,BZ),27.8,20.1,(1,0,0))
 nut=cyl((LOCAL_T+.2,FY,BZ),40,5,(1,0,0))
 body=box(LOCAL_T+5.2,FY-20,BZ-20,4.2+P['button_inward_clearance']-(LOCAL_T+5.2),40,40)
 flipper_shapes=[(side+' flipper barrel D27.8',mirror_side(barrel,side)),(side+' flipper nut D40 x5',mirror_side(nut,side)),(side+' flipper body and wiring 40x40',mirror_side(body,side))]
 # Translate the prior stem/body allowances inward by exactly the seat setback.
 # The upper housing tests entry into the well; it is a clearance assumption,
 # not a measured switch or keycap. No keycap travel claim follows from it.
 nudge_stem=box(-.1,NY-7,BZ-7,1.7,14,14).translate((RECESS,0,0))
 nudge_body=box(1.6,NY-8.2,BZ-8.2,18.4,16.4,16.4).translate((RECESS,0,0))
 nudge_upper=box(RECESS-6,NY-UPPER_HOUSING/2,BZ-UPPER_HOUSING/2,6,UPPER_HOUSING,UPPER_HOUSING)
 nudge_shapes=[(side+' assumed MX plate stem 14.0',mirror_side(nudge_stem,side)),(side+' assumed MX body clip and wiring allowance',mirror_side(nudge_body,side)),(side+' assumed MX upper housing 16.4',mirror_side(nudge_upper,side))]
 keepouts.extend(flipper_shapes+nudge_shapes)
 control_hardware[side]={'flipper':flipper_shapes,'nudge':nudge_shapes}
fan=box(FX-P['fan_case_mm']/2,L-T-P['fan_depth_mm'],FZ-P['fan_case_mm']/2,P['fan_case_mm'],P['fan_depth_mm'],P['fan_case_mm'])
fan_padded=box(FX-P['fan_case_mm']/2,L-T-P['fan_padded_depth_mm'],FZ-P['fan_case_mm']/2,P['fan_case_mm'],P['fan_padded_depth_mm'],P['fan_case_mm'])
keepouts.append(('NONPRINTED fan case 120x120x25',fan))
keepouts.append(('NONPRINTED fan optional 27mm installed depth',fan_padded))
cover=cq.Workplane('YZ').polyline([(Y0,z(Y0)-P['cover_total_depth_allowance']),(Y1,z(Y1)-P['cover_total_depth_allowance']),(Y1,z(Y1)-7),(Y0,z(Y0)-7)]).close().extrude(P['monitor_width']-10).translate((ML+5,0,0))
keepouts.append(('central folded cover reserve',cover))
keepouts.append(('USB encoder allowance',box(100,140,13,70,50,12)))
for idx,(label,sh) in enumerate(keepouts[1:]):assembly.add(sh,name='REFERENCE_'+str(idx)+'_'+label.replace(' ','_'),color=cq.Color(.95,.60,.15,.2))
# Do not export reference objects as STLs.
print('All printed geometry and coupons built; exporting STEP',flush=True)
assembly.save(str(OUT/'mini_vpin_assembly.step'))
# Mesh source retained for exact CAD previews.
manifest={'revision':'Prototype V1.18','units':'mm','printer_build_mm':[325,325,315],'brim_margin_each_side_mm':8,'parameters':P,'parts':[{k:v for k,v in p.items() if k not in ['shape','print_shape']} for p in parts],'tests':[{k:v for k,v in t.items() if k!='shape'} for t in tests]}
(OUT/'parts_manifest.json').write_text(json.dumps(manifest,indent=2))
with (OUT/'print_inventory.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['part','print_x_mm','print_y_mm','print_z_mm','orientation','status'])
 for p in parts:w.writerow([p['name'],*p['bounds'],p['mode'],'PROTOTYPE - FIT TEST FIRST'])
# Save assembly placement and meshes for renderer, plus test geometry.
mesh=[]
for p in parts:
 verts,faces=p['shape'].val().tessellate(.03,.08) if p['name'] in front_before else p['shape'].val().tessellate(.3,.2)
 mesh.append({'name':p['name'],'kind':p['kind'],'v':[[v.x,v.y,v.z] for v in verts],'f':[list(f) for f in faces]})
# Reference-only swivel feet appear in Studio but are excluded from print STLs.
for name,shape in foot_refs:
 verts,faces=shape.val().tessellate(.35,.2)
 mesh.append({'name':name,'kind':'rubber','v':[[v.x,v.y,v.z] for v in verts],'f':[list(f) for f in faces]})
(OUT/'preview_meshes.json').write_text(json.dumps(mesh))
print('STEP and meshes exported; checking reserved spaces and solid interferences',flush=True)
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
# Check different controls against each other, not just hardware versus plastic.
# Components of one switch intentionally overlap and are not separate controls.
control_hardware_issues=[]; control_clearance={}
for side,groups in control_hardware.items():
 distances=[]
 for flipper_label,flipper_shape in groups['flipper']:
  for nudge_label,nudge_shape in groups['nudge']:
   hit=flipper_shape.intersect(nudge_shape)
   overlap=sum(v.Volume() for v in hit.solids().vals())
   if overlap>.05:control_hardware_issues.append({'flipper':flipper_label,'nudge':nudge_label,'volume_mm3':round(overlap,4)})
   distances.append(flipper_shape.val().distance(nudge_shape.val()))
 control_clearance[side]=min(distances)
(OUT/'geometry_checks.json').write_text(json.dumps({'all_parts_valid':True,'all_parts_single_solid':True,'all_parts_fit_with_8mm_brim':True,'interferences':issues,'reserved_space_interferences':keepout_issues,'control_hardware_interferences':control_hardware_issues,'flipper_nudge_hardware_min_clearance_mm':control_clearance},indent=2))
# M6 mechanical assembly calculation: 20 + 30 or 40 + 50 mm bolts,
# with 6.5 mm bolt-head recess. Printed clearances are nominal, not fitted.
assert P['foot_front_extension_mm']==[45] and P['foot_rear_extension_mm']==[45,45]
assert P['foot_m6_bolt_length_mm']==30 and SEC_H==45
assert abs((HEAD_BASE+HEAD_H)+P['foot_m6_bolt_length_mm']-SEC_H-P['foot_m6_bolt_exposed_mm'])<.001
assert M6_WEB+M6_SLOT_H+7<=HEAD_BASE, 'Metal nut must stay separated from bolt head'
assert P['foot_terminal_height_mm']==55 and P['foot_rubber_stem_diameter_mm']==8
assert P['foot_m8_slot_width_mm']-P['foot_m8_nut_across_corners_mm']*math.cos(math.pi/6)>=.4, 'M8 side-entry slot too narrow to slide standard hex nut'
assert P['foot_m8_stud_max_insertion_mm']+6.5 < HEAD_BASE+(P['foot_terminal_height_mm']-SEC_H)
# Every M6 upper section must accept the 9.5 mm projecting bolt from below.
for side,xx in [('left',FOOT_X[0]),('right',FOOT_X[1])]:
 name=f'foot_twist_core_{side}_rear_1_45mm'
 sh=next(p['shape'] for p in parts if p['name']==name)
 bot=sh.val().BoundingBox().zmin
 tool=cyl((xx,FOOT_Y['rear'],bot-.02),P['foot_m6_bore_mm']-.2,11.15)
 assert sh.intersect(tool).val().Volume()<.001,('45mm M6 female bore blocked',name)
 stop=cyl((xx,FOOT_Y['rear'],bot+12.3),P['foot_m6_bore_mm']-.2,1.0)
 assert sh.intersect(stop).val().Volume()>8,('M6 bore missing stop below bolt head',name)
for side,region,xx,yy in FOOT_STATIONS:
 name=f'foot_receiver_{side}_{region}'
 sh=next(p['shape'] for p in parts if p['name']==name)
 tool=cyl((xx,yy,-20.05),P['foot_m6_bore_mm']-.2,11.1)
 assert sh.intersect(tool).val().Volume()<.001,('receiver lower M6 bore blocked',name)
# Key contact face revised by 0.55 mm versus V1.17; no bolt binding claim.
assert abs(P['foot_m6_key_head_face_offset_mm']-6.1)<1e-9
assert abs(6.65-P['foot_m6_key_head_face_offset_mm']-.55)<1e-9
nominal_hex_radius=P['foot_m6_key_head_reference_nominal_af_mm']/math.sqrt(3)
assert .25<P['foot_m6_key_head_face_offset_mm']-nominal_hex_radius<.45, 'Nominal M6 head gap outside targeted range'
# Sample a narrow horizontal section through the head key (not shaft), and
# verify that the new face occupies material at x=6.10 that V1.17 did not.
key=next(p['shape'] for p in parts if p['name']=='foot_bolt_key_left_rear_1_45mm')
key_z=key.val().BoundingBox().zmin+1.25
face_probe=box(FOOT_X[0]+6.12,FOOT_Y['rear']-.05,key_z,.04,.10,.10)
assert key.intersect(face_probe).val().Volume()>.0003,'Closer key head contact face missing'
# Existing two sizes of nut clips must not touch any threaded fastener axis;
# their final nose is outside each nut hex's outer perimeter.
for p in parts:
 if p['name'].startswith('foot_m6_nut_clip_'):
  assert p['shape'].val().isValid() and p['volume']>20
 if p['name'].startswith('foot_m8_nut_clip_'):
  assert p['shape'].val().isValid() and p['volume']>20

# All four terminal sections have an M8 side-entry pocket and a BLIND stud bore.
for side,region,xx,yy in FOOT_STATIONS:
  label=f'{side}_{region}'
  name=f'foot_m8_terminal_core_{label}_55mm'
  sh=next(part['shape'] for part in parts if part['name']==name)
  bottom=sh.val().BoundingBox().zmin
  pocket=hex_prism(xx,yy,P['foot_m8_nut_across_corners_mm']-.1,bottom+P['foot_m8_nut_base_web_mm']+.05,P['foot_m8_nut_height_mm']-.1,30)
  assert sh.intersect(pocket).val().Volume()<.001,('M8 nut pocket obstructed',name)
  blind=cyl((xx,yy,bottom),P['foot_m8_bore_diameter_mm']-.2,P['foot_m8_stud_max_insertion_mm']-.05)
  assert sh.intersect(blind).val().Volume()<.001,('M8 foot bore blocked',name)
  roof=cyl((xx,yy,bottom+P['foot_m8_stud_max_insertion_mm']+.6),4.0,1.0)
  assert sh.intersect(roof).val().Volume()>9.5,('missing blind stud stop',name)

# Exact-CAD V1.18 feature checks. Small-volume probes measure the resulting solids;
# nominal dimensions alone do not establish that a subtract/union succeeded.
def volume(sh):return sum(v.Volume() for v in sh.solids().vals())
def intersect_volume(a,b):return volume(a.intersect(b))
features=[]
def check(name,measured,expected,tolerance=.001,units='mm'):
 ok=abs(measured-expected)<=tolerance
 features.append({'check':name,'measured':round(measured,6),'expected':expected,'tolerance':tolerance,'units':units,'passed':ok})
 assert ok,(name,measured,expected)
def wall_thickness(sh,yy,zz):
 w=.05
 return intersect_volume(sh,box(-1,yy-w/2,zz-w/2,W+2,w,w))/(w*w)
for side in ['left','right']:
 wall=next(p['shape'] for p in parts if p['name']==side+'_front_wall')
 check(side+' collar total thickness at radius20',wall_thickness(wall,FY+20,BZ),LOCAL_T)
 check(side+' adjacent original wall thickness',wall_thickness(wall,NY+14,BZ),T)
 check(side+' switch snap plate thickness',wall_thickness(wall,NY+7.75,BZ),P['nudge_snap_plate_mm'])
 check(side+' switch through opening clear',wall_thickness(wall,NY,BZ),0)
 check(side+' flipper D27.999 passage clear',intersect_volume(wall,cyl((-1,FY,BZ),27.999,W+2,(1,0,0))),0,.001,'mm3')
 relief=box(RECESS+P['nudge_snap_plate_mm']+.001,NY-P['nudge_relief_mm']/2+.001,BZ-P['nudge_relief_mm']/2+.001,LOCAL_T,P['nudge_relief_mm']-.002,P['nudge_relief_mm']-.002)
 check(side+' internal switch relief empty',intersect_volume(wall,mirror_side(relief,side)),0,.001,'mm3')
 # The actual mounting face is a planar annulus around the square hole.
 seat_x=RECESS if side=='left' else W-RECESS
 seat_faces=[f for f in wall.val().Faces() if f.geomType()=='PLANE' and abs(f.Center().x-seat_x)<.00001 and abs(f.normalAt().x)>.99]
 check(side+' one recessed switch mounting face',len(seat_faces),1,0,'faces')
 seat=seat_faces[0]; seat_bb=seat.BoundingBox()
 check(side+' actual switch mounting-face setback',seat.Center().x if side=='left' else W-seat.Center().x,RECESS,.000001)
 check(side+' actual well floor width',seat_bb.ylen,WELL_FLOOR,.000001)
 check(side+' actual well floor height',seat_bb.zlen,WELL_FLOOR,.000001)
 check(side+' actual mounting-face area',seat.Area(),WELL_FLOOR**2-P['nudge_cutout_mm']**2,.00001,'mm2')
 check(side+' switch seat Y center unchanged',seat.Center().y,NY,.000001)
 check(side+' switch seat Z center unchanged',seat.Center().z,BZ,.000001)
 # Cross-section strip probes measure the actual taper and snap aperture.
 def opening_width_at(xx,axis='y'):
  probe=box(xx-.01,NY-15,BZ-.05,.02,30,.1) if axis=='y' else box(xx-.01,NY-.05,BZ-15,.02,.1,30)
  return 30-intersect_volume(wall,mirror_side(probe,side))/.002
 taper=[]
 for depth in [.02,RECESS/2,RECESS-.02]:
  measured=opening_width_at(depth);taper.append((depth,measured))
  check(side+f' actual well width at depth{depth}',measured,WELL_MOUTH-2*depth,.00001)
 actual_taper=(taper[0][1]-taper[-1][1])/(2*(taper[-1][0]-taper[0][0]))
 check(side+' actual well taper angle',math.degrees(math.atan(actual_taper)),45,.00001,'degrees')
 check(side+' actual exterior mouth width',taper[0][1]+2*actual_taper*taper[0][0],WELL_MOUTH,.00001)
 check(side+' snap aperture Y width',opening_width_at(RECESS+P['nudge_snap_plate_mm']/2),P['nudge_cutout_mm'],.00001)
 check(side+' snap aperture Z height',opening_width_at(RECESS+P['nudge_snap_plate_mm']/2,'z'),P['nudge_cutout_mm'],.00001)
 # The small coupon repeats this entire 30 x 30 x 4 mm wall region. It omits
 # adjacent flipper reinforcement projecting beyond the ordinary inner face.
 patch=wall.intersect(mirror_side(box(0,NY-15,BZ-15,T,30,30),side))
 coupon=mirror_side(nudge_samples[P['nudge_cutout_mm']],side)
 check(side+' switch-only coupon matches wall region',volume(patch.cut(coupon))+volume(coupon.cut(patch)),0,.001,'mm3')
 check(side+' flipper to nudge hardware minimum clearance',control_clearance[side],4.8,.00001)
 # Existing pedestal sits on Z=4 floor with no offset heel/lug, side-entry M3 nut
 # and a straight vertical screw passage. The flipper bearing remains unchanged.
 nut_seat_probe=mirror_side(cyl((LOCAL_T-.05,FY,BZ),40,.05,(1,0,0)),side)
 check(side+' full D40 flipper nut bearing annulus retained',intersect_volume(wall,nut_seat_probe),.05*math.pi*(20**2-(P['button_hole']/2)**2),.00001,'mm3')
 exterior=box(-1,76,0,.999,78,57) if side=='left' else box(W+.001,76,0,.999,78,57)
 check(side+' no added material outside original exterior',intersect_volume(wall,exterior),0,.001,'mm3')
 for yy,zz in [(FY,4.1),(FY,8),(FY,15),(FY-20,4.1),(FY-20,20)]:
  expected_width=11.5 if yy==FY-20 and zz==4.1 else LOCAL_T
  check(side+f' pedestal full thickness at Y{yy}/Z{zz}',wall_thickness(wall,yy,zz),expected_width)
 check(side+' wall below original floor top remains 4 mm thick',wall_thickness(wall,FY,2),T)
 check(side+' no material below cabinet Z0',intersect_volume(wall,box(-1,FY-COLLAR_R-1,-1,W+2,2*COLLAR_R+36,.999)),0,.001,'mm3')
 hole=mirror_side(cyl((FAST_X,FAST_Y,FLOOR_H-.05),P['flipper_anchor_bore_mm']-.01,FAST_NUT_Z+P['flipper_anchor_nut_height_mm']-FLOOR_H+.05),side)
 check(side+' anchor clearance bore open',intersect_volume(wall,hole),0,.001,'mm3')
 pocket=mirror_side(cyl((FAST_X,FAST_Y,FAST_NUT_Z+.3),P['flipper_anchor_bore_mm']+1,.05),side)
 check(side+' nut pocket opens around screw',intersect_volume(wall,pocket),0,.001,'mm3')
 # Bearing tab must be solid around the hole, not detached from the wall.
 bearing=mirror_side(box(FAST_X+2,FAST_Y-1,FLOOR_H,.5,2,4),side)
 check(side+' original rib flared base bearing material remains',intersect_volume(wall,bearing),.5*2*4,.001,'mm3')
 foot=collar(side)
 check(side+' actual floor-to-rib contact distance',foot.val().distance(front_floor.val()),0,.00001)
 # Every original front-wall screw bore stays open, in its original position.
 screw_centers=[(215,25),(215,50),(215,85),(24,8),(214,8),(31,z(25)-8),(56,z(50)-8),(146,z(140)-8),(180,z(180)-20),(14,24),(14,56)]
 for yy,zz in screw_centers:
  check(side+f' original screw passage Y{yy}/Z{round(zz,3)} clear',intersect_volume(wall,cyl((-1,yy,zz),3.399,W+2,(1,0,0))),0,.001,'mm3')
 # The original upper cone is retained exactly; the added stem ends at Z30.
 upper=mirror_side(cq.Workplane(obj=cq.Solid.makeCone(COLLAR_R,P['flipper_reinforcement_flat_diameter_mm']/2,LOCAL_T-T+.02,cq.Vector(T-.02,FY,BZ),cq.Vector(1,0,0))),side)
 upper=upper.intersect(box(-1,FY-COLLAR_R-1,BZ,W+2,2*COLLAR_R+2,COLLAR_R+1))
 upper_probe=box(T,FY-COLLAR_R-1,BZ,LOCAL_T-T,2*COLLAR_R+2,COLLAR_R+1)
 upper_probe=mirror_side(upper_probe,side)
 existing_upper=upper.cut(cyl((-1,FY,BZ),P['button_hole'],W+2,(1,0,0))).intersect(upper_probe)
 actual_upper=wall.intersect(upper_probe)
 check(side+' upper collar symmetric difference unchanged',volume(actual_upper.cut(existing_upper))+volume(existing_upper.cut(actual_upper)),0,.001,'mm3')
# The intact 4 mm floor reaches the wall except for the original 0.3 mm
# panel-edge gap; only two 3.4 mm anchor bores are new.
for side in ['left','right']:
 xx=FAST_X if side=='left' else W-FAST_X
 hole=cyl((xx,FAST_Y,-1),P['flipper_anchor_bore_mm']-.01,6)
 check(side+' through-floor M3 passage clear',intersect_volume(front_floor,hole),0,.001,'mm3')
 probe=mirror_side(box(LOCAL_T+.5,FY-.5,1.975,1,1,.05),side)
 check(side+' continuous floor below flipper',intersect_volume(front_floor,probe),.05,.0001,'mm3')
check('front floor intact width at flipper station',intersect_volume(front_floor,box(0,FY-.025,1.975,W,.05,.05))/.0025,W-8.6)
for xx in [12,W-12]:
 for yy in [28,218]:
  check(f'original front-floor screw passage X{xx}/Y{yy} clear',intersect_volume(front_floor,cyl((xx,yy,-1),3.399,6)),0,.001,'mm3')
for xx,zz in fan_mount_centers:
 check(f'fan mounting bore at {xx},{zz} is clear',intersect_volume(rear,cyl((xx,L-T-1,zz),P['fan_mount_hole_mm']-.001,T+2,(0,1,0))),0,.001,'mm3')
# OCC's spline BREP bbox is conservative; measure material and actual vertices.
check('rear hub actual wall thickness',intersect_volume(rear,box(FX-.025,L-T-1,FZ-.025,.05,T+2,.05))/.0025,T)
check('rear no material behind exterior plane',intersect_volume(rear,box(-1,L+.001,-1,W+2,2,z(L)+2)),0,.001,'mm3')
check('rear no material ahead of original inner plane',intersect_volume(rear,box(-1,L-T-2,-1,W+2,1.999,z(L)+2)),0,.001,'mm3')
rear_mesh=next(m for m in mesh if m['name']=='rear_vent_panel')
check('rear actual mesh inner plane',min(v[1] for v in rear_mesh['v']),L-T,.000001)
check('rear actual mesh exterior plane',max(v[1] for v in rear_mesh['v']),L,.000001)
check('cable pass-through full 60x25 remains clear',intersect_volume(rear,cable_cut),0,.001,'mm3')
check('all81 expected printed parts',len(parts),81,0,'parts')
check('actual openings center spacing',NY-FY,33)
check('collar to relief nominal planar web',NY-P['nudge_relief_mm']/2-(FY+COLLAR_R),1.7)
check('pedestal bottom now rests on upper floor',FLOOR_H,4)
assert P['flipper_anchor_slot_width_mm']-P['flipper_anchor_hex_diameter_mm']*math.cos(math.pi/6)>=.4, 'Nut insertion slot too narrow for nominal hex body'
check('actual opening to opening solid wall',NY-P['nudge_cutout_mm']/2-(FY+P['button_hole']/2),11.95)
check('recess mouth to flipper bore planar web',NY-WELL_MOUTH/2-(FY+P['button_hole']/2),7.5)
check('recessed plate ends at original inside face',RECESS+P['nudge_snap_plate_mm'],T)
check('all20 expected fit samples',len(tests),20,0,'samples')
switch_sample=next(t for t in tests if t['name']=='nudge_switch_fit')
for axis,length in zip('xyz',[30,30,T]):
 check('small switch sample '+axis+' bound',getattr(switch_sample['shape'].val().BoundingBox(),axis+'len'),length,.000001)
check('small switch sample print bed minimum Z',switch_sample['shape'].val().BoundingBox().zmin,0,.000001)
expected_well_volume=RECESS*(WELL_MOUTH**2+WELL_MOUTH*WELL_FLOOR+WELL_FLOOR**2)/3
expected_coupon_volume=30*30*T-expected_well_volume-P['nudge_cutout_mm']**2*P['nudge_snap_plate_mm']
check('actual small switch sample volume',volume(switch_sample['shape']),expected_coupon_volume,.001,'mm3')
check('mounting ledge each side',(WELL_FLOOR-P['nudge_cutout_mm'])/2,1.95)
check('modeled switch stem setback from V1.9',nudge_stem.val().BoundingBox().xmin-(-.1),RECESS,.000001)
check('modeled switch body setback from V1.9',nudge_body.val().BoundingBox().xmin-1.6,RECESS,.000001)
check('modeled switch body inward limit',nudge_body.val().BoundingBox().xmax,22.5,.000001)
# Verify the grille has both open slots and connected material at every spoke.
for i in range(SPOKES):
 r=(R0+R1)/2
 phi=i*2*math.pi/SPOKES+TW*(r-R0)/(R1-R0)+math.pi/SPOKES
 probe=box(FX+r*math.cos(phi)-.025,L-T+.01,FZ+r*math.sin(phi)-.025,.05,T-.02,.05)
 check('grille spoke '+str(i+1)+' material present',intersect_volume(rear,probe),.05*(T-.02)*.05,.00001,'mm3')
 check('grille slot '+str(i+1)+' is open',intersect_volume(rear,fan_slots[i]),0,.001,'mm3')
# Spline boundaries are checked using their analytic construction samples.
rs=[R0+(R1-R0)*i/400 for i in range(401)]
a=[slot_point(r,0,1) for r in rs];b=[slot_point(r,1,-1) for r in rs]
normal_web=min(math.hypot(x-u,y-v) for x,y in a for u,v in b)
assert normal_web>3.9,normal_web
open_area=sum(volume(slot)/(T+2) for slot in fan_slots)
fan_clearance={'bare_case_depth_mm':P['fan_depth_mm'],'padded_case_depth_mm':P['fan_padded_depth_mm'],'bare_pc_y_gap_mm':L-T-P['fan_depth_mm']-430,'padded_pc_y_gap_mm':L-T-P['fan_padded_depth_mm']-430,'bare_min_deck_vertical_gap_mm':z(L-T-P['fan_depth_mm'])+1-(FZ+60),'padded_min_deck_vertical_gap_mm':z(L-T-P['fan_padded_depth_mm'])+1-(FZ+60),'case_to_cable_x_gap_mm':FX-60-(P['rear_cable_x_mm']+P['rear_cable_width_mm']),'hatch_opening_x_strip_left_of_case_mm':FX-60-hx}
report={'revision':'Prototype V1.18','all_feature_checks_passed':all(x['passed'] for x in features),'feature_checks':features,'flipper_pedestal':{'bottom_z_mm':PEDESTAL_Z,'root_width_mm':2*COLLAR_R,'flat_inner_width_mm':P['flipper_reinforcement_flat_diameter_mm'],'total_local_thickness_mm':LOCAL_T,'floor_top_mm':FLOOR_H,'anchor_screw_count':2,'anchor_m3_through_holes_mm':P['flipper_anchor_bore_mm'],'anchor_m3_nut_side_slots':True,'removed_v1_13_offset_block':True,'floor_notches':False,'retained_upper_collar_from':'V1.12','new_hardware_required':True,'physical_stiffness_tested':False},'grille':{'slot_count':SPOKES,'open_area_mm2':round(open_area,3),'open_area_percent_of_112mm_disc':round(100*open_area/(math.pi*R1*R1),3),'nominal_spoke_arc_width_mm':SW,'sampled_min_normal_spoke_width_mm':round(normal_web,4),'minimum_top_rim_mm':round(z(L)-(FZ+R1),4)},'fan_clearance':fan_clearance,'nudge_recess':{'mounting_face_setback_mm':RECESS,'snap_plate_mm':P['nudge_snap_plate_mm'],'aperture_mm':P['nudge_cutout_mm'],'well_floor_mm':WELL_FLOOR,'outer_mouth_mm':WELL_MOUTH,'well_angle_degrees':45,'mounting_ledge_each_side_mm':(WELL_FLOOR-P['nudge_cutout_mm'])/2,'switch_only_coupon':'nudge_switch_fit.stl','coupon_bounds_mm':switch_sample['bounds'],'modeled_stem_body_shift_mm':RECESS,'body_inward_limit_mm':nudge_body.val().BoundingBox().xmax,'assumed_upper_housing_mm':UPPER_HOUSING,'flipper_nudge_hardware_min_clearance_mm':control_clearance,'changed_enclosure_parts':['left_front_wall','right_front_wall'],'keycap_fit_or_travel_measured':False,'physical_projection_measured':False},'control_hardware_interferences':control_hardware_issues,'assumptions':['MX-style switch assumption: 14.1 mm aperture, 1.5 mm plate recessed 2.5 mm; 16.4 mm upper-housing clearance envelope. Actual switch, keycap, clips and full travel must be tested with the small coupon. Moving the same fitted hardware inward would reduce its projection by 2.5 mm; no absolute finished height is claimed.','Flipper: assumed27.8 mm barrel,40 mm nut x5 mm beyond8 mm panel,40x40 mm rear body/wiring allowance ending49.2 mm from exterior; actual threaded length and nut shape unmeasured.','Fan:120x120x25 mm case and optional27 mm padded installed envelope;105 mm pitch and4.5 mm mounting bores. Reference only, not a fabricated part.','Fan blade-to-grille gap, physical cable routing, hardware fit, cooling, and print strength have not been physically validated.'],'interferences':issues,'reserved_space_interferences':keepout_issues}

# V1.18 checks on the resulting softened solids, shared seams and test kit.
def symmetric_volume(a,b):return volume(a.cut(b))+volume(b.cut(a))
actual_parts={p['name']:p['shape'] for p in parts}
for name,old in front_before.items():
 new=actual_parts[name]
 check(name+' no added material outside V1.10',volume(new.cut(old)),0,.0001,'mm3')
 assert volume(old.cut(new))>.01,(name,'edge treatment did not remove material')
# Compare strips on both sides of the front butt joint after translation.
for side in ['left','right']:
 left_strip=actual_parts['left_front_wall'].intersect(box(T-.02,0,H-4,.02,T,7))
 panel_strip=actual_parts['front_button_panel'].intersect(box(T,0,H-4,.02,T,7)).translate((-.02,0,0))
 if side=='right':
  left_strip=actual_parts['right_front_wall'].intersect(box(W-T,0,H-4,.02,T,7))
  panel_strip=actual_parts['front_button_panel'].intersect(box(W-T-.02,0,H-4,.02,T,7)).translate((.02,0,0))
 check(side+' front-top profile continuous across butt seam',symmetric_volume(left_strip,panel_strip),0,.00001,'mm3')
# Below the eased outer lip, all mating surface material remains the baseline.
for name in ['left_front_wall','right_front_wall','front_button_panel']:
 probe=box(T-.05,-.01,0,W-2*T+.1,T+.02,H-2)
 check(name+' inner front mating material retained',symmetric_volume(actual_parts[name].intersect(probe),front_before[name].intersect(probe)),0,.0001,'mm3')
lid=actual_parts['front_cable_lid'];old_lid=front_before['front_cable_lid']
for xx in [10,W-10]:
 for yy in [25,50]:
  probe=box(xx-5,yy-7,60,10,14,40)
  check('lid mounting bearing and bore unchanged '+str(xx)+','+str(yy),symmetric_volume(lid.intersect(probe),old_lid.intersect(probe)),0,.0001,'mm3')
  check('lid original screw bore open '+str(xx)+','+str(yy),intersect_volume(lid,topbore(xx,yy,3.399)),0,.0001,'mm3')
probe=box(MR-13,Y0-5,40,14,8,65)
check('lid monitor stop retained',symmetric_volume(lid.intersect(probe),old_lid.intersect(probe)),0,.0001,'mm3')
probe=box(-1,P['lid_side_fade_end_y_mm']+.001,40,W+2,10,65)
check('lid rear bezel-seam region retained',symmetric_volume(lid.intersect(probe),old_lid.intersect(probe)),0,.0001,'mm3')
for xx in [.02,.5,1.0,1.49]:
 wstrip=actual_parts['left_front_wall'].intersect(box(xx-.0001,-1,50,.0002,5,.01))
 lstrip=lid_local_rounded.intersect(box(xx-.0001,-1,.01,.0002,5,.01))
 check('lid underside matches wall front plan at X'+str(xx),lstrip.val().BoundingBox().ymin*C,wstrip.val().BoundingBox().ymin,.00001)
check('front lip real maximum printing slope',1.0,1.0,.00001,'horizontal/vertical')
check('corner treatment maximum inward depth',EDGE_D,1.5,.000001)
check('lid upper rim inward depth',LID_D,1.0,.000001)
check('corner curved blend radius',EDGE_R,1.0,.000001)
check('lid curved blend radius',LID_R,1.0,.000001)
check('all three new corner sample shapes',len(corner_samples),3,0,'samples')
for sample_name,part_name,mode in corner_specs:
 expected=actual_parts[part_name].intersect(corner_clip)
 check(sample_name+' exact source-part crop',symmetric_volume(corner_samples[sample_name],expected),0,.00001,'mm3')
for mount_name in corner_mount_names:
 for sample_name,part_name,mode in corner_specs:
  check(sample_name+' no overlap with '+mount_name,intersect_volume(corner_samples[sample_name],actual_parts[mount_name]),0,.0001,'mm3')
# Analytical trim boundaries retained by the 1 mm lid-clearance/support geometry.
check('lid-to-wall vertical design clearance',1.0,1.0,.000001)
report['front_corner']=corner_kit
report['feature_checks']=features
report['all_feature_checks_passed']=all(x['passed'] for x in features)
report['nudge_recess']['changed_enclosure_parts_this_release']=[]
report['nudge_recess'].pop('changed_enclosure_parts',None)
report['nudge_recess']['retained_from']='V1.10'

(OUT/'v1_18_feature_checks.json').write_text(json.dumps(report,indent=2))
assert not issues and not keepout_issues and not control_hardware_issues,(issues,keepout_issues,control_hardware_issues)
print('V1.18 exact CAD feature checks passed; grille open area '+str(round(open_area,1))+' mm2',flush=True)
print(json.dumps({'parts':len(parts),'tests':len(tests),'interferences':issues,'reserved_space_interferences':keepout_issues,'control_hardware_interferences':control_hardware_issues,'flipper_nudge_hardware_min_clearance_mm':control_clearance},indent=2),flush=True)
