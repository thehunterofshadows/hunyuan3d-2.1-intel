"""Deterministic railgun modeled from the approved concept; Blender 3.4+."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
OUT=Path('/work/assets/railgun-built')
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,metal=0,rough=.4,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m
graphite=mat('Graphite ceramic armor',(.055,.068,.082),.65,.32)
dark=mat('Recessed black alloy',(.014,.021,.027),.7,.38)
silver=mat('Satin titanium',(.39,.47,.53),.86,.27)
edge=mat('Machined edge alloy',(.19,.25,.30),.85,.3)
rubber=mat('Textured black grip',(.023,.029,.035),0,.78)
cyan=mat('Cyan accelerator emission',(.001,.30,.65),.05,.28,1.3)
orange=mat('Safety orange',(.95,.22,.025),.15,.37)
boltmat=mat('Dark fasteners',(.055,.065,.072),.9,.3)
parts=[]
def finish(o,name,material,bevel=.015):
 o.name=name;o.data.materials.append(material)
 if bevel:
  mod=o.modifiers.new('Manufactured edge bevel','BEVEL');mod.width=bevel;mod.segments=3
  mod=o.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
 for p in o.data.polygons:p.use_smooth=True
 o.data.use_auto_smooth=True;o.data.auto_smooth_angle=math.radians(40)
 parts.append(o);return o
def box(name,loc,scale,material,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.dimensions=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,material,bevel)
def profile(name,points,depth,material,y=0,bevel=.015):
 # points x,z clockwise or counterclockwise, extruded along Y.
 n=len(points);verts=[(x,y+d,z) for d in [-depth/2,depth/2] for x,z in points]
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 # Robust normals for arbitrary profile winding.
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
 return finish(o,name,material,bevel)
def cyl(name,loc,radius,depth,material,axis='Y',vertices=24,bevel=.004):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
 o=bpy.context.object
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 elif axis=='X':o.rotation_euler[1]=math.pi/2
 return finish(o,name,material,bevel)
def screw(x,z,y):
 cyl('Hex socket fastener',(x,y,z),.025,.012,boltmat,vertices=12)
 # Inset socket sits visibly outside head.
 cyl('Hex socket recess',(x,y+(.007 if y>0 else -.007),z),.012,.003,dark,vertices=6,bevel=0)

# Continuous accelerator chassis, two open rails with a luminous central core.
box('Accelerator inner spine',(-1.25,0,.22),(2.8,.19,.14),dark)
box('Continuous energy core',(-1.35,0,.22),(2.6,.11,.09),cyan,.02)
for side in [-1,1]:
 box('Exposed energy conduit',(-1.35,side*.103,.22),(2.6,.025,.055),cyan,.012)
 box('Upper induction conduit',(-1.35,side*.12,.35),(2.6,.035,.035),cyan,.009)
 box('Lower induction conduit',(-1.35,side*.12,.08),(2.6,.035,.035),cyan,.009)
for z in [.54,-.10]:
 profile('Long beveled accelerator rail',[(-2.65,z-.095),(-2.72,z+.045),(-2.58,z+.11),(-.05,z+.11),(.19,z-.04),(.04,z-.095)],.37,graphite,bevel=.025)
 for side in [-1,1]:
  box('Rail titanium edge',(-1.34,side*.191,z+.068),(2.54,.026,.035),silver,.009)
  box('Rail recessed seam',(-1.28,side*.195,z-.02),(2.32,.009,.025),dark,.003)
  for x in [-2.42,-1.70,-.95,-.26]:screw(x,z-.035,side*.208)
# Repeated magnetic coil braces, open gaps preserve the silhouette.
for i,x in enumerate([-2.28,-1.65,-1.02,-.39]):
 for side in [-1,1]:
  profile('Magnetic coil housing '+str(i),[(x-.075,.07),(x-.11,.15),(x-.11,.32),(x-.06,.4),(x+.06,.4),(x+.11,.32),(x+.11,.15),(x+.075,.07)],.075,edge,y=side*.11,bevel=.012)
  box('Cyan induction strip',(x,side*.153,.235),(.075,.012,.23),cyan,.01)
# Muzzle end with inset apertures and silver perimeter.
profile('Muzzle frame',[(-2.78,-.24),(-2.88,-.12),(-2.88,.57),(-2.78,.69),(-2.56,.69),(-2.52,.57),(-2.52,-.12),(-2.61,-.24)],.49,edge,bevel=.03)
for z in [-.075,.52]:
 box('Muzzle dark aperture',(-2.889,0,z),(.018,.33,.19),dark,.035)
 box('Muzzle energy aperture',(-2.9,0,z),(.02,.20,.055),cyan,.012)
for side in [-1,1]:
 box('Muzzle side armor',(-2.70,side*.249,.22),(.115,.025,.55),silver,.012)
 box('Muzzle cyan marker',(-2.775,side*.267,.22),(.035,.008,.25),cyan,.006)

# Angular receiver; broad clean panels with inset dark energy channel.
profile('Main receiver',[(-.32,.05),(-.37,.36),(-.12,.68),(.75,.68),(1.08,.44),(1.10,.03),(.83,-.25),(.14,-.25)],.48,graphite,bevel=.035)
profile('Top armored bridge',[(-.32,.56),(-.04,.81),(.79,.81),(1.09,.58),(.88,.54),(.68,.68),(.04,.68),(-.13,.54)],.39,dark,bevel=.018)
box('Top sight rail',(.34,0,.803),(.65,.18,.055),edge,.009)
for x in [-.20,-.08,.04,.16,.28,.40,.52,.64,.76]:
 box('Top cooling rib',(x,0,.72),(.045,.37,.045),graphite,.008)
for side in [-1,1]:
 y=side*.251
 profile('Receiver recessed channel',[(.01,.29),(.18,.48),(.79,.48),(.91,.35),(.79,.20),(.17,.20)],.024,dark,y=y,bevel=.015)
 box('Receiver cyan energy window',(.48,side*.268,.34),(.57,.014,.055),cyan,.015)
 profile('Diagonal titanium armor',[(-.34,.22),(-.31,.49),(-.10,.68),(.23,.68),(.37,.52),(.16,.28),(-.05,.09)],.045,silver,y=side*.285,bevel=.02)
 profile('Diagonal dark panel',[(-.23,.25),(-.19,.46),(-.04,.59),(.14,.59),(.23,.51),(.06,.33),(-.08,.19)],.012,graphite,y=side*.312,bevel=.012)
 box('Lower receiver silver trim',(.42,side*.252,-.16),(.59,.025,.045),edge,.01)
 for z in [.43,.32,.21]:box('Charge indicator',(.94,side*.26,z),(.065,.014,.047),cyan,.007)
 cyl('Stock hinge outer ring',(1.02,side*.266,.04),.126,.045,edge,vertices=32,bevel=.009)
 cyl('Stock hinge inset',(1.02,side*.293,.04),.086,.016,dark,vertices=32)
 cyl('Stock hinge hub',(1.02,side*.305,.04),.044,.012,boltmat,vertices=12)
 for x,z in [(-.19,.52),(.13,.54),(.73,.58),(.81,-.12),(.18,-.16)]:screw(x,z,side*.32)
 profile('Orange receiver accent',[(.77,.67),(.82,.70),(.99,.53),(.94,.50)],.015,orange,y=side*.253,bevel=.003)

# Stock core panel with separate perimeter beams.
profile('Stock inset armor',[(1.28,.24),(2.02,.25),(2.02,-.18),(1.86,-.17)],.16,dark,bevel=.015)
for side in [-1,1]:
 profile('Stock inset diagonal',[(1.39,.21),(1.48,.22),(1.98,-.10),(1.98,-.16)],.02,graphite,y=side*.09,bevel=.01)
# Stock perimeter.
profile('Stock upper beam',[(1.05,.43),(1.37,.47),(2.12,.42),(2.20,.30),(2.02,.25),(1.41,.29),(1.13,.24)],.30,graphite,bevel=.025)
profile('Stock lower diagonal',[(1.14,.03),(1.25,.15),(2.03,-.20),(2.18,-.20),(2.18,-.36),(1.98,-.36)],.27,graphite,bevel=.025)
profile('Stock rear brace',[(1.98,-.37),(2.20,-.37),(2.25,.38),(2.14,.48),(1.99,.36)],.36,edge,bevel=.03)
profile('Rubber shoulder pad',[(2.17,-.40),(2.30,-.36),(2.34,.35),(2.26,.45),(2.17,.42)],.40,rubber,bevel=.025)
for side in [-1,1]:
 box('Stock top silver insert',(1.72,side*.158,.386),(.61,.016,.05),silver,.012)
 profile('Stock orange marker',[(2.02,-.24),(2.10,-.20),(2.12,.08),(2.04,.15)],.016,orange,y=side*.192,bevel=.006)
 for z in [-.25,-.13,-.01,.11,.23]:box('Butt pad groove',(2.31,side*.18,z),(.025,.035,.025),dark,.003)

# Pistol grip, trigger and open guard.
profile('Pistol grip frame',[(.56,-.18),(.97,-.20),(.65,-1.00),(.38,-1.06),(.22,-.93)],.29,edge,bevel=.025)
profile('Pistol rubber grip',[(.56,-.29),(.83,-.31),(.58,-.94),(.41,-.98),(.32,-.88)],.31,rubber,bevel=.02)
for side in [-1,1]:
 for i in range(6):
  x=.46+i*.033;z=-.88+i*.087
  p=box('Pistol grip traction',(x,side*.16,z),(.18,.018,.025),graphite,.004);p.rotation_euler[1]=-.27
 profile('Grip base titanium',[(.25,-.94),(.38,-1.08),(.66,-1.02),(.67,-.95),(.41,-.99)],.035,silver,y=side*.15,bevel=.008)
profile('Trigger guard',[(-.02,-.23),(.08,-.27),(.16,-.55),(.47,-.56),(.51,-.63),(.09,-.64),(-.02,-.46)],.17,edge,bevel=.015)
profile('Orange trigger',[(.35,-.25),(.43,-.27),(.39,-.44),(.28,-.49),(.25,-.44),(.32,-.37)],.10,orange,bevel=.012)
# Front grip with strong mount.
profile('Foregrip mount',[(-1.28,-.2),(-.69,-.2),(-.74,-.37),(-1.20,-.37)],.34,graphite,bevel=.025)
profile('Foregrip frame',[(-1.16,-.34),(-.87,-.34),(-1.04,-.98),(-1.29,-.98)],.25,edge,bevel=.025)
profile('Foregrip rubber',[(-1.13,-.43),(-.96,-.43),(-1.09,-.90),(-1.22,-.90)],.27,rubber,bevel=.015)
for side in [-1,1]:
 for i in range(5):
  p=box('Foregrip traction',(-1.16+i*.021,side*.14,-.84+i*.076),(.14,.018,.023),graphite,.004);p.rotation_euler[1]=-.22
 screw(-1.0,-.27,side*.18)
 box('Foregrip orange mark',(-.84,side*.18,-.28),(.06,.012,.04),orange,.004)

# Weapon origin and named gameplay attachment markers.
root=bpy.data.objects.new('Railgun_Root',None);bpy.context.collection.objects.link(root)
for o in parts:o.parent=root
for name,loc in [('Muzzle',(-2.92,0,.22)),('RightHand',(.6,0,-.5)),('LeftHand',(-1.1,0,-.55))]:
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=root;o.location=loc
# Keep authoring dimensions explicit: export weapon ~1.3m long.
root.scale=(.25,.25,.25)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
root.select_set(True)
for o in root.children:o.select_set(True)
# Save editable source with all bevel modifiers and individually named parts.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'railgun.blend'))
deps=bpy.context.evaluated_depsgraph_get()
triangles=sum(sum(len(p.vertices)-2 for p in o.evaluated_get(deps).data.polygons) for o in parts)
original_count=len(parts)
# Apply bevel/normal modifiers then batch by material for eight draw calls.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.convert(target='MESH')
converted=list(bpy.context.selected_objects)
groups=[(m,[o for o in converted if o.data.materials[0]==m]) for m in [dark,cyan,graphite,silver,edge,orange,rubber,boltmat]]
for material,group in groups:
 if not group:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in group:o.select_set(True)
 bpy.context.view_layer.objects.active=group[0]
 bpy.ops.object.join();group[0].name=material.name
bpy.ops.object.select_all(action='DESELECT')
root.select_set(True)
for o in root.children:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'railgun.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True)
(OUT/'build-info.json').write_text(json.dumps({'triangles':triangles,'authoring_parts':original_count,'export_meshes':8,'length_m':1.305,'materials':8,'source':'procedural Blender hard-surface rebuild','rigged':False},indent=2))
print('RAILGUN_BUILD',triangles,'triangles',original_count,'authoring parts, 8 export meshes')
